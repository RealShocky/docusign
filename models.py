from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

# Association tables for many-to-many relationships
template_tags = Table('template_tags', Base.metadata,
    Column('template_id', Integer, ForeignKey('templates.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

contract_collaborators = Table('contract_collaborators', Base.metadata,
    Column('contract_id', Integer, ForeignKey('contracts.id')),
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role', String(50))
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    owned_contracts = relationship("Contract", back_populates="owner")
    comments = relationship("Comment", back_populates="user")

class Template(Base):
    __tablename__ = 'templates'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=False)
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    tags = relationship("Tag", secondary=template_tags, back_populates="templates")
    created_by = relationship("User")

class Tag(Base):
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    
    # Relationships
    templates = relationship("Template", secondary=template_tags, back_populates="tags")

class Contract(Base):
    __tablename__ = 'contracts'
    
    id = Column(String, primary_key=True)
    title = Column(String)
    content = Column(Text)
    status = Column(String(50), default='draft')  # draft, under_review, signed, expired
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey('users.id'))
    template_id = Column(Integer, ForeignKey('templates.id'), nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="owned_contracts")
    comments = relationship("Comment", back_populates="contract")
    versions = relationship("ContractVersion", back_populates="contract")
    collaborators = relationship("User", secondary=contract_collaborators)
    invitations = relationship("Invitation", backref="contract")

    def __repr__(self):
        return f"<Contract(id='{self.id}', title='{self.title}')>"

class ContractVersion(Base):
    __tablename__ = 'contract_versions'
    
    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'))
    content = Column(Text, nullable=False)
    version = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey('users.id'))
    
    # Relationships
    contract = relationship("Contract", back_populates="versions")
    created_by = relationship("User")

class Comment(Base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Boolean, default=False)
    parent_id = Column(Integer, ForeignKey('comments.id'), nullable=True)
    
    # Relationships
    contract = relationship("Contract", back_populates="comments")
    user = relationship("User", back_populates="comments")
    replies = relationship("Comment")

class Invitation(Base):
    __tablename__ = 'invitations'
    
    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'))
    email = Column(String(255), nullable=False)
    role = Column(String(50), default='viewer')  # viewer, editor, admin
    token = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), default='pending')  # pending, accepted, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationships
    contract = relationship("Contract")

class CalendarEvent(Base):
    __tablename__ = 'calendar_events'
    
    id = Column(Integer, primary_key=True)
    contract_id = Column(Integer, ForeignKey('contracts.id'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    event_type = Column(String(50))  # deadline, renewal, review
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    contract = relationship("Contract")
