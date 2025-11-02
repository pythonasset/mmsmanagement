# Maintenance Management System

A comprehensive web-based maintenance management system built with Python and Streamlit, featuring Google Earth integration for asset and work order tracking.

## Features

### 🏗️ Modular Architecture

- **Asset Management** - Hierarchical asset register (Class → Group → Type → Asset)
- **Work Order Management** - Complete work order lifecycle management
- **Inspection Management** - Asset inspection scheduling and tracking
- **Reporting & Analytics** - Comprehensive dashboards and reports
- **Google Earth Integration** - KML export for visual tracking

### 📍 Location-Based Tracking

- GPS coordinate storage for all assets
- Interactive map views using Folium
- Google Earth KML export for assets, work orders, and inspections
- Visual color-coding based on status, priority, and condition

### 📊 Analytics & Reporting

- Executive dashboard with KPIs
- Asset condition reports
- Work order trends and analytics
- Maintenance cost analysis
- Performance metrics

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup Steps

1. **Clone or download the project**

```bash
cd maintenance_management_system
```

2. **Create a virtual environment (recommended)**

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Create data directory**

```bash
mkdir -p data
```

## Running the Application

### Start the application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### First Run

On first run, the system will automatically:

- Create the SQLite database
- Initialize default asset classes:
  - Road Infrastructure
  - Stormwater Drainage Infrastructure
  - Recreational Infrastructure
  - Building Structures
  - Miscellaneous

## Usage Guide

### 1. Asset Management

#### Set Up Asset Hierarchy

1. Navigate to **Asset Management → Asset Hierarchy**
2. Create Asset Classes (top-level categories)
3. Add Asset Groups within each class
4. Define Asset Types within each group

#### Register Assets

1. Go to **Asset Management → Add New Asset**
2. Fill in asset details:
   - Asset ID (unique identifier)
   - Name and description
   - Asset type
   - Location (address and GPS coordinates)
   - Condition rating
   - Financial information
3. Submit to create the asset

#### View Assets

- **Asset Register** - Tabular view with filters
- **Asset Map** - Geographic visualization
- Click on any asset to view detailed information

### 2. Work Order Management

#### Create Work Orders

1. Navigate to **Work Order Management → Create Work Order**
2. Enter work order details:
   - Title and description
   - Associated asset
   - Work type and priority
   - Assignment and scheduling
   - Cost estimates
3. Optionally override location from asset

#### Track Work Orders

- Filter by status, priority, type
- View on interactive map
- Monitor completion rates
- Track costs and labor hours

### 3. Inspection Management

#### Schedule Inspections

1. Go to **Inspection Management → Create Inspection**
2. Select asset and inspection type
3. Record findings:
   - Condition rating
   - Defects found
   - Recommendations
   - Follow-up requirements

#### Inspection Tracking

- View all inspections with filters
- Track defect rates
- Monitor follow-up requirements
- Export inspection data

### 4. Reports & Analytics

#### Dashboard

- View key performance indicators
- Asset condition overview
- Work order trends
- System statistics

#### Asset Reports

- Asset register summary
- Condition reports
- Valuation reports
- Location reports

#### Maintenance Reports

- Work order summaries
- Cost analysis
- Inspection reports
- Performance metrics

### 5. Google Earth Integration

#### Export to KML

1. Navigate to any map view (Assets, Work Orders, or Inspections)
2. Click "Export to Google Earth (KML)"
3. Download the KML file
4. Open in Google Earth to visualize

#### Bulk Export

- Use sidebar "Export All to Google Earth" for complete export
- Generates separate KML files for assets, work orders, and inspections

## Database

### Location

SQLite database is stored at: `data/maintenance_management.db`

### Backup

To backup your data, simply copy the database file:

```bash
cp data/maintenance_management.db data/maintenance_management_backup.db
```

### Schema

The system includes the following main tables:

- `asset_classes` - Top-level asset categories
- `asset_groups` - Mid-level groupings
- `asset_types` - Detailed asset types
- `assets` - Individual asset records
- `work_orders` - Maintenance work orders
- `inspections` - Inspection records
- `users` - User management
- `audit_logs` - Audit trail

## Configuration

Edit `config/settings.py` to customize:

- Database path
- Default map center coordinates
- Asset classes
- Status options
- Priority levels
- Work order types
- Inspection types

## File Structure

```bash

maintenance_management_system/
├── app.py                          # Main application
├── requirements.txt                # Python dependencies
├── config/
│   └── settings.py                 # Configuration settings
├── modules/
│   ├── database.py                 # Database models
│   ├── asset_management.py         # Asset management module
│   ├── work_order_management.py    # Work order module
│   ├── inspection_management.py    # Inspection module
│   ├── reporting.py                # Reporting & analytics
│   └── google_earth.py             # KML export functionality
└── data/
    └── maintenance_management.db   # SQLite database (created on first run)
```

## Features by Module

### Asset Management

✅ Hierarchical asset structure (Class/Group/Type)  
✅ GPS coordinate tracking  
✅ Asset condition rating (1-5 scale)  
✅ Financial tracking (acquisition cost, current value)  
✅ Asset status management  
✅ Interactive map visualization  
✅ KML export for Google Earth  

### Work Order Management

✅ Work order creation and tracking  
✅ Priority-based management (Critical/High/Medium/Low)  
✅ Status workflow (Open/In Progress/On Hold/Completed/Cancelled)  
✅ Cost tracking (estimated vs actual)  
✅ Labor hours tracking  
✅ Assignment management  
✅ Location override capability  
✅ Map-based visualization  

### Inspection Management

✅ Inspection scheduling  
✅ Defect detection and recording  
✅ Condition assessment  
✅ Follow-up tracking  
✅ Inspector assignment  
✅ Recommendations capture  
✅ Work order generation from inspections  

### Reporting & Analytics

✅ Executive dashboard  
✅ Asset condition reports  
✅ Asset valuation reports  
✅ Work order analytics  
✅ Cost analysis  
✅ Performance metrics  
✅ Trend visualization  
✅ Export capabilities (CSV, Excel)  

## Troubleshooting

### Database Issues

If you encounter database errors:

```bash
# Delete the database and restart (WARNING: loses all data)
rm data/maintenance_management.db
streamlit run app.py
```

### Import Errors

If you get import errors:

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Port Already in Use

If port 8501 is busy:

```bash
streamlit run app.py --server.port 8502
```

## Future Enhancements

Planned features for future versions:

- User authentication and role-based access control
- Email notifications for work orders and inspections
- Mobile app integration
- Barcode/QR code scanning
- Predictive maintenance using ML
- Integration with external systems (ERP, Finance)
- Automated report scheduling
- Document attachment support
- Custom workflow configuration

## Support

For issues, questions, or feature requests:

- Email: <support@example.com>
- Documentation: [Link to documentation]
- GitHub Issues: [Link to issue tracker]

## License

[Your License Here]

## Credits

Built with:

- [Streamlit](https://streamlit.io/) - Web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [Folium](https://python-visualization.github.io/folium/) - Map visualization
- [Plotly](https://plotly.com/) - Interactive charts
- [SimpleKML](https://simplekml.readthedocs.io/) - Google Earth integration

---

**Version:** 1.0.0  
**Last Updated:** October 2025
