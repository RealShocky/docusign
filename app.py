from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from flask_session import Session
import os
from dotenv import load_dotenv, find_dotenv
import tempfile
from database import init_db, Session as DBSession
from services.file_service import FileService
from services.template_service import TemplateService
from services.collaboration_service import CollaborationService
from services.ai_service import AIService
from models import User, Contract, Template
import openai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, SignHere, Tabs, Recipients, Text
import base64
import jwt
import time
from fpdf import FPDF
import json
import pdfplumber
import os

# Debug: Print current working directory
print("Current working directory:", os.getcwd())

# Load environment variables from .env file
load_dotenv()

# Force clear any existing API key
if 'OPENAI_API_KEY' in os.environ:
    del os.environ['OPENAI_API_KEY']
    print("Cleared existing OPENAI_API_KEY from environment")

# Debug: Find all .env files
print("Looking for .env files...")
env_file = find_dotenv()
print("Found .env file:", env_file)

# Load environment variables
load_dotenv(override=True)  # Add override=True to force override existing env vars

# Debug: Print environment sources
print("\nAPI Key Sources:")
print("1. From os.environ:", os.environ.get('OPENAI_API_KEY', 'Not found in os.environ'))
print("2. From os.getenv:", os.getenv('OPENAI_API_KEY', 'Not found in getenv'))
print("3. Direct from openai.api_key:", getattr(openai, 'api_key', 'Not set in openai'))

# Configure OpenAI - Force set from .env file
with open('.env', 'r') as f:
    for line in f:
        if line.startswith('OPENAI_API_KEY='):
            openai.api_key = line.split('=', 1)[1].strip()
            print("Set API key directly from .env file")
            break

# Debug: Print final OpenAI key
print("4. Final OpenAI API Key:", openai.api_key[:10] + '...' if openai.api_key else 'Not set')

# Debug: Print environment variables
print("Environment variables loaded:")
print("OPENAI_API_KEY:", os.getenv('OPENAI_API_KEY', 'Not found'))
print("FLASK_ENV:", os.getenv('FLASK_ENV', 'Not found'))

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5000", "http://localhost", "https://vibrationrobotics.com", "http://vibrationrobotics.com"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Session configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
app.config['SESSION_TYPE'] = 'null'  # Use memory-based sessions instead of filesystem
Session(app)

# Initialize database
init_db()

# Initialize services
upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(upload_folder, exist_ok=True)
file_service = FileService(upload_folder)
ai_service = AIService()

# DocuSign Configuration
app.config.update(
    DOCUSIGN_INTEGRATION_KEY=os.getenv('DOCUSIGN_INTEGRATION_KEY'),
    DOCUSIGN_USER_ID=os.getenv('DOCUSIGN_USER_ID'),
    DOCUSIGN_ACCOUNT_ID=os.getenv('DOCUSIGN_ACCOUNT_ID'),
    DOCUSIGN_PRIVATE_KEY_PATH='private.key',
    DOCUSIGN_AUTH_SERVER='account-d.docusign.com'
)

