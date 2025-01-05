from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from pdf_processor import process_file
import os
import openai
import json
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, SignHere, Tabs, Text, DateSigned, Recipients
import base64
from fpdf import FPDF
import traceback
from dotenv import load_dotenv, find_dotenv
from flask_session import Session
from database import init_db, Session as DBSession
from services.ai_service import AIService
from services.invitation_service import InvitationService
from typing import Dict, Any
import PyPDF2
import pdfplumber
import jwt
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import tempfile
import os
from flask import has_request_context

# Load environment variables
load_dotenv()

# Debug: Print current working directory
print("Current working directory:", os.getcwd())

# Initialize Flask app
app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'null'  # Use memory-based sessions instead of filesystem
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
Session(app)

# Initialize database
init_db()

# Configure OpenAI
def configure_openai():
    openai.api_key = get_openai_key()

@app.before_request
def before_request():
    configure_openai()
    configure_docusign()

def get_openai_key():
    if not has_request_context():
        return os.getenv('OPENAI_API_KEY')
    return session.get('openai_key') or os.getenv('OPENAI_API_KEY')

def get_docusign_key():
    if not has_request_context():
        return os.getenv('DOCUSIGN_INTEGRATION_KEY')
    return session.get('docusign_key') or os.getenv('DOCUSIGN_INTEGRATION_KEY')

def configure_docusign():
    app.config.update(
        DOCUSIGN_INTEGRATION_KEY=get_docusign_key(),
        DOCUSIGN_USER_ID=os.getenv('DOCUSIGN_USER_ID'),
        DOCUSIGN_ACCOUNT_ID=os.getenv('DOCUSIGN_ACCOUNT_ID'),
        DOCUSIGN_PRIVATE_KEY_PATH='private.key',
        DOCUSIGN_AUTH_SERVER='account-d.docusign.com'
    )

# Initial configuration with environment variables
app.config.update(
    DOCUSIGN_INTEGRATION_KEY=os.getenv('DOCUSIGN_INTEGRATION_KEY'),
    DOCUSIGN_USER_ID=os.getenv('DOCUSIGN_USER_ID'),
    DOCUSIGN_ACCOUNT_ID=os.getenv('DOCUSIGN_ACCOUNT_ID'),
    DOCUSIGN_PRIVATE_KEY_PATH='private.key',
    DOCUSIGN_AUTH_SERVER='account-d.docusign.com'
)

# Initialize services
upload_folder = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(upload_folder, exist_ok=True)
ai_service = AIService()
invitation_service = InvitationService(DBSession())

# Debug: Find all .env files
print("Looking for .env files...")
env_file = find_dotenv()
print("Found .env file:", env_file)

# Debug: Print environment sources
print("\nAPI Key Sources:")
print("1. From os.environ:", os.environ.get('OPENAI_API_KEY', 'Not found in os.environ'))
print("2. From os.getenv:", os.getenv('OPENAI_API_KEY', 'Not found in getenv'))
print("3. Direct from openai.api_key:", getattr(openai, 'api_key', 'Not set in openai'))

# Debug: Print final OpenAI key
print("4. Final OpenAI API Key:", openai.api_key[:10] + '...' if openai.api_key else 'Not set')

# Debug: Print environment variables
print("Environment variables loaded:")
print("OPENAI_API_KEY:", os.getenv('OPENAI_API_KEY', 'Not found'))
print("FLASK_ENV:", os.getenv('FLASK_ENV', 'Not found'))

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
    return send_file('static/index.html')

@app.route('/js/<path:path>')
def serve_js(path):
    return send_file('static/js/' + path)

@app.route('/js/components/<path:path>')
def serve_components(path):
    return send_file('static/js/components/' + path)

@app.route('/callback')
def callback():
    return send_file('static/callback.html')

