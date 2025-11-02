"""
Work Order Management Module
Handles work order creation, tracking, and monitoring
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
from database import WorkOrder, Asset, User
from document_management import show_documents, get_document_count
from settings import DEFAULT_MAP_CENTER
from utils import format_date, format_datetime
from dropdown_utils import (
    get_dropdown_values,
    CATEGORY_WORK_ORDER_TYPE, CATEGORY_WORK_ORDER_PRIORITY, CATEGORY_WORK_ORDER_STATUS
)

def show_work_order_management(session):
    """Main work order management interface"""
    st.header("🔧 Work Order Management")
    
    # Check if quick action is set to show create form prominently
    if st.session_state.get('show_add_wo_form', False):
        st.success("📝 **Quick Create Work Order Form** - Use the form below or navigate to the 'Create Work Order' tab")
        with st.expander("🔧 Create Work Order", expanded=True):
            create_work_order(session, form_key_suffix="_quick")
        # Clear the flag after showing
        del st.session_state['show_add_wo_form']
        st.divider()
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Work Orders",
        "Create Work Order",
        "Work Order Map",
        "Analytics"
    ])
    
    with tab1:
        show_work_orders(session)
    
    with tab2:
        create_work_order(session)
    
    with tab3:
        show_work_order_map(session)
    
    with tab4:
        show_work_order_analytics(session)


def show_work_orders(session):
    """Display and filter work orders"""
    
    # Check if we're editing a work order
    if 'edit_wo_id' in st.session_state:
        edit_work_order_form(session, st.session_state['edit_wo_id'])
        return
    
    st.subheader("Work Order List")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    # Get dynamic dropdown values
    work_order_statuses = get_dropdown_values(session, CATEGORY_WORK_ORDER_STATUS)
    work_order_priorities = get_dropdown_values(session, CATEGORY_WORK_ORDER_PRIORITY)
    work_order_types = get_dropdown_values(session, CATEGORY_WORK_ORDER_TYPE)
    
    with col1:
        status_filter = st.selectbox("Status", ["All"] + work_order_statuses)
    
    with col2:
        priority_filter = st.selectbox("Priority", ["All"] + work_order_priorities)
    
    with col3:
        type_filter = st.selectbox("Type", ["All"] + work_order_types)
    
    with col4:
        search_term = st.text_input("Search", placeholder="WO Number or Title")
    
    # Date range filter
    st.warning("⚠️ **Date Picker Format:** Browser shows YYYY-MM-DD | **Your Format:** DD/MM/YYYY (Australian)")
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input("From Date", value=None, help="Browser shows YYYY-MM-DD, but dates will be converted to DD/MM/YYYY")
        if start_date:
            st.markdown(f"📅 **Selected:** {format_date(start_date)}")
    with col_date2:
        end_date = st.date_input("To Date", value=None, help="Browser shows YYYY-MM-DD, but dates will be converted to DD/MM/YYYY")
        if end_date:
            st.markdown(f"📅 **Selected:** {format_date(end_date)}")
    
    # Build query
    query = session.query(WorkOrder)
    
    if status_filter != "All":
        query = query.filter(WorkOrder.status == status_filter)
    
    if priority_filter != "All":
        query = query.filter(WorkOrder.priority == priority_filter)
    
    if type_filter != "All":
        query = query.filter(WorkOrder.work_type == type_filter)
    
    if search_term:
        query = query.filter(
            (WorkOrder.work_order_number.like(f"%{search_term}%")) |
            (WorkOrder.title.like(f"%{search_term}%"))
        )
    
    if start_date:
        query = query.filter(WorkOrder.created_date >= datetime.combine(start_date, datetime.min.time()))
    
    if end_date:
        query = query.filter(WorkOrder.created_date <= datetime.combine(end_date, datetime.max.time()))
    
    work_orders = query.order_by(WorkOrder.created_date.desc()).all()
    
    if work_orders:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Work Orders", len(work_orders))
        
        with col2:
            open_count = len([wo for wo in work_orders if wo.status in ["Open", "In Progress"]])
            st.metric("Open/In Progress", open_count)
        
        with col3:
            critical_count = len([wo for wo in work_orders if wo.priority == "Critical"])
            st.metric("Critical Priority", critical_count)
        
        with col4:
            overdue = len([wo for wo in work_orders if wo.due_date and wo.due_date < datetime.now() and wo.status != "Completed"])
            st.metric("Overdue", overdue)
        
        st.divider()
        
        # Convert to DataFrame
        wo_data = []
        for wo in work_orders:
            asset_name = wo.asset.name if wo.asset else "N/A"
            
            # Calculate status indicator
            status_emoji = {
                "Open": "🔵",
                "In Progress": "🟡",
                "On Hold": "🟠",
                "Completed": "🟢",
                "Cancelled": "⚫"
            }.get(wo.status, "⚪")
            
            priority_emoji = {
                "Critical": "🔴",
                "High": "🟠",
                "Medium": "🟡",
                "Low": "🟢"
            }.get(wo.priority, "⚪")
            
            wo_data.append({
                "WO Number": wo.work_order_number,
                "Title": wo.title,
                "Asset": asset_name,
                "Type": wo.work_type,
                "Priority": f"{priority_emoji} {wo.priority}",
                "Status": f"{status_emoji} {wo.status}",
                "Assigned To": wo.assigned_to or "Unassigned",
                "Created": format_date(wo.created_date),
                "Due Date": format_date(wo.due_date)
            })
        
        df = pd.DataFrame(wo_data)
        
        # Display interactive table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export options
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("📥 Export to CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    "work_orders.csv",
                    "text/csv",
                    key='download-wo-csv'
                )
        
        # Work order details
        st.divider()
        st.subheader("Work Order Details")
        wo_numbers = [wo.work_order_number for wo in work_orders]
        selected_wo = st.selectbox("Select Work Order", wo_numbers)
        
        if selected_wo:
            work_order = session.query(WorkOrder).filter_by(work_order_number=selected_wo).first()
            if work_order:
                show_work_order_details(session, work_order)
    else:
        st.warning("No work orders found matching the criteria.")


def show_work_order_details(session, work_order):
    """Display detailed work order information"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### Work Order Information")
        st.write(f"**WO Number:** {work_order.work_order_number}")
        st.write(f"**Title:** {work_order.title}")
        st.write(f"**Description:** {work_order.description or 'N/A'}")
        st.write(f"**Type:** {work_order.work_type}")
        st.write(f"**Priority:** {work_order.priority}")
        st.write(f"**Status:** {work_order.status}")
        
        if work_order.asset:
            st.write(f"**Asset:** {work_order.asset.name} ({work_order.asset.asset_id})")
        
        st.write(f"**Assigned To:** {work_order.assigned_to or 'Unassigned'}")
    
    with col2:
        st.write("### Timeline & Costs")
        st.write(f"**Created:** {format_datetime(work_order.created_date)}")
        st.write(f"**Scheduled:** {format_date(work_order.scheduled_date) if work_order.scheduled_date else 'Not scheduled'}")
        st.write(f"**Due Date:** {format_date(work_order.due_date) if work_order.due_date else 'N/A'}")
        st.write(f"**Start Date:** {format_date(work_order.start_date) if work_order.start_date else 'Not started'}")
        st.write(f"**Completion Date:** {format_date(work_order.completion_date) if work_order.completion_date else 'Not completed'}")
        
        st.divider()
        
        st.write(f"**Estimated Cost:** ${work_order.estimated_cost:,.2f}" if work_order.estimated_cost else "**Estimated Cost:** N/A")
        st.write(f"**Actual Cost:** ${work_order.actual_cost:,.2f}" if work_order.actual_cost else "**Actual Cost:** N/A")
        st.write(f"**Labor Hours:** {work_order.labor_hours or 'N/A'}")
    
    # Notes
    if work_order.notes:
        st.write("### Notes")
        st.info(work_order.notes)
    
    if work_order.completion_notes:
        st.write("### Completion Notes")
        st.success(work_order.completion_notes)
    
    # Show location on map
    latitude = work_order.latitude or (work_order.asset.latitude if work_order.asset else None)
    longitude = work_order.longitude or (work_order.asset.longitude if work_order.asset else None)
    
    if latitude and longitude:
        st.write("### Work Order Location")
        m = folium.Map(location=[latitude, longitude], zoom_start=15)
        folium.Marker(
            [latitude, longitude],
            popup=work_order.title,
            tooltip=work_order.work_order_number,
            icon=folium.Icon(color='red', icon='wrench', prefix='fa')
        ).add_to(m)
        folium_static(m, width=700, height=300)
    
    st.divider()
    
    # Show documents/attachments
    show_documents(session, 'work_order', work_order.id, f"Work Order {work_order.work_order_number}")
    
    st.divider()
    
    # Action buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        if st.button("✏️ Edit Work Order", use_container_width=True):
            st.session_state['edit_wo_id'] = work_order.id
            st.rerun()
    
    with col2:
        if work_order.status != "Completed" and st.button("✅ Mark Complete", use_container_width=True):
            work_order.status = "Completed"
            work_order.completion_date = datetime.now()
            session.commit()
            st.success("Work order marked as complete!")
            st.rerun()
    
    with col3:
        if st.button("🖨️ Print PDF", use_container_width=True):
            from print_manager import PrintManager
            from config_loader import get_config
            
            try:
                config = get_config()
                print_mgr = PrintManager(config)
                pdf_buffer = print_mgr.generate_work_order_pdf(work_order, session)
                
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_buffer,
                    file_name=f"WorkOrder_{work_order.work_order_number}_{datetime.now().strftime('%Y%m%d')}.pdf",
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
                html_content = print_mgr.generate_html_print_view('work_order', work_order, session)
                
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
            if st.checkbox("Confirm deletion"):
                session.delete(work_order)
                session.commit()
                st.success("Work order deleted!")
                st.rerun()


