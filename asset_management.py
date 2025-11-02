"""
Asset Management Module
Handles asset hierarchy, registration, and management
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
import folium
from streamlit_folium import folium_static
from database import Asset, AssetClass, AssetGroup, AssetType
from settings import CONDITION_RATINGS, DEFAULT_MAP_CENTER
from dropdown_utils import get_dropdown_values, CATEGORY_ASSET_STATUS
from document_management import show_documents, get_document_count

def show_asset_management(session):
    """Main asset management interface"""
    st.header("📦 Asset Management")
    
    # Check if quick action is set to show add form prominently
    if st.session_state.get('show_add_asset_form', False):
        st.success("📝 **Quick Add Asset Form** - Use the form below or navigate to the 'Add New Asset' tab")
        with st.expander("➕ Add New Asset", expanded=True):
            add_new_asset(session, form_key_suffix="_quick")
        # Clear the flag after showing
        del st.session_state['show_add_asset_form']
        st.divider()
    
    # Create tabs for different asset management functions
    tab1, tab2, tab3, tab4 = st.tabs([
        "Asset Register",
        "Asset Hierarchy",
        "Add New Asset",
        "Asset Map View"
    ])
    
    with tab1:
        show_asset_register(session)
    
    with tab2:
        show_asset_hierarchy(session)
    
    with tab3:
        add_new_asset(session)
    
    with tab4:
        show_asset_map(session)


def show_asset_register(session):
    """Display and manage asset register"""
    
    # Check if we're editing an asset
    if 'edit_asset_id' in st.session_state:
        edit_asset_form(session, st.session_state['edit_asset_id'])
        return
    
    st.subheader("Asset Register")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    # Get dynamic dropdown values
    asset_statuses = get_dropdown_values(session, CATEGORY_ASSET_STATUS)
    
    with col1:
        # Get all asset classes for filter
        asset_classes = session.query(AssetClass).all()
        class_options = ["All"] + [ac.name for ac in asset_classes]
        selected_class = st.selectbox("Filter by Class", class_options)
    
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + asset_statuses)
    
    with col3:
        search_term = st.text_input("Search Assets", placeholder="Asset ID or Name")
    
    # Build query
    query = session.query(Asset)
    
    if selected_class != "All":
        asset_class = session.query(AssetClass).filter_by(name=selected_class).first()
        if asset_class:
            asset_type_ids = [at.id for ag in asset_class.asset_groups for at in ag.asset_types]
            query = query.filter(Asset.asset_type_id.in_(asset_type_ids))
    
    if status_filter != "All":
        query = query.filter(Asset.status == status_filter)
    
    if search_term:
        query = query.filter(
            (Asset.asset_id.like(f"%{search_term}%")) |
            (Asset.name.like(f"%{search_term}%"))
        )
    
    assets = query.all()
    
    if assets:
        # Display summary
        st.info(f"Found {len(assets)} asset(s)")
        
        # Convert to DataFrame for display
        asset_data = []
        for asset in assets:
            asset_type_name = asset.asset_type.name if asset.asset_type else "N/A"
            asset_data.append({
                "Asset ID": asset.asset_id,
                "Name": asset.name,
                "Type": asset_type_name,
                "Status": asset.status,
                "Condition": CONDITION_RATINGS.get(asset.condition_rating, "N/A"),
                "Location": asset.address or "N/A",
                "Value": f"${asset.current_value:,.2f}" if asset.current_value else "N/A"
            })
        
        df = pd.DataFrame(asset_data)
        
        # Display as interactive table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export options
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("📥 Export to CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    "assets.csv",
                    "text/csv",
                    key='download-csv'
                )
        
        # Asset details view
        st.divider()
        st.subheader("Asset Details")
        asset_ids = [f"{a.asset_id} - {a.name}" for a in assets]
        selected_asset_str = st.selectbox("Select Asset to View/Edit", asset_ids)
        
        if selected_asset_str:
            selected_asset_id = selected_asset_str.split(" - ")[0]
            selected_asset = session.query(Asset).filter_by(asset_id=selected_asset_id).first()
            
            if selected_asset:
                show_asset_details(session, selected_asset)
    else:
        st.warning("No assets found matching the criteria.")


def show_asset_details(session, asset):
    """Display and edit asset details"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Asset Information**")
        st.write(f"**Asset ID:** {asset.asset_id}")
        st.write(f"**Name:** {asset.name}")
        st.write(f"**Description:** {asset.description or 'N/A'}")
        
        if asset.asset_type:
            st.write(f"**Type:** {asset.asset_type.name}")
            if asset.asset_type.asset_group:
                st.write(f"**Group:** {asset.asset_type.asset_group.name}")
                if asset.asset_type.asset_group.asset_class:
                    st.write(f"**Class:** {asset.asset_type.asset_group.asset_class.name}")
        
        st.write(f"**Status:** {asset.status}")
        st.write(f"**Condition:** {CONDITION_RATINGS.get(asset.condition_rating, 'N/A')}")
    
    with col2:
        st.write("**Location & Details**")
        st.write(f"**Address:** {asset.address or 'N/A'}")
        st.write(f"**Coordinates:** {asset.latitude}, {asset.longitude}" if asset.latitude and asset.longitude else "**Coordinates:** N/A")
        st.write(f"**Manufacturer:** {asset.manufacturer or 'N/A'}")
        st.write(f"**Model:** {asset.model or 'N/A'}")
        st.write(f"**Serial Number:** {asset.serial_number or 'N/A'}")
        st.write(f"**Acquisition Date:** {asset.acquisition_date or 'N/A'}")
        st.write(f"**Current Value:** ${asset.current_value:,.2f}" if asset.current_value else "**Current Value:** N/A")
    
    # Show location on map if coordinates available
    if asset.latitude and asset.longitude:
        st.write("**Asset Location**")
        m = folium.Map(location=[asset.latitude, asset.longitude], zoom_start=15)
        folium.Marker(
            [asset.latitude, asset.longitude],
            popup=asset.name,
            tooltip=asset.asset_id
        ).add_to(m)
        folium_static(m, width=700, height=300)
    
    st.divider()
    
    # Show documents/attachments
    show_documents(session, 'asset', asset.id, f"Asset {asset.asset_id}")
    
    st.divider()
    
    # Edit button
    if st.button("✏️ Edit Asset"):
        st.session_state['edit_asset_id'] = asset.id
        st.rerun()


