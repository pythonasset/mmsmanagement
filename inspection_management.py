"""
Inspection Management Module
Handles inspection scheduling, recording, and tracking
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
import folium
from streamlit_folium import folium_static
from database import Inspection, Asset, User
from document_management import show_documents, get_document_count
from settings import CONDITION_RATINGS
from utils import format_date, format_datetime
from dropdown_utils import get_dropdown_values, CATEGORY_INSPECTION_TYPE

def show_inspection_management(session):
    """Main inspection management interface"""
    st.header("🔍 Inspection Management")
    
    # Check if quick action is set to show create form prominently
    if st.session_state.get('show_add_insp_form', False):
        st.success("📝 **Quick Create Inspection Form** - Use the form below or navigate to the 'Create Inspection' tab")
        with st.expander("🔍 Create Inspection", expanded=True):
            create_inspection(session, form_key_suffix="_quick")
        # Clear the flag after showing
        del st.session_state['show_add_insp_form']
        st.divider()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Inspections",
        "Inspection Details",
        "Create Inspection",
        "Inspection Map"
    ])
    
    with tab1:
        show_inspections(session)
    
    with tab2:
        show_inspection_details_tab(session)
    
    with tab3:
        create_inspection(session)
    
    with tab4:
        show_inspection_map(session)


def show_inspections(session):
    """Display and filter inspections"""
    
    # Check if we're editing an inspection
    if 'edit_insp_id' in st.session_state:
        edit_inspection_form(session, st.session_state['edit_insp_id'], form_key_suffix="_list")
        return
    
    st.subheader("Inspection Records")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    # Get dynamic dropdown values
    inspection_types = get_dropdown_values(session, CATEGORY_INSPECTION_TYPE)
    
    with col1:
        type_filter = st.selectbox("Inspection Type", ["All"] + inspection_types)
    
    with col2:
        defects_filter = st.selectbox("Defects", ["All", "With Defects", "No Defects"])
    
    with col3:
        search_term = st.text_input("Search", placeholder="Inspection Number or Asset")
    
    # Date range filter
    st.warning("⚠️ **Date Picker Format:** Browser shows YYYY-MM-DD | **Your Format:** DD/MM/YYYY (Australian)")
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input("From Date", value=None, key="insp_start", help="Browser shows YYYY-MM-DD, but dates will be converted to DD/MM/YYYY")
        if start_date:
            st.markdown(f"📅 **Selected:** {format_date(start_date)}")
    with col_date2:
        end_date = st.date_input("To Date", value=None, key="insp_end", help="Browser shows YYYY-MM-DD, but dates will be converted to DD/MM/YYYY")
        if end_date:
            st.markdown(f"📅 **Selected:** {format_date(end_date)}")
    
    # Build query
    query = session.query(Inspection)
    
    if type_filter != "All":
        query = query.filter(Inspection.inspection_type == type_filter)
    
    if defects_filter == "With Defects":
        query = query.filter(Inspection.defects_found == True)
    elif defects_filter == "No Defects":
        query = query.filter(Inspection.defects_found == False)
    
    if search_term:
        query = query.filter(
            (Inspection.inspection_number.like(f"%{search_term}%"))
        )
    
    if start_date:
        query = query.filter(Inspection.inspection_date >= datetime.combine(start_date, datetime.min.time()))
    
    if end_date:
        query = query.filter(Inspection.inspection_date <= datetime.combine(end_date, datetime.max.time()))
    
    inspections = query.order_by(Inspection.inspection_date.desc()).all()
    
    if inspections:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Inspections", len(inspections))
        
        with col2:
            with_defects = len([i for i in inspections if i.defects_found])
            st.metric("With Defects", with_defects)
        
        with col3:
            follow_up = len([i for i in inspections if i.follow_up_required])
            st.metric("Require Follow-up", follow_up)
        
        with col4:
            avg_rating = sum(i.condition_rating for i in inspections if i.condition_rating) / len([i for i in inspections if i.condition_rating]) if any(i.condition_rating for i in inspections) else 0
            st.metric("Avg Condition", f"{avg_rating:.1f}")
        
        st.divider()
        
        # Convert to DataFrame
        insp_data = []
        for insp in inspections:
            asset_name = insp.asset.name if insp.asset else "N/A"
            asset_id = insp.asset.asset_id if insp.asset else "N/A"
            
            insp_data.append({
                "Inspection #": insp.inspection_number,
                "Asset": f"{asset_id} - {asset_name}",
                "Type": insp.inspection_type,
                "Date": format_date(insp.inspection_date),
                "Inspector": insp.inspector or "N/A",
                "Condition": CONDITION_RATINGS.get(insp.condition_rating, "N/A"),
                "Defects": "✓" if insp.defects_found else "✗",
                "Follow-up": "✓" if insp.follow_up_required else "✗",
                "Status": insp.status
            })
        
        df = pd.DataFrame(insp_data)
        
        # Display interactive table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export options
        if st.button("📥 Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                "inspections.csv",
                "text/csv",
                key='download-insp-csv'
            )
    else:
        st.warning("No inspections found matching the criteria.")


def show_inspection_details_tab(session):
    """Display the Inspection Details tab"""
    
    # Check if we're editing an inspection
    if 'edit_insp_id' in st.session_state:
        edit_inspection_form(session, st.session_state['edit_insp_id'], form_key_suffix="_details")
        return
    
    st.subheader("Inspection Details")
    
    # Get all inspections for the selector
    inspections = session.query(Inspection).order_by(Inspection.inspection_date.desc()).all()
    
    if inspections:
        # Inspection selector
        insp_numbers = ["Select an inspection..."] + [insp.inspection_number for insp in inspections]
        
        # Set default selection if there's a selected_inspection_id in session state
        default_index = 0
        if 'selected_inspection_id' in st.session_state and st.session_state['selected_inspection_id']:
            current_inspection = session.query(Inspection).filter_by(id=st.session_state['selected_inspection_id']).first()
            if current_inspection and current_inspection.inspection_number in insp_numbers:
                default_index = insp_numbers.index(current_inspection.inspection_number)
        
        selected_insp = st.selectbox(
            "Select Inspection to View Details",
            insp_numbers,
            index=default_index,
            key="insp_details_selector"
        )
        
        if selected_insp and selected_insp != "Select an inspection...":
            inspection = session.query(Inspection).filter_by(inspection_number=selected_insp).first()
            if inspection:
                # Update session state
                st.session_state['selected_inspection_id'] = inspection.id
                
                st.divider()
                show_inspection_details(session, inspection)
            else:
                st.error("Selected inspection not found.")
        else:
            # Show a helpful guide when nothing is selected
            st.info("👆 Select an inspection from the dropdown above to view its details.")
    else:
        st.warning("No inspections found in the system.")
        st.info("Create inspections from the **Create Inspection** tab.")


def show_inspection_details(session, inspection):
    """Display detailed inspection information"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Inspection Information")
        st.write(f"**Inspection #:** {inspection.inspection_number}")
        st.write(f"**Type:** {inspection.inspection_type}")
        st.write(f"**Date:** {format_datetime(inspection.inspection_date)}")
        st.write(f"**Inspector:** {inspection.inspector or 'N/A'}")
        st.write(f"**Status:** {inspection.status}")
        
        if inspection.asset:
            st.write(f"**Asset:** {inspection.asset.name} ({inspection.asset.asset_id})")
        
        st.write(f"**Condition Rating:** {CONDITION_RATINGS.get(inspection.condition_rating, 'N/A')}")
    
    with col2:
        st.write("### Findings")
        st.write(f"**Defects Found:** {'Yes' if inspection.defects_found else 'No'}")
        
        if inspection.defects_found and inspection.defect_description:
            st.warning(f"**Defect Description:**\n{inspection.defect_description}")
        
        st.write(f"**Follow-up Required:** {'Yes' if inspection.follow_up_required else 'No'}")
        
        if inspection.follow_up_required and inspection.follow_up_date:
            st.write(f"**Follow-up Date:** {inspection.follow_up_date}")
        
        if inspection.recommendations:
            st.info(f"**Recommendations:**\n{inspection.recommendations}")
    
    # Show location on map
    latitude = inspection.latitude or (inspection.asset.latitude if inspection.asset else None)
    longitude = inspection.longitude or (inspection.asset.longitude if inspection.asset else None)
    
    if latitude and longitude:
        st.write("### Inspection Location")
        m = folium.Map(location=[latitude, longitude], zoom_start=15)
        
        # Color based on defects
        color = 'red' if inspection.defects_found else 'green'
        
        folium.Marker(
            [latitude, longitude],
            popup=inspection.inspection_number,
            tooltip=f"{inspection.inspection_type}",
            icon=folium.Icon(color=color, icon='flag')
        ).add_to(m)
        folium_static(m, width=700, height=300)
    
    st.divider()
    
    # Show documents/attachments
    show_documents(session, 'inspection', inspection.id, f"Inspection {inspection.inspection_number}")
    
    st.divider()
    
    # Action buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("✏️ Edit", use_container_width=True):
            st.session_state['edit_insp_id'] = inspection.id
            st.rerun()
    
    with col2:
        if inspection.defects_found and st.button("🔧 Work Order", use_container_width=True):
            st.info("Work order creation from inspection would be implemented here")
    
    with col3:
        if st.button("🖨️ Print PDF", use_container_width=True):
            from print_manager import PrintManager
            from config_loader import get_config
            
            try:
                config = get_config()
                print_mgr = PrintManager(config)
                pdf_buffer = print_mgr.generate_inspection_pdf(inspection, session)
                
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_buffer,
                    file_name=f"Inspection_{inspection.inspection_number}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
    
    with col4:
        if st.button("🖨️ Browser Print", use_container_width=True):
            from print_manager import PrintManager
            from config_loader import get_config
            import streamlit.components.v1 as components
            
            try:
                config = get_config()
                print_mgr = PrintManager(config)
                html_content = print_mgr.generate_html_print_view('inspection', inspection, session)
                
                # Create a new window with printable content
                components.html(f"""
                    <script>
                        var printWindow = window.open('', '_blank');
                        printWindow.document.write(`{html_content}`);
                        printWindow.document.close();
                        printWindow.focus();
                        setTimeout(function() {{
                            printWindow.print();
                        }}, 500);
                    </script>
                    <p>Print window opened. If not, please check your popup blocker.</p>
                """, height=100)
            except Exception as e:
                st.error(f"Error opening print view: {str(e)}")
    
    with col5:
        if st.button("🗑️ Delete", use_container_width=True):
            if st.checkbox("Confirm deletion", key="del_insp_confirm"):
                session.delete(inspection)
                session.commit()
                st.success("Inspection deleted!")
                st.rerun()