def get_jwt_token():
    try:
        private_key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'private.key')
        print(f"Reading private key from: {private_key_path}")
        
        with open(private_key_path, 'r') as key_file:
            private_key = key_file.read().strip()
            print("Successfully read private key")
        
        iat = int(time.time())
        exp = iat + 3600  # Token valid for 1 hour
        
        claims = {
            'iss': app.config['DOCUSIGN_INTEGRATION_KEY'],
            'sub': app.config['DOCUSIGN_USER_ID'],
            'iat': iat,
            'exp': exp,
            'aud': 'account-d.docusign.com',
            'scope': 'signature impersonation'
        }
        
        print("Generating JWT with claims:", claims)
        token = jwt.encode(claims, private_key, algorithm='RS256')
        print("Successfully generated JWT token")
        return token
        
    except Exception as e:
        print(f"Error generating JWT token: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def create_docusign_api_client():
    try:
        print("Creating DocuSign API client...")
        api_client = ApiClient()
        api_client.host = "https://demo.docusign.net/restapi"
        
        # Get private key bytes
        private_key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'private.key')
        print(f"Reading private key from: {private_key_path}")
        with open(private_key_path, 'rb') as key_file:
            private_key_bytes = key_file.read()
        
        print("Requesting JWT user token from DocuSign...")
        print(f"Integration Key: {app.config['DOCUSIGN_INTEGRATION_KEY']}")
        print(f"Auth Server: {app.config['DOCUSIGN_AUTH_SERVER']}")
        
        # Request token with required parameters
        response = api_client.request_jwt_user_token(
            app.config['DOCUSIGN_INTEGRATION_KEY'],  # client_id
            app.config['DOCUSIGN_USER_ID'],  # user_id
            app.config['DOCUSIGN_AUTH_SERVER'],  # oauth_host_name
            private_key_bytes,  # private_key_bytes
            3600  # expires_in (1 hour)
        )
        
        print("Successfully got access token from DocuSign")
        api_client.set_default_header("Authorization", f"Bearer {response.access_token}")
        return api_client
        
    except Exception as e:
        print(f"Error creating DocuSign API client: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def get_db():
    db = DBSession()
    try:
        return db
    finally:
        db.close()

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/js/<path:path>')
def serve_js(path):
    return send_from_directory('static/js', path)

@app.route('/js/components/<path:path>')
def serve_components(path):
    return send_from_directory('static/js/components', path)

@app.route('/callback')
def callback():
    return send_from_directory('static', 'callback.html')

# API routes start with /api
@app.route('/api/auth/docusign-config')
def get_docusign_config():
    return jsonify({
        "authUri": "https://account-d.docusign.com/oauth/auth",
        "responseType": "code",
        "scopes": ["signature", "impersonation"],
        "clientId": os.getenv('DOCUSIGN_CLIENT_ID'),
        "redirectUri": os.getenv('DOCUSIGN_REDIRECT_URI')
    })

# DocuSign Authentication Routes
@app.route('/api/contracts/upload', methods=['POST'])
def upload_contract():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        text = file_service.process_file(file)
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/analyze', methods=['POST'])
def analyze_contract():
    if not request.json or 'content' not in request.json:
        return jsonify({"error": "No contract text provided"}), 400
    
    try:
        contract_text = request.json['content']
        
        # Use OpenAI for analysis
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": """You are a legal contract analysis assistant. Analyze the contract and provide a detailed analysis in the following format:

## 📋 Summary
[Provide a clear, concise summary of the contract's purpose and main points in a professional tone]

## 🎯 Key Points
[List each key point with proper markdown formatting. Use bold for headers and explain each point clearly]

1. **Parties Involved**: [Details]
2. **Purpose**: [Details]
3. **Terms**: [Details]
[Continue with other relevant points...]

## 💡 Suggestions for Improvement
[Provide specific, actionable suggestions in a clear format]

1. **[Suggestion Title]**: [Detailed explanation]
2. **[Suggestion Title]**: [Detailed explanation]
[Continue with other suggestions...]

Note: Use proper markdown formatting:
- Bold (**) for important terms
- Lists for better readability
- Clear section breaks
- Professional tone throughout"""},
                {"role": "user", "content": f"Please analyze this contract:\n\n{contract_text}"}
            ],
            temperature=0.7
        )
        
        analysis = response.choices[0].message['content']
        
        return jsonify({
            "analysis": analysis,
            "success": True
        })
        
    except Exception as e:
        print("\nError occurred during analysis:")
        print("Current API Key:", openai.api_key[:10] + '...' if openai.api_key else 'Not set')
        print("Error details:", str(e))
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@app.route('/api/rewrite', methods=['POST'])
def rewrite_contract():
    if not request.json:
        return jsonify({"error": "No JSON data provided"}), 400
        
    content = request.json.get('content')
    instructions = request.json.get('instructions')
    
    print(f"\nReceived rewrite request:")
    print(f"Instructions: {instructions}")
    print(f"Content length: {len(content) if content else 0} characters")
    
    if not content or not instructions:
        return jsonify({"error": "Content and instructions are required"}), 400
    
    try:
        print("Calling OpenAI for contract rewriting...")
        # Use OpenAI for contract rewriting
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": """You are a legal document assistant specializing in contract modification. 
                Your task is to rewrite contracts according to the provided instructions while:
                - Maintaining legal validity and enforceability
                - Preserving the original intent and key terms
                - Using clear, precise legal language
                - Following standard contract formatting
                - Including all necessary clauses and sections"""},
                {"role": "user", "content": f"""Please rewrite this contract according to these instructions:

Instructions:
{instructions}

Original Contract:
{content}"""}
            ],
            temperature=0.7
        )
        
        rewritten = response.choices[0].message['content']
        print("Successfully rewrote contract")
        print(f"New length: {len(rewritten)} characters")
        
        return jsonify({
            "rewritten": rewritten,
            "success": True
        })
        
    except Exception as e:
        print("\nError occurred during rewrite:")
        print("Error details:", str(e))
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to rewrite contract: {str(e)}"}), 500

@app.route('/api/templates')
def get_templates():
    # Sample templates - in a real app, these would come from a database
    templates = [
        {
            'id': 'nda',
            'name': 'Non-Disclosure Agreement (NDA)',
            'description': 'A comprehensive NDA for protecting confidential information',
            'content': '''[Your Company Name]
MUTUAL NON-DISCLOSURE AGREEMENT

This Mutual Non-Disclosure Agreement (this "Agreement") is made and entered into as of [Date], by and between [Your Company Name], located at [Your Address] and [Other Party Name], located at [Other Party Address].

1. Definition of Confidential Information...'''
        },
        {
            'id': 'service',
            'name': 'Service Agreement',
            'description': 'A detailed contract for service providers and clients',
            'content': '''SERVICE AGREEMENT

This Service Agreement (the "Agreement") is made and entered into as of [Date], by and between:

Provider: [Provider Name], located at [Provider Address]
Client: [Client Name], located at [Client Address]

1. Services...'''
        },
        {
            'id': 'employment',
            'name': 'Employment Contract',
            'description': 'A comprehensive employment agreement template',
            'content': '''EMPLOYMENT AGREEMENT

This Employment Agreement (the "Agreement") is made and entered into as of [Date], by and between:

Employer: [Company Name], located at [Company Address]
Employee: [Employee Name], residing at [Employee Address]

1. Position and Duties...'''
        }
    ]
    return jsonify(templates)

# Template Routes
@app.route('/api/templates')
def list_templates():
    db = get_db()
    try:
        templates = db.query(Template).all()
        return jsonify([{
            'id': t.id,
            'name': t.name,
            'description': t.description,
            'category': t.category,
            'tags': [{'id': tag.id, 'name': tag.name} for tag in t.tags]
        } for t in templates])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/templates/<int:template_id>')
def get_template(template_id):
    db = get_db()
    try:
        template = db.query(Template).get(template_id)
        if not template:
            return jsonify({'error': 'Template not found'}), 404
        return jsonify({
            'id': template.id,
            'name': template.name,
            'description': template.description,
            'content': template.content,
            'category': template.category,
            'tags': [{'id': tag.id, 'name': tag.name} for tag in template.tags]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/templates', methods=['POST'])
def create_template():
    if not request.json:
        return jsonify({"error": "No data provided"}), 400
        
    db = get_db()
    template_service = TemplateService(db)
    
    template = template_service.create_template(
        name=request.json['name'],
        content=request.json['content'],
        description=request.json.get('description'),
        category=request.json.get('category'),
        tags=request.json.get('tags', [])
    )
    
    return jsonify({
        'id': template.id,
        'name': template.name,
        'description': template.description,
        'category': template.category,
        'tags': [tag.name for tag in template.tags]
    })

# Collaboration Routes
@app.route('/api/contracts/<int:contract_id>/comments', methods=['GET'])
def get_comments(contract_id):
    db = get_db()
    collaboration_service = CollaborationService(db)
    include_resolved = request.args.get('include_resolved', 'false').lower() == 'true'
    
    comments = collaboration_service.get_comments(contract_id, include_resolved)
    return jsonify([{
        'id': c.id,
        'content': c.content,
        'user': {
            'id': c.user.id,
            'name': c.user.name
        },
        'created_at': c.created_at.isoformat(),
        'resolved': c.resolved,
        'parent_id': c.parent_id
    } for c in comments])

@app.route('/api/contracts/<int:contract_id>/comments', methods=['POST'])
def add_comment(contract_id):
    if not request.json or 'content' not in request.json:
        return jsonify({"error": "No comment content provided"}), 400
        
    db = get_db()
    collaboration_service = CollaborationService(db)
    
    # TODO: Get actual user_id from session
    user_id = 1
    
    comment = collaboration_service.add_comment(
        contract_id=contract_id,
        user_id=user_id,
        content=request.json['content'],
        parent_id=request.json.get('parent_id')
    )
    
    return jsonify({
        'id': comment.id,
        'content': comment.content,
        'user': {
            'id': comment.user.id,
            'name': comment.user.name
        },
        'created_at': comment.created_at.isoformat(),
        'resolved': comment.resolved,
        'parent_id': comment.parent_id
    })

@app.route('/api/contracts/<int:contract_id>/versions', methods=['GET'])
def list_versions(contract_id):
    db = get_db()
    collaboration_service = CollaborationService(db)
    
    versions = collaboration_service.list_versions(contract_id)
    return jsonify([{
        'version': v.version,
        'created_at': v.created_at.isoformat(),
        'created_by': {
            'id': v.created_by.id,
            'name': v.created_by.name
        }
    } for v in versions])

@app.route('/api/contracts/<int:contract_id>/versions', methods=['POST'])
def create_version(contract_id):
    if not request.json or 'content' not in request.json:
        return jsonify({"error": "No content provided"}), 400
        
    db = get_db()
    collaboration_service = CollaborationService(db)
    
    # TODO: Get actual user_id from session
    user_id = 1
    
    version = collaboration_service.create_version(
        contract_id=contract_id,
        content=request.json['content'],
        created_by_id=user_id
    )
    
    return jsonify({
        'version': version.version,
        'created_at': version.created_at.isoformat(),
        'created_by': {
            'id': version.created_by.id,
            'name': version.created_by.name
        }
    })

@app.route('/api/contracts/<int:contract_id>/versions/compare', methods=['GET'])
def compare_versions(contract_id):
    version1 = request.args.get('v1', type=int)
    version2 = request.args.get('v2', type=int)
    
    if not version1 or not version2:
        return jsonify({"error": "Both versions must be specified"}), 400
        
    db = get_db()
    collaboration_service = CollaborationService(db)
    
    comparison = collaboration_service.compare_versions(contract_id, version1, version2)
    if not comparison:
        return jsonify({"error": "Could not compare versions"}), 404
        
    return jsonify(comparison)

@app.route('/api/analyze-signature-positions', methods=['POST'])
def analyze_signature_positions():
    if not request.json or 'content' not in request.json:
        return jsonify({"error": "No contract text provided"}), 400
    
    try:
        contract_text = request.json['content']
        
        # Use OpenAI for signature placement analysis
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": """You are a legal document analysis assistant specialized in determining optimal signature placements.
                Analyze the contract and identify the most appropriate locations for signatures based on:
                1. Standard signature conventions
                2. Legal requirements
                3. Document structure and formatting
                4. Number of signers
                
                Return a JSON array where each item contains:
                {
                    "description": "Detailed explanation of why this is a good signature location",
                    "anchor_text": "The text that precedes or indicates where the signature should go",
                    "offset_type": "before" or "after" (relative to anchor_text),
                    "align": "left", "right", or "center",
                    "signer_role": "The role of who should sign here (e.g., 'client', 'company', etc.)"
                }"""},
                {"role": "user", "content": f"Analyze this contract and determine optimal signature positions:\n\n{contract_text}"}
            ],
            temperature=0.7
        )
        
        # Extract the suggestions
        suggestions = response.choices[0].message['content']
        
        return jsonify({
            "success": True,
            "positions": suggestions
        })
        
    except Exception as e:
        print(f"Error analyzing signature positions: {str(e)}")
        return jsonify({"error": str(e)}), 500

def analyze_signature_locations(contract_text):
    """Use GPT to find exact signature locations in the contract"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": """You are an expert at analyzing legal documents for signature placements.
                Look for these common signature patterns:
                
                1. Basic signature line:
                   By: ____________________
                
                2. Role-based signatures with labels like:
                   - [PARTY A] / [PARTY B]
                   - [SERVICE PROVIDER] / [CLIENT]
                   - [COMPANY] / [EMPLOYEE]
                   - [SELLER] / [BUYER]
                   
                3. Additional fields like:
                   Name:
                   Title:
                   Date:
                
                For each signature location found, determine:
                1. The role (e.g., "provider", "client", "party_a", "party_b", "company", "employee", "seller", "buyer")
                2. The exact anchor text ("By: ___" or similar)
                3. Any additional context (role label above the signature)
                4. Whether it's a primary or secondary signer
                
                Return a JSON array of signature locations, each containing:
                {
                    "role": "The signer role (e.g., provider, client)",
                    "anchor_text": "The exact text that precedes the signature line",
                    "context": "The role label or surrounding text",
                    "is_primary": true/false,
                    "additional_fields": ["Name", "Title", "Date"] (if present)
                }"""},
                {"role": "user", "content": f"Find all signature locations in this contract:\n\n{contract_text}"}
            ],
            temperature=0
        )
        
        locations = json.loads(response.choices[0].message['content'])
        print("AI found signature locations:", locations)
        return locations
    except Exception as e:
        print(f"Error analyzing signature locations: {str(e)}")
        return None

