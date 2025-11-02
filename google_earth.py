"""
Google Earth Integration Module
Handles KML file generation for assets and work orders
"""
import simplekml
from datetime import datetime

class GoogleEarthExporter:
    """Export assets and work orders to Google Earth KML format"""
    
    def __init__(self):
        self.kml = simplekml.Kml()
    
    def add_asset(self, asset, asset_type_name):
        """Add an asset to the KML file"""
        if asset.latitude and asset.longitude:
            # Determine icon based on status
            icon_url = self._get_asset_icon(asset.status)
            
            # Create placemark
            pnt = self.kml.newpoint(name=asset.name)
            pnt.coords = [(asset.longitude, asset.latitude)]
            pnt.style.iconstyle.icon.href = icon_url
            
            # Add description with asset details
            description = f"""
            <![CDATA[
            <h3>{asset.name}</h3>
            <table border="1" cellpadding="5" style="border-collapse: collapse;">
                <tr><td><b>Asset ID:</b></td><td>{asset.asset_id}</td></tr>
                <tr><td><b>Type:</b></td><td>{asset_type_name}</td></tr>
                <tr><td><b>Status:</b></td><td>{asset.status}</td></tr>
                <tr><td><b>Condition:</b></td><td>{self._get_condition_text(asset.condition_rating)}</td></tr>
                <tr><td><b>Address:</b></td><td>{asset.address or 'N/A'}</td></tr>
                <tr><td><b>Description:</b></td><td>{asset.description or 'N/A'}</td></tr>
                <tr><td><b>Manufacturer:</b></td><td>{asset.manufacturer or 'N/A'}</td></tr>
                <tr><td><b>Model:</b></td><td>{asset.model or 'N/A'}</td></tr>
                <tr><td><b>Serial Number:</b></td><td>{asset.serial_number or 'N/A'}</td></tr>
                <tr><td><b>Acquisition Date:</b></td><td>{asset.acquisition_date or 'N/A'}</td></tr>
                <tr><td><b>Current Value:</b></td><td>${asset.current_value or 0:,.2f}</td></tr>
            </table>
            ]]>
            """
            pnt.description = description
            
            # Set color based on condition
            if asset.condition_rating:
                pnt.style.iconstyle.color = self._get_condition_color(asset.condition_rating)
    
    def add_work_order(self, work_order, asset_name):
        """Add a work order to the KML file"""
        # Use work order location if available, otherwise use asset location
        latitude = work_order.latitude
        longitude = work_order.longitude
        
        if latitude and longitude:
            # Determine icon based on priority
            icon_url = self._get_work_order_icon(work_order.priority)
            
            # Create placemark
            pnt = self.kml.newpoint(name=f"WO: {work_order.work_order_number}")
            pnt.coords = [(longitude, latitude)]
            pnt.style.iconstyle.icon.href = icon_url
            
            # Add description with work order details
            description = f"""
            <![CDATA[
            <h3>Work Order: {work_order.work_order_number}</h3>
            <table border="1" cellpadding="5" style="border-collapse: collapse;">
                <tr><td><b>Title:</b></td><td>{work_order.title}</td></tr>
                <tr><td><b>Asset:</b></td><td>{asset_name}</td></tr>
                <tr><td><b>Type:</b></td><td>{work_order.work_type}</td></tr>
                <tr><td><b>Priority:</b></td><td>{work_order.priority}</td></tr>
                <tr><td><b>Status:</b></td><td>{work_order.status}</td></tr>
                <tr><td><b>Assigned To:</b></td><td>{work_order.assigned_to or 'Unassigned'}</td></tr>
                <tr><td><b>Scheduled Date:</b></td><td>{work_order.scheduled_date or 'Not scheduled'}</td></tr>
                <tr><td><b>Due Date:</b></td><td>{work_order.due_date or 'N/A'}</td></tr>
                <tr><td><b>Description:</b></td><td>{work_order.description or 'N/A'}</td></tr>
                <tr><td><b>Estimated Cost:</b></td><td>${work_order.estimated_cost or 0:,.2f}</td></tr>
                <tr><td><b>Actual Cost:</b></td><td>${work_order.actual_cost or 0:,.2f}</td></tr>
            </table>
            ]]>
            """
            pnt.description = description
            
            # Set color based on priority
            pnt.style.iconstyle.color = self._get_priority_color(work_order.priority)
    
    def add_inspection(self, inspection, asset_name):
        """Add an inspection to the KML file"""
        latitude = inspection.latitude
        longitude = inspection.longitude
        
        if latitude and longitude:
            # Create placemark
            pnt = self.kml.newpoint(name=f"Inspection: {inspection.inspection_number}")
            pnt.coords = [(longitude, latitude)]
            pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/flag.png'
            
            # Add description
            description = f"""
            <![CDATA[
            <h3>Inspection: {inspection.inspection_number}</h3>
            <table border="1" cellpadding="5" style="border-collapse: collapse;">
                <tr><td><b>Asset:</b></td><td>{asset_name}</td></tr>
                <tr><td><b>Type:</b></td><td>{inspection.inspection_type}</td></tr>
                <tr><td><b>Date:</b></td><td>{inspection.inspection_date}</td></tr>
                <tr><td><b>Inspector:</b></td><td>{inspection.inspector or 'N/A'}</td></tr>
                <tr><td><b>Condition Rating:</b></td><td>{self._get_condition_text(inspection.condition_rating)}</td></tr>
                <tr><td><b>Defects Found:</b></td><td>{'Yes' if inspection.defects_found else 'No'}</td></tr>
                <tr><td><b>Defect Description:</b></td><td>{inspection.defect_description or 'None'}</td></tr>
                <tr><td><b>Recommendations:</b></td><td>{inspection.recommendations or 'None'}</td></tr>
                <tr><td><b>Follow-up Required:</b></td><td>{'Yes' if inspection.follow_up_required else 'No'}</td></tr>
            </table>
            ]]>
            """
            pnt.description = description
            
            # Color code based on defects
            if inspection.defects_found:
                pnt.style.iconstyle.color = simplekml.Color.red
            else:
                pnt.style.iconstyle.color = simplekml.Color.green
    
    def save(self, filename):
        """Save the KML file"""
        self.kml.save(filename)
        return filename
    
    def _get_asset_icon(self, status):
        """Get icon URL based on asset status"""
        if status == "Active":
            return 'http://maps.google.com/mapfiles/kml/paddle/grn-circle.png'
        elif status == "Under Maintenance":
            return 'http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png'
        elif status == "Inactive":
            return 'http://maps.google.com/mapfiles/kml/paddle/red-circle.png'
        else:
            return 'http://maps.google.com/mapfiles/kml/paddle/wht-circle.png'
    
    def _get_work_order_icon(self, priority):
        """Get icon URL based on work order priority"""
        if priority == "Critical":
            return 'http://maps.google.com/mapfiles/kml/paddle/red-stars.png'
        elif priority == "High":
            return 'http://maps.google.com/mapfiles/kml/paddle/red-diamond.png'
        elif priority == "Medium":
            return 'http://maps.google.com/mapfiles/kml/paddle/ylw-diamond.png'
        else:
            return 'http://maps.google.com/mapfiles/kml/paddle/grn-diamond.png'
    
    def _get_condition_color(self, rating):
        """Get color based on condition rating"""
        if rating == 5:
            return simplekml.Color.green
        elif rating == 4:
            return simplekml.Color.lightgreen
        elif rating == 3:
            return simplekml.Color.yellow
        elif rating == 2:
            return simplekml.Color.orange
        else:
            return simplekml.Color.red
    
    def _get_priority_color(self, priority):
        """Get color based on priority"""
        if priority == "Critical":
            return simplekml.Color.darkred
        elif priority == "High":
            return simplekml.Color.red
        elif priority == "Medium":
            return simplekml.Color.orange
        else:
            return simplekml.Color.green
    
    def _get_condition_text(self, rating):
        """Convert condition rating to text"""
        ratings = {
            1: "Very Poor",
            2: "Poor",
            3: "Fair",
            4: "Good",
            5: "Excellent"
        }
        return ratings.get(rating, "N/A")