def create_work_order(session, form_key_suffix=""):
    """Form to create a new work order"""
    st.subheader("Create New Work Order")
    
    # Get dynamic dropdown values
    work_order_types = get_dropdown_values(session, CATEGORY_WORK_ORDER_TYPE)
    work_order_priorities = get_dropdown_values(session, CATEGORY_WORK_ORDER_PRIORITY)
    work_order_statuses = get_dropdown_values(session, CATEGORY_WORK_ORDER_STATUS)
    
    # Create unique form key
    form_key = f"new_work_order_form{form_key_suffix}"
    
    with st.form(form_key):
        col1, col2 = st.columns(2)
        
        with col1:
            # Generate WO number
            last_wo = session.query(WorkOrder).order_by(WorkOrder.id.desc()).first()
            next_number = 1 if not last_wo else int(last_wo.work_order_number.split('-')[-1]) + 1
            wo_number = f"WO-{next_number:05d}"
            
            st.text_input("Work Order Number", value=wo_number, disabled=True)
            title = st.text_input("Title*")
            description = st.text_area("Description")
            
            # Asset selection
            assets = session.query(Asset).all()
            asset_options = {f"{a.asset_id} - {a.name}": a.id for a in assets}
            selected_asset = st.selectbox("Asset", ["None"] + list(asset_options.keys()))
            
            work_type = st.selectbox("Work Type*", work_order_types if work_order_types else ["No types available"])
            priority = st.selectbox("Priority*", work_order_priorities if work_order_priorities else ["No priorities available"])
            status = st.selectbox("Status", work_order_statuses if work_order_statuses else ["No statuses available"], index=0)
        
        with col2:
            # Get active users for assignment
            users = session.query(User).filter(User.is_active == True).order_by(User.full_name).all()
            user_options = {"Unassigned": None}
            for user in users:
                display_name = user.full_name if user.full_name else user.username
                user_options[display_name] = display_name
            
            assigned_to = st.selectbox("Assigned To", options=list(user_options.keys()))
            
            scheduled_date = st.date_input("Scheduled Date", value=None, help="Format: DD/MM/YYYY (e.g., 31/01/2025)")
            due_date = st.date_input("Due Date", value=None, help="Format: DD/MM/YYYY (e.g., 31/01/2025)")
            
            estimated_cost = st.number_input("Estimated Cost ($)", min_value=0.0, value=0.0)
            labor_hours = st.number_input("Estimated Labor Hours", min_value=0.0, value=0.0)
            
            notes = st.text_area("Notes")
            
            # Optional location override
            st.write("**Location Override** (Optional - uses asset location if not specified)")
            col_lat, col_lon = st.columns(2)
            with col_lat:
                latitude = st.number_input("Latitude", value=None, format="%.6f", key=f"wo_lat{form_key_suffix}")
            with col_lon:
                longitude = st.number_input("Longitude", value=None, format="%.6f", key=f"wo_lon{form_key_suffix}")
        
        submitted = st.form_submit_button("➕ Create Work Order")
        
        if submitted:
            if not title:
                st.error("Please enter a title for the work order")
            else:
                # Get asset ID
                asset_id = None
                if selected_asset != "None":
                    asset_id = asset_options[selected_asset]
                
                # Get assigned user
                assigned_user = user_options[assigned_to]
                
                # Create new work order
                new_wo = WorkOrder(
                    work_order_number=wo_number,
                    asset_id=asset_id,
                    title=title,
                    description=description,
                    work_type=work_type,
                    priority=priority,
                    status=status,
                    assigned_to=assigned_user,
                    scheduled_date=datetime.combine(scheduled_date, datetime.min.time()) if scheduled_date else None,
                    due_date=datetime.combine(due_date, datetime.max.time()) if due_date else None,
                    estimated_cost=estimated_cost if estimated_cost > 0 else None,
                    labor_hours=labor_hours if labor_hours > 0 else None,
                    notes=notes if notes else None,
                    latitude=latitude if latitude else None,
                    longitude=longitude if longitude else None,
                    created_by="System"  # Replace with actual user
                )
                
                session.add(new_wo)
                session.commit()
                st.success(f"✅ Work Order {wo_number} created successfully!")
                st.balloons()


