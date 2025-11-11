"""
Costing Management Module
Handles cost tracking, Bill of Quantities (BOQ), and cost reporting for Work Orders and Inspections
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
from database import CostItem, WorkOrder, Inspection
from utils import format_date, format_datetime
import plotly.express as px
import plotly.graph_objects as go


def show_costs_in_detail_view(session, linked_type, linked_id, parent_number):
    """
    Display cost summary in work order or inspection detail views
    This function can be called from work_order_management.py and inspection_management.py
    """
    st.write("### 💰 Cost Details")
    
    # Get cost items
    cost_items = session.query(CostItem).filter_by(
        linked_type=linked_type,
        linked_id=linked_id
    ).all()
    
    if not cost_items:
        st.info("No costs recorded yet. Go to Costing Management to add cost items.")
        return
    
    # Calculate totals by category
    category_totals = {cat: 0.0 for cat in COST_CATEGORIES}
    for item in cost_items:
        if item.cost_category in category_totals:
            category_totals[item.cost_category] += item.total_cost or 0.0
    
    total_cost = sum(category_totals.values())
    
    # Display metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("💼 Labour", f"${category_totals['Labour']:,.2f}")
    
    with col2:
        st.metric("🧱 Material", f"${category_totals['Material']:,.2f}")
    
    with col3:
        st.metric("🚜 Plant", f"${category_totals['Plant']:,.2f}")
    
    with col4:
        st.metric("🔧 Repairs", f"${category_totals['Repairs']:,.2f}")
    
    with col5:
        st.metric("💰 Total", f"${total_cost:,.2f}")
    
    # Show brief BOQ
    with st.expander(f"📋 View Bill of Quantities ({len(cost_items)} items)", expanded=False):
        boq_data = []
        for item in cost_items:
            boq_data.append({
                "Item #": item.item_number or "-",
                "Category": item.cost_category,
                "Description": item.description[:50] + "..." if len(item.description) > 50 else item.description,
                "Quantity": f"{item.quantity:.2f}",
                "Unit": item.unit or "-",
                "Unit Rate": f"${item.unit_rate:,.2f}",
                "Total": f"${item.total_cost:,.2f}",
                "Approved": "✅" if item.approved else "⏳"
            })
        
        df = pd.DataFrame(boq_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.info(f"💡 Go to **Costing Management** to add, edit, or manage detailed costs for {parent_number}")


def get_total_cost(session, linked_type, linked_id):
    """
    Get total cost for a work order or inspection
    Returns: (total_cost, cost_items_count)
    """
    cost_items = session.query(CostItem).filter_by(
        linked_type=linked_type,
        linked_id=linked_id
    ).all()
    
    total_cost = sum(item.total_cost or 0 for item in cost_items)
    return total_cost, len(cost_items)

# Cost categories
COST_CATEGORIES = ["Labour", "Material", "Plant", "Repairs"]

# Common units
COMMON_UNITS = {
    "Labour": ["hours", "days", "weeks"],
    "Material": ["m³", "m²", "m", "kg", "tonne", "L", "each", "unit"],
    "Plant": ["hours", "days", "weeks", "months"],
    "Repairs": ["hours", "each", "unit", "lot"]
}


def show_costing_management(session):
    """Main costing management interface"""
    st.header("💰 Costing Management")
    
    st.info("""
    **Bill of Quantities (BOQ) System**
    
    Track and manage detailed costs for Work Orders and Inspections across four categories:
    - 💼 **Labour**: Personnel costs and labor hours
    - 🧱 **Material**: Materials and supplies used
    - 🚜 **Plant**: Equipment and machinery costs
    - 🔧 **Repairs**: Repair and maintenance costs
    """)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Work Order Costs",
        "Inspection Costs",
        "Cost Reports",
        "Cost Summary"
    ])
    
    with tab1:
        show_work_order_costing(session)
    
    with tab2:
        show_inspection_costing(session)
    
    with tab3:
        show_cost_reports(session)
    
    with tab4:
        show_cost_summary(session)


def show_work_order_costing(session):
    """Display and manage costs for work orders"""
    st.subheader("Work Order Costs - Bill of Quantities")
    
    # Get all work orders
    work_orders = session.query(WorkOrder).order_by(WorkOrder.created_date.desc()).all()
    
    if not work_orders:
        st.warning("No work orders found. Please create a work order first.")
        return
    
    # Select work order
    wo_options = {f"{wo.work_order_number} - {wo.title}": wo.id for wo in work_orders}
    selected_wo = st.selectbox("Select Work Order", list(wo_options.keys()))
    
    if selected_wo:
        wo_id = wo_options[selected_wo]
        work_order = session.query(WorkOrder).filter_by(id=wo_id).first()
        
        st.divider()
        
        # Display work order info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**WO Number:** {work_order.work_order_number}")
            st.write(f"**Title:** {work_order.title}")
        with col2:
            st.write(f"**Status:** {work_order.status}")
            st.write(f"**Priority:** {work_order.priority}")
        with col3:
            if work_order.asset:
                st.write(f"**Asset:** {work_order.asset.name}")
            st.write(f"**Assigned To:** {work_order.assigned_to or 'Unassigned'}")
        
        st.divider()
        
        # Get existing cost items
        cost_items = session.query(CostItem).filter_by(
            linked_type='work_order',
            linked_id=wo_id
        ).order_by(CostItem.item_number).all()
        
        # Display cost summary
        display_cost_summary(cost_items, work_order)
        
        st.divider()
        
        # Display BOQ
        if cost_items:
            display_bill_of_quantities(session, cost_items, 'work_order', wo_id)
        else:
            st.info("No cost items recorded yet. Add cost items using the form below.")
        
        st.divider()
        
        # Add new cost item form
        add_cost_item_form(session, 'work_order', wo_id, work_order.work_order_number)


def show_inspection_costing(session):
    """Display and manage costs for inspections"""
    st.subheader("Inspection Costs - Bill of Quantities")
    
    # Get all inspections
    inspections = session.query(Inspection).order_by(Inspection.inspection_date.desc()).all()
    
    if not inspections:
        st.warning("No inspections found. Please create an inspection first.")
        return
    
    # Select inspection
    insp_options = {f"{insp.inspection_number} - {insp.inspection_type}": insp.id for insp in inspections}
    selected_insp = st.selectbox("Select Inspection", list(insp_options.keys()))
    
    if selected_insp:
        insp_id = insp_options[selected_insp]
        inspection = session.query(Inspection).filter_by(id=insp_id).first()
        
        st.divider()
        
        # Display inspection info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Inspection #:** {inspection.inspection_number}")
            st.write(f"**Type:** {inspection.inspection_type}")
        with col2:
            st.write(f"**Date:** {format_date(inspection.inspection_date)}")
            st.write(f"**Inspector:** {inspection.inspector or 'N/A'}")
        with col3:
            if inspection.asset:
                st.write(f"**Asset:** {inspection.asset.name}")
            st.write(f"**Defects Found:** {'Yes' if inspection.defects_found else 'No'}")
        
        st.divider()
        
        # Get existing cost items
        cost_items = session.query(CostItem).filter_by(
            linked_type='inspection',
            linked_id=insp_id
        ).order_by(CostItem.item_number).all()
        
        # Display cost summary
        display_cost_summary(cost_items, inspection)
        
        st.divider()
        
        # Display BOQ
        if cost_items:
            display_bill_of_quantities(session, cost_items, 'inspection', insp_id)
        else:
            st.info("No cost items recorded yet. Add cost items using the form below.")
        
        st.divider()
        
        # Add new cost item form
        add_cost_item_form(session, 'inspection', insp_id, inspection.inspection_number)


def display_cost_summary(cost_items, parent_record):
    """Display summary of costs by category"""
    st.subheader("Cost Summary")
    
    # Calculate totals by category
    category_totals = {cat: 0.0 for cat in COST_CATEGORIES}
    for item in cost_items:
        if item.cost_category in category_totals:
            category_totals[item.cost_category] += item.total_cost or 0.0
    
    total_cost = sum(category_totals.values())
    
    # Display metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("💼 Labour", f"${category_totals['Labour']:,.2f}")
    
    with col2:
        st.metric("🧱 Material", f"${category_totals['Material']:,.2f}")
    
    with col3:
        st.metric("🚜 Plant", f"${category_totals['Plant']:,.2f}")
    
    with col4:
        st.metric("🔧 Repairs", f"${category_totals['Repairs']:,.2f}")
    
    with col5:
        st.metric("💰 Total Cost", f"${total_cost:,.2f}")
    
    # Compare with estimated cost for work orders
    if hasattr(parent_record, 'estimated_cost') and parent_record.estimated_cost:
        variance = total_cost - parent_record.estimated_cost
        variance_pct = (variance / parent_record.estimated_cost * 100) if parent_record.estimated_cost > 0 else 0
        
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Estimated Cost", f"${parent_record.estimated_cost:,.2f}")
        with col2:
            st.metric("Actual Cost", f"${total_cost:,.2f}")
        with col3:
            st.metric("Variance", f"${variance:,.2f}", delta=f"{variance_pct:.1f}%")


def display_bill_of_quantities(session, cost_items, linked_type, linked_id):
    """Display Bill of Quantities table with edit/delete functionality"""
    st.subheader("📋 Bill of Quantities (BOQ)")
    
    # Create DataFrame for display
    boq_data = []
    for item in cost_items:
        boq_data.append({
            "Item #": item.item_number or "-",
            "Category": item.cost_category,
            "Description": item.description,
            "Quantity": f"{item.quantity:.2f}",
            "Unit": item.unit or "-",
            "Unit Rate": f"${item.unit_rate:,.2f}",
            "Total Cost": f"${item.total_cost:,.2f}",
            "Supplier": item.supplier_contractor or "-",
            "Date": format_date(item.date_incurred) if item.date_incurred else "-",
            "Approved": "✅" if item.approved else "⏳",
            "ID": item.id
        })
    
    df = pd.DataFrame(boq_data)
    
    # Display table
    st.dataframe(df.drop(columns=['ID']), use_container_width=True, hide_index=True)
    
    # Export options
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("📥 Export BOQ to CSV", key=f"export_boq_{linked_type}_{linked_id}"):
            csv = df.drop(columns=['ID']).to_csv(index=False)
            st.download_button(
                "Download BOQ CSV",
                csv,
                f"BOQ_{linked_type}_{linked_id}_{datetime.now().strftime('%Y%m%d')}.csv",
                "text/csv",
                key=f'download-boq-csv_{linked_type}_{linked_id}'
            )
    
    st.divider()
    
    # Edit/Delete section
    st.subheader("Edit/Delete Cost Items")
    
    if cost_items:
        # Select item to edit/delete
        item_options = {f"{item.item_number or 'N/A'} - {item.description[:50]}": item.id for item in cost_items}
        selected_item_str = st.selectbox(
            "Select Cost Item",
            list(item_options.keys()),
            key=f"select_cost_item_{linked_type}_{linked_id}"
        )
        
        if selected_item_str:
            item_id = item_options[selected_item_str]
            cost_item = session.query(CostItem).filter_by(id=item_id).first()
            
            if cost_item:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Edit form
                    with st.expander("✏️ Edit Cost Item", expanded=False):
                        edit_cost_item_form(session, cost_item, linked_type, linked_id)
                
                with col2:
                    st.write("")  # Spacing
                    st.write("")  # Spacing
                    # Delete button
                    if st.button("🗑️ Delete Item", key=f"delete_{cost_item.id}", use_container_width=True):
                        if st.checkbox("Confirm deletion", key=f"confirm_delete_{cost_item.id}"):
                            session.delete(cost_item)
                            session.commit()
                            st.success("Cost item deleted!")
                            st.rerun()


def add_cost_item_form(session, linked_type, linked_id, parent_number):
    """Form to add a new cost item"""
    st.subheader("➕ Add New Cost Item")
    
    with st.form(f"add_cost_item_{linked_type}_{linked_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            item_number = st.text_input(
                "Item Number",
                placeholder="e.g., 1.1, 1.2, 2.1",
                help="BOQ item numbering (optional)"
            )
            
            cost_category = st.selectbox("Cost Category *", COST_CATEGORIES)
            
            description = st.text_area(
                "Description *",
                placeholder="Detailed description of the cost item",
                help="Provide a clear description of the work/material/equipment"
            )
            
            quantity = st.number_input("Quantity *", min_value=0.0, value=1.0, step=0.1)
            
            # Get units based on category
            unit_options = COMMON_UNITS.get(cost_category, ["each"])
            unit = st.selectbox("Unit *", unit_options + ["Other"])
            
            if unit == "Other":
                unit = st.text_input("Custom Unit", placeholder="Enter unit")
        
        with col2:
            unit_rate = st.number_input(
                "Unit Rate ($) *",
                min_value=0.0,
                value=0.0,
                step=0.01,
                help="Cost per unit"
            )
            
            # Calculate total automatically
            total_cost = quantity * unit_rate
            st.metric("Total Cost", f"${total_cost:,.2f}")
            
            supplier_contractor = st.text_input(
                "Supplier/Contractor",
                placeholder="Name of supplier or contractor"
            )
            
            date_incurred = st.date_input(
                "Date Incurred",
                value=date.today(),
                help="Date when cost was incurred"
            )
            
            invoice_reference = st.text_input(
                "Invoice/Reference #",
                placeholder="Invoice or reference number"
            )
            
            notes = st.text_area("Notes", placeholder="Additional notes or comments")
            
            approved = st.checkbox("Approved", value=False)
            
            if approved:
                approved_by = st.text_input("Approved By")
            else:
                approved_by = None
        
        submitted = st.form_submit_button("➕ Add Cost Item", type="primary")
        
        if submitted:
            if not description:
                st.error("Please provide a description for the cost item")
            elif quantity <= 0:
                st.error("Quantity must be greater than 0")
            elif unit_rate < 0:
                st.error("Unit rate cannot be negative")
            else:
                # Create new cost item
                new_cost_item = CostItem(
                    linked_type=linked_type,
                    linked_id=linked_id,
                    item_number=item_number if item_number else None,
                    cost_category=cost_category,
                    description=description,
                    quantity=quantity,
                    unit=unit,
                    unit_rate=unit_rate,
                    total_cost=total_cost,
                    supplier_contractor=supplier_contractor if supplier_contractor else None,
                    date_incurred=date_incurred,
                    invoice_reference=invoice_reference if invoice_reference else None,
                    notes=notes if notes else None,
                    approved=approved,
                    approved_by=approved_by if approved else None,
                    approval_date=datetime.now() if approved else None,
                    created_by="System"  # Replace with actual user
                )
                
                session.add(new_cost_item)
                session.commit()
                st.success(f"✅ Cost item added successfully to {parent_number}!")
                st.rerun()


def edit_cost_item_form(session, cost_item, linked_type, linked_id):
    """Form to edit an existing cost item"""
    
    with st.form(f"edit_cost_item_{cost_item.id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            item_number = st.text_input(
                "Item Number",
                value=cost_item.item_number or "",
                placeholder="e.g., 1.1, 1.2, 2.1"
            )
            
            cost_category = st.selectbox(
                "Cost Category *",
                COST_CATEGORIES,
                index=COST_CATEGORIES.index(cost_item.cost_category) if cost_item.cost_category in COST_CATEGORIES else 0
            )
            
            description = st.text_area("Description *", value=cost_item.description)
            
            quantity = st.number_input(
                "Quantity *",
                min_value=0.0,
                value=float(cost_item.quantity),
                step=0.1
            )
            
            unit = st.text_input("Unit *", value=cost_item.unit or "")
        
        with col2:
            unit_rate = st.number_input(
                "Unit Rate ($) *",
                min_value=0.0,
                value=float(cost_item.unit_rate),
                step=0.01
            )
            
            # Calculate total automatically
            total_cost = quantity * unit_rate
            st.metric("Total Cost", f"${total_cost:,.2f}")
            
            supplier_contractor = st.text_input(
                "Supplier/Contractor",
                value=cost_item.supplier_contractor or ""
            )
            
            date_incurred = st.date_input(
                "Date Incurred",
                value=cost_item.date_incurred if cost_item.date_incurred else date.today()
            )
            
            invoice_reference = st.text_input(
                "Invoice/Reference #",
                value=cost_item.invoice_reference or ""
            )
            
            notes = st.text_area("Notes", value=cost_item.notes or "")
            
            approved = st.checkbox("Approved", value=cost_item.approved)
            
            if approved:
                approved_by = st.text_input(
                    "Approved By",
                    value=cost_item.approved_by or ""
                )
            else:
                approved_by = None
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submitted = st.form_submit_button("💾 Save Changes", type="primary")
        with col_btn2:
            cancel = st.form_submit_button("❌ Cancel")
        
        if cancel:
            st.rerun()
        
        if submitted:
            if not description:
                st.error("Please provide a description for the cost item")
            elif quantity <= 0:
                st.error("Quantity must be greater than 0")
            elif unit_rate < 0:
                st.error("Unit rate cannot be negative")
            else:
                # Update cost item
                cost_item.item_number = item_number if item_number else None
                cost_item.cost_category = cost_category
                cost_item.description = description
                cost_item.quantity = quantity
                cost_item.unit = unit
                cost_item.unit_rate = unit_rate
                cost_item.total_cost = total_cost
                cost_item.supplier_contractor = supplier_contractor if supplier_contractor else None
                cost_item.date_incurred = date_incurred
                cost_item.invoice_reference = invoice_reference if invoice_reference else None
                cost_item.notes = notes if notes else None
                cost_item.approved = approved
                cost_item.approved_by = approved_by if approved else None
                cost_item.approval_date = datetime.now() if approved and not cost_item.approved else cost_item.approval_date
                cost_item.modified_by = "System"  # Replace with actual user
                
                session.commit()
                st.success("✅ Cost item updated successfully!")
                st.rerun()


def show_cost_reports(session):
    """Display cost reports and analytics"""
    st.subheader("Cost Reports & Analytics")
    
    # Get all cost items
    cost_items = session.query(CostItem).all()
    
    if not cost_items:
        st.warning("No cost items recorded yet.")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        linked_type_filter = st.selectbox("Type", ["All", "Work Orders", "Inspections"])
    
    with col2:
        category_filter = st.selectbox("Category", ["All"] + COST_CATEGORIES)
    
    with col3:
        approval_filter = st.selectbox("Approval Status", ["All", "Approved", "Pending"])
    
    # Apply filters
    filtered_items = cost_items
    
    if linked_type_filter == "Work Orders":
        filtered_items = [item for item in filtered_items if item.linked_type == 'work_order']
    elif linked_type_filter == "Inspections":
        filtered_items = [item for item in filtered_items if item.linked_type == 'inspection']
    
    if category_filter != "All":
        filtered_items = [item for item in filtered_items if item.cost_category == category_filter]
    
    if approval_filter == "Approved":
        filtered_items = [item for item in filtered_items if item.approved]
    elif approval_filter == "Pending":
        filtered_items = [item for item in filtered_items if not item.approved]
    
    if not filtered_items:
        st.info("No cost items match the selected filters.")
        return
    
    # Summary metrics
    total_cost = sum(item.total_cost or 0 for item in filtered_items)
    approved_cost = sum(item.total_cost or 0 for item in filtered_items if item.approved)
    pending_cost = sum(item.total_cost or 0 for item in filtered_items if not item.approved)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Cost Items", len(filtered_items))
    
    with col2:
        st.metric("Total Cost", f"${total_cost:,.2f}")
    
    with col3:
        st.metric("Approved Cost", f"${approved_cost:,.2f}")
    
    with col4:
        st.metric("Pending Approval", f"${pending_cost:,.2f}")
    
    st.divider()
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Cost by category
        category_totals = {}
        for item in filtered_items:
            category_totals[item.cost_category] = category_totals.get(item.cost_category, 0) + (item.total_cost or 0)
        
        fig_category = px.pie(
            values=list(category_totals.values()),
            names=list(category_totals.keys()),
            title="Cost Distribution by Category"
        )
        st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        # Approval status
        approved_count = len([item for item in filtered_items if item.approved])
        pending_count = len([item for item in filtered_items if not item.approved])
        
        fig_approval = px.pie(
            values=[approved_count, pending_count],
            names=["Approved", "Pending"],
            title="Cost Items by Approval Status"
        )
        st.plotly_chart(fig_approval, use_container_width=True)
    
    # Cost trend over time
    monthly_data = {}
    for item in filtered_items:
        if item.date_incurred:
            month_key = item.date_incurred.strftime("%Y-%m")
            monthly_data[month_key] = monthly_data.get(month_key, 0) + (item.total_cost or 0)
    
    if monthly_data:
        sorted_months = sorted(monthly_data.keys())
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=sorted_months,
            y=[monthly_data[m] for m in sorted_months],
            mode='lines+markers',
            name='Total Cost'
        ))
        fig_trend.update_layout(
            title="Monthly Cost Trend",
            xaxis_title="Month",
            yaxis_title="Total Cost ($)"
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    st.divider()
    
    # Detailed list
    st.subheader("Detailed Cost Items")
    
    report_data = []
    for item in filtered_items:
        # Get parent record details
        if item.linked_type == 'work_order':
            wo = session.query(WorkOrder).filter_by(id=item.linked_id).first()
            parent_ref = wo.work_order_number if wo else "N/A"
            parent_title = wo.title if wo else "N/A"
        else:
            insp = session.query(Inspection).filter_by(id=item.linked_id).first()
            parent_ref = insp.inspection_number if insp else "N/A"
            parent_title = insp.inspection_type if insp else "N/A"
        
        report_data.append({
            "Type": item.linked_type.replace('_', ' ').title(),
            "Reference": parent_ref,
            "Title": parent_title,
            "Item #": item.item_number or "-",
            "Category": item.cost_category,
            "Description": item.description[:50] + "..." if len(item.description) > 50 else item.description,
            "Quantity": f"{item.quantity:.2f}",
            "Unit": item.unit or "-",
            "Unit Rate": f"${item.unit_rate:,.2f}",
            "Total Cost": f"${item.total_cost:,.2f}",
            "Date": format_date(item.date_incurred) if item.date_incurred else "-",
            "Approved": "✅" if item.approved else "⏳"
        })
    
    df = pd.DataFrame(report_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Export report
    if st.button("📥 Export Report to CSV"):
        csv = df.to_csv(index=False)
        st.download_button(
            "Download Cost Report CSV",
            csv,
            f"Cost_Report_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv",
            key='download-cost-report-csv'
        )


def show_cost_summary(session):
    """Display overall cost summary"""
    st.subheader("Overall Cost Summary")
    
    # Get all cost items
    cost_items = session.query(CostItem).all()
    
    if not cost_items:
        st.warning("No cost items recorded yet.")
        return
    
    # Overall totals
    total_items = len(cost_items)
    total_cost = sum(item.total_cost or 0 for item in cost_items)
    
    wo_items = [item for item in cost_items if item.linked_type == 'work_order']
    insp_items = [item for item in cost_items if item.linked_type == 'inspection']
    
    wo_cost = sum(item.total_cost or 0 for item in wo_items)
    insp_cost = sum(item.total_cost or 0 for item in insp_items)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Cost Items", total_items)
        st.metric("Total Cost", f"${total_cost:,.2f}")
    
    with col2:
        st.metric("Work Order Costs", f"${wo_cost:,.2f}")
        st.write(f"*{len(wo_items)} cost items*")
    
    with col3:
        st.metric("Inspection Costs", f"${insp_cost:,.2f}")
        st.write(f"*{len(insp_items)} cost items*")
    
    st.divider()
    
    # Cost by category - overall
    st.subheader("Cost Breakdown by Category")
    
    category_totals = {cat: 0.0 for cat in COST_CATEGORIES}
    for item in cost_items:
        if item.cost_category in category_totals:
            category_totals[item.cost_category] += item.total_cost or 0.0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💼 Labour", f"${category_totals['Labour']:,.2f}")
        labour_pct = (category_totals['Labour'] / total_cost * 100) if total_cost > 0 else 0
        st.write(f"*{labour_pct:.1f}% of total*")
    
    with col2:
        st.metric("🧱 Material", f"${category_totals['Material']:,.2f}")
        material_pct = (category_totals['Material'] / total_cost * 100) if total_cost > 0 else 0
        st.write(f"*{material_pct:.1f}% of total*")
    
    with col3:
        st.metric("🚜 Plant", f"${category_totals['Plant']:,.2f}")
        plant_pct = (category_totals['Plant'] / total_cost * 100) if total_cost > 0 else 0
        st.write(f"*{plant_pct:.1f}% of total*")
    
    with col4:
        st.metric("🔧 Repairs", f"${category_totals['Repairs']:,.2f}")
        repairs_pct = (category_totals['Repairs'] / total_cost * 100) if total_cost > 0 else 0
        st.write(f"*{repairs_pct:.1f}% of total*")
    
    st.divider()
    
    # Top cost items
    st.subheader("Top 10 Cost Items")
    
    sorted_items = sorted(cost_items, key=lambda x: x.total_cost or 0, reverse=True)[:10]
    
    top_items_data = []
    for idx, item in enumerate(sorted_items, 1):
        # Get parent record details
        if item.linked_type == 'work_order':
            wo = session.query(WorkOrder).filter_by(id=item.linked_id).first()
            parent_ref = wo.work_order_number if wo else "N/A"
        else:
            insp = session.query(Inspection).filter_by(id=item.linked_id).first()
            parent_ref = insp.inspection_number if insp else "N/A"
        
        top_items_data.append({
            "Rank": idx,
            "Reference": parent_ref,
            "Category": item.cost_category,
            "Description": item.description[:60] + "..." if len(item.description) > 60 else item.description,
            "Total Cost": f"${item.total_cost:,.2f}"
        })
    
    df_top = pd.DataFrame(top_items_data)
    st.dataframe(df_top, use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Approval status summary
    st.subheader("Approval Status")
    
    approved_items = [item for item in cost_items if item.approved]
    pending_items = [item for item in cost_items if not item.approved]
    
    approved_cost = sum(item.total_cost or 0 for item in approved_items)
    pending_cost = sum(item.total_cost or 0 for item in pending_items)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("✅ Approved Items", len(approved_items))
        st.metric("Approved Cost", f"${approved_cost:,.2f}")
    
    with col2:
        st.metric("⏳ Pending Items", len(pending_items))
        st.metric("Pending Cost", f"${pending_cost:,.2f}")
    
    if pending_items:
        st.warning(f"⚠️ {len(pending_items)} cost items totaling ${pending_cost:,.2f} are awaiting approval.")