def create_inspection(session, form_key_suffix=""):
    """Form to create a new inspection"""
    st.subheader("Create New Inspection")
    
    # Get dynamic dropdown values
    inspection_types = get_dropdown_values(session, CATEGORY_INSPECTION_TYPE)
    
    # Create unique form key
    form_key = f"new_inspection_form{form_key_suffix}"
    
    with st.form(form_key):
        col1, col2 = st.columns(2)
        
        with col1:
            # Generate inspection number
            last_insp = session.query(Inspection).order_by(Inspection.id.desc()).first()
            next_number = 1 if not last_insp else int(last_insp.inspection_number.split('-')[-1]) + 1
            insp_number = f"INSP-{next_number:05d}"
            
            st.text_input("Inspection Number", value=insp_number, disabled=True)
            
            # Asset selection
            assets = session.query(Asset).all()
            asset_options = {f"{a.asset_id} - {a.name}": a.id for a in assets}
            selected_asset = st.selectbox("Asset*", list(asset_options.keys()) if asset_options else [])
            
            inspection_type = st.selectbox("Inspection Type*", inspection_types if inspection_types else ["No types available"])
            inspection_date = st.date_input("Inspection Date*", value=date.today(), help="Format: DD/MM/YYYY (e.g., 31/01/2025)")
            inspection_time = st.time_input("Inspection Time")
            
            # Get active users for inspector selection
            users = session.query(User).filter(User.is_active == True).order_by(User.full_name).all()
            inspector_options = {"Unassigned": None}
            for user in users:
                display_name = user.full_name if user.full_name else user.username
                inspector_options[display_name] = display_name
            
            inspector = st.selectbox("Inspector Name", options=list(inspector_options.keys()))
            status = st.selectbox("Status", ["Scheduled", "Completed", "Cancelled"])
        
        with col2:
            condition_rating = st.select_slider(
                "Condition Rating",
                options=[1, 2, 3, 4, 5],
                value=3,
                format_func=lambda x: CONDITION_RATINGS[x]
            )
            
            defects_found = st.checkbox("Defects Found")
            
            # Set default text based on whether defects are found
            default_defect_text = "" if defects_found else "No defects identified"
            
            defect_description = st.text_area(
                "Defect Description",
                value=default_defect_text,
                disabled=not defects_found,
                help="Describe any defects found during inspection"
            )
            
            recommendations = st.text_area("Recommendations")
            
            follow_up_required = st.checkbox("Follow-up Required")
            follow_up_date = st.date_input(
                "Follow-up Date",
                value=None,
                disabled=not follow_up_required,
                help="Format: DD/MM/YYYY (e.g., 31/01/2025)"
            )
            
            # Optional location override
            st.write("**Location Override** (Optional)")
            col_lat, col_lon = st.columns(2)
            with col_lat:
                latitude = st.number_input("Latitude", value=None, format="%.6f", key=f"insp_lat{form_key_suffix}")
            with col_lon:
                longitude = st.number_input("Longitude", value=None, format="%.6f", key=f"insp_lon{form_key_suffix}")
        
        submitted = st.form_submit_button("➕ Create Inspection")
        
        if submitted:
            if not selected_asset:
                st.error("Please select an asset for the inspection")
            else:
                # Combine date and time
                insp_datetime = datetime.combine(inspection_date, inspection_time)
                
                # Get inspector name
                inspector_name = inspector_options[inspector]
                
                # Create new inspection
                new_inspection = Inspection(
                    inspection_number=insp_number,
                    asset_id=asset_options[selected_asset],
                    inspection_type=inspection_type,
                    inspection_date=insp_datetime,
                    inspector=inspector_name,
                    status=status,
                    condition_rating=condition_rating,
                    defects_found=defects_found,
                    defect_description=defect_description if defect_description else None,
                    recommendations=recommendations if recommendations else None,
                    follow_up_required=follow_up_required,
                    follow_up_date=follow_up_date if follow_up_required else None,
                    latitude=latitude if latitude else None,
                    longitude=longitude if longitude else None
                )
                
                session.add(new_inspection)
                session.commit()
                st.success(f"✅ Inspection {insp_number} created successfully!")
                
                # If defects found, suggest creating work order
                if defects_found:
                    st.info("💡 Defects were found. Consider creating a work order to address them.")
                
                st.balloons()