# API routes start with /api
@app.route('/api/settings/save', methods=['POST'])
def save_settings():
    try:
        data = request.get_json()
        openai_key = data.get('openaiKey')
        docusign_key = data.get('docusignKey')
        
        # Store keys in session
        if openai_key:
            session['openai_key'] = openai_key
        if docusign_key:
            session['docusign_key'] = docusign_key
            
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

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
        text = process_file(file)
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        # Read file bytes
        file_bytes = file.read()
        
        # Process file based on type
        content = process_file(file_bytes, file.filename)
        
        if content is None:
            return jsonify({'error': 'Could not process file'}), 400

        return jsonify({'content': content})
    except Exception as e:
        print("Error processing file:", str(e))
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to process file: {str(e)}'}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_contract():
    if not request.json or 'content' not in request.json:
        return jsonify({"error": "No content provided"}), 400

    try:
        content = request.json['content']
        
        # Get model from environment variable or use default
        model = os.getenv('OPENAI_MODEL', 'gpt-4-1106-preview')
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": """You are a legal expert analyzing contracts. 
                For each contract, provide a structured analysis with the following sections:

                1. Key Terms and Definitions
                2. Obligations and Responsibilities
                3. Termination and Duration
                4. Legal Compliance
                5. Recommendations

                For each section, provide specific items in this format:
                SECTION NAME:
                - Item Title: Detailed description of the item
                - Another Item: Its description"""},
                {"role": "user", "content": f"Analyze this contract and provide a structured analysis with the sections and items as specified:\n\n{content}"}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Extract the analysis from the response
        analysis = response.choices[0].message['content']
        print("Raw analysis:", analysis)  # Debug print
        
        # Parse the analysis into structured sections
        sections = []
        current_section = None
        current_items = []
        
        lines = analysis.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a section header (ends with : and is not an item)
            if line.endswith(':') and not line.startswith('-'):
                # Save previous section if it exists
                if current_section and current_items:
                    sections.append({
                        'title': current_section,
                        'items': current_items
                    })
                current_section = line.rstrip(':')
                current_items = []
            
            # Check if this is an item (starts with -)
            elif line.startswith('-'):
                item_text = line[1:].strip()
                if ':' in item_text:
                    title, desc = item_text.split(':', 1)
                    current_items.append({
                        'title': title.strip(),
                        'description': desc.strip()
                    })
                else:
                    current_items.append({
                        'title': item_text,
                        'description': ''
                    })
        
        # Add the last section
        if current_section and current_items:
            sections.append({
                'title': current_section,
                'items': current_items
            })
        
        # If no sections were found, create a default section
        if not sections:
            sections = [{
                'title': 'Contract Analysis',
                'items': [{
                    'title': 'General Analysis',
                    'description': analysis
                }]
            }]
        
        print("Structured sections:", sections)  # Debug print
        return jsonify({'sections': sections})

    except Exception as e:
        print(f"Error in analyze_contract: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

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

@app.route('/api/analyze/risks', methods=['POST'])
def analyze_risks():
    if not request.json or 'content' not in request.json:
        return jsonify({"error": "No contract text provided"}), 400
    
    try:
        contract_text = request.json['content']
        
        # Get model from environment variable or use default
        model = os.getenv('OPENAI_MODEL', 'gpt-4-1106-preview')
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": """You are a legal expert analyzing contract risks.
                Provide a risk analysis with:
                1. Overall risk score (1-10)
                2. Summary of key risks
                3. Detailed analysis of concerning clauses
                
                Format the response as:
                RISK_SCORE: [1-10]
                SUMMARY: [brief overview of risks]
                CONCERNS:
                - [concern title] | [risk level: HIGH/MEDIUM/LOW] | [description]"""},
                {"role": "user", "content": f"Analyze the risks in this contract:\n\n{contract_text}"}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Extract the analysis from the response
        analysis = response.choices[0].message['content']
        
        # Parse the response into structured format
        lines = analysis.split('\n')
        result = {
            'risk_score': None,
            'summary': '',
            'concerns': []
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('RISK_SCORE:'):
                score = line.split(':', 1)[1].strip()
                try:
                    result['risk_score'] = int(score)
                except:
                    result['risk_score'] = 5  # default score
            elif line.startswith('SUMMARY:'):
                result['summary'] = line.split(':', 1)[1].strip()
            elif line.startswith('-'):
                parts = line[1:].split('|')
                if len(parts) >= 3:
                    result['concerns'].append({
                        'title': parts[0].strip(),
                        'level': parts[1].strip(),
                        'description': parts[2].strip()
                    })
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in risk analysis endpoint: {str(e)}")
        return jsonify({"error": f"Risk analysis failed: {str(e)}"}), 500

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
            "rewritten_text": rewritten,  # Changed from "rewritten" to "rewritten_text"
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

@app.route('/api/send', methods=['POST'])
def send_contract():
    if not request.json:
        return jsonify({"error": "No JSON data provided"}), 400
        
    contract = request.json.get('contract')
    signers = request.json.get('signers')
    use_ai_positioning = request.json.get('use_ai_positioning', False)
    
    if not contract or not signers:
        return jsonify({"error": "Contract and signers are required"}), 400

    try:
        # Convert contract text to PDF
        print("Converting contract to PDF...")
        pdf_bytes = create_pdf_from_text(contract)
        doc_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        print("Creating envelope definition...")
        docusign_signers = []
        
        # Try AI-based positioning if requested
        signature_positions = None
        if use_ai_positioning:
            print("Attempting AI-based signature positioning...")
            try:
                signature_locations = analyze_signature_locations(contract)
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

def find_text_position_in_pdf(pdf_bytes, search_text):
    """Find the position of text in a PDF file"""
    try:
        # Create a temporary file to store PDF bytes
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(pdf_bytes)
            temp_path = temp_file.name

        positions = []
        # Open the PDF with pdfplumber
        with pdfplumber.open(temp_path) as pdf:
            # Search each page
            for page_num, page in enumerate(pdf.pages):
                # Extract text and its positions
                words = page.extract_words(x_tolerance=3, y_tolerance=3)
                
                # Search for the text
                for word in words:
                    if search_text.lower() in word['text'].lower():
                        # Convert position to DocuSign coordinate system
                        # DocuSign uses points from bottom-left, pdfplumber uses points from top-left
                        x = word['x0']
                        y = page.height - word['y0']  # Convert to bottom-up coordinate system
                        
                        positions.append({
                            'page_number': page_num + 1,
                            'x': x,
                            'y': y,
                            'width': word['width'],
                            'height': word['height']
                        })

        # Clean up temporary file
        os.unlink(temp_path)

        # Return the first occurrence if found
        return positions[0] if positions else None

    except Exception as e:
        print(f"Error finding text position: {str(e)}")
        return None

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

def analyze_signature_locations(contract_text):
    """Analyze contract text to find potential signature locations using OpenAI"""
    try:
        prompt = """Analyze this contract and identify where signatures should be placed. Look for:
        1. Signature lines or blocks at the end of sections
        2. Places marked with 'signature', 'signed by', etc.
        3. Areas near date fields or witness blocks
        
        For each location found, provide:
        1. The exact text that comes before the signature (anchor_text)
        2. Surrounding context if the anchor text alone is ambiguous
        3. Any additional fields needed (date, name, title, etc.)
        
        Contract text:
        {text}
        """.format(text=contract_text)

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a contract analysis assistant. Respond in JSON format."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )

        # Parse the response to extract signature locations
        result = response.choices[0].message.content
        
        # Extract key components using GPT
        structure_prompt = f"""
        Based on this analysis, provide a structured JSON with:
        1. overall_risk_score (number 1-10)
        2. risk_summary (string)
        3. clauses (array of objects with 'clause', 'risk_level', and 'details')
        
        Analysis:
        {result}
        """
        
        structure_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a JSON formatter for legal analysis."},
                {"role": "user", "content": structure_prompt}
            ],
            temperature=0
        )
        
        # Parse the structured response
        import json
        structured_analysis = json.loads(structure_response.choices[0].message.content)
        
        return structured_analysis
            
    except Exception as e:
        print(f"Error analyzing signature locations: {str(e)}")
        return None

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

class RiskService:
    def __init__(self):
        self.risk_prompt = """
        Analyze the following contract for potential risks and issues. Consider:
        1. Legal compliance
        2. Financial risks
        3. Liability concerns
        4. Ambiguous language
        5. Missing clauses
        6. Unfavorable terms
        
        Provide a detailed analysis with:
        1. Overall risk score (1-10)
        2. Risk summary
        3. Specific clause analysis
        
        Contract:
        {contract_text}
        """

    def analyze_contract_risks(self, contract_text: str) -> Dict[str, Any]:
        try:
            # Prepare the analysis prompt
            analysis_prompt = self.risk_prompt.format(contract_text=contract_text)
            
            # Get analysis from GPT
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a legal expert specializing in contract risk analysis."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.7
            )
            
            # Parse the response
            analysis_text = response.choices[0].message.content
            
            # Extract key components using GPT
            structure_prompt = f"""
            Based on this analysis, provide a structured JSON with:
            1. overall_risk_score (number 1-10)
            2. risk_summary (string)
            3. clauses (array of objects with 'clause', 'risk_level', and 'details')
            
            Analysis:
            {analysis_text}
            """
            
            structure_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a JSON formatter for legal analysis."},
                    {"role": "user", "content": structure_prompt}
                ],
                temperature=0
            )
            
            # Parse the structured response
            import json
            structured_analysis = json.loads(structure_response.choices[0].message.content)
            
            return structured_analysis
            
        except Exception as e:
            print(f"Error in risk analysis: {str(e)}")
            raise Exception(f"Failed to analyze risks: {str(e)}")

# Invitation Routes
@app.route('/api/contracts/<int:contract_id>/invitations', methods=['POST'])
def invite_collaborator(contract_id):
    try:
        data = request.get_json()
        email = data.get('email')
        role = data.get('role', 'viewer')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
            
        invitation = invitation_service.create_invitation(contract_id, email, role)
        return jsonify({
            'id': invitation.id,
            'email': invitation.email,
            'role': invitation.role,
            'status': invitation.status,
            'expires_at': invitation.expires_at.isoformat()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contracts/<int:contract_id>/invitations', methods=['GET'])
def list_invitations(contract_id):
    try:
        invitations = invitation_service.list_invitations(contract_id)
        return jsonify([{
            'id': inv.id,
            'email': inv.email,
            'role': inv.role,
            'status': inv.status,
            'expires_at': inv.expires_at.isoformat()
        } for inv in invitations]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/invitations/<token>/accept', methods=['POST'])
def accept_invitation(token):
    try:
        contract = invitation_service.accept_invitation(token)
        if not contract:
            return jsonify({'error': 'Invalid or expired invitation'}), 400
            
        return jsonify({
            'message': 'Invitation accepted successfully',
            'contract_id': contract.id
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