def export_assets_to_kml(session, filename="assets.kml"):
    """Export all assets with locations to KML file"""
    from database import Asset, AssetType
    
    exporter = GoogleEarthExporter()
    
    # Get all assets with coordinates
    assets = session.query(Asset).filter(
        Asset.latitude.isnot(None),
        Asset.longitude.isnot(None)
    ).all()
    
    for asset in assets:
        asset_type_name = asset.asset_type.name if asset.asset_type else "Unknown"
        exporter.add_asset(asset, asset_type_name)
    
    return exporter.save(filename)


def export_work_orders_to_kml(session, filename="work_orders.kml"):
    """Export all work orders with locations to KML file"""
    from database import WorkOrder, Asset
    
    exporter = GoogleEarthExporter()
    
    # Get all work orders
    work_orders = session.query(WorkOrder).all()
    
    for wo in work_orders:
        # Use work order location if available, otherwise use asset location
        if wo.latitude and wo.longitude:
            asset_name = wo.asset.name if wo.asset else "Unknown Asset"
            exporter.add_work_order(wo, asset_name)
        elif wo.asset and wo.asset.latitude and wo.asset.longitude:
            # Copy asset location to work order for this export
            wo.latitude = wo.asset.latitude
            wo.longitude = wo.asset.longitude
            exporter.add_work_order(wo, wo.asset.name)
    
    return exporter.save(filename)


def export_inspections_to_kml(session, filename="inspections.kml"):
    """Export all inspections with locations to KML file"""
    from database import Inspection, Asset
    
    exporter = GoogleEarthExporter()
    
    # Get all inspections
    inspections = session.query(Inspection).all()
    
    for inspection in inspections:
        # Use inspection location if available, otherwise use asset location
        if inspection.latitude and inspection.longitude:
            asset_name = inspection.asset.name if inspection.asset else "Unknown Asset"
            exporter.add_inspection(inspection, asset_name)
        elif inspection.asset and inspection.asset.latitude and inspection.asset.longitude:
            # Copy asset location to inspection for this export
            inspection.latitude = inspection.asset.latitude
            inspection.longitude = inspection.asset.longitude
            exporter.add_inspection(inspection, inspection.asset.name)
    
    return exporter.save(filename)