def find_text_position_in_pdf(pdf_content, search_text):
    """Find the y-coordinate of specific text in the PDF"""
    try:
        print(f"Looking for text: '{search_text}' in PDF...")
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(pdf_content)
            tmp_file.flush()
            print(f"Created temporary PDF file: {tmp_file.name}")
            
            # Extract text and positions using pdfplumber
            with pdfplumber.open(tmp_file.name) as pdf:
                print("Opened PDF with pdfplumber")
                page = pdf.pages[0]  # Assume signatures are on first page
                words = page.extract_words(x_tolerance=3, y_tolerance=3)
                print(f"Found {len(words)} words on page")
                
                # Look for the search text
                for word in words:
                    if search_text.lower() in word['text'].lower():
                        print(f"Found match at: x={word['x0']}, y={word['y0']}")
                        # Return position, converting from PDF coordinates
                        return {
                            'x': word['x0'],
                            'y': word['y0'],
                            'page': 1
                        }
                print(f"Text '{search_text}' not found in PDF")
        return None
    except Exception as e:
        print(f"Error finding text position: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # Clean up temp file
        if 'tmp_file' in locals():
            os.unlink(tmp_file.name)
            print("Cleaned up temporary PDF file")

@app.route('/api/send', methods=['POST'])
def send_contract():
    if not request.json:
        return jsonify({"error": "No JSON data provided"}), 400
        
    contract_text = request.json.get('contract')
    signers = request.json.get('signers')
    use_ai_positioning = request.json.get('use_ai_positioning', False)
    
    if not contract_text or not signers:
        return jsonify({"error": "Contract and signers are required"}), 400

    try:
        # Convert contract text to PDF
        print("Converting contract to PDF...")
        pdf_bytes = create_pdf_from_text(contract_text)
        doc_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        print("Creating envelope definition...")
        docusign_signers = []
        
        # Try AI-based positioning if requested
        signature_positions = None
        if use_ai_positioning:
            print("Attempting AI-based signature positioning...")
            try:
                signature_locations = analyze_signature_locations(contract_text)
                if signature_locations:
                    signature_positions = []
                    for loc in signature_locations:
                        position = find_text_position_in_pdf(pdf_bytes, loc['anchor_text'])
                        if not position and 'context' in loc:
                            position = find_text_position_in_pdf(pdf_bytes, loc['context'])
                            if position:
                                position['y'] += 20  # Move down by 20 points
                        if position:
                            signature_positions.append({
                                'position': position,
                                'additional_fields': loc.get('additional_fields', [])
                            })
                    print(f"Found {len(signature_positions)} signature positions using AI")
            except Exception as e:
                print(f"AI positioning failed, falling back to default: {str(e)}")
                signature_positions = None
        
        # Use default positions if AI positioning failed or wasn't requested
        if not signature_positions:
            print("Using default signature positions...")
            # Standard PDF page is 612 x 792 points
            # Place signatures in bottom third of page with proper margins
            signature_positions = [
                {
                    'position': {
                        'x': 50,  # Left margin
                        'y': 650,  # About 142 points from bottom
                        'page': 1
                    },
                    'additional_fields': []
                },
                {
                    'position': {
                        'x': 350,  # Right side of page
                        'y': 650,  # Same vertical position
                        'page': 1
                    },
                    'additional_fields': []
                }
            ]
        
        # Add signers with their signature positions
        for i, signer in enumerate(signers, 1):
            print(f"Adding signer {i}: {signer['name']} ({signer['email']})")
            
            # Get position for this signer
            sig_data = signature_positions[min(i-1, len(signature_positions)-1)]
            position = sig_data['position']
            
            # Add signature field
            sign_here = SignHere(
                document_id="1",
                page_number=str(position['page']),
                recipient_id=str(i),
                x_position=str(int(float(position['x']))),
                y_position=str(int(float(position['y'])))
            )
            
            # Add name field
            name_text = Text(
                document_id="1",
                page_number=str(position['page']),
                recipient_id=str(i),
                x_position=str(int(float(position['x']) + 20)),  # Offset slightly from signature
                y_position=str(int(float(position['y']) - 30)),  # Place above signature
                font="helvetica",
                font_size="size11",
                value=signer['name']
            )
            
            # Add any additional fields from AI analysis
            additional_tabs = [name_text]
            y_offset = 30
            for field in sig_data['additional_fields']:
                additional_tabs.append(
                    Text(
                        document_id="1",
                        page_number=str(position['page']),
                        recipient_id=str(i),
                        x_position=str(int(float(position['x']))),
                        y_position=str(int(float(position['y']) + y_offset)),
                        font="helvetica",
                        font_size="size11",
                        tab_label=field.lower(),
                        width=200
                    )
                )
                y_offset += 30
            
            signer_obj = Signer(
                email=signer['email'],
                name=signer['name'],
                recipient_id=str(i),
                routing_order=str(i),
                tabs=Tabs(
                    sign_here_tabs=[sign_here],
                    text_tabs=additional_tabs
                )
            )
            
            docusign_signers.append(signer_obj)
            
        # Create Recipients object with signers
        recipients = Recipients(signers=docusign_signers)
            
        # Create envelope definition with recipients
        envelope_definition = EnvelopeDefinition(
            email_subject="Please sign this document",
            documents=[
                Document(
                    document_base64=doc_b64,
                    name="Contract.pdf",
                    file_extension="pdf",
                    document_id="1"
                )
            ],
            recipients=recipients,
            status="sent"
        )

        print("Creating DocuSign API client...")
        api_client = create_docusign_api_client()
        print("Creating envelope...")
        envelope_api = EnvelopesApi(api_client)
        envelope_summary = envelope_api.create_envelope(
            account_id=app.config['DOCUSIGN_ACCOUNT_ID'],
            envelope_definition=envelope_definition
        )

        print(f"Successfully sent envelope with ID: {envelope_summary.envelope_id}")
        return jsonify({
            "success": True,
            "message": f"Contract sent successfully to {len(signers)} signers",
            "envelope_id": envelope_summary.envelope_id
        })

    except Exception as e:
        print(f"Error sending contract via DocuSign: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Error args: {e.args}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to send contract: {str(e)}"}), 500

