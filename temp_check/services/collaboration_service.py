from models import Contract, Comment, User, ContractVersion
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

class CollaborationService:
    def __init__(self, db: Session):
        self.db = db

    def add_collaborator(self, contract_id: int, user_id: int, role: str = 'viewer') -> bool:
        """Add a collaborator to a contract."""
        contract = self.db.query(Contract).filter(Contract.id == contract_id).first()
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not contract or not user:
            return False
            
        if user not in contract.collaborators:
            contract.collaborators.append(user)
            self.db.commit()
        return True

    def remove_collaborator(self, contract_id: int, user_id: int) -> bool:
        """Remove a collaborator from a contract."""
        contract = self.db.query(Contract).filter(Contract.id == contract_id).first()
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not contract or not user:
            return False
            
        if user in contract.collaborators:
            contract.collaborators.remove(user)
            self.db.commit()
        return True

    def add_comment(self, contract_id: int, user_id: int, content: str,
                   parent_id: Optional[int] = None) -> Optional[Comment]:
        """Add a comment to a contract."""
        comment = Comment(
            contract_id=contract_id,
            user_id=user_id,
            content=content,
            parent_id=parent_id
        )
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def resolve_comment(self, comment_id: int) -> bool:
        """Mark a comment as resolved."""
        comment = self.db.query(Comment).filter(Comment.id == comment_id).first()
        if not comment:
            return False
            
        comment.resolved = True
        self.db.commit()
        return True

    def get_comments(self, contract_id: int, include_resolved: bool = False) -> List[Comment]:
        """Get all comments for a contract."""
        query = self.db.query(Comment).filter(Comment.contract_id == contract_id)
        if not include_resolved:
            query = query.filter(Comment.resolved == False)
        return query.all()

    def create_version(self, contract_id: int, content: str,
                      created_by_id: int) -> ContractVersion:
        """Create a new version of a contract."""
        contract = self.db.query(Contract).filter(Contract.id == contract_id).first()
        
        # Increment version number
        new_version_num = contract.version + 1
        contract.version = new_version_num
        
        # Create version record
        version = ContractVersion(
            contract_id=contract_id,
            content=content,
            version=new_version_num,
            created_by_id=created_by_id
        )
        
        # Update contract content
        contract.content = content
        contract.updated_at = datetime.utcnow()
        
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version

    def get_version(self, contract_id: int, version_num: int) -> Optional[ContractVersion]:
        """Get a specific version of a contract."""
        return self.db.query(ContractVersion).filter(
            ContractVersion.contract_id == contract_id,
            ContractVersion.version == version_num
        ).first()

    def list_versions(self, contract_id: int) -> List[ContractVersion]:
        """List all versions of a contract."""
        return self.db.query(ContractVersion).filter(
            ContractVersion.contract_id == contract_id
        ).order_by(ContractVersion.version.desc()).all()

    def compare_versions(self, contract_id: int, version1: int,
                        version2: int) -> dict:
        """Compare two versions of a contract."""
        v1 = self.get_version(contract_id, version1)
        v2 = self.get_version(contract_id, version2)
        
        if not v1 or not v2:
            return None
            
        # TODO: Implement diff logic
        return {
            'version1': {
                'number': v1.version,
                'content': v1.content,
                'created_at': v1.created_at,
                'created_by': v1.created_by_id
            },
            'version2': {
                'number': v2.version,
                'content': v2.content,
                'created_at': v2.created_at,
                'created_by': v2.created_by_id
            }
        }
