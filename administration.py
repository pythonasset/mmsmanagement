"""
Administration Module
Manage system configuration, dropdown values, and users
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
from database import User, AssetClass, AssetGroup, AssetType, DropdownValue
from settings import (
    WORK_ORDER_PRIORITIES, WORK_ORDER_STATUS, WORK_ORDER_TYPES,
    ASSET_STATUS_OPTIONS, INSPECTION_TYPES, CONDITION_RATINGS, USER_ROLES,
    FILE_FORMATS
)

def show_administration(session):
    """Main administration interface"""
    st.header("⚙️ System Administration")
    
    # Create tabs for different admin functions
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 User Management",
        "📋 Dropdown Values",
        "🏗️ Asset Hierarchy",
        "⚙️ System Settings"
    ])
    
    with tab1:
        show_user_management(session)
    
    with tab2:
        show_dropdown_management(session)
    
    with tab3:
        show_asset_hierarchy_management(session)
    
    with tab4:
        show_system_settings(session)


def show_user_management(session):
    """Manage system users"""
    st.subheader("👥 User Management")
    
    # Get dynamic dropdown values
    from dropdown_utils import get_dropdown_values, CATEGORY_USER_ROLE
    user_roles = get_dropdown_values(session, CATEGORY_USER_ROLE)
    
    # User list
    users = session.query(User).order_by(User.full_name).all()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("### Current Users")
        
        if users:
            user_data = []
            for user in users:
                user_data.append({
                    "ID": user.id,
                    "Username": user.username,
                    "Full Name": user.full_name or "N/A",
                    "Email": user.email or "N/A",
                    "Role": user.role or "N/A",
                    "Department": user.department or "N/A",
                    "Active": "✅" if user.is_active else "❌",
                    "Last Login": user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Never"
                })
            
            df = pd.DataFrame(user_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No users in the system. Add your first user below.")
    
    with col2:
        st.write("### Add New User")
        
        with st.form("add_user_form"):
            username = st.text_input("Username*", max_chars=50)
            full_name = st.text_input("Full Name", max_chars=100)
            email = st.text_input("Email", max_chars=100)
            role = st.selectbox("Role", user_roles if user_roles else ["No roles available"])
            department = st.text_input("Department", max_chars=100)
            is_active = st.checkbox("Active", value=True)
            
            submitted = st.form_submit_button("➕ Add User")
            
            if submitted:
                if not username:
                    st.error("Username is required")
                else:
                    # Check if username already exists
                    existing = session.query(User).filter(User.username == username).first()
                    if existing:
                        st.error("Username already exists")
                    else:
                        new_user = User(
                            username=username,
                            full_name=full_name if full_name else None,
                            email=email if email else None,
                            role=role,
                            department=department if department else None,
                            is_active=is_active,
                            created_date=datetime.now()
                        )
                        session.add(new_user)
                        session.commit()
                        st.success(f"✅ User '{username}' added successfully!")
                        st.rerun()
    
    # Edit/Delete user section
    if users:
        st.divider()
        st.write("### Edit/Delete User")
        
        user_select = st.selectbox(
            "Select User",
            options=[f"{u.username} - {u.full_name or 'No Name'}" for u in users],
            key="edit_user_select"
        )
        
        # Find selected user
        selected_username = user_select.split(" - ")[0]
        selected_user = session.query(User).filter(User.username == selected_username).first()
        
        if selected_user:
            col1, col2 = st.columns(2)
            
            with col1:
                with st.form("edit_user_form"):
                    st.write("**Edit User**")
                    new_full_name = st.text_input("Full Name", value=selected_user.full_name or "")
                    new_email = st.text_input("Email", value=selected_user.email or "")
                    new_role = st.selectbox("Role", user_roles if user_roles else ["No roles available"], index=user_roles.index(selected_user.role) if selected_user.role in user_roles else 0)
                    new_department = st.text_input("Department", value=selected_user.department or "")
                    new_is_active = st.checkbox("Active", value=selected_user.is_active)
                    
                    update_submitted = st.form_submit_button("💾 Update User")
                    
                    if update_submitted:
                        selected_user.full_name = new_full_name if new_full_name else None
                        selected_user.email = new_email if new_email else None
                        selected_user.role = new_role
                        selected_user.department = new_department if new_department else None
                        selected_user.is_active = new_is_active
                        
                        session.commit()
                        st.success("✅ User updated successfully!")
                        st.rerun()
            
            with col2:
                st.write("**Delete User**")
                st.warning(f"Delete user: {selected_user.username}?")
                
                if st.button("🗑️ Delete User", type="secondary"):
                    if st.checkbox("Confirm deletion", key="confirm_delete_user"):
                        session.delete(selected_user)
                        session.commit()
                        st.success("User deleted!")
                        st.rerun()


def show_dropdown_management(session):
    """Manage dropdown values with full CRUD operations"""
    st.subheader("📋 Dropdown Value Management")
    
    # Import dropdown utilities
    from dropdown_utils import (
        initialize_dropdown_defaults,
        CATEGORY_WORK_ORDER_TYPE, CATEGORY_WORK_ORDER_PRIORITY, CATEGORY_WORK_ORDER_STATUS,
        CATEGORY_ASSET_STATUS, CATEGORY_CONDITION_RATING, CATEGORY_INSPECTION_TYPE,
        CATEGORY_USER_ROLE, CATEGORY_FILE_FORMAT
    )
    
    # Initialize dropdown values if needed
    initialize_dropdown_defaults(session)
    
    st.info("💡 Manage all dropdown values used throughout the application. Changes take effect immediately.")
    
    # Category selection
    categories = [
        (CATEGORY_WORK_ORDER_TYPE, "🔧 Work Order Types"),
        (CATEGORY_WORK_ORDER_PRIORITY, "⚡ Work Order Priorities"),
        (CATEGORY_WORK_ORDER_STATUS, "📊 Work Order Status"),
        (CATEGORY_ASSET_STATUS, "🏢 Asset Status Options"),
        (CATEGORY_CONDITION_RATING, "⭐ Condition Ratings"),
        (CATEGORY_INSPECTION_TYPE, "🔍 Inspection Types"),
        (CATEGORY_USER_ROLE, "👤 User Roles"),
        (CATEGORY_FILE_FORMAT, "📄 File Formats")
    ]
    
    # Create tabs for each category
    tabs = st.tabs([display_name for _, display_name in categories])
    
    for idx, (category, display_name) in enumerate(categories):
        with tabs[idx]:
            manage_dropdown_category(session, category, display_name)


def manage_dropdown_category(session, category, display_name):
    """Manage a specific dropdown category with Add/Edit/Delete operations"""
    from dropdown_utils import add_dropdown_value, update_dropdown_value, delete_dropdown_value
    from database import DropdownValue
    
    # Get all values for this category
    dropdown_values = session.query(DropdownValue).filter(
        DropdownValue.category == category,
        DropdownValue.is_active == True
    ).order_by(DropdownValue.display_order, DropdownValue.value).all()
    
    st.write(f"### {display_name}")
    st.caption(f"Total values: {len(dropdown_values)}")
    
    # Display current values in a table
    if dropdown_values:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write("#### Current Values")
            for idx, dv in enumerate(dropdown_values):
                value_col, action_col = st.columns([3, 1])
                
                with value_col:
                    if dv.is_default:
                        st.write(f"**{idx + 1}.** {dv.value} `(Default)`")
                    else:
                        st.write(f"**{idx + 1}.** {dv.value}")
                
                with action_col:
                    # Edit and Delete buttons
                    edit_key = f"edit_{category}_{dv.id}"
                    delete_key = f"delete_{category}_{dv.id}"
                    
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("✏️", key=edit_key, help="Edit", use_container_width=True):
                            st.session_state[f'editing_{category}'] = dv.id
                            st.rerun()
                    with btn_col2:
                        if st.button("🗑️", key=delete_key, help="Delete", use_container_width=True, type="secondary"):
                            st.session_state[f'confirm_delete_{category}'] = dv.id
        
        with col2:
            st.write("#### Actions")
            
            # Handle delete confirmation
            if f'confirm_delete_{category}' in st.session_state:
                delete_id = st.session_state[f'confirm_delete_{category}']
                dv_to_delete = session.query(DropdownValue).filter(
                    DropdownValue.id == delete_id
                ).first()
                
                if dv_to_delete:
                    st.warning(f"Delete '{dv_to_delete.value}'?")
                    col_yes, col_no = st.columns(2)
                    with col_yes:
                        if st.button("✅ Yes", key=f"yes_delete_{category}_{delete_id}", use_container_width=True):
                            delete_dropdown_value(session, delete_id)
                            st.success("Deleted!")
                            del st.session_state[f'confirm_delete_{category}']
                            st.rerun()
                    with col_no:
                        if st.button("❌ No", key=f"no_delete_{category}_{delete_id}", use_container_width=True):
                            del st.session_state[f'confirm_delete_{category}']
                            st.rerun()
            
            # Handle edit
            if f'editing_{category}' in st.session_state:
                edit_id = st.session_state[f'editing_{category}']
                dv_to_edit = session.query(DropdownValue).filter(
                    DropdownValue.id == edit_id
                ).first()
                
                if dv_to_edit:
                    st.write("**Edit Value**")
                    new_value = st.text_input(
                        "New Value",
                        value=dv_to_edit.value,
                        key=f"edit_input_{category}_{edit_id}"
                    )
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.button("💾 Save", key=f"save_edit_{category}_{edit_id}", use_container_width=True):
                            if new_value and new_value != dv_to_edit.value:
                                update_dropdown_value(session, edit_id, new_value=new_value)
                                st.success("Updated!")
                                del st.session_state[f'editing_{category}']
                                st.rerun()
                            elif not new_value:
                                st.error("Value cannot be empty")
                            else:
                                del st.session_state[f'editing_{category}']
                                st.rerun()
                    with col_cancel:
                        if st.button("❌ Cancel", key=f"cancel_edit_{category}_{edit_id}", use_container_width=True):
                            del st.session_state[f'editing_{category}']
                            st.rerun()
    else:
        st.info("No values defined for this category yet.")
    
    st.divider()
    
    # Add new value form
    st.write("#### ➕ Add New Value")
    with st.form(f"add_{category}_form"):
        new_value = st.text_input(
            "Value",
            placeholder=f"Enter new {display_name.lower()} value",
            key=f"new_value_{category}"
        )
        
        submitted = st.form_submit_button("Add Value", use_container_width=True)
        
        if submitted:
            if new_value:
                result = add_dropdown_value(session, category, new_value)
                if result:
                    st.success(f"✅ Added '{new_value}' successfully!")
                    st.rerun()
                else:
                    st.error(f"❌ '{new_value}' already exists in this category.")
            else:
                st.error("Please enter a value.")


def manage_file_formats():
    """Manage file format options"""
    import json
    import os
    
    # Path to settings file
    settings_file = "settings.py"
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("**Current File Formats**")
        
        # Display current formats in a nice grid
        if FILE_FORMATS:
            # Create rows of 5 items each
            formats_per_row = 5
            for i in range(0, len(FILE_FORMATS), formats_per_row):
                row_formats = FILE_FORMATS[i:i+formats_per_row]
                cols = st.columns(formats_per_row)
                for idx, fmt in enumerate(row_formats):
                    with cols[idx]:
                        st.button(f"📄 {fmt}", key=f"fmt_{i}_{idx}", disabled=True, use_container_width=True)
        else:
            st.info("No file formats defined.")
    
    with col2:
        st.write("**Add New Format**")
        
        with st.form("add_file_format_form"):
            new_format = st.text_input(
                "Format Extension",
                placeholder="e.g., DOCX, JPG",
                max_chars=20,
                help="Enter file extension without the dot"
            ).upper()
            
            if st.form_submit_button("➕ Add Format"):
                if not new_format:
                    st.error("Please enter a format")
                elif new_format in FILE_FORMATS:
                    st.warning(f"Format '{new_format}' already exists")
                else:
                    st.success(f"✅ To add '{new_format}', please edit the settings.py file and add it to the FILE_FORMATS list.")
                    st.code(f"""
