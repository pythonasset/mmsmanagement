"""
Reporting and Analytics Module
Comprehensive reporting and data visualization
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import Asset, WorkOrder, Inspection, AssetClass, AssetType
from settings import CONDITION_RATINGS
from utils import format_date, format_datetime

def show_reporting(session):
    """Main reporting and analytics interface"""
    st.header("📊 Reports & Analytics")
    
    # Create tabs for different reports
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Dashboard",
        "Asset Reports",
        "Maintenance Reports",
        "Inspection Reports",
        "Custom Reports"
    ])
    
    with tab1:
        show_dashboard(session)
    
    with tab2:
        show_asset_reports(session)
    
    with tab3:
        show_maintenance_reports(session)
    
    with tab4:
        show_inspection_reports(session)
    
    with tab5:
        show_custom_reports(session)


def show_dashboard(session):
    """Executive dashboard with key metrics"""
    st.subheader("Executive Dashboard")
    
    # Key Performance Indicators
    st.write("### Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Total assets
    total_assets = session.query(Asset).count()
    with col1:
        st.metric("Total Assets", total_assets)
    
    # Active work orders
    active_wo = session.query(WorkOrder).filter(
        WorkOrder.status.in_(["Open", "In Progress"])
    ).count()
    with col2:
        st.metric("Active Work Orders", active_wo)
    
    # Inspections this month
    month_start = datetime.now().replace(day=1)
    inspections_month = session.query(Inspection).filter(
        Inspection.inspection_date >= month_start
    ).count()
    with col3:
        st.metric("Inspections This Month", inspections_month)
    
    # Total asset value
    total_value = session.query(Asset).with_entities(
        Asset.current_value
    ).all()
    asset_value = sum(v[0] for v in total_value if v[0])
    with col4:
        st.metric("Total Asset Value", f"${asset_value:,.0f}")
    
    st.divider()
    
    # Asset condition overview
    st.write("### Asset Condition Overview")
    
    assets = session.query(Asset).filter(Asset.condition_rating.isnot(None)).all()
    if assets:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Condition distribution
            condition_data = {}
            for asset in assets:
                rating_text = CONDITION_RATINGS.get(asset.condition_rating, "Unknown")
                condition_data[rating_text] = condition_data.get(rating_text, 0) + 1
            
            fig = px.pie(
                values=list(condition_data.values()),
                names=list(condition_data.keys()),
                title="Asset Condition Distribution",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Assets requiring attention (condition <= 2)
            poor_assets = [a for a in assets if a.condition_rating <= 2]
            st.metric("Assets Requiring Attention", len(poor_assets))
            
            if poor_assets:
                st.write("**Poor Condition Assets:**")
                for asset in poor_assets[:5]:
                    st.write(f"- {asset.name} ({CONDITION_RATINGS[asset.condition_rating]})")
                if len(poor_assets) > 5:
                    st.write(f"...and {len(poor_assets) - 5} more")
    
    st.divider()
    
    # Work order trends
    st.write("### Work Order Trends (Last 6 Months)")
    
    work_orders = session.query(WorkOrder).all()
    if work_orders:
        # Group by month
        six_months_ago = datetime.now() - timedelta(days=180)
        recent_wo = [wo for wo in work_orders if wo.created_date >= six_months_ago]
        
        monthly_data = {}
        monthly_completed = {}
        
        for wo in recent_wo:
            month_key = wo.created_date.strftime("%Y-%m")
            monthly_data[month_key] = monthly_data.get(month_key, 0) + 1
            
            if wo.status == "Completed":
                monthly_completed[month_key] = monthly_completed.get(month_key, 0) + 1
        
        if monthly_data:
            sorted_months = sorted(monthly_data.keys())
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=sorted_months,
                y=[monthly_data[m] for m in sorted_months],
                mode='lines+markers',
                name='Created',
                line=dict(color='blue')
            ))
            fig.add_trace(go.Scatter(
                x=sorted_months,
                y=[monthly_completed.get(m, 0) for m in sorted_months],
                mode='lines+markers',
                name='Completed',
                line=dict(color='green')
            ))
            fig.update_layout(
                title="Work Orders Created vs Completed",
                xaxis_title="Month",
                yaxis_title="Count"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Asset classes overview
    st.write("### Assets by Class")
    
    asset_classes = session.query(AssetClass).all()
    if asset_classes:
        class_data = []
        for ac in asset_classes:
            asset_count = sum(len(at.assets) for ag in ac.asset_groups for at in ag.asset_types)
            class_data.append({
                "Class": ac.name,
                "Asset Count": asset_count
            })
        
        if class_data:
            df = pd.DataFrame(class_data)
            fig = px.bar(
                df,
                x="Class",
                y="Asset Count",
                title="Assets by Class"
            )
            st.plotly_chart(fig, use_container_width=True)


def show_asset_reports(session):
    """Asset-focused reports"""
    st.subheader("Asset Reports")
    
    report_type = st.selectbox(
        "Select Report Type",
        [
            "Asset Register Summary",
            "Asset Condition Report",
            "Asset Valuation Report",
            "Asset Location Report"
        ]
    )
    
    if report_type == "Asset Register Summary":
        show_asset_register_summary(session)
    elif report_type == "Asset Condition Report":
        show_asset_condition_report(session)
    elif report_type == "Asset Valuation Report":
        show_asset_valuation_report(session)
    elif report_type == "Asset Location Report":
        show_asset_location_report(session)


def show_asset_register_summary(session):
    """Complete asset register summary"""
    st.write("### Asset Register Summary")
    
    assets = session.query(Asset).all()
    
    if assets:
        data = []
        for asset in assets:
            asset_type = asset.asset_type.name if asset.asset_type else "N/A"
            asset_group = asset.asset_type.asset_group.name if asset.asset_type and asset.asset_type.asset_group else "N/A"
            asset_class = asset.asset_type.asset_group.asset_class.name if asset.asset_type and asset.asset_type.asset_group and asset.asset_type.asset_group.asset_class else "N/A"
            
            data.append({
                "Asset ID": asset.asset_id,
                "Name": asset.name,
                "Class": asset_class,
                "Group": asset_group,
                "Type": asset_type,
                "Status": asset.status,
                "Condition": CONDITION_RATINGS.get(asset.condition_rating, "N/A"),
                "Acquisition Date": format_date(asset.acquisition_date),
                "Current Value": f"${asset.current_value:,.2f}" if asset.current_value else "N/A",
                "Location": asset.address or "N/A"
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download CSV",
                csv,
                "asset_register_summary.csv",
                "text/csv"
            )
        
        with col2:
            # Excel export would go here
            st.info(f"Total Assets: {len(assets)}")


def show_asset_condition_report(session):
    """Asset condition analysis report"""
    st.write("### Asset Condition Report")
    
    # Filter by class
    asset_classes = session.query(AssetClass).all()
    class_options = ["All"] + [ac.name for ac in asset_classes]
    selected_class = st.selectbox("Filter by Class", class_options, key="cond_class")
    
    # Build query
    query = session.query(Asset).filter(Asset.condition_rating.isnot(None))
    
    if selected_class != "All":
        asset_class = session.query(AssetClass).filter_by(name=selected_class).first()
        if asset_class:
            asset_type_ids = [at.id for ag in asset_class.asset_groups for at in ag.asset_types]
            query = query.filter(Asset.asset_type_id.in_(asset_type_ids))
    
    assets = query.all()
    
    if assets:
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        avg_condition = sum(a.condition_rating for a in assets) / len(assets)
        with col1:
            st.metric("Average Condition", f"{avg_condition:.2f}")
        
        poor_count = len([a for a in assets if a.condition_rating <= 2])
        with col2:
            st.metric("Poor Condition", poor_count)
        
        excellent_count = len([a for a in assets if a.condition_rating == 5])
        with col3:
            st.metric("Excellent Condition", excellent_count)
        
        # Detailed table
        data = []
        for asset in assets:
            data.append({
                "Asset ID": asset.asset_id,
                "Name": asset.name,
                "Type": asset.asset_type.name if asset.asset_type else "N/A",
                "Condition Rating": asset.condition_rating,
                "Condition": CONDITION_RATINGS[asset.condition_rating],
                "Status": asset.status,
                "Last Modified": format_date(asset.modified_date)
            })
        
        df = pd.DataFrame(data)
        df = df.sort_values("Condition Rating")
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Visualization
        condition_counts = df["Condition"].value_counts()
        fig = px.bar(
            x=condition_counts.index,
            y=condition_counts.values,
            title="Asset Count by Condition",
            labels={'x': 'Condition', 'y': 'Count'},
            color=condition_counts.values,
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)


def show_asset_valuation_report(session):
    """Asset valuation and financial report"""
    st.write("### Asset Valuation Report")
    
    assets = session.query(Asset).filter(Asset.current_value.isnot(None)).all()
    
    if assets:
        # Summary metrics
        total_value = sum(a.current_value for a in assets)
        avg_value = total_value / len(assets)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Asset Value", f"${total_value:,.2f}")
        
        with col2:
            st.metric("Average Asset Value", f"${avg_value:,.2f}")
        
        with col3:
            st.metric("Assets Valued", len(assets))
        
        # Value by class
        class_values = {}
        for asset in assets:
            if asset.asset_type and asset.asset_type.asset_group and asset.asset_type.asset_group.asset_class:
                class_name = asset.asset_type.asset_group.asset_class.name
                class_values[class_name] = class_values.get(class_name, 0) + asset.current_value
        
        if class_values:
            fig = px.pie(
                values=list(class_values.values()),
                names=list(class_values.keys()),
                title="Asset Value Distribution by Class"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        data = []
        for asset in assets:
            data.append({
                "Asset ID": asset.asset_id,
                "Name": asset.name,
                "Type": asset.asset_type.name if asset.asset_type else "N/A",
                "Acquisition Cost": f"${asset.acquisition_cost:,.2f}" if asset.acquisition_cost else "N/A",
                "Current Value": f"${asset.current_value:,.2f}",
                "Acquisition Date": format_date(asset.acquisition_date)
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)


def show_asset_location_report(session):
    """Asset location and geographic distribution report"""
    st.write("### Asset Location Report")
    
    assets = session.query(Asset).filter(
        Asset.latitude.isnot(None),
        Asset.longitude.isnot(None)
    ).all()
    
    if assets:
        st.info(f"Assets with location data: {len(assets)}")
        
        # Geographic distribution
        data = []
        for asset in assets:
            data.append({
                "Asset ID": asset.asset_id,
                "Name": asset.name,
                "Address": asset.address or "N/A",
                "Latitude": f"{asset.latitude:.6f}",
                "Longitude": f"{asset.longitude:.6f}",
                "Type": asset.asset_type.name if asset.asset_type else "N/A",
                "Status": asset.status
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download Location Data",
            csv,
            "asset_locations.csv",
            "text/csv"
        )
    else:
        st.warning("No assets with location data available.")


def show_maintenance_reports(session):
    """Maintenance and work order reports"""
    st.subheader("Maintenance Reports")
    
    report_type = st.selectbox(
        "Select Report Type",
        [
            "Work Order Summary",
            "Maintenance Cost Analysis",
            "Inspection Report",
            "Maintenance Performance"
        ]
    )
    
    if report_type == "Work Order Summary":
        show_work_order_summary(session)
    elif report_type == "Maintenance Cost Analysis":
        show_cost_analysis(session)
    elif report_type == "Inspection Report":
        show_inspection_report(session)
    elif report_type == "Maintenance Performance":
        show_performance_metrics(session)


def show_work_order_summary(session):
    """Work order summary report"""
    st.write("### Work Order Summary")
    
    # Prominent date format banner
    st.warning("⚠️ **Date Picker Format:** Browser shows YYYY-MM-DD | **Your Format:** DD/MM/YYYY (Australian)")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From Date", value=None, key="wo_sum_start", help="Browser shows YYYY-MM-DD, but dates will be converted to DD/MM/YYYY")
        if start_date:
            st.markdown(f"📅 **Selected:** {format_date(start_date)}")
    with col2:
        end_date = st.date_input("To Date", value=None, key="wo_sum_end", help="Browser shows YYYY-MM-DD, but dates will be converted to DD/MM/YYYY")
        if end_date:
            st.markdown(f"📅 **Selected:** {format_date(end_date)}")
    
    # Display selected date range in locale format
    if start_date and end_date:
        st.success(f"✅ **Filtering from {format_date(start_date)} to {format_date(end_date)}**")
    elif start_date:
        st.success(f"✅ **Filtering from {format_date(start_date)} onwards**")
    elif end_date:
        st.success(f"✅ **Filtering up to {format_date(end_date)}**")
    
    query = session.query(WorkOrder)
    
    if start_date:
        query = query.filter(WorkOrder.created_date >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(WorkOrder.created_date <= datetime.combine(end_date, datetime.max.time()))
    
    work_orders = query.all()
    
    if work_orders:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Work Orders", len(work_orders))
        
        with col2:
            completed = len([wo for wo in work_orders if wo.status == "Completed"])
            st.metric("Completed", completed)
        
        with col3:
            in_progress = len([wo for wo in work_orders if wo.status == "In Progress"])
            st.metric("In Progress", in_progress)
        
        with col4:
            completion_rate = (completed / len(work_orders) * 100) if work_orders else 0
            st.metric("Completion Rate", f"{completion_rate:.1f}%")
        
        # By priority
        st.write("### Work Orders by Priority")
        priority_data = {}
        for wo in work_orders:
            priority_data[wo.priority] = priority_data.get(wo.priority, 0) + 1
        
        fig = px.bar(
            x=list(priority_data.keys()),
            y=list(priority_data.values()),
            title="Work Orders by Priority",
            labels={'x': 'Priority', 'y': 'Count'}
        )
        st.plotly_chart(fig, use_container_width=True)


def show_cost_analysis(session):
    """Maintenance cost analysis"""
    st.write("### Maintenance Cost Analysis")
    
    work_orders = session.query(WorkOrder).filter(WorkOrder.actual_cost.isnot(None)).all()
    
    if work_orders:
        total_cost = sum(wo.actual_cost for wo in work_orders)
        avg_cost = total_cost / len(work_orders)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Maintenance Cost", f"${total_cost:,.2f}")
        
        with col2:
            st.metric("Average Cost per Work Order", f"${avg_cost:,.2f}")
        
        # Cost by type
        type_costs = {}
        for wo in work_orders:
            type_costs[wo.work_type] = type_costs.get(wo.work_type, 0) + wo.actual_cost
        
        fig = px.pie(
            values=list(type_costs.values()),
            names=list(type_costs.keys()),
            title="Cost Distribution by Work Type"
        )
        st.plotly_chart(fig, use_container_width=True)


def show_inspection_report(session):
    """Inspection summary report with date filtering"""
    st.write("### Inspection Report")
    
    # Prominent date format banner
    st.warning("⚠️ **Date Picker Format:** Browser shows YYYY-MM-DD | **Your Format:** DD/MM/YYYY (Australian)")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From Date", value=None, key="maint_insp_start", help="Browser shows YYYY-MM-DD, but dates will be converted to DD/MM/YYYY")
        if start_date:
            st.markdown(f"📅 **Selected:** {format_date(start_date)}")
    with col2:
        end_date = st.date_input("To Date", value=None, key="maint_insp_end", help="Browser shows YYYY-MM-DD, but dates will be converted to DD/MM/YYYY")
        if end_date:
            st.markdown(f"📅 **Selected:** {format_date(end_date)}")
    
    # Display selected date range in locale format
    if start_date and end_date:
        st.success(f"✅ **Filtering from {format_date(start_date)} to {format_date(end_date)}**")
    elif start_date:
        st.success(f"✅ **Filtering from {format_date(start_date)} onwards**")
    elif end_date:
        st.success(f"✅ **Filtering up to {format_date(end_date)}**")
    
    # Build query with date filters
    query = session.query(Inspection)
    
    if start_date:
        query = query.filter(Inspection.inspection_date >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(Inspection.inspection_date <= datetime.combine(end_date, datetime.max.time()))
    
    inspections = query.all()
    
    if inspections:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Inspections", len(inspections))
        
        with col2:
            with_defects = len([i for i in inspections if i.defects_found])
            st.metric("With Defects", with_defects)
        
        with col3:
            defect_rate = (with_defects / len(inspections) * 100) if inspections else 0
            st.metric("Defect Rate", f"{defect_rate:.1f}%")
        
        # Inspections by type
        type_data = {}
        for insp in inspections:
            type_data[insp.inspection_type] = type_data.get(insp.inspection_type, 0) + 1
        
        fig = px.bar(
            x=list(type_data.keys()),
            y=list(type_data.values()),
            title="Inspections by Type"
        )
        st.plotly_chart(fig, use_container_width=True)


def show_performance_metrics(session):
    """Maintenance performance metrics"""
    st.write("### Maintenance Performance Metrics")
    
    work_orders = session.query(WorkOrder).all()
    
    if work_orders:
        # Response time (time from creation to start)
        response_times = []
        for wo in work_orders:
            if wo.start_date:
                delta = (wo.start_date - wo.created_date).days
                response_times.append(delta)
        
        if response_times:
            avg_response = sum(response_times) / len(response_times)
            st.metric("Average Response Time", f"{avg_response:.1f} days")
        
        # Completion time (time from start to completion)
        completion_times = []
        for wo in work_orders:
            if wo.start_date and wo.completion_date:
                delta = (wo.completion_date - wo.start_date).days
                completion_times.append(delta)
        
        if completion_times:
            avg_completion = sum(completion_times) / len(completion_times)
            st.metric("Average Completion Time", f"{avg_completion:.1f} days")


def show_inspection_reports(session):
    """Inspection reports and analytics"""
    st.subheader("Inspection Reports")
    
    report_type = st.selectbox(
        "Select Inspection Report Type",
        [
            "Inspection Summary",
            "Defect Analysis",
            "Condition Trend Report",
            "Inspector Performance"
        ],
        key="insp_report_type"
    )
    
    if report_type == "Inspection Summary":
        show_inspection_summary(session)
    elif report_type == "Defect Analysis":
        show_defect_analysis(session)
    elif report_type == "Condition Trend Report":
        show_condition_trends(session)
    elif report_type == "Inspector Performance":
        show_inspector_performance(session)


def show_inspection_summary(session):
    """Inspection summary report with date filtering"""
    st.write("### Inspection Summary Report")
    
    # Prominent date format banner
    st.warning("⚠️ **Date Picker Format:** Browser shows YYYY-MM-DD | **Your Format:** DD/MM/YYYY (Australian)")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From Date", value=None, key="insp_sum_start", help="Browser shows YYYY-MM-DD, but dates will be converted to DD/MM/YYYY")
        if start_date:
            st.markdown(f"📅 **Selected:** {format_date(start_date)}")
    with col2:
        end_date = st.date_input("To Date", value=None, key="insp_sum_end", help="Browser shows YYYY-MM-DD, but dates will be converted to DD/MM/YYYY")
        if end_date:
            st.markdown(f"📅 **Selected:** {format_date(end_date)}")
    
    # Display selected date range in locale format
    if start_date and end_date:
        st.success(f"✅ **Filtering from {format_date(start_date)} to {format_date(end_date)}**")
    elif start_date:
        st.success(f"✅ **Filtering from {format_date(start_date)} onwards**")
    elif end_date:
        st.success(f"✅ **Filtering up to {format_date(end_date)}**")
    
    # Build query
    query = session.query(Inspection)
    
    if start_date:
        query = query.filter(Inspection.inspection_date >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(Inspection.inspection_date <= datetime.combine(end_date, datetime.max.time()))
    
    inspections = query.all()
    
    if inspections:
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Inspections", len(inspections))
        
        with col2:
            with_defects = len([i for i in inspections if i.defects_found])
            st.metric("With Defects", with_defects)
        
        with col3:
            defect_rate = (with_defects / len(inspections) * 100) if inspections else 0
            st.metric("Defect Rate", f"{defect_rate:.1f}%")
        
        with col4:
            avg_condition = sum(i.condition_rating for i in inspections if i.condition_rating) / len([i for i in inspections if i.condition_rating]) if any(i.condition_rating for i in inspections) else 0
            st.metric("Avg Condition", f"{avg_condition:.1f}")
        
        st.divider()
        
        # Inspections by Type
        st.write("### Inspections by Type")
        type_counts = {}
        for insp in inspections:
            type_counts[insp.inspection_type] = type_counts.get(insp.inspection_type, 0) + 1
        
        fig = px.pie(
            names=list(type_counts.keys()),
            values=list(type_counts.values()),
            title="Distribution of Inspection Types"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Inspections by Status
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### By Status")
            status_counts = {}
            for insp in inspections:
                status_counts[insp.status] = status_counts.get(insp.status, 0) + 1
            
            status_df = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
            st.dataframe(status_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.write("### By Condition Rating")
            condition_counts = {}
            for insp in inspections:
                if insp.condition_rating:
                    rating_text = CONDITION_RATINGS.get(insp.condition_rating, "Unknown")
                    condition_counts[rating_text] = condition_counts.get(rating_text, 0) + 1
            
            if condition_counts:
                condition_df = pd.DataFrame(list(condition_counts.items()), columns=['Condition', 'Count'])
                st.dataframe(condition_df, use_container_width=True, hide_index=True)
        
        # Detailed inspection list
        st.divider()
        st.write("### Detailed Inspection List")
        
        insp_data = []
        for insp in inspections:
            asset_name = insp.asset.name if insp.asset else "N/A"
            asset_id = insp.asset.asset_id if insp.asset else "N/A"
            
            insp_data.append({
                "Inspection #": insp.inspection_number,
                "Date": format_date(insp.inspection_date),
                "Asset": f"{asset_id} - {asset_name}",
                "Type": insp.inspection_type,
                "Inspector": insp.inspector or "N/A",
                "Condition": CONDITION_RATINGS.get(insp.condition_rating, "N/A"),
                "Defects": "✓" if insp.defects_found else "✗",
                "Status": insp.status
            })
        
        df = pd.DataFrame(insp_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export option
        if st.button("📥 Export to CSV", key="export_insp_summary"):
            csv = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                "inspection_summary.csv",
                "text/csv",
                key='download-csv-insp-summary'
            )
    else:
        st.info("No inspections found for the selected date range.")


def show_defect_analysis(session):
    """Analysis of defects found during inspections"""
    st.write("### Defect Analysis Report")
    
    # Get inspections with defects
    inspections_with_defects = session.query(Inspection).filter(
        Inspection.defects_found == True
    ).all()
    
    if inspections_with_defects:
        # Metrics
        total_inspections = session.query(Inspection).count()
        defect_count = len(inspections_with_defects)
        defect_rate = (defect_count / total_inspections * 100) if total_inspections > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Inspections with Defects", defect_count)
        
        with col2:
            st.metric("Total Inspections", total_inspections)
        
        with col3:
            st.metric("Overall Defect Rate", f"{defect_rate:.1f}%")
        
        st.divider()
        
        # Defects by inspection type
        st.write("### Defects by Inspection Type")
        type_defects = {}
        for insp in inspections_with_defects:
            type_defects[insp.inspection_type] = type_defects.get(insp.inspection_type, 0) + 1
        
        fig = px.bar(
            x=list(type_defects.keys()),
            y=list(type_defects.values()),
            title="Defects by Inspection Type",
            labels={'x': 'Inspection Type', 'y': 'Number of Defects'},
            color=list(type_defects.values()),
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Defect details table
        st.write("### Defect Details")
        
        defect_data = []
        for insp in inspections_with_defects:
            asset_info = f"{insp.asset.asset_id} - {insp.asset.name}" if insp.asset else "N/A"
            
            defect_data.append({
                "Inspection #": insp.inspection_number,
                "Date": format_date(insp.inspection_date),
                "Asset": asset_info,
                "Type": insp.inspection_type,
                "Inspector": insp.inspector or "N/A",
                "Condition": CONDITION_RATINGS.get(insp.condition_rating, "N/A"),
                "Defect Description": insp.defect_description[:50] + "..." if insp.defect_description and len(insp.defect_description) > 50 else insp.defect_description or "N/A",
                "Follow-up Required": "✓" if insp.follow_up_required else "✗"
            })
        
        df = pd.DataFrame(defect_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export option
        if st.button("📥 Export Defect Report", key="export_defects"):
            csv = df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                "defect_analysis.csv",
                "text/csv",
                key='download-csv-defects'
            )
    else:
        st.success("✅ No defects found in any inspections!")


def show_condition_trends(session):
    """Show condition trends over time"""
    st.write("### Asset Condition Trend Report")
    
    # Get all inspections with condition ratings
    inspections = session.query(Inspection).filter(
        Inspection.condition_rating.isnot(None)
    ).order_by(Inspection.inspection_date).all()
    
    if inspections:
        # Overall condition trend
        st.write("### Overall Condition Trend Over Time")
        
        # Prepare data for time series
        trend_data = []
        for insp in inspections:
            trend_data.append({
                'Date': insp.inspection_date.date() if insp.inspection_date else None,
                'Condition Rating': insp.condition_rating,
                'Asset': insp.asset.name if insp.asset else "Unknown"
            })
        
        df = pd.DataFrame(trend_data)
        
        # Line chart showing average condition over time
        if not df.empty:
            monthly_avg = df.groupby(pd.Grouper(key='Date', freq='M'))['Condition Rating'].mean().reset_index()
            
            fig = px.line(
                monthly_avg,
                x='Date',
                y='Condition Rating',
                title='Average Condition Rating Over Time',
                labels={'Date': 'Month', 'Condition Rating': 'Avg Condition'}
            )
            fig.update_layout(yaxis_range=[0, 5])
            st.plotly_chart(fig, use_container_width=True)
        
        # Condition distribution
        st.write("### Current Condition Distribution")
        
        condition_counts = {}
        for insp in inspections:
            rating_text = CONDITION_RATINGS.get(insp.condition_rating, "Unknown")
            condition_counts[rating_text] = condition_counts.get(rating_text, 0) + 1
        
        fig = px.pie(
            names=list(condition_counts.keys()),
            values=list(condition_counts.values()),
            title="Distribution of Condition Ratings",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Assets requiring attention
        st.write("### Assets Requiring Attention")
        
        poor_condition = [insp for insp in inspections if insp.condition_rating and insp.condition_rating <= 2]
        
        if poor_condition:
            attention_data = []
            for insp in poor_condition[-10:]:  # Last 10
                attention_data.append({
                    "Asset": f"{insp.asset.asset_id} - {insp.asset.name}" if insp.asset else "N/A",
                    "Last Inspection": format_date(insp.inspection_date),
                    "Condition": CONDITION_RATINGS.get(insp.condition_rating, "N/A"),
                    "Inspector": insp.inspector or "N/A"
                })
            
            df_attention = pd.DataFrame(attention_data)
            st.dataframe(df_attention, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No assets currently in poor condition!")
    else:
        st.info("No inspection data available with condition ratings.")


def show_inspector_performance(session):
    """Inspector performance metrics"""
    st.write("### Inspector Performance Report")
    
    # Get all inspections
    inspections = session.query(Inspection).filter(
        Inspection.inspector.isnot(None)
    ).all()
    
    if inspections:
        # Performance by inspector
        inspector_stats = {}
        
        for insp in inspections:
            if insp.inspector not in inspector_stats:
                inspector_stats[insp.inspector] = {
                    'total': 0,
                    'with_defects': 0,
                    'completed': 0,
                    'avg_condition': []
                }
            
            inspector_stats[insp.inspector]['total'] += 1
            
            if insp.defects_found:
                inspector_stats[insp.inspector]['with_defects'] += 1
            
            if insp.status == "Completed":
                inspector_stats[insp.inspector]['completed'] += 1
            
            if insp.condition_rating:
                inspector_stats[insp.inspector]['avg_condition'].append(insp.condition_rating)
        
        # Create summary table
        performance_data = []
        for inspector, stats in inspector_stats.items():
            avg_cond = sum(stats['avg_condition']) / len(stats['avg_condition']) if stats['avg_condition'] else 0
            defect_rate = (stats['with_defects'] / stats['total'] * 100) if stats['total'] > 0 else 0
            completion_rate = (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            performance_data.append({
                "Inspector": inspector,
                "Total Inspections": stats['total'],
                "Completed": stats['completed'],
                "Completion Rate": f"{completion_rate:.1f}%",
                "Defects Found": stats['with_defects'],
                "Defect Rate": f"{defect_rate:.1f}%",
                "Avg Condition Rating": f"{avg_cond:.1f}"
            })
        
        df = pd.DataFrame(performance_data)
        df = df.sort_values("Total Inspections", ascending=False)
        
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Visual comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Inspections per Inspector")
            fig = px.bar(
                df,
                x="Inspector",
                y="Total Inspections",
                title="Total Inspections by Inspector",
                color="Total Inspections",
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("### Defect Detection Rate")
            # Convert defect rate back to numeric for plotting
            df_plot = df.copy()
            df_plot['Defect Rate Numeric'] = df_plot['Defect Rate'].str.rstrip('%').astype(float)
            
            fig = px.bar(
                df_plot,
                x="Inspector",
                y="Defect Rate Numeric",
                title="Defect Detection Rate by Inspector",
                labels={'Defect Rate Numeric': 'Defect Rate (%)'},
                color="Defect Rate Numeric",
                color_continuous_scale='Oranges'
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No inspection data available with inspector information.")


def show_custom_reports(session):
    """Custom report builder"""
    st.subheader("Custom Report Builder")
    
    st.info("🚧 Custom report builder functionality coming soon!")
    
    st.write("""
    The custom report builder will allow you to:
    - Select specific fields to include
    - Apply custom filters
    - Create calculated fields
    - Save report templates
    - Schedule automated reports
    """)
