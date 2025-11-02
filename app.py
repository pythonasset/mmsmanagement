"""
Main Application File for Maintenance Management System
Web-based Asset and Maintenance Management with Google Earth Integration
"""
import streamlit as st
from database import init_database, get_session, AssetClass, AssetGroup, AssetType
from asset_management import show_asset_management
from work_order_management import show_work_order_management
from inspection_management import show_inspection_management
from reporting import show_reporting
from administration import show_administration
from faq import show_faq
from document_viewer import show_document_viewer
from settings import DEFAULT_ASSET_CLASSES
from config_loader import get_config

# Load configuration
try:
    config = get_config()
    APP_TITLE = config.APP_TITLE
    APP_ICON = config.APP_ICON
    COMPANY_NAME = config.COMPANY_NAME
except Exception as e:
    st.error(f"Error loading configuration: {str(e)}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_database_engine():
    """Get cached database engine"""
    return init_database()

@st.cache_resource
def get_database_session(_engine):
    """Get database session from cached engine"""
    return get_session(_engine)

def initialize_database():
    """Initialize database and create default data if needed"""
    engine = get_database_engine()
    session = get_database_session(engine)
    
    # Check if we need to create default asset classes (only runs once)
    existing_classes = session.query(AssetClass).count()
    
    if existing_classes == 0:
        st.info("Initializing database with default asset classes...")
        
        for class_data in DEFAULT_ASSET_CLASSES:
            asset_class = AssetClass(
                name=class_data["name"],
                description=class_data["description"]
            )
            session.add(asset_class)
        
        session.commit()
        st.success("Database initialized successfully!")
    
    # Initialize dropdown values (cached internally)
    from dropdown_utils import initialize_dropdown_defaults
    initialize_dropdown_defaults(session)
    
    return session

@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_dashboard_stats(_session):
    """Get cached dashboard statistics"""
    from database import Asset, WorkOrder, Inspection
    
    return {
        'total_assets': _session.query(Asset).count(),
        'open_work_orders': _session.query(WorkOrder).filter(
            WorkOrder.status.in_(["Open", "In Progress"])
        ).count(),
        'total_inspections': _session.query(Inspection).count(),
        'asset_classes': _session.query(AssetClass).count()
    }

def show_home_page(session):
    """Display home/welcome page"""
    st.markdown(f'<div class="main-header">{APP_ICON} {APP_TITLE}</div>', unsafe_allow_html=True)
    
    # System Overview - moved to top
    st.divider()
    
    st.write("### System Overview")
    
    # Get cached statistics
    with st.spinner('Loading dashboard statistics...'):
        stats = get_dashboard_stats(session)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Assets", stats['total_assets'])
    
    with col2:
        st.metric("Open Work Orders", stats['open_work_orders'])
    
    with col3:
        st.metric("Total Inspections", stats['total_inspections'])
    
    with col4:
        st.metric("Asset Classes", stats['asset_classes'])
    
    st.divider()
    
    # Welcome and features
    st.write(f"""
    ## Welcome to the {COMPANY_NAME} Maintenance Management System
    
    This comprehensive system helps you manage and track:
    - 📦 **Assets** - Complete asset register with hierarchy management
    - 🔧 **Work Orders** - Maintenance work order creation and tracking
    - 🔍 **Inspections** - Inspection scheduling and defect tracking
    - 📊 **Reports** - Comprehensive analytics and reporting
    - 🌍 **Google Earth Integration** - Visual tracking on maps and Google Earth
    """)
    
    # Getting Started expander
    with st.expander("🚀 Getting Started", expanded=False):
        st.write("""
        1. **Set Up Asset Hierarchy** - Navigate to Asset Management to configure asset classes, groups, and types
        2. **Add Assets** - Register your assets with location data
        3. **Create Work Orders** - Track maintenance activities
        4. **Schedule Inspections** - Monitor asset conditions
        5. **Generate Reports** - Analyze performance and trends
        """)
    
    # Key Features expander
    with st.expander("⭐ Key Features", expanded=False):
        st.write("""
        - ✅ **Modular Design** - Organized by functional areas
        - ✅ **Location Tracking** - GPS coordinates and Google Earth/Maps integration
        - ✅ **Hierarchical Assets** - Class → Group → Type → Asset structure
        - ✅ **Work Order Management** - Priority-based scheduling
        - ✅ **Inspection Tracking** - Defect detection and follow-up
        - ✅ **Analytics Dashboard** - Real-time metrics and visualizations
        - ✅ **Export Capabilities** - CSV, Excel, and KML formats
        """)
    
    st.divider()
    
    st.caption("💡 Use the sidebar navigation to explore different sections of the system.")

def main():
    """Main application entry point"""
    
    # Initialize database
    try:
        session = initialize_database()
    except Exception as e:
        st.error(f"Database initialization error: {str(e)}")
        st.stop()
    
    # Sidebar navigation
    st.sidebar.markdown('<div class="sidebar-header">📋 Navigation</div>', unsafe_allow_html=True)
    
    page = st.sidebar.radio(
        "Go to",
        [
            "🏠 Home",
            "📦 Asset Management",
            "🔧 Work Order Management",
            "🔍 Inspection Management",
            "📊 Reports & Analytics",
            "📁 Documents",
            "⚙️ Administration",
            "❓ FAQ & Help"
        ]
    )
    
    st.sidebar.divider()
    
    # System information
    st.sidebar.markdown("### System Information")
    st.sidebar.info(f"""
    **System:** {APP_TITLE}  
    **Version:** {config.VERSION}  
    **Environment:** {config.ENVIRONMENT}
    """)
    
    # Registration information
    with st.sidebar.expander("📋 Registration Info"):
        st.write(f"""
        **Registered To:**  
        {config.REGISTERED_TO}
        
        **Department:**  
        {config.DEPARTMENT}
        
        **ABN:** {config.ABN}
        """)
    
    # Developer information
    with st.sidebar.expander("🔧 Developer Info"):
        st.write(f"""
        **Produced By:**  
        {config.PRODUCED_BY}
        
        **Support:** {config.SUPPORT_PHONE}  
        **Email:** {config.DEVELOPER_CONTACT}
        """)
        if config.DEVELOPER_WEBSITE:
            st.markdown(f"[🌐 Website]({config.DEVELOPER_WEBSITE})")
    
    # Quick actions
    st.sidebar.markdown("### Quick Actions")
    
    if st.sidebar.button("➕ Quick Add Asset"):
        st.session_state['quick_action'] = 'add_asset'
    
    if st.sidebar.button("🔧 Quick Add Work Order"):
        st.session_state['quick_action'] = 'add_work_order'
    
    if st.sidebar.button("🔍 Quick Add Inspection"):
        st.session_state['quick_action'] = 'add_inspection'
    
    st.sidebar.divider()
    
    # Export options
    st.sidebar.markdown("### Export Options")
    
    if st.sidebar.button("📍 Export All to Google Earth"):
        from google_earth import (
            export_assets_to_kml,
            export_work_orders_to_kml,
            export_inspections_to_kml
        )
        
        try:
            # Export all data
            asset_file = export_assets_to_kml(session, "all_assets.kml")
            wo_file = export_work_orders_to_kml(session, "all_work_orders.kml")
            insp_file = export_inspections_to_kml(session, "all_inspections.kml")
            
            st.sidebar.success("✅ KML files generated!")
            
            with open(asset_file, 'rb') as f:
                st.sidebar.download_button(
                    "Download Assets KML",
                    f,
                    file_name="all_assets.kml",
                    mime="application/vnd.google-earth.kml+xml"
                )
        except Exception as e:
            st.sidebar.error(f"Export error: {str(e)}")
    
    # Handle quick actions - override page selection if quick action is set
    if 'quick_action' in st.session_state:
        quick_action = st.session_state['quick_action']
        
        if quick_action == 'add_asset':
            # Navigate to Asset Management and trigger add form
            page = "📦 Asset Management"
            st.session_state['show_add_asset_form'] = True
            st.info("💡 Quick Action: Add New Asset form opened below")
        
        elif quick_action == 'add_work_order':
            # Navigate to Work Order Management and trigger add form
            page = "🔧 Work Order Management"
            st.session_state['show_add_wo_form'] = True
            st.info("💡 Quick Action: Create Work Order form opened below")
        
        elif quick_action == 'add_inspection':
            # Navigate to Inspection Management and trigger add form
            page = "🔍 Inspection Management"
            st.session_state['show_add_insp_form'] = True
            st.info("💡 Quick Action: Create Inspection form opened below")
        
        # Clear the quick action
        del st.session_state['quick_action']
    
    # Main content area - route to selected page
    if page == "🏠 Home":
        show_home_page(session)
    elif page == "📦 Asset Management":
        show_asset_management(session)
    elif page == "🔧 Work Order Management":
        show_work_order_management(session)
    elif page == "🔍 Inspection Management":
        show_inspection_management(session)
    elif page == "📊 Reports & Analytics":
        show_reporting(session)
    elif page == "📁 Documents":
        show_document_viewer(session)
    elif page == "⚙️ Administration":
        show_administration(session)
    elif page == "❓ FAQ & Help":
        show_faq()
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8rem; padding: 20px;">
        Maintenance Management System v1.0.0 | Built with Streamlit | 
        <a href="https://github.com" target="_blank">Documentation</a> | 
        <a href="mailto:support@example.com">Support</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