def edit_work_order_form(session, work_order_id):
    """Form to edit an existing work order"""
    st.subheader("✏️ Edit Work Order")
    
    # Get the work order
    work_order = session.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    
    if not work_order:
        st.error("Work order not found!")
        if st.button("← Back to Work Orders"):
            del st.session_state['edit_wo_id']
            st.rerun()
        return
    
    # Get dynamic dropdown values
    work_order_types = get_dropdown_values(session, CATEGORY_WORK_ORDER_TYPE)
    work_order_priorities = get_dropdown_values(session, CATEGORY_WORK_ORDER_PRIORITY)
    work_order_statuses = get_dropdown_values(session, CATEGORY_WORK_ORDER_STATUS)
    
    # Get all assets for dropdown
    assets = session.query(Asset).order_by(Asset.name).all()
    asset_options = {"None": None}
    for asset in assets:
        asset_options[f"{asset.name} ({asset.asset_id})"] = asset.id
    
    # Find current asset selection
    current_asset_selection = "None"
    if work_order.asset_id:
        for key, value in asset_options.items():
            if value == work_order.asset_id:
                current_asset_selection = key
                break
    
    with st.form("edit_work_order_form"):
        st.write(f"**Work Order Number:** {work_order.work_order_number}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_asset = st.selectbox(
                "Related Asset",
                options=list(asset_options.keys()),
                index=list(asset_options.keys()).index(current_asset_selection)
            )
            
            title = st.text_input("Work Order Title *", value=work_order.title)
            description = st.text_area("Description", value=work_order.description or "")
            
            work_type = st.selectbox(
                "Work Type",
                work_order_types if work_order_types else ["No types available"],
                index=work_order_types.index(work_order.work_type) if work_order.work_type in work_order_types else 0
            )
            priority = st.selectbox(
                "Priority",
                work_order_priorities if work_order_priorities else ["No priorities available"],
                index=work_order_priorities.index(work_order.priority) if work_order.priority in work_order_priorities else 0
            )
            status = st.selectbox(
                "Status",
                work_order_statuses if work_order_statuses else ["No statuses available"],
                index=work_order_statuses.index(work_order.status) if work_order.status in work_order_statuses else 0
            )
        
        with col2:
            # Get active users for assignment
            users = session.query(User).filter(User.is_active == True).order_by(User.full_name).all()
            user_options = {"Unassigned": None}
            for user in users:
                display_name = user.full_name if user.full_name else user.username
                user_options[display_name] = display_name
            
            # Find current assignment
            current_assignment = "Unassigned"
            if work_order.assigned_to:
                current_assignment = work_order.assigned_to
                # Make sure it's in the options, or add it
                if current_assignment not in user_options:
                    user_options[current_assignment] = current_assignment
            
            assigned_to = st.selectbox(
                "Assigned To",
                options=list(user_options.keys()),
                index=list(user_options.keys()).index(current_assignment) if current_assignment in user_options else 0
            )
            
            scheduled_date = st.date_input(
                "Scheduled Date",
                value=work_order.scheduled_date.date() if work_order.scheduled_date else None,
                help="Format: DD/MM/YYYY (e.g., 31/01/2025)"
            )
            due_date = st.date_input(
                "Due Date",
                value=work_order.due_date.date() if work_order.due_date else None,
                help="Format: DD/MM/YYYY (e.g., 31/01/2025)"
            )
            start_date = st.date_input(
                "Start Date",
                value=work_order.start_date.date() if work_order.start_date else None,
                help="Format: DD/MM/YYYY (e.g., 31/01/2025)"
            )
            completion_date = st.date_input(
                "Completion Date",
                value=work_order.completion_date.date() if work_order.completion_date else None,
                help="Format: DD/MM/YYYY (e.g., 31/01/2025)"
            )
            
            estimated_cost = st.number_input(
                "Estimated Cost ($)",
                min_value=0.0,
                value=float(work_order.estimated_cost) if work_order.estimated_cost else 0.0
            )
            actual_cost = st.number_input(
                "Actual Cost ($)",
                min_value=0.0,
                value=float(work_order.actual_cost) if work_order.actual_cost else 0.0
            )
            labor_hours = st.number_input(
                "Labor Hours",
                min_value=0.0,
                value=float(work_order.labor_hours) if work_order.labor_hours else 0.0
            )
            
            notes = st.text_area("Notes", value=work_order.notes or "")
            completion_notes = st.text_area("Completion Notes", value=work_order.completion_notes or "")
            
            # Location override
            st.write("**Location Override** (Optional)")
            col_lat, col_lon = st.columns(2)
            with col_lat:
                latitude = st.number_input(
                    "Latitude",
                    value=float(work_order.latitude) if work_order.latitude else None,
                    format="%.6f",
                    key="edit_wo_lat"
                )
            with col_lon:
                longitude = st.number_input(
                    "Longitude",
                    value=float(work_order.longitude) if work_order.longitude else None,
                    format="%.6f",
                    key="edit_wo_lon"
                )
        
        # Form buttons
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Save Changes", type="primary")
        with col2:
            cancel = st.form_submit_button("❌ Cancel")
        
        if cancel:
            del st.session_state['edit_wo_id']
            st.rerun()
        
        if submitted:
            if not title:
                st.error("Please enter a title for the work order")
            else:
                # Update work order
                work_order.asset_id = asset_options[selected_asset]
                work_order.title = title
                work_order.description = description if description else None
                work_order.work_type = work_type
                work_order.priority = priority
                work_order.status = status
                work_order.assigned_to = user_options[assigned_to]
                work_order.scheduled_date = datetime.combine(scheduled_date, datetime.min.time()) if scheduled_date else None
                work_order.due_date = datetime.combine(due_date, datetime.max.time()) if due_date else None
                work_order.start_date = datetime.combine(start_date, datetime.min.time()) if start_date else None
                work_order.completion_date = datetime.combine(completion_date, datetime.max.time()) if completion_date else None
                work_order.estimated_cost = estimated_cost if estimated_cost > 0 else None
                work_order.actual_cost = actual_cost if actual_cost > 0 else None
                work_order.labor_hours = labor_hours if labor_hours > 0 else None
                work_order.notes = notes if notes else None
                work_order.completion_notes = completion_notes if completion_notes else None
                work_order.latitude = latitude if latitude else None
                work_order.longitude = longitude if longitude else None
                
                session.commit()
                st.success(f"✅ Work Order {work_order.work_order_number} updated successfully!")
                del st.session_state['edit_wo_id']
                st.rerun()
    
    # Show a back button outside the form
    if st.button("← Back to Work Orders"):
        del st.session_state['edit_wo_id']
        st.rerun()


