import docusign_esign as docusign
from docusign_esign import ApiClient, EnvelopesApi, OAuthToken
import os
import base64
import requests
from urllib.parse import quote

class DocuSignService:
    def __init__(self):
        self.integration_key = os.getenv('DOCUSIGN_INTEGRATION_KEY')
        self.account_id = os.getenv('DOCUSIGN_ACCOUNT_ID')
        self.api_client = None
        self.base_uri = "https://demo.docusign.net/restapi"
        self.oauth_host_name = "account-d.docusign.com"
        self.redirect_uri = "https://vibrationrobotics.com/callback"  # Your redirect URI

    def get_consent_url(self):
        """Get the consent URL for OAuth authorization"""
        # Construct consent URL
        consent_url = f"https://{self.oauth_host_name}/oauth/auth"
        consent_url += f"?response_type=code"
        consent_url += f"&scope={quote('signature')}"
        consent_url += f"&client_id={self.integration_key}"
        consent_url += f"&redirect_uri={quote(self.redirect_uri)}"
        
        return consent_url

    def get_token_from_code(self, code):
        """Exchange authorization code for access token"""
        # Token request
        token_url = f"https://{self.oauth_host_name}/oauth/token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': self.integration_key,
            'client_secret': os.getenv('DOCUSIGN_CLIENT_SECRET'),  # You'll need to add this to .env
            'redirect_uri': self.redirect_uri
        }
        
        response = requests.post(token_url, headers=headers, data=data)
        if response.status_code != 200:
            raise Exception(f"Failed to get access token: {response.text}")
            
        token_data = response.json()
        return token_data['access_token']

    def setup_client(self, access_token):
        """Set up API client with access token"""
        self.api_client = ApiClient()
        self.api_client.host = self.base_uri
        self.api_client.set_default_header("Authorization", f"Bearer {access_token}")

    def send_envelope(self, contract_data, signers):
        """Create and send envelope for signature"""
        if not self.api_client:
            raise Exception("API client not initialized. Call setup_client() first.")
            
        envelopes_api = EnvelopesApi(self.api_client)
        
        # Create envelope definition
        envelope_definition = docusign.EnvelopeDefinition(
            email_subject="Please sign this document",
            documents=[{
                "documentBase64": base64.b64encode(contract_data.encode()).decode(),
                "name": "Contract.pdf",
                "fileExtension": "pdf",
                "documentId": "1"
            }],
            recipients={
                "signers": [
                    {
                        "email": signer["email"],
                        "name": signer["name"],
                        "recipientId": str(i+1),
                        "routingOrder": str(i+1)
                    } for i, signer in enumerate(signers)
                ]
            },
            status="sent"
        )
        
        try:
            envelope_summary = envelopes_api.create_envelope(
                account_id=self.account_id,
                envelope_definition=envelope_definition
            )
            return envelope_summary
        except docusign_esign.rest.ApiException as e:
            raise Exception(f"Error creating envelope: {str(e)}")
