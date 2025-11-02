"""
Configuration Loader for Maintenance Management System
Reads settings from config.ini file
"""
import configparser
import os
from pathlib import Path
import streamlit as st

class AppConfig:
    """Application configuration manager"""
    
    def __init__(self, config_file='config.ini'):
        """Initialize configuration from INI file"""
        self.config = configparser.ConfigParser()
        self.config_file = config_file
        
        # Check if config file exists
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file '{config_file}' not found!")
        
        # Read configuration with UTF-8 encoding to support emojis and special characters
        self.config.read(config_file, encoding='utf-8')
        
        # Application settings
        self.APP_TITLE = self.config.get('Application', 'app_title', fallback='Maintenance Management System')
        self.APP_ICON = self.config.get('Application', 'app_icon', fallback='🏢')
        self.VERSION = self.config.get('Application', 'version', fallback='1.0.0')
        self.ENVIRONMENT = self.config.get('Application', 'environment', fallback='Production')
        
        # Organization settings
        self.COMPANY_NAME = self.config.get('Organization', 'company_name', fallback='Your Organization')
        self.REGISTERED_TO = self.config.get('Organization', 'registered_to', fallback='Your Organization')
        self.DEPARTMENT = self.config.get('Organization', 'department', fallback='Asset Management')
        self.ABN = self.config.get('Organization', 'abn', fallback='N/A')
        
        # Developer settings
        self.PRODUCED_BY = self.config.get('Developer', 'produced_by', fallback='MMS Pty Ltd')
        self.DEVELOPER_CONTACT = self.config.get('Developer', 'developer_contact', fallback='')
        self.DEVELOPER_WEBSITE = self.config.get('Developer', 'developer_website', fallback='')
        self.SUPPORT_PHONE = self.config.get('Developer', 'support_phone', fallback='')
        
        # Database settings
        self.DATABASE_PATH = self.config.get('Database', 'database_path', fallback='data/maintenance_management.db')
        self.BACKUP_PATH = self.config.get('Database', 'backup_path', fallback='data/backups')
        
        # Document paths
        self.DOCUMENT_ROOT = self.config.get('Documents', 'document_root', fallback='documents')
        self.ASSET_DOCUMENTS = self.config.get('Documents', 'asset_documents', fallback='documents/assets')
        self.WORKORDER_DOCUMENTS = self.config.get('Documents', 'workorder_documents', fallback='documents/work_orders')
        self.INSPECTION_DOCUMENTS = self.config.get('Documents', 'inspection_documents', fallback='documents/inspections')
        
        # Regional settings
        self.COUNTRY = self.config.get('Regional', 'country', fallback='Australia')
        self.TIMEZONE = self.config.get('Regional', 'timezone', fallback='Australia/Sydney')
        self.CURRENCY = self.config.get('Regional', 'currency', fallback='AUD')
        self.CURRENCY_SYMBOL = self.config.get('Regional', 'currency_symbol', fallback='$')
        
        # Feature flags
        self.ENABLE_GOOGLE_EARTH = self.config.getboolean('Features', 'enable_google_earth', fallback=True)
        self.ENABLE_DOCUMENT_MANAGEMENT = self.config.getboolean('Features', 'enable_document_management', fallback=True)
        self.ENABLE_USER_MANAGEMENT = self.config.getboolean('Features', 'enable_user_management', fallback=True)
        self.ENABLE_REPORTS = self.config.getboolean('Features', 'enable_reports', fallback=True)
        
        # Support information
        self.SUPPORT_EMAIL = self.config.get('Support', 'support_email', fallback='')
        self.SUPPORT_HOURS = self.config.get('Support', 'support_hours', fallback='')
        self.EMERGENCY_CONTACT = self.config.get('Support', 'emergency_contact', fallback='')
        
        # Create necessary directories
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            os.path.dirname(self.DATABASE_PATH),
            self.BACKUP_PATH,
            self.DOCUMENT_ROOT,
            self.ASSET_DOCUMENTS,
            self.WORKORDER_DOCUMENTS,
            self.INSPECTION_DOCUMENTS
        ]
        
        for directory in directories:
            if directory:
                Path(directory).mkdir(parents=True, exist_ok=True)
    
    def get_info_dict(self):
        """Get configuration information as a dictionary for display"""
        return {
            'Application': {
                'Title': self.APP_TITLE,
                'Version': self.VERSION,
                'Environment': self.ENVIRONMENT
            },
            'Organization': {
                'Company Name': self.COMPANY_NAME,
                'Registered To': self.REGISTERED_TO,
                'Department': self.DEPARTMENT,
                'ABN': self.ABN
            },
            'Developer': {
                'Produced By': self.PRODUCED_BY,
                'Contact': self.DEVELOPER_CONTACT,
                'Website': self.DEVELOPER_WEBSITE,
                'Support Phone': self.SUPPORT_PHONE
            },
            'Support': {
                'Email': self.SUPPORT_EMAIL,
                'Hours': self.SUPPORT_HOURS,
                'Emergency': self.EMERGENCY_CONTACT
            }
        }
    
    def reload(self):
        """Reload configuration from file"""
        self.__init__(self.config_file)


# Global configuration instance
_config = None

@st.cache_resource
def get_config():
    """Get the global configuration instance (cached)"""
    return AppConfig()

def reload_config():
    """Reload configuration from file"""
    # Clear the cache to force reload
    get_config.clear()
    return get_config()