def show_work_order_map(session):
    """Display work orders on a map"""
    st.subheader("Work Order Map View")
    
    # Get dynamic dropdown values
    work_order_statuses = get_dropdown_values(session, CATEGORY_WORK_ORDER_STATUS)
    work_order_priorities = get_dropdown_values(session, CATEGORY_WORK_ORDER_PRIORITY)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All"] + work_order_statuses, key="map_status")
    with col2:
        priority_filter = st.selectbox("Filter by Priority", ["All"] + work_order_priorities, key="map_priority")
    with col3:
        date_range = st.selectbox("Date Range", ["All", "Today", "This Week", "This Month", "Overdue"])
    
    # Build query
    query = session.query(WorkOrder)
    
    if status_filter != "All":
        query = query.filter(WorkOrder.status == status_filter)
    
    if priority_filter != "All":
        query = query.filter(WorkOrder.priority == priority_filter)
    
    # Date range filtering
    if date_range == "Today":
        today = datetime.now().date()
        query = query.filter(WorkOrder.created_date >= datetime.combine(today, datetime.min.time()))
    elif date_range == "This Week":
        week_start = datetime.now().date() - timedelta(days=datetime.now().weekday())
        query = query.filter(WorkOrder.created_date >= datetime.combine(week_start, datetime.min.time()))
    elif date_range == "This Month":
        month_start = datetime.now().date().replace(day=1)
        query = query.filter(WorkOrder.created_date >= datetime.combine(month_start, datetime.min.time()))
    elif date_range == "Overdue":
        query = query.filter(WorkOrder.due_date < datetime.now(), WorkOrder.status != "Completed")
    
    work_orders = query.all()
    
    # Filter work orders with location data
    wo_with_location = []
    for wo in work_orders:
        lat = wo.latitude or (wo.asset.latitude if wo.asset else None)
        lon = wo.longitude or (wo.asset.longitude if wo.asset else None)
        if lat and lon:
            wo_with_location.append((wo, lat, lon))
    
    if wo_with_location:
        st.info(f"Displaying {len(wo_with_location)} work orders on map")
        
        # Calculate map center
        avg_lat = sum(lat for _, lat, _ in wo_with_location) / len(wo_with_location)
        avg_lon = sum(lon for _, _, lon in wo_with_location) / len(wo_with_location)
        
        # Create map
        m = folium.Map(location=[avg_lat, avg_lon], zoom_start=12)
        
        # Add markers
        for wo, lat, lon in wo_with_location:
            # Color based on priority
            color_map = {
                "Critical": "darkred",
                "High": "red",
                "Medium": "orange",
                "Low": "green"
            }
            color = color_map.get(wo.priority, "blue")
            
            # Icon based on status
            icon = "wrench" if wo.status == "In Progress" else "exclamation-sign"
            
            popup_html = f"""
            <b>{wo.work_order_number}</b><br>
            <b>{wo.title}</b><br>
            Priority: {wo.priority}<br>
            Status: {wo.status}<br>
            Assigned: {wo.assigned_to or 'Unassigned'}<br>
            Due: {format_date(wo.due_date)}
            """
            
            folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=wo.work_order_number,
                icon=folium.Icon(color=color, icon=icon)
            ).add_to(m)
        
        # Display map
        folium_static(m, width=1000, height=600)
        
        # Export to KML
        if st.button("📍 Export to Google Earth (KML)"):
            from google_earth import export_work_orders_to_kml
            kml_file = export_work_orders_to_kml(session, "work_orders.kml")
            with open(kml_file, 'rb') as f:
                st.download_button(
                    "Download KML File",
                    f,
                    file_name="work_orders.kml",
                    mime="application/vnd.google-earth.kml+xml"
                )
    else:
        st.warning("No work orders with location data found matching the criteria.")


