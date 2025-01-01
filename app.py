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
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, SignHere, Tabs, Recipients
import base64
import jwt
import time
from fpdf import FPDF

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
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = tempfile.gettempdir()
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
    
    if not content or not instructions:
        return jsonify({"error": "Content and instructions are required"}), 400
    
    try:
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
        
        return jsonify({
            "rewritten": rewritten,
            "success": True
        })
        
    except Exception as e:
        print("\nError occurred during rewrite:")
        print("Error details:", str(e))
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
        
    contract_text = request.json.get('contract')
    signers = request.json.get('signers')
    
    if not contract_text or not signers:
        return jsonify({"error": "Contract and signers are required"}), 400

    try:
        # Convert contract text to PDF
        print("Converting contract to PDF...")
        pdf_bytes = create_pdf_from_text(contract_text)
        doc_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        print("Creating envelope definition...")
        # Create list to store signers
        docusign_signers = []
        
        # Add signers
        for i, signer in enumerate(signers, 1):
            print(f"Adding signer {i}: {signer['name']} ({signer['email']})")
            
            # Add signature field at the bottom
            sign_here = SignHere(
                document_id="1",
                page_number="1",
                recipient_id=str(i),
                x_position="100",
                y_position="600"
            )
            
            signer_obj = Signer(
                email=signer['email'],
                name=signer['name'],
                recipient_id=str(i),
                routing_order=str(i),
                tabs=Tabs(sign_here_tabs=[sign_here])
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
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Split text into lines and write to PDF
    lines = text.split('\n')
    for line in lines:
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
