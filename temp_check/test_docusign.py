import os
from docusign_esign import ApiClient, EnvelopesApi, EnvelopeDefinition, Document, Signer, SignHere, Tabs
from docusign_esign.client.api_exception import ApiException
import base64
import time
from dotenv import load_dotenv
import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json

# Load environment variables
load_dotenv()

# DocuSign configuration
INTEGRATION_KEY = os.getenv('DOCUSIGN_INTEGRATION_KEY')
USER_ID = os.getenv('DOCUSIGN_USER_ID')
ACCOUNT_ID = os.getenv('DOCUSIGN_ACCOUNT_ID')
PRIVATE_KEY_PATH = os.getenv('DOCUSIGN_PRIVATE_KEY_PATH')
BASE_PATH = "https://demo.docusign.net/restapi"
OAUTH_HOST_NAME = "account-d.docusign.com"
SCOPES = ["signature", "impersonation"]

# Global variable to store the authorization code
authorization_code = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global authorization_code
        
        # Parse the query parameters
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if 'code' in params:
            authorization_code = params['code'][0]
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            response = """
            <html>
            <body>
                <h1>Authorization Successful!</h1>
                <p>You can close this window and return to the application.</p>
                <script>window.close();</script>
            </body>
            </html>
            """
            self.wfile.write(response.encode())
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'Authorization code not found')

def start_callback_server():
    """Start the callback server"""
    server = HTTPServer(('localhost', 8080), CallbackHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server

def get_consent():
    """Get consent for the application"""
    global authorization_code
    authorization_code = None
    
    # Start the callback server
    server = start_callback_server()
    
    # Construct consent URL
    consent_url = f"https://{OAUTH_HOST_NAME}/oauth/auth"
    consent_url += f"?response_type=code"
    consent_url += f"&scope={urllib.parse.quote(' '.join(SCOPES))}"
    consent_url += f"&client_id={INTEGRATION_KEY}"
    consent_url += f"&redirect_uri=http://localhost:8080/callback"
    
    print(f"\nOpening browser for consent...\n")
    webbrowser.open(consent_url)
    
    # Wait for the authorization code
    while authorization_code is None:
        time.sleep(1)
    
    # Shutdown the server
    server.shutdown()
    server.server_close()
    
    print("Consent granted!")
    return authorization_code

def get_private_key():
    """Read the private key file"""
    with open(PRIVATE_KEY_PATH, 'r') as key_file:
        private_key = key_file.read()
    return private_key

def create_api_client():
    """Create and configure API client"""
    api_client = ApiClient()
    api_client.host = BASE_PATH

    try:
        # Configure JWT authentication
        private_key = get_private_key()
        response = api_client.request_jwt_user_token(
            client_id=INTEGRATION_KEY,
            user_id=USER_ID,
            oauth_host_name=OAUTH_HOST_NAME,
            private_key_bytes=private_key,
            expires_in=3600,
            scopes=SCOPES
        )
        
        access_token = response.access_token
        api_client.set_default_header("Authorization", f"Bearer {access_token}")
        
        return api_client
    except ApiException as e:
        if "consent_required" in str(e):
            print("Consent required. Opening browser...")
            get_consent()
            
            # Try again after consent
            response = api_client.request_jwt_user_token(
                client_id=INTEGRATION_KEY,
                user_id=USER_ID,
                oauth_host_name=OAUTH_HOST_NAME,
                private_key_bytes=private_key,
                expires_in=3600,
                scopes=SCOPES
            )
            
            access_token = response.access_token
            api_client.set_default_header("Authorization", f"Bearer {access_token}")
            
            return api_client
        else:
            raise e

def create_envelope(api_client, test_number):
    """Create an envelope with a test document"""
    # Create the document
    with open("test_document.pdf", "rb") as file:
        content_bytes = file.read()
    base64_file_content = base64.b64encode(content_bytes).decode('ascii')

    # Create the document model
    document = Document(
        document_base64=base64_file_content,
        name=f'Test Document {test_number}',
        file_extension='pdf',
        document_id='1'
    )

    # Create the signer model
    signer = Signer(
        email=os.getenv('TEST_SIGNER_EMAIL'),
        name=os.getenv('TEST_SIGNER_NAME'),
        recipient_id="1",
        routing_order="1"
    )

    # Create a sign_here tab (signing field on document)
    sign_here = SignHere(
        anchor_string="/sn1/",
        anchor_units="pixels",
        anchor_y_offset="10",
        anchor_x_offset="20"
    )

    # Add the tab to the signer
    signer.tabs = Tabs(sign_here_tabs=[sign_here])

    # Create the envelope definition
    envelope_definition = EnvelopeDefinition(
        email_subject=f"Please sign this document #{test_number}",
        documents=[document],
        recipients={"signers": [signer]},
        status="sent"
    )

    return envelope_definition

def run_test_sequence():
    """Run a single test"""
    print("Creating API client...")
    api_client = create_api_client()
    
    print("Initializing Envelopes API...")
    envelopes_api = EnvelopesApi(api_client)
    
    try:
        print("\nCreating and sending envelope...")
        
        # Create and send envelope
        envelope_definition = create_envelope(api_client, 1)
        envelope_summary = envelopes_api.create_envelope(ACCOUNT_ID, envelope_definition=envelope_definition)
        envelope_id = envelope_summary.envelope_id
        
        print(f"Envelope created with ID: {envelope_id}")
        
        # Get envelope status
        envelope_info = envelopes_api.get_envelope(ACCOUNT_ID, envelope_id)
        print(f"Envelope status: {envelope_info.status}")
        print(f"\nA signing request has been sent to {os.getenv('TEST_SIGNER_EMAIL')}")
                
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    run_test_sequence()
