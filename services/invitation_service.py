from datetime import datetime, timedelta
import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from models import Invitation, User, Contract
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import smtplib

class InvitationService:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv('GMAIL_USER')
        self.sender_password = os.getenv('GMAIL_APP_PASSWORD')

    def create_invitation(self, contract_id: int, email: str, role: str = 'viewer') -> Invitation:
        """Create a new invitation for a contract."""
        # Generate unique token
        token = str(uuid.uuid4())
        
        # Create invitation with 7-day expiration
        invitation = Invitation(
            contract_id=contract_id,
            email=email,
            role=role,
            token=token,
            expires_at=datetime.utcnow() + timedelta(days=7)
        )
        
        self.db.add(invitation)
        self.db.commit()
        
        # Send invitation email
        self._send_invitation_email(invitation)
        
        return invitation

    def accept_invitation(self, token: str) -> Optional[Contract]:
        """Accept an invitation and add user as collaborator."""
        invitation = self.db.query(Invitation).filter_by(token=token, status='pending').first()
        
        if not invitation or invitation.expires_at < datetime.utcnow():
            return None
            
        # Get or create user
        user = self.db.query(User).filter_by(email=invitation.email).first()
        if not user:
            user = User(email=invitation.email, name=invitation.email.split('@')[0])
            self.db.add(user)
        
        # Add user as collaborator if not already
        contract = invitation.contract
        if user not in contract.collaborators:
            contract.collaborators.append(user)
        
        # Update invitation status
        invitation.status = 'accepted'
        
        self.db.commit()
        return contract

    def list_invitations(self, contract_id: int) -> List[Invitation]:
        """List all invitations for a contract."""
        return self.db.query(Invitation).filter_by(contract_id=contract_id).all()

    def _send_invitation_email(self, invitation: Invitation):
        """Send invitation email to collaborator."""
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = invitation.email
        msg['Subject'] = f"You've been invited to collaborate on a contract"

        # Create the invitation URL (update with your actual domain)
        base_url = os.getenv('APP_URL', 'http://localhost:5000')
        invitation_url = f"{base_url}/accept-invitation/{invitation.token}"

        body = f"""
        Hello,

        You've been invited to collaborate on a contract with the role of {invitation.role}.
        
        Click the following link to accept the invitation:
        {invitation_url}

        This invitation will expire in 7 days.

        Best regards,
        DocuSign Team
        """

        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
        except Exception as e:
            print(f"Failed to send invitation email: {str(e)}")
