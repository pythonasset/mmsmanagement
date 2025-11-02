"""
Sample Data Initialization Script
Populates the database with sample data for testing and demonstration
"""
import sys
from datetime import datetime, timedelta, date
from random import choice, uniform, randint
from database import (
    init_database, get_session, AssetClass, AssetGroup, AssetType,
    Asset, WorkOrder, Inspection, User
)
from settings import (
    ASSET_STATUS_OPTIONS, WORK_ORDER_PRIORITIES, WORK_ORDER_STATUS,
    WORK_ORDER_TYPES, INSPECTION_TYPES
)

def create_sample_data():
    """Create comprehensive sample data"""
    print("Initializing database...")
    engine = init_database()
    session = get_session(engine)
    
    print("Creating sample asset hierarchy...")
    
    # Asset Classes, Groups, and Types
    asset_structure = {
        "Road Infrastructure": {
            "Road Network": ["Main Road", "Local Street", "Laneway", "Footpath"],
            "Traffic Control": ["Traffic Light", "Speed Sign", "Stop Sign", "Parking Sign"],
            "Road Furniture": ["Guardrail", "Bollard", "Street Light", "Bus Shelter"]
        },
        "Stormwater Drainage Infrastructure": {
            "Drainage Pipes": ["Main Pipe", "Branch Pipe", "Culvert"],
            "Drainage Structures": ["Pit", "Gully", "Inlet", "Outlet"],
            "Water Quality": ["Biofilter", "Gross Pollutant Trap", "Sediment Basin"]
        },
        "Recreational Infrastructure": {
            "Playgrounds": ["Playground Equipment", "Safety Surface", "Fence", "Seating"],
            "Sports Facilities": ["Sports Field", "Court", "Track", "Goal Post"],
            "Parks": ["BBQ Facility", "Picnic Table", "Park Bench", "Drinking Fountain"]
        },
        "Building Structures": {
            "Civic Buildings": ["Town Hall", "Library", "Community Center", "Office"],
            "Public Amenities": ["Public Toilet", "Change Room", "Kiosk"],
            "Storage": ["Shed", "Depot", "Warehouse"]
        }
    }
    
    asset_types_dict = {}
    
    for class_name, groups in asset_structure.items():
        # Create or get asset class
        asset_class = session.query(AssetClass).filter_by(name=class_name).first()
        if not asset_class:
            asset_class = AssetClass(name=class_name, description=f"{class_name} assets")
            session.add(asset_class)
            session.flush()
        
        for group_name, types in groups.items():
            # Create asset group
            asset_group = AssetGroup(
                name=group_name,
                description=f"{group_name} in {class_name}",
                asset_class_id=asset_class.id
            )
            session.add(asset_group)
            session.flush()
            
            for type_name in types:
                # Create asset type
                asset_type = AssetType(
                    name=type_name,
                    description=f"{type_name} asset",
                    asset_group_id=asset_group.id
                )
                session.add(asset_type)
                session.flush()
                asset_types_dict[f"{class_name}_{group_name}_{type_name}"] = asset_type
    
    session.commit()
    print(f"Created {len(asset_types_dict)} asset types")
    
    print("Creating sample assets...")
    
    # Sample locations in Melbourne area
    sample_locations = [
        {"lat": -37.8136, "lon": 144.9631, "address": "Federation Square, Melbourne VIC 3000"},
        {"lat": -37.8183, "lon": 144.9671, "address": "Alexandra Gardens, Melbourne VIC 3004"},
        {"lat": -37.8085, "lon": 144.9631, "address": "Queen Victoria Market, Melbourne VIC 3000"},
        {"lat": -37.8226, "lon": 144.9824, "address": "Royal Botanic Gardens, Melbourne VIC 3141"},
        {"lat": -37.8102, "lon": 144.9628, "address": "State Library Victoria, Melbourne VIC 3000"},
        {"lat": -37.8141, "lon": 144.9771, "address": "Treasury Gardens, Melbourne VIC 3002"},
        {"lat": -37.8197, "lon": 144.9729, "address": "Yarra Park, Melbourne VIC 3002"},
        {"lat": -37.8069, "lon": 144.9941, "address": "Fitzroy Gardens, Melbourne VIC 3002"},
        {"lat": -37.8256, "lon": 144.9612, "address": "Albert Park, Melbourne VIC 3206"},
        {"lat": -37.8116, "lon": 144.9502, "address": "Docklands, Melbourne VIC 3008"},
    ]
    
    assets = []
    asset_id_counter = 1
    
    # Create 50 sample assets
    for i in range(50):
        # Random asset type
        type_key = choice(list(asset_types_dict.keys()))
        asset_type = asset_types_dict[type_key]
        
        # Random location
        location = choice(sample_locations)
        
        # Add some variation to coordinates
        lat = location["lat"] + uniform(-0.01, 0.01)
        lon = location["lon"] + uniform(-0.01, 0.01)
        
        # Create asset
        asset = Asset(
            asset_id=f"AST-{asset_id_counter:05d}",
            name=f"{asset_type.name} {asset_id_counter}",
            description=f"Sample {asset_type.name} asset for testing",
            asset_type_id=asset_type.id,
            status=choice(ASSET_STATUS_OPTIONS),
            condition_rating=randint(1, 5),
            latitude=lat,
            longitude=lon,
            address=location["address"],
            acquisition_date=date.today() - timedelta(days=randint(365, 3650)),
            acquisition_cost=round(uniform(1000, 100000), 2),
            current_value=round(uniform(500, 80000), 2),
            manufacturer=choice(["ABC Corp", "XYZ Industries", "Global Assets Ltd", "BuildCo", "MaintainPro"]),
            model=f"Model-{randint(100, 999)}",
            serial_number=f"SN{randint(10000, 99999)}",
            created_by="System",
            modified_by="System"
        )
        session.add(asset)
        assets.append(asset)
        asset_id_counter += 1
    
    session.commit()
    print(f"Created {len(assets)} sample assets")
    
    print("Creating sample work orders...")
    
    work_orders = []
    wo_counter = 1
    
    # Create 30 work orders
    for i in range(30):
        asset = choice(assets)
        
        created_date = datetime.now() - timedelta(days=randint(0, 90))
        
        wo_status = choice(WORK_ORDER_STATUS)
        
        # Set dates based on status
        scheduled_date = None
        start_date = None
        completion_date = None
        
        if wo_status in ["In Progress", "Completed", "Cancelled"]:
            scheduled_date = created_date + timedelta(days=randint(1, 7))
            start_date = scheduled_date + timedelta(days=randint(0, 3))
            
            if wo_status == "Completed":
                completion_date = start_date + timedelta(days=randint(1, 14))
        
        work_order = WorkOrder(
            work_order_number=f"WO-{wo_counter:05d}",
            asset_id=asset.id,
            title=f"{choice(WORK_ORDER_TYPES)} - {asset.name}",
            description=f"Sample work order for {asset.name}",
            work_type=choice(WORK_ORDER_TYPES),
            priority=choice(WORK_ORDER_PRIORITIES),
            status=wo_status,
            created_date=created_date,
            scheduled_date=scheduled_date,
            start_date=start_date,
            completion_date=completion_date,
            due_date=created_date + timedelta(days=randint(7, 30)),
            assigned_to=choice(["John Smith", "Jane Doe", "Bob Wilson", "Alice Brown", "Charlie Davis"]),
            estimated_cost=round(uniform(100, 5000), 2),
            actual_cost=round(uniform(100, 5000), 2) if wo_status == "Completed" else None,
            labor_hours=round(uniform(1, 40), 1) if wo_status == "Completed" else None,
            notes="Sample work order created for testing purposes",
            latitude=asset.latitude,
            longitude=asset.longitude,
            created_by="System"
        )
        session.add(work_order)
        work_orders.append(work_order)
        wo_counter += 1
    
    session.commit()
    print(f"Created {len(work_orders)} sample work orders")
    
    print("Creating sample inspections...")
    
    inspections = []
    insp_counter = 1
    
    # Create 25 inspections
    for i in range(25):
        asset = choice(assets)
        
        inspection_date = datetime.now() - timedelta(days=randint(0, 180))
        
        defects_found = choice([True, False, False])  # 33% chance of defects
        
        inspection = Inspection(
            inspection_number=f"INSP-{insp_counter:05d}",
            asset_id=asset.id,
            inspection_type=choice(INSPECTION_TYPES),
            inspection_date=inspection_date,
            inspector=choice(["Inspector A", "Inspector B", "Inspector C", "Inspector D"]),
            status=choice(["Completed", "Completed", "Scheduled"]),
            condition_rating=randint(1, 5),
            defects_found=defects_found,
            defect_description="Sample defect description found during inspection" if defects_found else None,
            recommendations="Recommend maintenance action" if defects_found else "Asset in good condition",
            follow_up_required=defects_found,
            follow_up_date=date.today() + timedelta(days=randint(7, 30)) if defects_found else None,
            latitude=asset.latitude,
            longitude=asset.longitude
        )
        session.add(inspection)
        inspections.append(inspection)
        insp_counter += 1
    
    session.commit()
    print(f"Created {len(inspections)} sample inspections")
    
    print("Creating sample users...")
    
    # Create sample users
    users = [
        User(username="admin", email="admin@example.com", full_name="System Administrator", role="Admin", department="IT"),
        User(username="manager1", email="manager1@example.com", full_name="John Manager", role="Manager", department="Operations"),
        User(username="tech1", email="tech1@example.com", full_name="Jane Technician", role="Technician", department="Maintenance"),
        User(username="inspector1", email="inspector1@example.com", full_name="Bob Inspector", role="Inspector", department="Quality"),
        User(username="viewer1", email="viewer1@example.com", full_name="Alice Viewer", role="Viewer", department="Finance"),
    ]
    
    for user in users:
        session.add(user)
    
    session.commit()
    print(f"Created {len(users)} sample users")
    
    print("\n" + "="*60)
    print("Sample data creation completed successfully!")
    print("="*60)
    print("\nSummary:")
    print(f"  - Asset Classes: {session.query(AssetClass).count()}")
    print(f"  - Asset Groups: {session.query(AssetGroup).count()}")
    print(f"  - Asset Types: {session.query(AssetType).count()}")
    print(f"  - Assets: {session.query(Asset).count()}")
    print(f"  - Work Orders: {session.query(WorkOrder).count()}")
    print(f"  - Inspections: {session.query(Inspection).count()}")
    print(f"  - Users: {session.query(User).count()}")
    print("\nYou can now run the application with: streamlit run app.py")

if __name__ == "__main__":
    try:
        create_sample_data()
    except Exception as e:
        print(f"\nError creating sample data: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