def edit_inspection_form(session, inspection_id, form_key_suffix=""):
    """Form to edit an existing inspection"""
    st.subheader("✏️ Edit Inspection")
    
    # Get the inspection
    inspection = session.query(Inspection).filter(Inspection.id == inspection_id).first()
    
    if not inspection:
        st.error("Inspection not found!")
        if st.button("← Back to Inspections"):
            del st.session_state['edit_insp_id']
            st.rerun()
        return
    
    # Get dynamic dropdown values
    inspection_types = get_dropdown_values(session, CATEGORY_INSPECTION_TYPE)
    
    # Get all assets for dropdown
    assets = session.query(Asset).all()
    asset_options = {f"{a.asset_id} - {a.name}": a.id for a in assets}
    
    # Find current asset selection
    current_asset_selection = list(asset_options.keys())[0] if asset_options else None
    if inspection.asset_id:
        for key, value in asset_options.items():
            if value == inspection.asset_id:
                current_asset_selection = key
                break
    
    with st.form(f"edit_inspection_form{form_key_suffix}"):
        st.write(f"**Inspection Number:** {inspection.inspection_number}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_asset = st.selectbox(
                "Asset*",
                options=list(asset_options.keys()) if asset_options else [],
                index=list(asset_options.keys()).index(current_asset_selection) if current_asset_selection in asset_options else 0
            )
            
            inspection_type = st.selectbox(
                "Inspection Type*",
                inspection_types if inspection_types else ["No types available"],
                index=inspection_types.index(inspection.inspection_type) if inspection.inspection_type in inspection_types else 0
            )
            
            inspection_date = st.date_input(
                "Inspection Date*",
                value=inspection.inspection_date.date() if inspection.inspection_date else date.today(),
                help="Format: DD/MM/YYYY (e.g., 31/01/2025)"
            )
            inspection_time = st.time_input(
                "Inspection Time",
                value=inspection.inspection_date.time() if inspection.inspection_date else None
            )
            
            # Get active users for inspector selection
            users = session.query(User).filter(User.is_active == True).order_by(User.full_name).all()
            inspector_options = {"Unassigned": None}
            for user in users:
                display_name = user.full_name if user.full_name else user.username
                inspector_options[display_name] = display_name
            
            # Find current inspector
            current_inspector = "Unassigned"
            if inspection.inspector:
                current_inspector = inspection.inspector
                # Make sure it's in the options, or add it
                if current_inspector not in inspector_options:
                    inspector_options[current_inspector] = current_inspector
            
            inspector = st.selectbox(
                "Inspector Name",
                options=list(inspector_options.keys()),
                index=list(inspector_options.keys()).index(current_inspector) if current_inspector in inspector_options else 0
            )
            
            status = st.selectbox(
                "Status",
                ["Scheduled", "Completed", "Cancelled"],
                index=["Scheduled", "Completed", "Cancelled"].index(inspection.status) if inspection.status in ["Scheduled", "Completed", "Cancelled"] else 0
            )
        
        with col2:
            condition_rating = st.select_slider(
                "Condition Rating",
                options=[1, 2, 3, 4, 5],
                value=inspection.condition_rating if inspection.condition_rating else 3,
                format_func=lambda x: CONDITION_RATINGS[x]
            )
            
            defects_found = st.checkbox("Defects Found", value=inspection.defects_found)
            
            defect_description = st.text_area(
                "Defect Description",
                value=inspection.defect_description or "",
                disabled=not defects_found
            )
            
            recommendations = st.text_area(
                "Recommendations",
                value=inspection.recommendations or ""
            )
            
            follow_up_required = st.checkbox(
                "Follow-up Required",
                value=inspection.follow_up_required
            )
            follow_up_date = st.date_input(
                "Follow-up Date",
                value=inspection.follow_up_date if inspection.follow_up_date else None,
                disabled=not follow_up_required,
                help="Format: DD/MM/YYYY (e.g., 31/01/2025)"
            )
            
            # Location override
            st.write("**Location Override** (Optional)")
            col_lat, col_lon = st.columns(2)
            with col_lat:
                latitude = st.number_input(
                    "Latitude",
                    value=float(inspection.latitude) if inspection.latitude else None,
                    format="%.6f",
                    key=f"edit_insp_lat{form_key_suffix}"
                )
            with col_lon:
                longitude = st.number_input(
                    "Longitude",
                    value=float(inspection.longitude) if inspection.longitude else None,
                    format="%.6f",
                    key=f"edit_insp_lon{form_key_suffix}"
                )
        
        # Form buttons
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Save Changes", type="primary")
        with col2:
            cancel = st.form_submit_button("❌ Cancel")
        
        if cancel:
            del st.session_state['edit_insp_id']
            st.rerun()
        
        if submitted:
            if not selected_asset:
                st.error("Please select an asset for the inspection")
            else:
                # Combine date and time
                insp_datetime = datetime.combine(inspection_date, inspection_time)
                
                # Update inspection
                inspection.asset_id = asset_options[selected_asset]
                inspection.inspection_type = inspection_type
                inspection.inspection_date = insp_datetime
                inspection.inspector = inspector_options[inspector]
                inspection.status = status
                inspection.condition_rating = condition_rating
                inspection.defects_found = defects_found
                inspection.defect_description = defect_description if defects_found else None
                inspection.recommendations = recommendations if recommendations else None
                inspection.follow_up_required = follow_up_required
                inspection.follow_up_date = follow_up_date if follow_up_required else None
                inspection.latitude = latitude if latitude else None
                inspection.longitude = longitude if longitude else None
                
                session.commit()
                st.success(f"✅ Inspection {inspection.inspection_number} updated successfully!")
                del st.session_state['edit_insp_id']
                st.rerun()
    
    # Show a back button outside the form
    if st.button("← Back to Inspections", key=f"back_from_edit_insp{form_key_suffix}"):
        del st.session_state['edit_insp_id']
        st.rerun()


