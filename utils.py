"""
Utility functions for the Maintenance Management System
"""
import locale
import os
from datetime import datetime, date
from typing import Optional, Union

# Force detection on every import - don't cache
_DETECTED_FORMAT = None
_FORCE_AUSTRALIAN_FORMAT = True  # Set to True to force Australian format

def _detect_date_format():
    """Detect the date format from Windows regional settings or system locale"""
    global _DETECTED_FORMAT
    
    if _DETECTED_FORMAT is not None:
        return _DETECTED_FORMAT
    
    try:
        # Try to set locale to system default
        locale.setlocale(locale.LC_TIME, '')
        current_locale = locale.getlocale(locale.LC_TIME)
        
        # Check if it's an Australian or UK locale (DD/MM/YYYY format)
        if current_locale and current_locale[0]:
            locale_name = current_locale[0].lower()
            if 'australia' in locale_name or 'english_australia' in locale_name:
                _DETECTED_FORMAT = 'DD/MM/YYYY'
                return _DETECTED_FORMAT
            elif 'en_gb' in locale_name or 'uk' in locale_name or 'british' in locale_name:
                _DETECTED_FORMAT = 'DD/MM/YYYY'
                return _DETECTED_FORMAT
            elif 'en_us' in locale_name or 'united_states' in locale_name or 'english_united states' in locale_name:
                _DETECTED_FORMAT = 'MM/DD/YYYY'
                return _DETECTED_FORMAT
        
        # Test format by formatting a known date and checking the output
        test_date = datetime(2025, 1, 31)  # Jan 31, 2025
        formatted = test_date.strftime('%x')
        
        # Parse the result to determine format
        # Check for DD/MM/YYYY (starts with 31)
        if formatted.startswith('31') or '/01/' in formatted or formatted.endswith('/2025'):
            _DETECTED_FORMAT = 'DD/MM/YYYY'  # Day first (AU, UK, EU)
        # Check for MM/DD/YYYY (starts with 01 and has 31 later)
        elif (formatted.startswith('01') or formatted.startswith('1')) and '/31/' in formatted:
            _DETECTED_FORMAT = 'MM/DD/YYYY'  # Month first (US)
        # Check for YYYY/MM/DD or YYYY-MM-DD
        elif formatted.startswith('2025'):
            _DETECTED_FORMAT = 'YYYY/MM/DD'  # Year first (ISO)
        else:
            # Default to DD/MM/YYYY for ambiguous cases
            _DETECTED_FORMAT = 'DD/MM/YYYY'
            
    except Exception:
        # Default to DD/MM/YYYY (Australian format)
        _DETECTED_FORMAT = 'DD/MM/YYYY'
    
    return _DETECTED_FORMAT


def format_date(date_obj: Optional[Union[datetime, date]], include_time: bool = False) -> str:
    """
    Format a date or datetime object using system locale settings
    
    Args:
        date_obj: The date or datetime object to format
        include_time: Whether to include time in the output (for datetime objects)
    
    Returns:
        Formatted date string according to system locale, or 'N/A' if date_obj is None
    """
    if date_obj is None:
        return "N/A"
    
    # Check if forced Australian format
    if _FORCE_AUSTRALIAN_FORMAT:
        detected_format = 'DD/MM/YYYY'
    else:
        detected_format = _detect_date_format()
    
    try:
        if isinstance(date_obj, datetime):
            dt = date_obj
        elif isinstance(date_obj, date):
            dt = datetime.combine(date_obj, datetime.min.time())
        else:
            return str(date_obj)
        
        # Format based on detected format
        if detected_format == 'DD/MM/YYYY':
            date_str = dt.strftime('%d/%m/%Y')
            if include_time:
                time_str = dt.strftime('%H:%M:%S')
                return f"{date_str} {time_str}"
            return date_str
        elif detected_format == 'MM/DD/YYYY':
            date_str = dt.strftime('%m/%d/%Y')
            if include_time:
                time_str = dt.strftime('%H:%M:%S')
                return f"{date_str} {time_str}"
            return date_str
        else:  # YYYY/MM/DD or other
            date_str = dt.strftime('%Y/%m/%d')
            if include_time:
                time_str = dt.strftime('%H:%M:%S')
                return f"{date_str} {time_str}"
            return date_str
            
    except Exception as e:
        # Fallback to DD/MM/YYYY (Australian format)
        if isinstance(date_obj, datetime):
            if include_time:
                return date_obj.strftime('%d/%m/%Y %H:%M:%S')
            else:
                return date_obj.strftime('%d/%m/%Y')
        elif isinstance(date_obj, date):
            return date_obj.strftime('%d/%m/%Y')
        else:
            return str(date_obj)


def format_datetime(datetime_obj: Optional[datetime]) -> str:
    """
    Format a datetime object using system locale settings with time
    
    Args:
        datetime_obj: The datetime object to format
    
    Returns:
        Formatted datetime string according to system locale, or 'N/A' if datetime_obj is None
    """
    return format_date(datetime_obj, include_time=True)


def format_date_short(date_obj: Optional[Union[datetime, date]]) -> str:
    """
    Format a date object using short date format
    
    Args:
        date_obj: The date or datetime object to format
    
    Returns:
        Formatted short date string, or 'N/A' if date_obj is None
    """
    # Use the same format as format_date (no time)
    return format_date(date_obj, include_time=False)


def get_locale_info() -> dict:
    """
    Get information about the current locale settings
    
    Returns:
        Dictionary with locale information
    """
    try:
        current_locale = locale.getlocale(locale.LC_TIME)
        
        if _FORCE_AUSTRALIAN_FORMAT:
            detected_format = 'DD/MM/YYYY (Forced Australian)'
        else:
            detected_format = _detect_date_format()
        
        locale_name = "System Default"
        if current_locale and current_locale[0]:
            locale_name = current_locale[0]
        
        return {
            "locale": locale_name,
            "date_format": detected_format,
            "sample": format_date(datetime.now())
        }
    except:
        return {
            "locale": "Unknown",
            "date_format": "DD/MM/YYYY (default)",
            "sample": datetime.now().strftime('%d/%m/%Y')
        }