def show_asset_hierarchy(session):
    """Display and manage asset hierarchy (Classes, Groups, Types)"""
    st.subheader("Asset Hierarchy Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("### Asset Classes")
        asset_classes = session.query(AssetClass).all()
        
        for ac in asset_classes:
            with st.expander(f"📁 {ac.name}"):
                st.write(f"**Description:** {ac.description or 'N/A'}")
                st.write(f"**Groups:** {len(ac.asset_groups)}")
                if st.button(f"Delete", key=f"del_class_{ac.id}"):
                    session.delete(ac)
                    session.commit()
                    st.success(f"Deleted {ac.name}")
                    st.rerun()
        
        # Add new class
        with st.form("new_class"):
            st.write("**Add New Class**")
            new_class_name = st.text_input("Class Name")
            new_class_desc = st.text_area("Description")
            if st.form_submit_button("Add Class"):
                if new_class_name:
                    new_class = AssetClass(
                        name=new_class_name,
                        description=new_class_desc
                    )
                    session.add(new_class)
                    session.commit()
                    st.success(f"Added {new_class_name}")
                    st.rerun()
    
    with col2:
        st.write("### Asset Groups")
        
        # Select class for adding group
        class_for_group = st.selectbox(
            "Select Class for New Group",
            [ac.name for ac in asset_classes] if asset_classes else []
        )
        
        # Display existing groups
        asset_groups = session.query(AssetGroup).all()
        for ag in asset_groups:
            with st.expander(f"📂 {ag.name}"):
                st.write(f"**Class:** {ag.asset_class.name if ag.asset_class else 'N/A'}")
                st.write(f"**Description:** {ag.description or 'N/A'}")
                st.write(f"**Types:** {len(ag.asset_types)}")
                if st.button(f"Delete", key=f"del_group_{ag.id}"):
                    session.delete(ag)
                    session.commit()
                    st.success(f"Deleted {ag.name}")
                    st.rerun()
        
        # Add new group
        if asset_classes:
            with st.form("new_group"):
                st.write("**Add New Group**")
                new_group_name = st.text_input("Group Name")
                new_group_desc = st.text_area("Description")
                if st.form_submit_button("Add Group"):
                    if new_group_name and class_for_group:
                        selected_class = session.query(AssetClass).filter_by(name=class_for_group).first()
                        if selected_class:
                            new_group = AssetGroup(
                                name=new_group_name,
                                description=new_group_desc,
                                asset_class_id=selected_class.id
                            )
                            session.add(new_group)
                            session.commit()
                            st.success(f"Added {new_group_name}")
                            st.rerun()
    
    with col3:
        st.write("### Asset Types")
        
        # Select group for adding type
        group_for_type = st.selectbox(
            "Select Group for New Type",
            [ag.name for ag in asset_groups] if asset_groups else []
        )
        
        # Display existing types
        asset_types = session.query(AssetType).all()
        for at in asset_types:
            with st.expander(f"📄 {at.name}"):
                st.write(f"**Group:** {at.asset_group.name if at.asset_group else 'N/A'}")
                st.write(f"**Description:** {at.description or 'N/A'}")
                st.write(f"**Assets:** {len(at.assets)}")
                if st.button(f"Delete", key=f"del_type_{at.id}"):
                    if len(at.assets) == 0:
                        session.delete(at)
                        session.commit()
                        st.success(f"Deleted {at.name}")
                        st.rerun()
                    else:
                        st.error("Cannot delete type with existing assets")
        
        # Add new type
        if asset_groups:
            with st.form("new_type"):
                st.write("**Add New Type**")
                new_type_name = st.text_input("Type Name")
                new_type_desc = st.text_area("Description")
                if st.form_submit_button("Add Type"):
                    if new_type_name and group_for_type:
                        selected_group = session.query(AssetGroup).filter_by(name=group_for_type).first()
                        if selected_group:
                            new_type = AssetType(
                                name=new_type_name,
                                description=new_type_desc,
                                asset_group_id=selected_group.id
                            )
                            session.add(new_type)
                            session.commit()
                            st.success(f"Added {new_type_name}")
                            st.rerun()


def add_new_asset(session, form_key_suffix=""):
    """Form to add a new asset"""
    st.subheader("Add New Asset")
    
    # Get dynamic dropdown values
    asset_statuses = get_dropdown_values(session, CATEGORY_ASSET_STATUS)
    
    # Create unique form key
    form_key = f"new_asset_form{form_key_suffix}"
    
    with st.form(form_key):
        col1, col2 = st.columns(2)
        
        with col1:
            asset_id = st.text_input("Asset ID*", help="Unique identifier for the asset")
            asset_name = st.text_input("Asset Name*")
            asset_description = st.text_area("Description")
            
            # Asset type selection
            asset_types = session.query(AssetType).all()
            type_options = {f"{at.name} ({at.asset_group.name})": at.id for at in asset_types}
            selected_type = st.selectbox("Asset Type*", list(type_options.keys()) if type_options else [])
            
            status = st.selectbox("Status", asset_statuses if asset_statuses else ["No statuses available"])
            condition = st.select_slider("Condition Rating", options=[1, 2, 3, 4, 5],
                                        format_func=lambda x: CONDITION_RATINGS[x])
        
        with col2:
            # Location
            address = st.text_input("Address")
            col_lat, col_lon = st.columns(2)
            with col_lat:
                latitude = st.number_input("Latitude", value=None, format="%.6f")
            with col_lon:
                longitude = st.number_input("Longitude", value=None, format="%.6f")
            
            location_desc = st.text_area("Location Description")
            
            # Asset details
            manufacturer = st.text_input("Manufacturer")
            model = st.text_input("Model")
            serial_number = st.text_input("Serial Number")
            
            col_date, col_cost = st.columns(2)
            with col_date:
                acquisition_date = st.date_input("Acquisition Date", value=None, format="DD/MM/YYYY", help="Format: DD/MM/YYYY (e.g., 31/01/2025)")
            with col_cost:
                acquisition_cost = st.number_input("Acquisition Cost ($)", min_value=0.0, value=0.0)
                current_value = st.number_input("Current Value ($)", min_value=0.0, value=0.0)
        
        submitted = st.form_submit_button("➕ Add Asset")
        
        if submitted:
            if not asset_id or not asset_name or not selected_type:
                st.error("Please fill in all required fields (marked with *)")
            else:
                # Check if asset ID already exists
                existing = session.query(Asset).filter_by(asset_id=asset_id).first()
                if existing:
                    st.error(f"Asset ID {asset_id} already exists!")
                else:
                    # Create new asset
                    new_asset = Asset(
                        asset_id=asset_id,
                        name=asset_name,
                        description=asset_description,
                        asset_type_id=type_options[selected_type],
                        status=status,
                        condition_rating=condition,
                        address=address,
                        latitude=latitude if latitude else None,
                        longitude=longitude if longitude else None,
                        location_description=location_desc,
                        manufacturer=manufacturer,
                        model=model,
                        serial_number=serial_number,
                        acquisition_date=acquisition_date,
                        acquisition_cost=acquisition_cost if acquisition_cost > 0 else None,
                        current_value=current_value if current_value > 0 else None,
                        created_by="System",  # Replace with actual user
                        modified_by="System"
                    )
                    
                    session.add(new_asset)
                    session.commit()
                    st.success(f"✅ Asset {asset_id} - {asset_name} added successfully!")
                    st.balloons()


def edit_asset_form(session, asset_id):
    """Form to edit an existing asset"""
    st.subheader("✏️ Edit Asset")
    
    # Get the asset
    asset = session.query(Asset).filter(Asset.id == asset_id).first()
    
    if not asset:
        st.error("Asset not found!")
        if st.button("← Back to Asset Register"):
            del st.session_state['edit_asset_id']
            st.rerun()
        return
    
    # Get dynamic dropdown values
    asset_statuses = get_dropdown_values(session, CATEGORY_ASSET_STATUS)
    
    with st.form("edit_asset_form"):
        st.write(f"**Asset ID:** {asset.asset_id}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            asset_name = st.text_input("Asset Name*", value=asset.name)
            asset_description = st.text_area("Description", value=asset.description or "")
            
            # Asset type selection
            asset_types = session.query(AssetType).all()
            type_options = {f"{at.name} ({at.asset_group.name})": at.id for at in asset_types}
            
            # Find current type
            current_type_key = None
            if asset.asset_type:
                current_type_key = f"{asset.asset_type.name} ({asset.asset_type.asset_group.name})"
            
            current_type_index = 0
            if current_type_key and current_type_key in type_options:
                current_type_index = list(type_options.keys()).index(current_type_key)
            
            selected_type = st.selectbox(
                "Asset Type*",
                list(type_options.keys()) if type_options else [],
                index=current_type_index
            )
            
            status = st.selectbox(
                "Status",
                asset_statuses if asset_statuses else ["No statuses available"],
                index=asset_statuses.index(asset.status) if asset.status in asset_statuses else 0
            )
            
            condition = st.select_slider(
                "Condition Rating",
                options=[1, 2, 3, 4, 5],
                value=asset.condition_rating if asset.condition_rating else 3,
                format_func=lambda x: CONDITION_RATINGS[x]
            )
        
        with col2:
            # Location
            address = st.text_input("Address", value=asset.address or "")
            col_lat, col_lon = st.columns(2)
            with col_lat:
                latitude = st.number_input(
                    "Latitude",
                    value=float(asset.latitude) if asset.latitude else None,
                    format="%.6f",
                    key="edit_asset_lat"
                )
            with col_lon:
                longitude = st.number_input(
                    "Longitude",
                    value=float(asset.longitude) if asset.longitude else None,
                    format="%.6f",
                    key="edit_asset_lon"
                )
            
            location_desc = st.text_area("Location Description", value=asset.location_description or "")
            
            # Asset details
            manufacturer = st.text_input("Manufacturer", value=asset.manufacturer or "")
            model = st.text_input("Model", value=asset.model or "")
            serial_number = st.text_input("Serial Number", value=asset.serial_number or "")
            
            col_date, col_cost = st.columns(2)
            with col_date:
                acquisition_date = st.date_input(
                    "Acquisition Date",
                    value=asset.acquisition_date if asset.acquisition_date else None,
                    format="DD/MM/YYYY",
                    help="Format: DD/MM/YYYY (e.g., 31/01/2025)"
                )
            with col_cost:
                acquisition_cost = st.number_input(
                    "Acquisition Cost ($)",
                    min_value=0.0,
                    value=float(asset.acquisition_cost) if asset.acquisition_cost else 0.0
                )
                current_value = st.number_input(
                    "Current Value ($)",
                    min_value=0.0,
                    value=float(asset.current_value) if asset.current_value else 0.0
                )
        
        # Form buttons
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Save Changes", type="primary")
        with col2:
            cancel = st.form_submit_button("❌ Cancel")
        
        if cancel:
            del st.session_state['edit_asset_id']
            st.rerun()
        
        if submitted:
            if not asset_name or not selected_type:
                st.error("Please fill in all required fields (marked with *)")
            else:
                # Update asset
                asset.name = asset_name
                asset.description = asset_description
                asset.asset_type_id = type_options[selected_type]
                asset.status = status
                asset.condition_rating = condition
                asset.address = address
                asset.latitude = latitude if latitude else None
                asset.longitude = longitude if longitude else None
                asset.location_description = location_desc
                asset.manufacturer = manufacturer
                asset.model = model
                asset.serial_number = serial_number
                asset.acquisition_date = acquisition_date
                asset.acquisition_cost = acquisition_cost if acquisition_cost > 0 else None
                asset.current_value = current_value if current_value > 0 else None
                asset.modified_by = "System"  # Replace with actual user
                asset.modified_date = datetime.now()
                
                session.commit()
                st.success(f"✅ Asset {asset.asset_id} updated successfully!")
                del st.session_state['edit_asset_id']
                st.rerun()
    
    # Show a back button outside the form
    if st.button("← Back to Asset Register", key="back_from_edit_asset"):
        del st.session_state['edit_asset_id']
        st.rerun()


def show_asset_map(session):
    """Display all assets on a map"""
    st.subheader("Asset Map View")
    
    # Get dynamic dropdown values
    asset_statuses = get_dropdown_values(session, CATEGORY_ASSET_STATUS)
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        asset_classes = session.query(AssetClass).all()
        class_options = ["All"] + [ac.name for ac in asset_classes]
        selected_class = st.selectbox("Filter by Class", class_options, key="map_class_filter")
    
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All"] + asset_statuses, key="map_status_filter")
    
    # Build query
    query = session.query(Asset).filter(
        Asset.latitude.isnot(None),
        Asset.longitude.isnot(None)
    )
    
    if selected_class != "All":
        asset_class = session.query(AssetClass).filter_by(name=selected_class).first()
        if asset_class:
            asset_type_ids = [at.id for ag in asset_class.asset_groups for at in ag.asset_types]
            query = query.filter(Asset.asset_type_id.in_(asset_type_ids))
    
    if status_filter != "All":
        query = query.filter(Asset.status == status_filter)
    
    assets = query.all()
    
    if assets:
        st.info(f"Displaying {len(assets)} assets on map")
        
        # Calculate map center
        avg_lat = sum(a.latitude for a in assets) / len(assets)
        avg_lon = sum(a.longitude for a in assets) / len(assets)
        
        # Create map
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
        
        # Add markers for each asset
        for asset in assets:
            # Color based on condition
            if asset.condition_rating:
                if asset.condition_rating >= 4:
                    color = 'green'
                elif asset.condition_rating == 3:
                    color = 'orange'
                else:
                    color = 'red'
            else:
                color = 'gray'
            
            popup_html = f"""
            <b>{asset.name}</b><br>
            ID: {asset.asset_id}<br>
            Status: {asset.status}<br>
            Condition: {CONDITION_RATINGS.get(asset.condition_rating, 'N/A')}<br>
            Type: {asset.asset_type.name if asset.asset_type else 'N/A'}
            """
            
            folium.Marker(
                location=[asset.latitude, asset.longitude],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=asset.name,
                icon=folium.Icon(color=color, icon='info-sign')
            ).add_to(m)
        
        # Display map
        folium_static(m, width=1000, height=600)
        
        # Export to KML button
        if st.button("📍 Export to Google Earth (KML)"):
            from google_earth import export_assets_to_kml
            kml_file = export_assets_to_kml(session, "assets.kml")
            with open(kml_file, 'rb') as f:
                st.download_button(
                    "Download KML File",
                    f,
                    file_name="assets.kml",
                    mime="application/vnd.google-earth.kml+xml"
                )
    else:
        st.warning("No assets with location data found matching the criteria.")
