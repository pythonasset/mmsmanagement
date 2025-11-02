# Configuration Guide

## Overview

The Maintenance Management System uses a `config.ini` file for all configuration settings. This makes it easy to customize the application for your organization without modifying code.

## Location

The configuration file must be located in the root directory of the application:

```bash
/mmsmanagement/
  ├── config.ini        ← Configuration file
  ├── app.py
  ├── database.py
  └── ...
```

## Configuration Sections

### [Application]

Application-level settings:

- `app_title` - The name of your application
- `app_icon` - Emoji icon for the application
- `version` - Current version number
- `environment` - Production, Development, or Testing

### [Organization]

Your organization's details:

- `company_name` - Your company/organization name
- `registered_to` - License holder name
- `department` - Department using the system
- `abn` - Australian Business Number

### [Developer]

Developer/vendor information:

- `produced_by` - Software developer/vendor name
- `developer_contact` - Support email address
- `developer_website` - Developer website URL
- `support_phone` - Support phone number

### [Database]

Database configuration:

- `database_path` - Path to SQLite database file
- `backup_path` - Path for database backups

### [Documents]

Document storage paths:

- `document_root` - Root directory for all documents
- `asset_documents` - Subdirectory for asset documents
- `workorder_documents` - Subdirectory for work order documents
- `inspection_documents` - Subdirectory for inspection documents

### [Regional]

Regional settings:

- `country` - Country name
- `timezone` - Timezone (e.g., Australia/Sydney)
- `currency` - Currency code (e.g., AUD)
- `currency_symbol` - Currency symbol (e.g., $)

### [Features]

Feature flags to enable/disable functionality:

- `enable_google_earth` - Enable/disable Google Earth export
- `enable_document_management` - Enable/disable document management
- `enable_user_management` - Enable/disable user management
- `enable_reports` - Enable/disable reporting features

### [Support]

Support contact information:

- `support_email` - Support email address
- `support_hours` - Support hours of operation
- `emergency_contact` - Emergency contact number

## How to Modify

1. **Stop the Application** - Close Streamlit if it's running
2. **Edit config.ini** - Use any text editor to modify the file
3. **Save Changes** - Save the file
4. **Restart Application** - Run `streamlit run app.py`

## Example Customization

To customize for your organization:

```ini
[Organization]
company_name = Acme Corporation
registered_to = Acme Corporation Pty Ltd
department = Facilities Management
abn = 12 345 678 901

[Developer]
produced_by = Your Software Company
developer_contact = support@yourcompany.com
developer_website = https://www.yourcompany.com
support_phone = 1300 123 456
```

## Viewing Configuration

Configuration settings can be viewed in the application:

1. Navigate to **⚙️ Administration**
2. Select **System Settings** tab
3. Expand the **📄 Configuration Overview** sections

## Sidebar Information

The sidebar displays:

- **System Information** - App title, version, environment
- **📋 Registration Info** (expandable) - Registered to, department, ABN
- **🔧 Developer Info** (expandable) - Developer name, contact, website

## Important Notes

- ✅ All paths are created automatically on startup
- ✅ Settings are loaded once when the application starts
- ✅ Changes require application restart to take effect
- ⚠️ Do not delete required sections (will use defaults)
- ⚠️ Keep proper INI file format (section headers in [brackets])

## Troubleshooting

**Configuration file not found:**

- Ensure `config.ini` is in the application root directory
- Check file name spelling (case-sensitive on some systems)

**Invalid configuration:**

- Check INI file syntax
- Ensure section headers use [square brackets]
- Verify boolean values are `True` or `False`

**Changes not appearing:**

- Restart the Streamlit application
- Clear browser cache (Ctrl+Shift+R)

## Support

For configuration assistance, refer to:

- Application: **⚙️ Administration** → **System Settings**
- Developer contact information in the sidebar
- `config.ini` file comments
