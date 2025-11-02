"""
Document Viewer Module
View and manage all documents across assets, work orders, and inspections
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from database import Document, Asset, WorkOrder, Inspection
from utils import format_date, format_datetime

def show_document_viewer(session):
    """Main document viewer interface"""
    st.header("📁 Document Library")
    
    st.info("💡 View and manage all documents attached to assets, work orders, and inspections")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 All Documents",
        "📦 Asset Documents",
        "🔧 Work Order Documents",
        "🔍 Inspection Documents"
    ])
    
    with tab1:
        show_all_documents(session)
    
    with tab2:
        show_asset_documents(session)
    
    with tab3:
        show_work_order_documents(session)
    
    with tab4:
        show_inspection_documents(session)


def show_all_documents(session):
    """Display all documents from all sources"""
    st.subheader("All Documents")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filter_type = st.selectbox(
            "Filter by Source",
            ["All", "Assets", "Work Orders", "Inspections"]
        )
    
    with col2:
        filter_doc_type = st.selectbox(
            "Filter by Document Type",
            ["All", "Photo", "Plan", "Manual", "Drawing", "Specification", 
             "Report", "Certificate", "Warranty", "Invoice", "Other"]
        )
    
    with col3:
        filter_format = st.selectbox(
            "Filter by Format",
            ["All", "PDF", "DOCX", "XLSX", "JPG", "PNG", "DWG", "Other"]
        )
    
    with col4:
        search_term = st.text_input("Search", placeholder="Search by title or file name")
    
    # Get all active documents
    query = session.query(Document).filter(Document.is_active == True)
    
    # Apply filters
    if filter_type != "All":
        type_map = {
            "Assets": "asset",
            "Work Orders": "work_order",
            "Inspections": "inspection"
        }
        query = query.filter(Document.linked_type == type_map[filter_type])
    
    if filter_doc_type != "All":
        query = query.filter(Document.document_type == filter_doc_type)
    
    if filter_format != "All":
        query = query.filter(Document.file_format == filter_format)
    
    if search_term:
        search_filter = f"%{search_term}%"
        query = query.filter(
            (Document.title.like(search_filter)) |
            (Document.file_name.like(search_filter))
        )
    
    documents = query.order_by(Document.upload_date.desc()).all()
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_docs = len(documents)
        st.metric("Total Documents", total_docs)
    
    with col2:
        asset_docs = len([d for d in documents if d.linked_type == 'asset'])
        st.metric("Asset Documents", asset_docs)
    
    with col3:
        wo_docs = len([d for d in documents if d.linked_type == 'work_order'])
        st.metric("Work Order Documents", wo_docs)
    
    with col4:
        insp_docs = len([d for d in documents if d.linked_type == 'inspection'])
        st.metric("Inspection Documents", insp_docs)
    
    st.divider()
    
    # Display documents
    if documents:
        doc_data = []
        for doc in documents:
            # Get linked entity name
            linked_name = "N/A"
            if doc.linked_type == 'asset':
                asset = session.query(Asset).filter(Asset.id == doc.linked_id).first()
                linked_name = f"{asset.asset_id} - {asset.name}" if asset else "N/A"
            elif doc.linked_type == 'work_order':
                wo = session.query(WorkOrder).filter(WorkOrder.id == doc.linked_id).first()
                linked_name = f"{wo.work_order_number} - {wo.title}" if wo else "N/A"
            elif doc.linked_type == 'inspection':
                insp = session.query(Inspection).filter(Inspection.id == doc.linked_id).first()
                linked_name = f"{insp.inspection_number}" if insp else "N/A"
            
            doc_data.append({
                "ID": doc.id,
                "Source": doc.linked_type.replace('_', ' ').title(),
                "Linked To": linked_name,
                "Type": doc.document_type,
                "Title": doc.title,
                "Format": doc.file_format or "N/A",
                "Size": doc.file_size or "N/A",
                "Uploaded": format_date(doc.upload_date),
                "By": doc.uploaded_by or "N/A"
            })
        
        df = pd.DataFrame(doc_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Quick actions
        st.write("### Quick Actions")
        selected_doc_id = st.selectbox(
            "Select Document for Details",
            options=[f"{doc.id} - {doc.title}" for doc in documents]
        )
        
        if selected_doc_id:
            doc_id = int(selected_doc_id.split(" - ")[0])
            show_document_details(session, doc_id, context="all")
    else:
        st.info("No documents found matching the filters.")


def show_asset_documents(session):
    """Display documents linked to assets"""
    st.subheader("Asset Documents")
    
    # Get all assets with documents
    documents = session.query(Document).filter(
        Document.linked_type == 'asset',
        Document.is_active == True
    ).order_by(Document.upload_date.desc()).all()
    
    if documents:
        # Group by asset
        asset_groups = {}
        for doc in documents:
            asset = session.query(Asset).filter(Asset.id == doc.linked_id).first()
            if asset:
                asset_key = f"{asset.asset_id} - {asset.name}"
                if asset_key not in asset_groups:
                    asset_groups[asset_key] = []
                asset_groups[asset_key].append(doc)
        
        # Display by asset
        for asset_key, docs in asset_groups.items():
            with st.expander(f"📦 {asset_key} ({len(docs)} documents)", expanded=False):
                for doc in docs:
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    with col1:
                        st.write(f"**{doc.title}**")
                    with col2:
                        st.write(f"Type: {doc.document_type}")
                    with col3:
                        st.write(f"Format: {doc.file_format or 'N/A'}")
                    with col4:
                        if st.button(f"View", key=f"asset_doc_{doc.id}"):
                            st.session_state['view_doc_id'] = doc.id
                            st.rerun()
                st.write(f"**Path**: `{docs[0].file_path if docs else 'N/A'}`")
    else:
        st.info("No documents attached to assets yet.")
    
    # Show document details if selected
    if 'view_doc_id' in st.session_state:
        show_document_details(session, st.session_state['view_doc_id'], context="asset")
        if st.button("← Back to List", key="back_asset_docs"):
            del st.session_state['view_doc_id']
            st.rerun()


def show_work_order_documents(session):
    """Display documents linked to work orders"""
    st.subheader("Work Order Documents")
    
    # Get all work orders with documents
    documents = session.query(Document).filter(
        Document.linked_type == 'work_order',
        Document.is_active == True
    ).order_by(Document.upload_date.desc()).all()
    
    if documents:
        # Group by work order
        wo_groups = {}
        for doc in documents:
            wo = session.query(WorkOrder).filter(WorkOrder.id == doc.linked_id).first()
            if wo:
                wo_key = f"{wo.work_order_number} - {wo.title}"
                if wo_key not in wo_groups:
                    wo_groups[wo_key] = []
                wo_groups[wo_key].append(doc)
        
        # Display by work order
        for wo_key, docs in wo_groups.items():
            with st.expander(f"🔧 {wo_key} ({len(docs)} documents)", expanded=False):
                for doc in docs:
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    with col1:
                        st.write(f"**{doc.title}**")
                    with col2:
                        st.write(f"Type: {doc.document_type}")
                    with col3:
                        st.write(f"Format: {doc.file_format or 'N/A'}")
                    with col4:
                        if st.button(f"View", key=f"wo_doc_{doc.id}"):
                            st.session_state['view_doc_id'] = doc.id
                            st.rerun()
                st.write(f"**Path**: `{docs[0].file_path if docs else 'N/A'}`")
    else:
        st.info("No documents attached to work orders yet.")
    
    # Show document details if selected
    if 'view_doc_id' in st.session_state:
        show_document_details(session, st.session_state['view_doc_id'], context="wo")
        if st.button("← Back to List", key="back_wo_docs"):
            del st.session_state['view_doc_id']
            st.rerun()


def show_inspection_documents(session):
    """Display documents linked to inspections"""
    st.subheader("Inspection Documents")
    
    # Get all inspections with documents
    documents = session.query(Document).filter(
        Document.linked_type == 'inspection',
        Document.is_active == True
    ).order_by(Document.upload_date.desc()).all()
    
    if documents:
        # Group by inspection
        insp_groups = {}
        for doc in documents:
            insp = session.query(Inspection).filter(Inspection.id == doc.linked_id).first()
            if insp:
                insp_key = f"{insp.inspection_number} - {insp.inspection_type}"
                if insp_key not in insp_groups:
                    insp_groups[insp_key] = []
                insp_groups[insp_key].append(doc)
        
        # Display by inspection
        for insp_key, docs in insp_groups.items():
            with st.expander(f"🔍 {insp_key} ({len(docs)} documents)", expanded=False):
                for doc in docs:
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                    with col1:
                        st.write(f"**{doc.title}**")
                    with col2:
                        st.write(f"Type: {doc.document_type}")
                    with col3:
                        st.write(f"Format: {doc.file_format or 'N/A'}")
                    with col4:
                        if st.button(f"View", key=f"insp_doc_{doc.id}"):
                            st.session_state['view_doc_id'] = doc.id
                            st.rerun()
                st.write(f"**Path**: `{docs[0].file_path if docs else 'N/A'}`")
    else:
        st.info("No documents attached to inspections yet.")
    
    # Show document details if selected
    if 'view_doc_id' in st.session_state:
        show_document_details(session, st.session_state['view_doc_id'], context="insp")
        if st.button("← Back to List", key="back_insp_docs"):
            del st.session_state['view_doc_id']
            st.rerun()


def show_document_details(session, document_id, context="viewer"):
    """Display detailed information about a document
    
    Args:
        session: Database session
        document_id: ID of document to display
        context: Unique context string to prevent duplicate keys (e.g., 'all', 'asset', 'wo', 'insp')
    """
    doc = session.query(Document).filter(Document.id == document_id).first()
    
    if not doc:
        st.error("Document not found!")
        return
    
    st.divider()
    st.write("### 📄 Document Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Document Information**")
        st.write(f"**ID:** {doc.id}")
        st.write(f"**Type:** {doc.document_type}")
        st.write(f"**Title:** {doc.title}")
        st.write(f"**Description:** {doc.description or 'N/A'}")
        st.write(f"**Format:** {doc.file_format or 'N/A'}")
        st.write(f"**Size:** {doc.file_size or 'N/A'}")
        st.write(f"**Version:** {doc.version or 'N/A'}")
    
    with col2:
        st.write("**Linked To**")
        
        # Get linked entity details
        if doc.linked_type == 'asset':
            asset = session.query(Asset).filter(Asset.id == doc.linked_id).first()
            if asset:
                st.write(f"**Source:** Asset")
                st.write(f"**Asset ID:** {asset.asset_id}")
                st.write(f"**Asset Name:** {asset.name}")
        elif doc.linked_type == 'work_order':
            wo = session.query(WorkOrder).filter(WorkOrder.id == doc.linked_id).first()
            if wo:
                st.write(f"**Source:** Work Order")
                st.write(f"**WO Number:** {wo.work_order_number}")
                st.write(f"**Title:** {wo.title}")
        elif doc.linked_type == 'inspection':
            insp = session.query(Inspection).filter(Inspection.id == doc.linked_id).first()
            if insp:
                st.write(f"**Source:** Inspection")
                st.write(f"**Inspection #:** {insp.inspection_number}")
                st.write(f"**Type:** {insp.inspection_type}")
        
        st.write(f"**Uploaded By:** {doc.uploaded_by or 'N/A'}")
        st.write(f"**Upload Date:** {format_datetime(doc.upload_date)}")
        st.write(f"**Last Modified:** {format_datetime(doc.last_modified)}")
    
    # File location
    st.write("### 📂 File Location")
    st.code(doc.file_path, language=None)
    
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Copy the path above and paste it into your file explorer or browser")
    with col2:
        if st.button("📋 Copy Path to Clipboard", key=f"copy_path_{context}_{doc.id}"):
            st.info("Path displayed above - use Ctrl+C to copy")
    
    # Notes
    if doc.notes:
        st.write("### 📝 Notes")
        st.info(doc.notes)

