"""
Configuration settings for Maintenance Management System
"""

# Database configuration
DATABASE_PATH = 'sqlite:///data/maintenance_management.db'

# Application settings
APP_TITLE = "Maintenance Management System"
APP_ICON = "🔧"
COMPANY_NAME = "Your Organization"

# Map settings
DEFAULT_MAP_CENTER = [-37.8136, 144.9631]  # Melbourne, Australia
DEFAULT_MAP_ZOOM = 11

# Asset condition ratings
CONDITION_RATINGS = {
    1: "Very Poor",
    2: "Poor",
    3: "Fair",
    4: "Good",
    5: "Excellent"
}

# Asset status options
ASSET_STATUS_OPTIONS = [
    "Active",
    "Inactive",
    "Under Maintenance",
    "Disposed",
    "Reserved"
]

# Work order priorities
WORK_ORDER_PRIORITIES = [
    "Critical",
    "High",
    "Medium",
    "Low"
]

# Work order status
WORK_ORDER_STATUS = [
    "Open",
    "In Progress",
    "On Hold",
    "Completed",
    "Cancelled"
]

# Work order types
WORK_ORDER_TYPES = [
    "Preventive Maintenance",
    "Corrective Maintenance",
    "Emergency Repair",
    "Inspection",
    "Installation",
    "Replacement",
    "Other"
]

# Inspection types
INSPECTION_TYPES = [
    "Routine Inspection",
    "Safety Inspection",
    "Condition Assessment",
    "Compliance Audit",
    "Pre-Purchase Inspection",
    "Post-Work Inspection"
]

# User roles
USER_ROLES = [
    "Admin",
    "Manager",
    "Supervisor",
    "Technician",
    "Inspector",
    "Viewer"
]

# Asset classes (default)
DEFAULT_ASSET_CLASSES = [
    {
        "name": "Road Infrastructure",
        "description": "Roads, pavements, and related infrastructure"
    },
    {
        "name": "Stormwater Drainage Infrastructure",
        "description": "Drainage systems, pipes, and related assets"
    },
    {
        "name": "Recreational Infrastructure",
        "description": "Parks, playgrounds, and recreational facilities"
    },
    {
        "name": "Building Structures",
        "description": "Buildings and permanent structures"
    },
    {
        "name": "Miscellaneous",
        "description": "Other assets including biodiversity assets, artwork, etc."
    }
]

# Export formats
EXPORT_FORMATS = ["CSV", "Excel", "KML (Google Earth)", "PDF"]

# Date format
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# File formats for document management
FILE_FORMATS = [
    "PDF",
    "DOCX",
    "DOC",
    "XLSX",
    "XLS",
    "JPG",
    "JPEG",
    "PNG",
    "GIF",
    "BMP",
    "TIFF",
    "DWG",
    "DXF",
    "DWF",
    "RVT",
    "SKP",
    "MP4",
    "AVI",
    "MOV",
    "TXT",
    "CSV",
    "ZIP",
    "RAR",
    "7Z",
    "Other"
]

# Pagination
ITEMS_PER_PAGE = 20
