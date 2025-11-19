from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Float, Enum as SQLEnum
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    CLIENT = "client"
    CA = "ca"

class PBCStatus(enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    SUBMITTED = "Submitted"
    VERIFIED = "Verified"
    REJECTED = "Rejected"

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    company_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    ca_profile = relationship("CAProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    client_profile = relationship("ClientProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

class CAProfile(Base):
    __tablename__ = 'ca_profiles'
    
    ca_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), unique=True, nullable=False)
    firm_name = Column(String, nullable=False)
    membership_no = Column(String, unique=True, nullable=False)
    firm_registration_no = Column(String, nullable=True)  # ← ADD THIS LINE
    invite_code = Column(String, unique=True, nullable=False)
    
    user = relationship("User", back_populates="ca_profile")
    clients = relationship("ClientProfile", back_populates="linked_ca")
    audit_projects = relationship("AuditProject", back_populates="ca")

class ClientProfile(Base):
    __tablename__ = 'client_profiles'
    
    client_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), unique=True, nullable=False)
    ca_id = Column(Integer, ForeignKey('ca_profiles.ca_id'), nullable=True)
    company_name = Column(String, nullable=False)
    gstin = Column(String)
    financial_year = Column(String)
    
    user = relationship("User", back_populates="client_profile")
    linked_ca = relationship("CAProfile", back_populates="clients")
    audit_projects = relationship("AuditProject", back_populates="client")

class AuditProject(Base):
    __tablename__ = 'audit_projects'
    
    project_id = Column(Integer, primary_key=True)
    ca_id = Column(Integer, ForeignKey('ca_profiles.ca_id'), nullable=False)
    client_id = Column(Integer, ForeignKey('client_profiles.client_id'), nullable=False)
    project_name = Column(String, nullable=False)
    financial_year = Column(String, nullable=False)
    audit_type = Column(String, default="Statutory Audit")
    status = Column(String, default="Active")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    ca = relationship("CAProfile", back_populates="audit_projects")
    client = relationship("ClientProfile", back_populates="audit_projects")
    pbc_items = relationship("PBCItem", back_populates="project", cascade="all, delete-orphan")
    trial_balance = relationship("TrialBalance", back_populates="project", uselist=False, cascade="all, delete-orphan")

class TrialBalance(Base):
    __tablename__ = 'trial_balances'
    
    tb_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('audit_projects.project_id'), unique=True, nullable=False)
    filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    total_debit = Column(Float, default=0.0)
    total_credit = Column(Float, default=0.0)
    account_count = Column(Integer, default=0)
    
    project = relationship("AuditProject", back_populates="trial_balance")

class PBCItem(Base):
    __tablename__ = 'pbc_items'
    
    pbc_id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('audit_projects.project_id'), nullable=False)
    item_number = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    item_description = Column(Text, nullable=False)
    why_needed = Column(Text)
    due_date = Column(DateTime, nullable=True)
    status = Column(SQLEnum(PBCStatus), default=PBCStatus.PENDING)
    priority = Column(String, default="Medium")
    ai_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("AuditProject", back_populates="pbc_items")
    documents = relationship("PBCDocument", back_populates="pbc_item", cascade="all, delete-orphan")
    comments = relationship("PBCComment", back_populates="pbc_item", cascade="all, delete-orphan")

class PBCDocument(Base):
    __tablename__ = 'pbc_documents'
    
    doc_id = Column(Integer, primary_key=True)
    pbc_id = Column(Integer, ForeignKey('pbc_items.pbc_id'), nullable=False)
    filename = Column(String, nullable=False)
    file_size = Column(Integer)
    file_type = Column(String)
    uploaded_by = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    ai_analysis = Column(Text)
    is_verified = Column(Boolean, default=False)
    verified_by = Column(Integer, ForeignKey('users.user_id'), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    pbc_item = relationship("PBCItem", back_populates="documents")

class PBCComment(Base):
    __tablename__ = 'pbc_comments'
    
    comment_id = Column(Integer, primary_key=True)
    pbc_id = Column(Integer, ForeignKey('pbc_items.pbc_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    comment_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    pbc_item = relationship("PBCItem", back_populates="comments")

# Database initialization
def init_database():
    engine = create_engine('sqlite:///pbc_automator.db', connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return engine

def get_session():
    engine = create_engine('sqlite:///pbc_automator.db', connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()