def show_work_order_analytics(session):
    """Display work order analytics and reports"""
    st.subheader("Work Order Analytics")
    
    # Get all work orders
    work_orders = session.query(WorkOrder).all()
    
    if not work_orders:
        st.warning("No work orders available for analysis.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_wo = len(work_orders)
        st.metric("Total Work Orders", total_wo)
    
    with col2:
        completed = len([wo for wo in work_orders if wo.status == "Completed"])
        completion_rate = (completed / total_wo * 100) if total_wo > 0 else 0
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    with col3:
        total_cost = sum(wo.actual_cost for wo in work_orders if wo.actual_cost)
        st.metric("Total Actual Cost", f"${total_cost:,.2f}")
    
    with col4:
        avg_hours = sum(wo.labor_hours for wo in work_orders if wo.labor_hours) / len([wo for wo in work_orders if wo.labor_hours]) if any(wo.labor_hours for wo in work_orders) else 0
        st.metric("Avg Labor Hours", f"{avg_hours:.1f}")
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Status distribution
        status_counts = {}
        for wo in work_orders:
            status_counts[wo.status] = status_counts.get(wo.status, 0) + 1
        
        fig_status = px.pie(
            values=list(status_counts.values()),
            names=list(status_counts.keys()),
            title="Work Orders by Status"
        )
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Priority distribution
        priority_counts = {}
        for wo in work_orders:
            priority_counts[wo.priority] = priority_counts.get(wo.priority, 0) + 1
        
        fig_priority = px.bar(
            x=list(priority_counts.keys()),
            y=list(priority_counts.values()),
            title="Work Orders by Priority",
            labels={'x': 'Priority', 'y': 'Count'}
        )
        st.plotly_chart(fig_priority, use_container_width=True)
    
    # Work type distribution
    type_counts = {}
    for wo in work_orders:
        type_counts[wo.work_type] = type_counts.get(wo.work_type, 0) + 1
    
    fig_type = px.bar(
        x=list(type_counts.keys()),
        y=list(type_counts.values()),
        title="Work Orders by Type",
        labels={'x': 'Work Type', 'y': 'Count'}
    )
    st.plotly_chart(fig_type, use_container_width=True)
    
    # Monthly trend
    monthly_data = {}
    for wo in work_orders:
        month_key = wo.created_date.strftime("%Y-%m")
        monthly_data[month_key] = monthly_data.get(month_key, 0) + 1
    
    if monthly_data:
        sorted_months = sorted(monthly_data.keys())
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=sorted_months,
            y=[monthly_data[m] for m in sorted_months],
            mode='lines+markers',
            name='Work Orders'
        ))
        fig_trend.update_layout(
            title="Monthly Work Order Trend",
            xaxis_title="Month",
            yaxis_title="Number of Work Orders"
        )
        st.plotly_chart(fig_trend, use_container_width=True)