def show_inspection_map(session):
    """Display inspections on a map"""
    st.subheader("Inspection Map View")
    
    # Get dynamic dropdown values
    inspection_types = get_dropdown_values(session, CATEGORY_INSPECTION_TYPE)
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        type_filter = st.selectbox("Filter by Type", ["All"] + inspection_types, key="map_type")
    with col2:
        defects_filter = st.selectbox("Filter by Defects", ["All", "With Defects", "No Defects"], key="map_defects")
    
    # Build query
    query = session.query(Inspection)
    
    if type_filter != "All":
        query = query.filter(Inspection.inspection_type == type_filter)
    
    if defects_filter == "With Defects":
        query = query.filter(Inspection.defects_found == True)
    elif defects_filter == "No Defects":
        query = query.filter(Inspection.defects_found == False)
    
    inspections = query.all()
    
    # Filter inspections with location data
    insp_with_location = []
    for insp in inspections:
        lat = insp.latitude or (insp.asset.latitude if insp.asset else None)
        lon = insp.longitude or (insp.asset.longitude if insp.asset else None)
        if lat and lon:
            insp_with_location.append((insp, lat, lon))
    
    if insp_with_location:
        st.info(f"Displaying {len(insp_with_location)} inspections on map")
        
        # Calculate map center
        avg_lat = sum(lat for _, lat, _ in insp_with_location) / len(insp_with_location)
        avg_lon = sum(lon for _, _, lon in insp_with_location) / len(insp_with_location)
        
        # Create map
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
        
        # Add markers
        for insp, lat, lon in insp_with_location:
            # Color based on defects
            color = 'red' if insp.defects_found else 'green'
            
            # Create popup
            asset_name = insp.asset.name if insp.asset else "N/A"
            popup_html = f"""
            <b>{insp.inspection_number}</b><br>
            <b>{insp.inspection_type}</b><br>
            Asset: {asset_name}<br>
            Date: {insp.inspection_date.strftime('%Y-%m-%d')}<br>
            Inspector: {insp.inspector or 'N/A'}<br>
            Condition: {CONDITION_RATINGS.get(insp.condition_rating, 'N/A')}<br>
            Defects: {'Yes' if insp.defects_found else 'No'}<br>
            Follow-up: {'Required' if insp.follow_up_required else 'Not Required'}
            """
            
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=insp.inspection_number,
                icon=folium.Icon(color=color, icon='flag')
            ).add_to(m)
        
        # Display map
        folium_static(m, width=1000, height=600)
        
        # Export to KML
        if st.button("📍 Export to Google Earth (KML)"):
            from google_earth import export_inspections_to_kml
            kml_file = export_inspections_to_kml(session, "inspections.kml")
            with open(kml_file, 'rb') as f:
                st.download_button(
                    "Download KML File",
                    f,
                    file_name="inspections.kml",
                    mime="application/vnd.google-earth.kml+xml"
                )
    else:
        st.warning("No inspections with location data found matching the criteria.")
