"""
Database Models for Maintenance Management System
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class AssetClass(Base):
    """Asset Class - Top level categorization"""
    __tablename__ = 'asset_classes'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    created_date = Column(DateTime, default=datetime.now)
    modified_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    asset_groups = relationship("AssetGroup", back_populates="asset_class", cascade="all, delete-orphan")

class AssetGroup(Base):
    """Asset Group - Mid level categorization"""
    __tablename__ = 'asset_groups'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    asset_class_id = Column(Integer, ForeignKey('asset_classes.id'))
    created_date = Column(DateTime, default=datetime.now)
    modified_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    asset_class = relationship("AssetClass", back_populates="asset_groups")
    asset_types = relationship("AssetType", back_populates="asset_group", cascade="all, delete-orphan")

class AssetType(Base):
    """Asset Type - Detailed categorization"""
    __tablename__ = 'asset_types'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    asset_group_id = Column(Integer, ForeignKey('asset_groups.id'))
    created_date = Column(DateTime, default=datetime.now)
    modified_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    asset_group = relationship("AssetGroup", back_populates="asset_types")
    assets = relationship("Asset", back_populates="asset_type", cascade="all, delete-orphan")

class Asset(Base):
    """Asset Register - Individual assets"""
    __tablename__ = 'assets'
    
    id = Column(Integer, primary_key=True)
    asset_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    asset_type_id = Column(Integer, ForeignKey('asset_types.id'))
    
    # Location information
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(String(300))
    location_description = Column(Text)
    
    # Asset details
    acquisition_date = Column(Date)
    acquisition_cost = Column(Float)
    current_value = Column(Float)
    condition_rating = Column(Integer)  # 1-5 scale
    status = Column(String(50))  # Active, Inactive, Disposed, etc.
    
    # Additional fields
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100))
    warranty_expiry = Column(Date)
    
    created_date = Column(DateTime, default=datetime.now)
    modified_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String(100))
    modified_by = Column(String(100))
    
    # Relationships
    asset_type = relationship("AssetType", back_populates="assets")
    work_orders = relationship("WorkOrder", back_populates="asset", cascade="all, delete-orphan")
    inspections = relationship("Inspection", back_populates="asset", cascade="all, delete-orphan")

class WorkOrder(Base):
    """Work Orders for maintenance activities"""
    __tablename__ = 'work_orders'
    
    id = Column(Integer, primary_key=True)
    work_order_number = Column(String(50), unique=True, nullable=False)
    asset_id = Column(Integer, ForeignKey('assets.id'))
    
    title = Column(String(200), nullable=False)
    description = Column(Text)
    work_type = Column(String(50))  # Preventive, Corrective, Emergency, etc.
    priority = Column(String(20))  # Low, Medium, High, Critical
    status = Column(String(50))  # Open, In Progress, Completed, Cancelled
    
    # Dates
    created_date = Column(DateTime, default=datetime.now)
    scheduled_date = Column(DateTime)
    start_date = Column(DateTime)
    completion_date = Column(DateTime)
    due_date = Column(DateTime)
    
    # Personnel
    assigned_to = Column(String(100))
    created_by = Column(String(100))
    completed_by = Column(String(100))
    
    # Cost information
    estimated_cost = Column(Float)
    actual_cost = Column(Float)
    labor_hours = Column(Float)
    
    # Additional details
    notes = Column(Text)
    completion_notes = Column(Text)
    
    # Location (can override asset location)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Relationships
    asset = relationship("Asset", back_populates="work_orders")

class Inspection(Base):
    """Inspection records"""
    __tablename__ = 'inspections'
    
    id = Column(Integer, primary_key=True)
    inspection_number = Column(String(50), unique=True, nullable=False)
    asset_id = Column(Integer, ForeignKey('assets.id'))
    
    inspection_type = Column(String(100))
    inspection_date = Column(DateTime, nullable=False)
    inspector = Column(String(100))
    
    # Results
    condition_rating = Column(Integer)  # 1-5 scale
    defects_found = Column(Boolean, default=False)
    defect_description = Column(Text)
    
    # Recommendations
    recommendations = Column(Text)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(Date)
    
    # Status
    status = Column(String(50))  # Scheduled, Completed, Cancelled
    
    created_date = Column(DateTime, default=datetime.now)
    modified_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Location
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Relationships
    asset = relationship("Asset", back_populates="inspections")

class User(Base):
    """User management"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True)
    full_name = Column(String(100))
    role = Column(String(50))  # Admin, Manager, Technician, Viewer
    department = Column(String(100))
    is_active = Column(Boolean, default=True)
    
    created_date = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)

class Document(Base):
    """Document/Attachment management for assets, work orders, and inspections"""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    
    # Link to parent record
    linked_type = Column(String(50))  # 'asset', 'work_order', 'inspection'
    linked_id = Column(Integer)  # ID of the linked record
    
    # Document details
    document_type = Column(String(50))  # Photo, Plan, Manual, Drawing, Report, etc.
    title = Column(String(200))
    description = Column(Text)
    file_path = Column(String(500))  # Path to file (local, network, or URL)
    file_name = Column(String(200))
    file_size = Column(String(50))  # e.g., "2.5 MB"
    file_format = Column(String(50))  # PDF, JPG, PNG, DWG, etc.
    
    # Metadata
    uploaded_by = Column(String(100))
    upload_date = Column(DateTime, default=datetime.now)
    last_modified = Column(DateTime, onupdate=datetime.now)
    version = Column(String(20))
    is_active = Column(Boolean, default=True)
    notes = Column(Text)


class AuditLog(Base):
    """Audit trail for all transactions"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now)
    user_id = Column(String(100))
    action = Column(String(50))  # Create, Update, Delete
    table_name = Column(String(50))
    record_id = Column(Integer)
    old_values = Column(Text)
    new_values = Column(Text)
    ip_address = Column(String(50))


class DropdownValue(Base):
    """Stores customizable dropdown values for the application"""
    __tablename__ = 'dropdown_values'
    
    id = Column(Integer, primary_key=True)
    category = Column(String(50), nullable=False)  # e.g., 'work_order_type', 'priority', etc.
    value = Column(String(200), nullable=False)
    display_order = Column(Integer, default=0)  # For ordering values
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)  # If this is a system default value
    created_date = Column(DateTime, default=datetime.now)
    modified_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)


# Database initialization
def init_database(db_path='sqlite:///data/maintenance_management.db'):
    """Initialize the database"""
    engine = create_engine(db_path, echo=False)
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    """Get database session"""
    Session = sessionmaker(bind=engine)
    return Session()
