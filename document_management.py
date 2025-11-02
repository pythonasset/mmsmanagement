"""
Document Management Module
Handles attachments for assets, work orders, and inspections
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import os
from database import Document
from settings import FILE_FORMATS
from utils import format_date, format_datetime

# Document type options
DOCUMENT_TYPES = [
    "Photo",
    "Plan",
    "Manual",
    "Drawing",
    "Specification",
    "Report",
    "Certificate",
    "Warranty",
    "Invoice",
    "Other"
]

def show_documents(session, linked_type, linked_id, entity_name="Record"):
    """Display documents attached to a record"""
    st.markdown(f"### 📎 Attached Documents")
    
    # Get all active documents for this record
    documents = session.query(Document).filter(
        Document.linked_type == linked_type,
        Document.linked_id == linked_id,
        Document.is_active == True
    ).order_by(Document.upload_date.desc()).all()
    
    if documents:
        # Display documents in a table
        doc_data = []
        for doc in documents:
            doc_data.append({
                "ID": doc.id,
                "Type": doc.document_type,
                "Title": doc.title,
                "File Name": doc.file_name or "N/A",
                "Format": doc.file_format or "N/A",
                "Size": doc.file_size or "N/A",
                "Uploaded": format_date(doc.upload_date),
                "By": doc.uploaded_by or "N/A"
            })
        
        df = pd.DataFrame(doc_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Document actions
        st.write("### Document Actions")
        
        # Document selection
        selected_doc_id = st.selectbox(
            "Select Document",
            options=[f"{doc.id} - {doc.title}" for doc in documents],
            key=f"doc_select_{linked_type}_{linked_id}"
        )
        
        if selected_doc_id:
            doc_id = int(selected_doc_id.split(" - ")[0])
            doc = session.query(Document).filter(Document.id == doc_id).first()
            
            if doc:
                # Action buttons in a row
                col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
                
                with col1:
                    # View document button
                    if st.button("👁️ View Document", key=f"view_doc_{doc_id}", use_container_width=True):
                        st.session_state[f'view_doc_{linked_type}_{linked_id}'] = doc_id
                
                with col2:
                    # Edit button
                    if st.button("✏️ Edit Document", key=f"edit_doc_{doc_id}", use_container_width=True):
                        st.session_state[f'edit_doc_{linked_type}_{linked_id}'] = doc_id
                        st.rerun()
                
                with col3:
                    # Delete document button
                    if st.button("🗑️ Delete", type="secondary", key=f"del_doc_btn_{doc_id}", use_container_width=True):
                        st.session_state[f'confirm_delete_{linked_type}_{linked_id}_{doc_id}'] = True
                
                # Show delete confirmation if delete button was clicked
                if st.session_state.get(f'confirm_delete_{linked_type}_{linked_id}_{doc_id}', False):
                    st.warning(f"⚠️ Are you sure you want to delete '{doc.title}'?")
                    confirm_col1, confirm_col2, confirm_col3 = st.columns([1, 1, 3])
                    with confirm_col1:
                        if st.button("✅ Yes, Delete", key=f"confirm_yes_{doc_id}", type="primary"):
                            doc.is_active = False  # Soft delete
                            session.commit()
                            st.success("Document deleted successfully!")
                            del st.session_state[f'confirm_delete_{linked_type}_{linked_id}_{doc_id}']
                            st.rerun()
                    with confirm_col2:
                        if st.button("❌ Cancel", key=f"confirm_no_{doc_id}"):
                            del st.session_state[f'confirm_delete_{linked_type}_{linked_id}_{doc_id}']
                            st.rerun()
                
                # Show document details if view button was clicked
                if st.session_state.get(f'view_doc_{linked_type}_{linked_id}', None) == doc_id:
                    st.divider()
                    st.write("### 📄 Document Details")
                    
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        st.write(f"**Type:** {doc.document_type}")
                        st.write(f"**Title:** {doc.title}")
                        st.write(f"**Description:** {doc.description or 'N/A'}")
                        st.write(f"**File Name:** {doc.file_name or 'N/A'}")
                        st.write(f"**Format:** {doc.file_format or 'N/A'}")
                        st.write(f"**Size:** {doc.file_size or 'N/A'}")
                    
                    with detail_col2:
                        st.write(f"**Version:** {doc.version or 'N/A'}")
                        st.write(f"**Uploaded By:** {doc.uploaded_by or 'N/A'}")
                        st.write(f"**Upload Date:** {format_datetime(doc.upload_date)}")
                        st.write(f"**Last Modified:** {format_datetime(doc.last_modified)}")
                        st.write(f"**Status:** {'Active' if doc.is_active else 'Inactive'}")
                    
                    st.write(f"**File Path:** `{doc.file_path}`")
                    st.write(f"**Notes:** {doc.notes or 'N/A'}")
                    
                    # File action buttons
                    file_col1, file_col2, file_col3 = st.columns([1, 1, 2])
                    with file_col1:
                        if st.button("📂 Copy Path", key=f"copy_path_{doc_id}"):
                            st.code(doc.file_path, language=None)
                            st.caption("Path displayed above - copy it to access the file")
                    
                    with file_col2:
                        if st.button("🔙 Close Details", key=f"close_view_{doc_id}"):
                            del st.session_state[f'view_doc_{linked_type}_{linked_id}']
                            st.rerun()
    else:
        st.info(f"No documents attached to this {entity_name.lower()} yet.")
    
    st.divider()
    
    # Check if we're editing a document
    if f'edit_doc_{linked_type}_{linked_id}' in st.session_state:
        edit_doc_id = st.session_state[f'edit_doc_{linked_type}_{linked_id}']
        edit_document_form(session, edit_doc_id, linked_type, linked_id)
    else:
        # Add new document button
        if st.button(f"➕ Add New Document to {entity_name}", key=f"add_doc_btn_{linked_type}_{linked_id}"):
            st.session_state[f'add_doc_{linked_type}_{linked_id}'] = True
            st.rerun()
        
        # Show add form if button was clicked
        if st.session_state.get(f'add_doc_{linked_type}_{linked_id}', False):
            add_document_form(session, linked_type, linked_id, entity_name)


def add_document_form(session, linked_type, linked_id, entity_name="Record"):
    """Form to add a new document with drag-and-drop file upload"""
    st.write(f"### ➕ Add New Document to {entity_name}")
    
    # File uploader (outside form for immediate feedback)
    st.write("#### 📎 Upload File (Drag & Drop or Browse)")
    uploaded_file = st.file_uploader(
        "Drag and drop a file here or click to browse",
        type=None,  # Accept all file types
        key=f"file_upload_{linked_type}_{linked_id}",
        help="Upload a file to automatically populate metadata fields"
    )
    
    # Extract metadata if file is uploaded
    auto_file_name = ""
    auto_file_size = ""
    auto_file_format = "Other"
    auto_title = ""
    
    if uploaded_file is not None:
        # Get file metadata
        auto_file_name = uploaded_file.name
        auto_title = os.path.splitext(uploaded_file.name)[0]  # Filename without extension
        
        # Get file size
        file_size_bytes = uploaded_file.size
        if file_size_bytes < 1024:
            auto_file_size = f"{file_size_bytes} B"
        elif file_size_bytes < 1024 * 1024:
            auto_file_size = f"{file_size_bytes / 1024:.2f} KB"
        elif file_size_bytes < 1024 * 1024 * 1024:
            auto_file_size = f"{file_size_bytes / (1024 * 1024):.2f} MB"
        else:
            auto_file_size = f"{file_size_bytes / (1024 * 1024 * 1024):.2f} GB"
        
        # Get file format
        file_ext = os.path.splitext(uploaded_file.name)[1].upper().replace('.', '')
        if file_ext in FILE_FORMATS:
            auto_file_format = file_ext
        
        st.success(f"✅ File '{uploaded_file.name}' uploaded! Metadata extracted below.")
        st.info("💡 Please specify where to save the file and complete the remaining fields.")
    
    with st.form(f"add_document_form_{linked_type}_{linked_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            document_type = st.selectbox("Document Type*", DOCUMENT_TYPES)
            title = st.text_input(
                "Document Title*", 
                value=auto_title,
                max_chars=200,
                help="Auto-populated from uploaded filename"
            )
            description = st.text_area("Description")
            
            # File format pre-selected if detected
            format_index = 0
            if auto_file_format in FILE_FORMATS:
                format_index = FILE_FORMATS.index(auto_file_format)
            file_format = st.selectbox("File Format*", FILE_FORMATS, index=format_index)
        
        with col2:
            # File path field
            if uploaded_file:
                st.write("**Save Location**")
                save_location = st.text_input(
                    "Directory Path*",
                    placeholder="C:\\Documents\\MyFolder or \\\\server\\share\\folder",
                    help="Specify where to save the uploaded file",
                    max_chars=500
                )
                
                # Construct full path
                if save_location:
                    full_path = os.path.join(save_location, auto_file_name)
                    st.caption(f"Full path: `{full_path}`")
                    file_path = full_path
                else:
                    file_path = ""
            else:
                file_path = st.text_input(
                    "File Path*",
                    help="Enter full path: C:\\Documents\\file.pdf or \\\\server\\share\\file.pdf or URL",
                    max_chars=500
                )
            
            file_name = st.text_input(
                "File Name", 
                value=auto_file_name,
                max_chars=200,
                help="Auto-populated from upload"
            )
            file_size = st.text_input(
                "File Size",
                value=auto_file_size,
                max_chars=50,
                help="Auto-calculated from upload"
            )
            version = st.text_input("Version (optional)", max_chars=20)
        
        notes = st.text_area("Notes")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Add Document", type="primary")
        with col2:
            cancel = st.form_submit_button("❌ Cancel")
        
        if cancel:
            st.session_state[f'add_doc_{linked_type}_{linked_id}'] = False
            st.rerun()
        
        if submitted:
            if not title:
                st.error("Title is required")
            elif uploaded_file and not save_location:
                st.error("Please specify a directory path where to save the uploaded file")
            elif not uploaded_file and not file_path:
                st.error("Either upload a file or enter a file path")
            else:
                # Save uploaded file if present
                if uploaded_file and save_location:
                    try:
                        # Create directory if it doesn't exist
                        os.makedirs(save_location, exist_ok=True)
                        
                        # Save file
                        full_save_path = os.path.join(save_location, auto_file_name)
                        with open(full_save_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        st.success(f"✅ File saved to: {full_save_path}")
                        file_path = full_save_path
                    except Exception as e:
                        st.error(f"Error saving file: {str(e)}")
                        st.warning("Document record will be created, but file was not saved. Please save manually.")
                
                # Create new document
                new_doc = Document(
                    linked_type=linked_type,
                    linked_id=linked_id,
                    document_type=document_type,
                    title=title,
                    description=description if description else None,
                    file_path=file_path,
                    file_name=file_name if file_name else None,
                    file_size=file_size if file_size else None,
                    file_format=file_format if file_format else None,
                    version=version if version else None,
                    notes=notes if notes else None,
                    uploaded_by="System",  # Replace with actual user
                    upload_date=datetime.now(),
                    is_active=True
                )
                
                session.add(new_doc)
                session.commit()
                st.success(f"✅ Document '{title}' added successfully!")
                st.session_state[f'add_doc_{linked_type}_{linked_id}'] = False
                st.rerun()


def edit_document_form(session, document_id, linked_type, linked_id):
    """Form to edit an existing document"""
    st.write("### ✏️ Edit Document")
    
    doc = session.query(Document).filter(Document.id == document_id).first()
    
    if not doc:
        st.error("Document not found!")
        if st.button("← Back", key=f"back_edit_doc_{document_id}"):
            del st.session_state[f'edit_doc_{linked_type}_{linked_id}']
            st.rerun()
        return
    
    with st.form(f"edit_document_form_{document_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            document_type = st.selectbox(
                "Document Type*",
                DOCUMENT_TYPES,
                index=DOCUMENT_TYPES.index(doc.document_type) if doc.document_type in DOCUMENT_TYPES else 0
            )
            title = st.text_input("Document Title*", value=doc.title, max_chars=200)
            description = st.text_area("Description", value=doc.description or "")
            
            # File format dropdown with current value
            current_format_index = 0
            if doc.file_format and doc.file_format in FILE_FORMATS:
                current_format_index = FILE_FORMATS.index(doc.file_format)
            file_format = st.selectbox("File Format*", FILE_FORMATS, index=current_format_index)
        
        with col2:
            file_path = st.text_input(
                "File Path*",
                value=doc.file_path,
                help="Enter full path: C:\\Documents\\file.pdf or \\\\server\\share\\file.pdf or URL",
                max_chars=500
            )
            file_name = st.text_input("File Name", value=doc.file_name or "", max_chars=200)
            file_size = st.text_input("File Size", value=doc.file_size or "", max_chars=50)
            version = st.text_input("Version", value=doc.version or "", max_chars=20)
        
        notes = st.text_area("Notes", value=doc.notes or "")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 Save Changes", type="primary")
        with col2:
            cancel = st.form_submit_button("❌ Cancel")
        
        if cancel:
            del st.session_state[f'edit_doc_{linked_type}_{linked_id}']
            st.rerun()
        
        if submitted:
            if not title or not file_path:
                st.error("Title and File Path are required")
            else:
                # Update document
                doc.document_type = document_type
                doc.title = title
                doc.description = description if description else None
                doc.file_path = file_path
                doc.file_name = file_name if file_name else None
                doc.file_size = file_size if file_size else None
                doc.file_format = file_format if file_format else None
                doc.version = version if version else None
                doc.notes = notes if notes else None
                doc.last_modified = datetime.now()
                
                session.commit()
                st.success(f"✅ Document '{title}' updated successfully!")
                del st.session_state[f'edit_doc_{linked_type}_{linked_id}']
                st.rerun()
    
    # Back button outside form
    if st.button("← Back to Documents", key=f"back_edit_doc_btn_{document_id}"):
        del st.session_state[f'edit_doc_{linked_type}_{linked_id}']
        st.rerun()


def get_document_count(session, linked_type, linked_id):
    """Get count of active documents for a record"""
    count = session.query(Document).filter(
        Document.linked_type == linked_type,
        Document.linked_id == linked_id,
        Document.is_active == True
    ).count()
    return count