# In settings.py, add to FILE_FORMATS list:
FILE_FORMATS = [
    # ... existing formats ...
    "{new_format}",
]
                    """)
    
    st.divider()
    
    # Delete format section
    st.write("**Remove File Format**")
    st.warning("⚠️ Removing a format won't delete existing documents, but the format won't appear in new document forms.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if FILE_FORMATS:
            format_to_remove = st.selectbox(
                "Select format to remove",
                options=FILE_FORMATS,
                key="remove_format_select"
            )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("🗑️ Remove Format", type="secondary", key="remove_format_btn"):
            if format_to_remove:
                st.info(f"To remove '{format_to_remove}', edit settings.py and remove it from the FILE_FORMATS list.")
    
    st.divider()
    
    # Instructions
    with st.expander("📖 How to Modify File Formats"):
        st.markdown("""
        ### Manual Modification
        
        File formats are stored in the `settings.py` file. To modify them:
        
        1. **Open** `settings.py` in a text editor
        2. **Find** the `FILE_FORMATS` list
        3. **Add, Edit, or Remove** format entries
        4. **Save** the file
        5. **Restart** the application
        
        ### Example FILE_FORMATS List
        
        ```python
        FILE_FORMATS = [
            "PDF",
            "DOCX",
            "JPG",
            "PNG",
            "DWG",
            "Other"
        ]
        ```
        
        ### Tips
        - Use uppercase for consistency (e.g., "PDF" not "pdf")
        - Don't include the dot (e.g., "PDF" not ".pdf")
        - Keep "Other" as the last option for flexibility
        - Restart the app after changes
        """)


def show_asset_hierarchy_management(session):
    """Manage asset classes, groups, and types"""
    st.subheader("🏗️ Asset Hierarchy Management")
    
    tab1, tab2, tab3 = st.tabs(["Asset Classes", "Asset Groups", "Asset Types"])
    
    with tab1:
        manage_asset_classes(session)
    
    with tab2:
        manage_asset_groups(session)
    
    with tab3:
        manage_asset_types(session)


def manage_asset_classes(session):
    """Manage asset classes"""
    st.write("### Asset Classes")
    
    classes = session.query(AssetClass).order_by(AssetClass.name).all()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if classes:
            class_data = []
            for cls in classes:
                class_data.append({
                    "ID": cls.id,
                    "Name": cls.name,
                    "Description": cls.description or "N/A"
                })
            
            df = pd.DataFrame(class_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No asset classes defined.")
    
    with col2:
        st.write("**Add New Class**")
        with st.form("add_asset_class_form"):
            class_name = st.text_input("Class Name*")
            class_desc = st.text_area("Description")
            
            if st.form_submit_button("➕ Add Class"):
                if not class_name:
                    st.error("Class name is required")
                else:
                    new_class = AssetClass(
                        name=class_name,
                        description=class_desc if class_desc else None
                    )
                    session.add(new_class)
                    session.commit()
                    st.success("✅ Asset class added!")
                    st.rerun()
    
    # Edit/Delete section
    if classes:
        st.divider()
        st.write("**Edit/Delete Asset Class**")
        
        selected_class = st.selectbox(
            "Select Class",
            options=[c.name for c in classes],
            key="edit_class_select"
        )
        
        cls = session.query(AssetClass).filter(AssetClass.name == selected_class).first()
        
        if cls:
            col1, col2 = st.columns(2)
            
            with col1:
                with st.form("edit_class_form"):
                    new_name = st.text_input("Name", value=cls.name)
                    new_desc = st.text_area("Description", value=cls.description or "")
                    
                    if st.form_submit_button("💾 Update"):
                        cls.name = new_name
                        cls.description = new_desc if new_desc else None
                        session.commit()
                        st.success("✅ Class updated!")
                        st.rerun()
            
            with col2:
                st.write("**Delete**")
                st.warning(f"Delete: {cls.name}?")
                if st.button("🗑️ Delete", key="delete_class"):
                    if st.checkbox("Confirm", key="confirm_delete_class"):
                        session.delete(cls)
                        session.commit()
                        st.success("Deleted!")
                        st.rerun()


def manage_asset_groups(session):
    """Manage asset groups"""
    st.write("### Asset Groups")
    
    groups = session.query(AssetGroup).order_by(AssetGroup.name).all()
    classes = session.query(AssetClass).order_by(AssetClass.name).all()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if groups:
            group_data = []
            for grp in groups:
                class_name = grp.asset_class.name if grp.asset_class else "N/A"
                group_data.append({
                    "ID": grp.id,
                    "Name": grp.name,
                    "Class": class_name,
                    "Description": grp.description or "N/A"
                })
            
            df = pd.DataFrame(group_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No asset groups defined.")
    
    with col2:
        st.write("**Add New Group**")
        if not classes:
            st.warning("⚠️ Please create an Asset Class first")
        else:
            with st.form("add_asset_group_form"):
                group_name = st.text_input("Group Name*")
                group_class = st.selectbox("Asset Class*", options=[c.name for c in classes])
                group_desc = st.text_area("Description")
                
                if st.form_submit_button("➕ Add Group"):
                    if not group_name:
                        st.error("Group name is required")
                    else:
                        class_obj = session.query(AssetClass).filter(AssetClass.name == group_class).first()
                        new_group = AssetGroup(
                            name=group_name,
                            class_id=class_obj.id,
                            description=group_desc if group_desc else None
                        )
                        session.add(new_group)
                        session.commit()
                        st.success("✅ Asset group added!")
                        st.rerun()
    
    # Edit/Delete section
    if groups:
        st.divider()
        st.write("**Edit/Delete Asset Group**")
        
        selected_group = st.selectbox(
            "Select Group",
            options=[g.name for g in groups],
            key="edit_group_select"
        )
        
        grp = session.query(AssetGroup).filter(AssetGroup.name == selected_group).first()
        
        if grp:
            col1, col2 = st.columns(2)
            
            with col1:
                with st.form("edit_group_form"):
                    new_name = st.text_input("Name", value=grp.name)
                    current_class_name = grp.asset_class.name if grp.asset_class else classes[0].name
                    new_class = st.selectbox(
                        "Asset Class",
                        options=[c.name for c in classes],
                        index=[c.name for c in classes].index(current_class_name) if current_class_name in [c.name for c in classes] else 0
                    )
                    new_desc = st.text_area("Description", value=grp.description or "")
                    
                    if st.form_submit_button("💾 Update"):
                        class_obj = session.query(AssetClass).filter(AssetClass.name == new_class).first()
                        grp.name = new_name
                        grp.class_id = class_obj.id
                        grp.description = new_desc if new_desc else None
                        session.commit()
                        st.success("✅ Group updated!")
                        st.rerun()
            
            with col2:
                st.write("**Delete**")
                st.warning(f"Delete: {grp.name}?")
                if st.button("🗑️ Delete", key="delete_group"):
                    if st.checkbox("Confirm", key="confirm_delete_group"):
                        session.delete(grp)
                        session.commit()
                        st.success("Deleted!")
                        st.rerun()


def manage_asset_types(session):
    """Manage asset types"""
    st.write("### Asset Types")
    
    types = session.query(AssetType).order_by(AssetType.name).all()
    groups = session.query(AssetGroup).order_by(AssetGroup.name).all()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if types:
            type_data = []
            for typ in types:
                group_name = typ.asset_group.name if typ.asset_group else "N/A"
                type_data.append({
                    "ID": typ.id,
                    "Name": typ.name,
                    "Group": group_name,
                    "Description": typ.description or "N/A"
                })
            
            df = pd.DataFrame(type_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No asset types defined.")
    
    with col2:
        st.write("**Add New Type**")
        if not groups:
            st.warning("⚠️ Please create an Asset Group first")
        else:
            with st.form("add_asset_type_form"):
                type_name = st.text_input("Type Name*")
                type_group = st.selectbox("Asset Group*", options=[g.name for g in groups])
                type_desc = st.text_area("Description")
                
                if st.form_submit_button("➕ Add Type"):
                    if not type_name:
                        st.error("Type name is required")
                    else:
                        group_obj = session.query(AssetGroup).filter(AssetGroup.name == type_group).first()
                        new_type = AssetType(
                            name=type_name,
                            group_id=group_obj.id,
                            description=type_desc if type_desc else None
                        )
                        session.add(new_type)
                        session.commit()
                        st.success("✅ Asset type added!")
                        st.rerun()
    
    # Edit/Delete section
    if types:
        st.divider()
        st.write("**Edit/Delete Asset Type**")
        
        selected_type = st.selectbox(
            "Select Type",
            options=[t.name for t in types],
            key="edit_type_select"
        )
        
        typ = session.query(AssetType).filter(AssetType.name == selected_type).first()
        
        if typ:
            col1, col2 = st.columns(2)
            
            with col1:
                with st.form("edit_type_form"):
                    new_name = st.text_input("Name", value=typ.name)
                    current_group_name = typ.asset_group.name if typ.asset_group else groups[0].name
                    new_group = st.selectbox(
                        "Asset Group",
                        options=[g.name for g in groups],
                        index=[g.name for g in groups].index(current_group_name) if current_group_name in [g.name for g in groups] else 0
                    )
                    new_desc = st.text_area("Description", value=typ.description or "")
                    
                    if st.form_submit_button("💾 Update"):
                        group_obj = session.query(AssetGroup).filter(AssetGroup.name == new_group).first()
                        typ.name = new_name
                        typ.group_id = group_obj.id
                        typ.description = new_desc if new_desc else None
                        session.commit()
                        st.success("✅ Type updated!")
                        st.rerun()
            
            with col2:
                st.write("**Delete**")
                st.warning(f"Delete: {typ.name}?")
                if st.button("🗑️ Delete", key="delete_type"):
                    if st.checkbox("Confirm", key="confirm_delete_type"):
                        session.delete(typ)
                        session.commit()
                        st.success("Deleted!")
                        st.rerun()


def show_system_settings(session):
    """System settings and configuration"""
    st.subheader("⚙️ System Settings")
    
    # Load configuration
    from config_loader import get_config
    config = get_config()
    
    st.write("### 📄 Configuration Overview")
    st.caption("Settings loaded from config.ini file")
    
    # Application Information
    with st.expander("🏢 Application Information", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Title:** {config.APP_TITLE}")
            st.write(f"**Version:** {config.VERSION}")
            st.write(f"**Environment:** {config.ENVIRONMENT}")
        with col2:
            st.write(f"**Icon:** {config.APP_ICON}")
            st.write(f"**Database:** {config.DATABASE_PATH}")
    
    # Organization Information
    with st.expander("🏛️ Organization Information"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Company:** {config.COMPANY_NAME}")
            st.write(f"**Registered To:** {config.REGISTERED_TO}")
        with col2:
            st.write(f"**Department:** {config.DEPARTMENT}")
            st.write(f"**ABN:** {config.ABN}")
    
    # Developer Information
    with st.expander("🔧 Developer Information"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Produced By:** {config.PRODUCED_BY}")
            st.write(f"**Contact:** {config.DEVELOPER_CONTACT}")
        with col2:
            st.write(f"**Website:** {config.DEVELOPER_WEBSITE}")
            st.write(f"**Support Phone:** {config.SUPPORT_PHONE}")
    
    # Support Information
    with st.expander("📞 Support Information"):
        st.write(f"**Email:** {config.SUPPORT_EMAIL}")
        st.write(f"**Hours:** {config.SUPPORT_HOURS}")
        st.write(f"**Emergency:** {config.EMERGENCY_CONTACT}")
    
    # Document Paths
    with st.expander("📁 Document Storage Paths"):
        st.write(f"**Root:** {config.DOCUMENT_ROOT}")
        st.write(f"**Assets:** {config.ASSET_DOCUMENTS}")
        st.write(f"**Work Orders:** {config.WORKORDER_DOCUMENTS}")
        st.write(f"**Inspections:** {config.INSPECTION_DOCUMENTS}")
    
    # Feature Flags
    with st.expander("🎛️ Feature Flags"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Google Earth:** {'✅ Enabled' if config.ENABLE_GOOGLE_EARTH else '❌ Disabled'}")
            st.write(f"**Documents:** {'✅ Enabled' if config.ENABLE_DOCUMENT_MANAGEMENT else '❌ Disabled'}")
        with col2:
            st.write(f"**User Management:** {'✅ Enabled' if config.ENABLE_USER_MANAGEMENT else '❌ Disabled'}")
            st.write(f"**Reports:** {'✅ Enabled' if config.ENABLE_REPORTS else '❌ Disabled'}")
    
    st.divider()
    
    st.info("""
    **📝 Configuration Files:**
    - `config.ini` - Main application configuration (editable)
    - `settings.py` - Application settings and dropdown defaults
    - `database.py` - Database models and structure
    - `requirements.txt` - Python package dependencies
    
    **To modify settings:** Edit the `config.ini` file and restart the application.
    """)
    
    # Display locale information
    st.write("### 🌍 Regional Settings (Date & Time Format)")
    from utils import get_locale_info
    from datetime import datetime
    locale_info = get_locale_info()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**System Locale:** `{locale_info['locale']}`")
    with col2:
        st.write(f"**Date Format:** {locale_info['date_format']}")
    with col3:
        st.write(f"**Today's Date:** {locale_info['sample']}")
    
    st.divider()
    
    # Date formatting examples
    st.write("**📅 Date Display Examples:**")
    example_date = datetime(2025, 11, 1, 14, 30, 0)
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Date Only:**")
        from utils import format_date
        st.code(format_date(example_date), language=None)
    with col2:
        st.write("**Date & Time:**")
        from utils import format_datetime
        st.code(format_datetime(example_date), language=None)
    
    st.info("""
    **ℹ️ How Date Formatting Works:**
    
    - **Display Dates:** All dates shown in tables, reports, and details use your system's regional format
    - **Detected Format:** The application automatically detects your Windows regional settings
    - **Australian Format:** DD/MM/YYYY (e.g., 31/12/2025)
    - **US Format:** MM/DD/YYYY (e.g., 12/31/2025)
    - **Date Pickers:** Filter controls (From/To dates) use your browser's locale format
    - **Report Filters:** Selected date ranges are displayed in your locale format for confirmation
    - **Exports:** CSV exports include dates in your format for consistency
    
    **To change your date format:** Update your computer's regional settings in Windows Control Panel → Region.
    The application will detect the change when you restart it.
    """)
    
    st.divider()
    
    st.write("### Database Statistics")
    
    from database import Asset, WorkOrder, Inspection
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_users = session.query(User).count()
        st.metric("Total Users", total_users)
    
    with col2:
        total_assets = session.query(Asset).count()
        st.metric("Total Assets", total_assets)
    
    with col3:
        total_work_orders = session.query(WorkOrder).count()
        st.metric("Total Work Orders", total_work_orders)
    
    with col4:
        total_inspections = session.query(Inspection).count()
        st.metric("Total Inspections", total_inspections)
    
    st.divider()
    
    # Show backup management interface
    show_backup_management(session)


def show_backup_management(session):
    """Backup and restore management interface"""
    st.write("### 💾 Backup & Restore")
    
    from backup_manager import BackupManager
    from config_loader import get_config
    
    config = get_config()
    backup_mgr = BackupManager(config)
    
    # Show backup statistics
    stats = backup_mgr.get_backup_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Backups", stats['total_backups'])
    
    with col2:
        st.metric("Total Size", stats['total_size'])
    
    with col3:
        if stats['newest_backup']:
            from utils import format_datetime
            st.metric("Latest Backup", format_datetime(stats['newest_backup']))
        else:
            st.metric("Latest Backup", "None")
    
    with col4:
        st.metric("Backup Location", config.BACKUP_PATH)
    
    st.divider()
    
    # Create tabs for backup operations
    tab1, tab2, tab3 = st.tabs(["📥 Create Backup", "📤 Restore Backup", "🗂️ Manage Backups"])
    
    with tab1:
        show_create_backup_tab(backup_mgr)
    
    with tab2:
        show_restore_backup_tab(backup_mgr)
    
    with tab3:
        show_manage_backups_tab(backup_mgr)


def show_create_backup_tab(backup_mgr):
    """Create backup tab interface"""
    st.write("### Create New Backup")
    
    st.info("💡 Create a backup of your database and optionally include documents and configuration.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("#### Backup Options")
        
        backup_type = st.radio(
            "Backup Type",
            ["Full Backup (Database + Documents)", "Database Only"],
            help="Full backup includes all data. Database only is faster and smaller."
        )
        
        include_config = st.checkbox(
            "Include Configuration File",
            value=False,
            help="Include config.ini in the backup"
        )
        
        backup_name = st.text_input(
            "Backup Name (optional)",
            placeholder="e.g., before_update, monthly_backup",
            help="Add a custom name to identify this backup"
        )
        
        st.divider()
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("💾 Create Full Backup", type="primary", use_container_width=True):
                with st.spinner("Creating backup..."):
                    if backup_type == "Database Only":
                        success, path, message = backup_mgr.create_database_only_backup()
                    else:
                        success, path, message = backup_mgr.create_backup(
                            include_documents=True,
                            include_config=include_config,
                            backup_name=backup_name if backup_name else None
                        )
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        
                        # Offer download
                        if path and Path(path).exists():
                            with open(path, 'rb') as f:
                                st.download_button(
                                    label="📥 Download Backup",
                                    data=f,
                                    file_name=Path(path).name,
                                    mime="application/zip" if Path(path).suffix == '.zip' else "application/octet-stream",
                                    use_container_width=True
                                )
                    else:
                        st.error(f"❌ {message}")
        
        with col_btn2:
            if st.button("🗄️ Quick Database Backup", use_container_width=True):
                with st.spinner("Creating database backup..."):
                    success, path, message = backup_mgr.create_database_only_backup()
                    
                    if success:
                        st.success(f"✅ {message}")
                        if path and Path(path).exists():
                            with open(path, 'rb') as f:
                                st.download_button(
                                    label="📥 Download",
                                    data=f,
                                    file_name=Path(path).name,
                                    mime="application/octet-stream",
                                    use_container_width=True
                                )
                    else:
                        st.error(f"❌ {message}")
    
    with col2:
        st.write("#### Backup Information")
        
        st.info("""
        **Full Backup Includes:**
        - ✅ Complete database
        - ✅ All documents
        - ✅ Document attachments
        - 📋 Configuration (optional)
        
        **Database Only:**
        - ✅ Database file only
        - ⚡ Fast and small
        - 💾 Good for daily backups
        """)
        
        st.warning("""
        **⚠️ Important:**
        - Store backups in a safe location
        - Test restore periodically
        - Keep multiple backup versions
        """)


def show_restore_backup_tab(backup_mgr):
    """Restore backup tab interface"""
    st.write("### Restore from Backup")
    
    backups = backup_mgr.list_backups()
    
    if not backups:
        st.warning("⚠️ No backups available. Create a backup first.")
        return
    
    st.warning("""
    **⚠️ WARNING: Restoring a backup will replace current data!**
    
    - Current database will be backed up before restore
    - A safety backup will be created automatically
    - This action cannot be undone (except by restoring the safety backup)
    """)
    
    st.divider()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("#### Select Backup to Restore")
        
        # Create backup selection list with details
        backup_options = []
        for backup in backups:
            from utils import format_datetime
            option = f"{backup['filename']} - {backup['type']} - {backup['size']} - {format_datetime(backup['created'])}"
            backup_options.append(option)
        
        selected_backup = st.selectbox(
            "Available Backups",
            options=backup_options,
            help="Select a backup to restore"
        )
        
        # Get the selected backup details
        selected_index = backup_options.index(selected_backup)
        backup_to_restore = backups[selected_index]
        
        # Show backup details
        st.write("**Selected Backup Details:**")
        col_a, col_b = st.columns(2)
        with col_a:
            st.write(f"**File:** {backup_to_restore['filename']}")
            st.write(f"**Type:** {backup_to_restore['type']}")
        with col_b:
            st.write(f"**Size:** {backup_to_restore['size']}")
            from utils import format_datetime
            st.write(f"**Created:** {format_datetime(backup_to_restore['created'])}")
        
        st.divider()
        
        # Restore options (only for full backups)
        if backup_to_restore['type'] == 'Full Backup':
            st.write("**Restore Options:**")
            restore_documents = st.checkbox("Restore Documents", value=True)
            restore_config = st.checkbox("Restore Configuration", value=False)
        else:
            restore_documents = False
            restore_config = False
            st.info("Database-only backup will restore database file only.")
        
        st.divider()
        
        # Confirmation and restore
        st.write("**⚠️ Confirm Restore Operation**")
        confirm_restore = st.checkbox(
            "I understand that this will replace my current data",
            key="confirm_restore_checkbox"
        )
        
        if st.button("🔄 Restore Backup", type="primary", disabled=not confirm_restore, use_container_width=True):
            with st.spinner("Restoring backup... Please wait..."):
                success, message = backup_mgr.restore_backup(
                    backup_to_restore['path'],
                    restore_documents=restore_documents,
                    restore_config=restore_config
                )
                
                if success:
                    st.success(f"✅ {message}")
                    st.info("🔄 Please refresh the page to see the restored data.")
                    if st.button("🔄 Refresh Page Now"):
                        st.rerun()
                else:
                    st.error(f"❌ {message}")
    
    with col2:
        st.write("#### Restore Tips")
        
        st.info("""
        **Before Restoring:**
        1. Create a current backup
        2. Close all other sessions
        3. Ensure no one else is using the system
        
        **After Restoring:**
        1. Verify data integrity
        2. Check recent records
        3. Test key functions
        4. Inform other users
        """)


def show_manage_backups_tab(backup_mgr):
    """Manage existing backups tab interface"""
    st.write("### Manage Existing Backups")
    
    backups = backup_mgr.list_backups()
    
    if not backups:
        st.info("📂 No backups available yet. Create your first backup!")
        return
    
    st.write(f"**Total Backups:** {len(backups)}")
    
    st.divider()
    
    # Display backups in a table
    st.write("#### Backup Files")
    
    import pandas as pd
    from utils import format_datetime
    
    backup_data = []
    for backup in backups:
        backup_data.append({
            "Filename": backup['filename'],
            "Type": backup['type'],
            "Size": backup['size'],
            "Created": format_datetime(backup['created']),
            "Path": backup['path']
        })
    
    df = pd.DataFrame(backup_data)
    st.dataframe(df[['Filename', 'Type', 'Size', 'Created']], use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Backup operations
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("#### Backup Operations")
        
        # Select backup for operations
        backup_filenames = [b['filename'] for b in backups]
        selected_backup_name = st.selectbox(
            "Select Backup",
            options=backup_filenames,
            key="manage_backup_select"
        )
        
        # Find selected backup
        selected_backup = next((b for b in backups if b['filename'] == selected_backup_name), None)
        
        if selected_backup:
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                # Download backup
                if st.button("📥 Download", use_container_width=True):
                    backup_path = Path(selected_backup['path'])
                    if backup_path.exists():
                        with open(backup_path, 'rb') as f:
                            st.download_button(
                                label=f"📥 Download {selected_backup['filename']}",
                                data=f,
                                file_name=selected_backup['filename'],
                                mime="application/zip" if backup_path.suffix == '.zip' else "application/octet-stream",
                                key=f"download_{selected_backup['filename']}"
                            )
                    else:
                        st.error("Backup file not found")
            
            with col_b:
                # Delete backup
                if st.button("🗑️ Delete", type="secondary", use_container_width=True):
                    st.session_state['confirm_delete_backup'] = selected_backup['path']
            
            with col_c:
                # View info
                if st.button("ℹ️ Details", use_container_width=True):
                    st.session_state['show_backup_details'] = selected_backup['path']
            
            # Handle delete confirmation
            if 'confirm_delete_backup' in st.session_state and st.session_state['confirm_delete_backup'] == selected_backup['path']:
                st.warning(f"⚠️ Delete backup: {selected_backup['filename']}?")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("✅ Yes, Delete", key="yes_delete_backup", use_container_width=True):
                        success, message = backup_mgr.delete_backup(selected_backup['path'])
                        if success:
                            st.success(message)
                            del st.session_state['confirm_delete_backup']
                            st.rerun()
                        else:
                            st.error(message)
                with col_no:
                    if st.button("❌ Cancel", key="no_delete_backup", use_container_width=True):
                        del st.session_state['confirm_delete_backup']
                        st.rerun()
            
            # Show backup details
            if 'show_backup_details' in st.session_state and st.session_state['show_backup_details'] == selected_backup['path']:
                with st.expander("📋 Backup Details", expanded=True):
                    st.write(f"**Filename:** {selected_backup['filename']}")
                    st.write(f"**Type:** {selected_backup['type']}")
                    st.write(f"**Size:** {selected_backup['size']}")
                    st.write(f"**Created:** {format_datetime(selected_backup['created'])}")
                    st.write(f"**Path:** {selected_backup['path']}")
                    
                    if st.button("❌ Close Details"):
                        del st.session_state['show_backup_details']
                        st.rerun()
    
    with col2:
        st.write("#### Maintenance")
        
        # Cleanup old backups
        keep_count = st.number_input(
            "Keep Recent Backups",
            min_value=1,
            max_value=50,
            value=10,
            help="Number of recent backups to keep when cleaning up"
        )
        
        if st.button("🧹 Clean Up Old Backups", use_container_width=True):
            success, deleted_count, message = backup_mgr.cleanup_old_backups(keep_count=keep_count)
            if success:
                if deleted_count > 0:
                    st.success(message)
                    st.rerun()
                else:
                    st.info(message)
            else:
                st.error(message)
        
        st.divider()
        
        # Export backup info
        if st.button("📄 Export Backup Info", use_container_width=True):
            backup_info = backup_mgr.export_backup_info()
            import json
            json_data = json.dumps(backup_info, default=str, indent=2)
            st.download_button(
                label="💾 Download Backup Info (JSON)",
                data=json_data,
                file_name=f"backup_info_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )

