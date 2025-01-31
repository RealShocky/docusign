from models import Template, Tag
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

class TemplateService:
    def __init__(self, db: Session):
        self.db = db

    def create_template(self, name: str, content: str, description: Optional[str] = None,
                       category: Optional[str] = None, created_by_id: int = None,
                       tags: List[str] = None) -> Template:
        """Create a new contract template."""
        template = Template(
            name=name,
            content=content,
            description=description,
            category=category,
            created_by_id=created_by_id
        )

        if tags:
            for tag_name in tags:
                tag = self.db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    self.db.add(tag)
                template.tags.append(tag)

        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def get_template(self, template_id: int) -> Optional[Template]:
        """Get a template by ID."""
        return self.db.query(Template).filter(Template.id == template_id).first()

    def list_templates(self, category: Optional[str] = None,
                      tags: List[str] = None) -> List[Template]:
        """List all templates, optionally filtered by category and tags."""
        query = self.db.query(Template)
        
        if category:
            query = query.filter(Template.category == category)
        
        if tags:
            for tag in tags:
                query = query.filter(Template.tags.any(Tag.name == tag))
        
        return query.all()

    def update_template(self, template_id: int, **kwargs) -> Optional[Template]:
        """Update a template."""
        template = self.get_template(template_id)
        if not template:
            return None

        for key, value in kwargs.items():
            if hasattr(template, key):
                setattr(template, key, value)

        template.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(template)
        return template

    def delete_template(self, template_id: int) -> bool:
        """Delete a template."""
        template = self.get_template(template_id)
        if not template:
            return False

        self.db.delete(template)
        self.db.commit()
        return True

    def get_template_by_name(self, name: str) -> Optional[Template]:
        """Get a template by name."""
        return self.db.query(Template).filter(Template.name == name).first()

    def search_templates(self, query: str) -> List[Template]:
        """Search templates by name or description."""
        return self.db.query(Template).filter(
            (Template.name.ilike(f"%{query}%")) |
            (Template.description.ilike(f"%{query}%"))
        ).all()

    def get_templates_by_tag(self, tag_name: str) -> List[Template]:
        """Get all templates with a specific tag."""
        return self.db.query(Template).filter(
            Template.tags.any(Tag.name == tag_name)
        ).all()
