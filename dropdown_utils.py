"""
Utility functions for managing dropdown values
"""
import streamlit as st
from database import DropdownValue
from settings import (
    WORK_ORDER_TYPES, WORK_ORDER_PRIORITIES, WORK_ORDER_STATUS,
    ASSET_STATUS_OPTIONS, CONDITION_RATINGS, INSPECTION_TYPES,
    USER_ROLES, FILE_FORMATS
)

# Category constants
CATEGORY_WORK_ORDER_TYPE = "work_order_type"
CATEGORY_WORK_ORDER_PRIORITY = "work_order_priority"
CATEGORY_WORK_ORDER_STATUS = "work_order_status"
CATEGORY_ASSET_STATUS = "asset_status"
CATEGORY_CONDITION_RATING = "condition_rating"
CATEGORY_INSPECTION_TYPE = "inspection_type"
CATEGORY_USER_ROLE = "user_role"
CATEGORY_FILE_FORMAT = "file_format"

# Mapping of categories to their display names
CATEGORY_DISPLAY_NAMES = {
    CATEGORY_WORK_ORDER_TYPE: "Work Order Types",
    CATEGORY_WORK_ORDER_PRIORITY: "Work Order Priorities",
    CATEGORY_WORK_ORDER_STATUS: "Work Order Status",
    CATEGORY_ASSET_STATUS: "Asset Status Options",
    CATEGORY_CONDITION_RATING: "Condition Ratings",
    CATEGORY_INSPECTION_TYPE: "Inspection Types",
    CATEGORY_USER_ROLE: "User Roles",
    CATEGORY_FILE_FORMAT: "File Formats"
}

# Default values from settings.py
DEFAULT_VALUES = {
    CATEGORY_WORK_ORDER_TYPE: WORK_ORDER_TYPES,
    CATEGORY_WORK_ORDER_PRIORITY: WORK_ORDER_PRIORITIES,
    CATEGORY_WORK_ORDER_STATUS: WORK_ORDER_STATUS,
    CATEGORY_ASSET_STATUS: ASSET_STATUS_OPTIONS,
    CATEGORY_CONDITION_RATING: [f"{k} - {v}" for k, v in CONDITION_RATINGS.items()],
    CATEGORY_INSPECTION_TYPE: INSPECTION_TYPES,
    CATEGORY_USER_ROLE: USER_ROLES,
    CATEGORY_FILE_FORMAT: FILE_FORMATS
}


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_dropdown_values(_session, category):
    """
    Get dropdown values for a category from database, with fallback to settings.py (cached)
    
    Args:
        _session: SQLAlchemy session (prefixed with _ to avoid hashing)
        category: Category name (e.g., 'work_order_type')
    
    Returns:
        List of values for the dropdown
    """
    # Try to get from database
    db_values = _session.query(DropdownValue).filter(
        DropdownValue.category == category,
        DropdownValue.is_active == True
    ).order_by(DropdownValue.display_order, DropdownValue.value).all()
    
    if db_values:
        return [v.value for v in db_values]
    
    # Fallback to settings.py defaults
    return DEFAULT_VALUES.get(category, [])


def initialize_dropdown_defaults(session):
    """
    Initialize dropdown values from settings.py if database is empty
    
    Args:
        session: SQLAlchemy session
    """
    # Check if any dropdown values exist
    existing = session.query(DropdownValue).count()
    if existing > 0:
        return  # Already initialized
    
    # Initialize with default values
    for category, values in DEFAULT_VALUES.items():
        for idx, value in enumerate(values):
            dropdown_value = DropdownValue(
                category=category,
                value=value,
                display_order=idx,
                is_active=True,
                is_default=True
            )
            session.add(dropdown_value)
    
    session.commit()


def add_dropdown_value(session, category, value, display_order=None):
    """
    Add a new dropdown value
    
    Args:
        session: SQLAlchemy session
        category: Category name
        value: Value to add
        display_order: Optional display order (defaults to last)
    
    Returns:
        The created DropdownValue object or None if already exists
    """
    # Check if value already exists in this category
    existing = session.query(DropdownValue).filter(
        DropdownValue.category == category,
        DropdownValue.value == value
    ).first()
    
    if existing:
        return None  # Already exists
    
    # Get max display order if not specified
    if display_order is None:
        max_order = session.query(DropdownValue).filter(
            DropdownValue.category == category
        ).count()
        display_order = max_order
    
    dropdown_value = DropdownValue(
        category=category,
        value=value,
        display_order=display_order,
        is_active=True,
        is_default=False
    )
    
    session.add(dropdown_value)
    session.commit()
    return dropdown_value


def update_dropdown_value(session, dropdown_id, new_value=None, new_display_order=None):
    """
    Update a dropdown value
    
    Args:
        session: SQLAlchemy session
        dropdown_id: ID of the dropdown value to update
        new_value: New value (optional)
        new_display_order: New display order (optional)
    
    Returns:
        True if updated, False otherwise
    """
    dropdown_value = session.query(DropdownValue).filter(
        DropdownValue.id == dropdown_id
    ).first()
    
    if not dropdown_value:
        return False
    
    if new_value is not None:
        dropdown_value.value = new_value
    
    if new_display_order is not None:
        dropdown_value.display_order = new_display_order
    
    session.commit()
    return True


def delete_dropdown_value(session, dropdown_id):
    """
    Delete (deactivate) a dropdown value
    
    Args:
        session: SQLAlchemy session
        dropdown_id: ID of the dropdown value to delete
    
    Returns:
        True if deleted, False otherwise
    """
    dropdown_value = session.query(DropdownValue).filter(
        DropdownValue.id == dropdown_id
    ).first()
    
    if not dropdown_value:
        return False
    
    # Soft delete by marking as inactive
    dropdown_value.is_active = False
    session.commit()
    return True


def reorder_dropdown_values(session, category, value_ids_in_order):
    """
    Reorder dropdown values for a category
    
    Args:
        session: SQLAlchemy session
        category: Category name
        value_ids_in_order: List of dropdown value IDs in desired order
    """
    for idx, value_id in enumerate(value_ids_in_order):
        dropdown_value = session.query(DropdownValue).filter(
            DropdownValue.id == value_id,
            DropdownValue.category == category
        ).first()
        
        if dropdown_value:
            dropdown_value.display_order = idx
    
    session.commit()

