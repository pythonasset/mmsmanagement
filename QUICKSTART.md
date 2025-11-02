# Quick Start Guide - Maintenance Management System

## 5-Minute Setup

### Step 1: Install Python Dependencies (1 minute)

```bash
cd maintenance_management_system
pip install -r requirements.txt
```

### Step 2: Run the Application (30 seconds)

```bash
streamlit run app.py
```

The application will open automatically in your browser at <http://localhost:8501>

### Step 3: Optional - Load Sample Data (1 minute)

To populate the system with sample data for testing:

```bash
python create_sample_data.py
```

This will create:

- Sample asset hierarchy (Classes, Groups, Types)
- 50 sample assets with locations
- 30 sample work orders
- 25 sample inspections
- 5 sample users

### Step 4: Start Using the System

#### First Task: Add Your First Asset

1. Click "📦 Asset Management" in the sidebar
2. Go to "Add New Asset" tab
3. Fill in:
   - Asset ID: `ROAD-001`
   - Name: `Main Street Section 1`
   - Select an Asset Type
   - Enter GPS coordinates (e.g., -37.8136, 144.9631 for Melbourne)
4. Click "Add Asset"

#### Second Task: Create a Work Order

1. Click "🔧 Work Order Management"
2. Go to "Create Work Order" tab
3. Fill in:
   - Title: `Repair pothole on Main Street`
   - Select your asset
   - Set Priority: `High`
   - Add description
4. Click "Create Work Order"

#### Third Task: View on Map

1. Go to "Work Order Map" tab
2. See your work order displayed on the interactive map
3. Click "Export to Google Earth (KML)" to view in Google Earth

#### Fourth Task: Generate Reports

1. Click "📊 Reports & Analytics"
2. View the Dashboard for system overview
3. Explore different report types

## Common Tasks

### Exporting to Google Earth

1. Navigate to any map view (Assets, Work Orders, or Inspections)
2. Click the "📍 Export to Google Earth (KML)" button
3. Download the KML file
4. Open in Google Earth application or Google Earth Web

### Creating Asset Hierarchy

1. Go to "📦 Asset Management → Asset Hierarchy"
2. Add Asset Classes (e.g., "Roads", "Buildings")
3. Add Groups within each class
4. Add Types within each group
5. Now you can assign these types when creating assets

### Filtering and Searching

- All list views have filters at the top
- Use search boxes to find specific items
- Date range filters for time-based queries
- Export filtered results to CSV

### Understanding Asset Condition Ratings

- 5 = Excellent (Green)
- 4 = Good (Light Green)
- 3 = Fair (Yellow)
- 2 = Poor (Orange)
- 1 = Very Poor (Red)

## Tips for Best Results

1. **Always include GPS coordinates** for assets to enable map visualization
2. **Use consistent naming conventions** for Asset IDs
3. **Set realistic due dates** for work orders
4. **Record inspection findings** promptly
5. **Link work orders to assets** for better tracking
6. **Use priority levels** appropriately (Critical, High, Medium, Low)
7. **Export to KML regularly** for backup and visualization

## Troubleshooting

### Port Already in Use

```bash
streamlit run app.py --server.port 8502
```

### Database Reset (WARNING: Deletes all data)

```bash
rm data/maintenance_management.db
streamlit run app.py
```

### Reinstall Dependencies

```bash
pip install -r requirements.txt --upgrade --force-reinstall
```

## Next Steps

1. **Customize Settings** - Edit `config/settings.py` to match your organization
2. **Add Real Assets** - Replace sample data with your actual assets
3. **Set Up Users** - Create user accounts for your team
4. **Configure Workflows** - Customize work order types and statuses
5. **Schedule Inspections** - Set up regular inspection schedules
6. **Generate Reports** - Create custom reports for stakeholders

## Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Review the functional requirements in the original Excel file
- Contact support: <support@example.com>

---

**You're now ready to manage your assets efficiently!** 🎉