def create_pdf_from_text(text):
    from fpdf import FPDF
    
    # Create PDF object
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', size=10)
    
    # Replace problematic Unicode characters with ASCII equivalents
    text = text.replace('\u2013', '-')  # Replace en-dash with hyphen
    text = text.replace('\u2014', '--')  # Replace em-dash with double hyphen
    text = text.replace('\u2018', "'")   # Replace left single quote
    text = text.replace('\u2019', "'")   # Replace right single quote
    text = text.replace('\u201C', '"')   # Replace left double quote
    text = text.replace('\u201D', '"')   # Replace right double quote
    text = text.replace('\u2026', '...') # Replace ellipsis
    
    # Split text into lines and write to PDF
    lines = text.split('\n')
    for line in lines:
        # Encode line to ASCII, replacing unknown characters
        line = line.encode('ascii', 'replace').decode('ascii')
        pdf.multi_cell(0, 10, txt=line)
    
    # Get PDF as bytes
    return pdf.output(dest='S').encode('latin-1')

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv('GMAIL_USER')  # Your Gmail address
SENDER_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')  # Your Gmail App Password

def send_email(recipient_email, recipient_name, contract_content):
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = "Contract for Signature"

        # Email body
        body = f"""Hello {recipient_name},

A contract has been sent to you for review and signature.

Contract Details:
{contract_content[:500]}... [Contract Preview]

Please review and sign the contract at your earliest convenience.

Best regards,
Document Signing System"""

        msg.attach(MIMEText(body, 'plain'))

        # Create SMTP session
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        print(f"Email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email to {recipient_email}: {str(e)}")
        return False

# Risk Assessment Routes
@app.route('/api/analyze/risks', methods=['POST'])
def analyze_risks():
    if not request.json or 'content' not in request.json:
        return jsonify({"error": "No contract text provided"}), 400
    
    try:
        contract_text = request.json['content']
        risk_service = RiskService()
        analysis = risk_service.analyze_contract_risks(contract_text)
        return jsonify(analysis)
    except Exception as e:
        print(f"Error in risk analysis endpoint: {str(e)}")
        return jsonify({"error": f"Risk analysis failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
