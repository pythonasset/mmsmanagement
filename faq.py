"""
FAQ and Future Enhancements Module
Frequently Asked Questions and System Roadmap
"""
import streamlit as st

def show_faq():
    """Display FAQ and Future Enhancements"""
    st.header("❓ FAQ & Future Enhancements")
    
    # Create tabs
    tab1, tab2 = st.tabs(["📚 Frequently Asked Questions", "🚀 Future Enhancements"])
    
    with tab1:
        show_faqs()
    
    with tab2:
        show_future_enhancements()


def show_faqs():
    """Display FAQs organized by subject matter"""
    st.subheader("Frequently Asked Questions")
    
    st.info("💡 Click on any question below to see the answer")
    
    # General System Questions
    st.markdown("### 🏠 General System Questions")
    
    with st.expander("1. What is the Maintenance Management System (MMS)?"):
        st.write("MMS is a comprehensive web-based application for managing assets, work orders, inspections, and maintenance activities. It helps organizations track and maintain their infrastructure assets efficiently.")
    
    with st.expander("2. Who can use this system?"):
        st.write("The system is designed for maintenance teams, facility managers, technicians, inspectors, and administrators. Different user roles have different access levels and permissions.")
    
    with st.expander("3. What are the system requirements?"):
        st.write("You need a modern web browser (Chrome, Firefox, Edge, or Safari) and an internet connection. The system runs on any device - desktop, tablet, or mobile.")
    
    with st.expander("4. How do I log in to the system?"):
        st.write("Currently, the system uses a simplified authentication. In production, you would log in with your username and password assigned by your administrator.")
    
    with st.expander("5. Can I access the system on my mobile device?"):
        st.write("Yes! The interface is responsive and works on smartphones and tablets. However, some features work best on larger screens.")
    
    with st.expander("6. How is my data stored?"):
        st.write("Data is stored in a SQLite database located in the `data/` directory. For production use, this can be migrated to PostgreSQL, MySQL, or other enterprise databases.")
    
    with st.expander("7. Can multiple users access the system simultaneously?"):
        st.write("Yes, the system supports multiple concurrent users. Each user's session is independent.")
    
    with st.expander("8. What happens if I lose my internet connection?"):
        st.write("If you're using the cloud-hosted version, you'll need internet access. For on-premise installations, you only need local network access.")
    
    with st.expander("9. How often is the system updated?"):
        st.write("Updates and new features are released regularly. Check the Future Enhancements tab to see what's coming next!")
    
    with st.expander("10. Where can I get help if I have issues?"):
        st.write("Contact your system administrator or refer to the documentation. You can also check the relevant FAQ sections below for specific topics.")
    
    st.divider()
    
    # Asset Management FAQs
    st.markdown("### 📦 Asset Management")
    
    with st.expander("1. How do I add a new asset?"):
        st.write("Navigate to Asset Management → View Assets tab, then fill out the form with asset details including Asset ID, name, type, location coordinates, and other relevant information.")
    
    with st.expander("2. What is the asset hierarchy (Class/Group/Type)?"):
        st.markdown("""
        Assets are organized in three levels:
        - **Class**: Broad category (e.g., Road Infrastructure)
        - **Group**: Subcategory within class (e.g., Sealed Roads)
        - **Type**: Specific asset type (e.g., Asphalt Road)
        """)
    
    with st.expander("3. Can I import multiple assets at once?"):
        st.write("Bulk import functionality is planned for future releases. Currently, assets must be added individually through the form.")
    
    with st.expander("4. How do I edit an existing asset?"):
        st.write("Go to Asset Management → View Assets, find your asset in the list, and click the '✏️ Edit Asset' button to modify its details.")
    
    with st.expander("5. What are GPS coordinates used for?"):
        st.write("GPS coordinates (latitude/longitude) place your asset on the map and enable location-based features like proximity searches and Google Earth exports.")
    
    with st.expander("6. What is the condition rating scale?"):
        st.markdown("""
        Condition ratings range from 1-5:
        - **1**: Very Poor
        - **2**: Poor
        - **3**: Fair
        - **4**: Good
        - **5**: Excellent
        """)
    
    with st.expander("7. Can I attach photos or documents to assets?"):
        st.write("Document and photo attachment functionality is planned for future releases.")
    
    with st.expander("8. How do I search for specific assets?"):
        st.write("Use the search bar in the Asset Management tab to search by Asset ID or name. You can also filter by class, group, type, and status.")
    
    with st.expander("9. What does 'Asset Status' mean?"):
        st.markdown("""
        Asset status indicates the current state:
        - **Active**: In normal operation
        - **Inactive**: Not currently in use
        - **Under Maintenance**: Being repaired/maintained
        - **Disposed**: Removed from service
        - **Reserved**: Set aside for specific use
        """)
    
    with st.expander("10. Can I delete an asset?"):
        st.write("Yes, but be cautious! Deleting an asset is permanent. Make sure to check for associated work orders and inspections first.")
    
    st.divider()
    
    # Work Order Management FAQs
    st.markdown("### 🔧 Work Order Management")
    
    with st.expander("1. How do I create a new work order?"):
        st.write("Go to Work Order Management → Create Work Order tab. Fill in the details including title, asset, work type, priority, and assigned personnel.")
    
    with st.expander("2. What is a Work Order Number?"):
        st.write("Work Order Numbers (e.g., WO-00001) are automatically generated unique identifiers for tracking each work order throughout its lifecycle.")
    
    with st.expander("3. What are the different work order types?"):
        st.markdown("""
        - **Preventive Maintenance**: Scheduled routine maintenance
        - **Corrective Maintenance**: Repairs to fix issues
        - **Emergency Repair**: Urgent fixes
        - **Inspection**: Assessment work
        - **Installation**: New equipment setup
        - **Replacement**: Component replacement
        - **Other**: Miscellaneous work
        """)
    
    with st.expander("4. What do the priority levels mean?"):
        st.markdown("""
        - **Critical**: Immediate attention required (safety/major impact)
        - **High**: Urgent, schedule within 24-48 hours
        - **Medium**: Standard priority, schedule within 1 week
        - **Low**: Can be scheduled when convenient
        """)
    
    with st.expander("5. How do I assign work orders to technicians?"):
        st.write("Use the 'Assigned To' dropdown in the work order form to select from active users in the system.")
    
    with st.expander("6. What's the difference between Scheduled Date and Due Date?"):
        st.markdown("""
        - **Scheduled Date**: When the work is planned to start
        - **Due Date**: Deadline for completion
        """)
    
    with st.expander("7. How do I track work order costs?"):
        st.write("Enter estimated costs when creating the work order, then update with actual costs upon completion. The system tracks both for budget analysis.")
    
    with st.expander("8. Can I see work orders on a map?"):
        st.write("Yes! Use the Work Order Map tab to visualize all work orders by location. Color coding indicates priority levels.")
    
    with st.expander("9. How do I mark a work order as complete?"):
        st.write("Open the work order details and click '✅ Mark Complete'. Add completion notes and actual costs before finalizing.")
    
    with st.expander("10. Can I create a work order from an inspection?"):
        st.write("This feature is planned! When inspections find defects, you'll be able to automatically generate work orders.")
    
    st.divider()
    
    # Inspection Management FAQs
    st.markdown("### 🔍 Inspection Management")
    
    with st.expander("1. How do I schedule an inspection?"):
        st.write("Go to Inspection Management → Create Inspection tab. Select the asset, inspection type, date/time, and assign an inspector.")
    
    with st.expander("2. What types of inspections can I perform?"):
        st.markdown("""
        - **Routine Inspection**: Regular scheduled checks
        - **Safety Inspection**: Safety compliance checks
        - **Condition Assessment**: Detailed condition evaluation
        - **Compliance Audit**: Regulatory compliance verification
        - **Pre-Purchase Inspection**: Before asset acquisition
        - **Post-Work Inspection**: After maintenance completion
        """)
    
    with st.expander("3. How do I record inspection findings?"):
        st.write("In the inspection form, set the condition rating, check 'Defects Found' if applicable, and describe any defects in detail.")
    
    with st.expander("4. What if I find defects during inspection?"):
        st.write("Check the 'Defects Found' box and describe the issues. The system will suggest creating a work order to address them.")
    
    with st.expander("5. Can I schedule follow-up inspections?"):
        st.write("Yes! Check 'Follow-up Required' and set a follow-up date when creating or editing an inspection.")
    
    with st.expander("6. How do I assign inspections to inspectors?"):
        st.write("Use the 'Inspector Name' dropdown to select from active users in the system. Only active users appear in the list.")
    
    with st.expander("7. Can I see inspection history for an asset?"):
        st.write("Filter inspections by asset in the Inspections tab to view all inspection records for a specific asset.")
    
    with st.expander("8. What are recommendations in inspections?"):
        st.write("Recommendations are suggestions for maintenance, repairs, or further actions based on inspection findings.")
    
    with st.expander("9. Can I export inspection reports?"):
        st.write("Currently, you can export inspection data to CSV or view on Google Earth. Formatted PDF reports are planned for future releases.")
    
    with st.expander("10. How often should I inspect my assets?"):
        st.write("Inspection frequency depends on asset type, criticality, and regulatory requirements. Set up routine inspections based on your organization's standards.")
    
    st.divider()
    
    # Reporting & Analytics FAQs
    st.markdown("### 📊 Reporting & Analytics")
    
    with st.expander("1. What reports are available?"):
        st.markdown("""
        The system provides:
        - Asset condition dashboards
        - Work order status and trends
        - Cost analysis reports
        - Inspection summaries
        - Maintenance history
        """)
    
    with st.expander("2. Can I customize date ranges for reports?"):
        st.write("Yes! Most reports allow you to filter by date range, asset type, status, and other criteria.")
    
    with st.expander("3. How do I export report data?"):
        st.write("Use the export buttons to download data in CSV or Excel format. Google Earth KML exports are also available for location-based data.")
    
    with st.expander("4. What is the dashboard showing?"):
        st.write("The dashboard provides a quick overview of system statistics including total assets, open work orders, recent inspections, and key metrics.")
    
    with st.expander("5. Can I schedule automated reports?"):
        st.write("Automated report scheduling is planned for future releases. You'll be able to receive regular email reports.")
    
    st.divider()
    
    # Administration FAQs
    st.markdown("### ⚙️ Administration")
    
    with st.expander("1. How do I add new users?"):
        st.write("Go to Administration → User Management tab. Click 'Add New User' and fill in the user details including username, role, and department.")
    
    with st.expander("2. What are the different user roles?"):
        st.markdown("""
        - **Admin**: Full system access
        - **Manager**: Can manage assets and work orders
        - **Supervisor**: Can assign and oversee work
        - **Technician**: Can complete assigned work orders
        - **Inspector**: Can perform inspections
        - **Viewer**: Read-only access
        """)
    
    with st.expander("3. How do I modify dropdown values?"):
        st.write("View current dropdown values in Administration → Dropdown Values tab. To modify them, edit the `settings.py` file or contact your administrator.")
    
    with st.expander("4. Can I create custom asset types?"):
        st.write("Yes! Go to Administration → Asset Hierarchy tab to add custom asset classes, groups, and types specific to your organization.")
    
    with st.expander("5. How do I backup the database?"):
        st.write("Database backup functionality is in development. Currently, you can manually copy the `data/maintenance_management.db` file.")


def show_future_enhancements():
    """Display planned future enhancements"""
    st.subheader("🚀 Future Enhancements Roadmap")
    
    st.info("🎯 Here's what's coming next to the Maintenance Management System!")
    
    # Short-term enhancements (Next 3 months)
    with st.expander("📅 **Short-term Enhancements** (Next 3 Months)", expanded=True):
        st.markdown("""
        ### Phase 1: Core Improvements
        
        **Authentication & Security**
        - ✨ User login/logout functionality
        - 🔐 Password encryption and reset
        - 👤 User session management
        - 🛡️ Role-based access control (RBAC)
        - 📝 Audit logging for all actions
        
        **File Attachments**
        - 📎 Attach photos to assets
        - 📄 Upload documents (PDFs, Word, Excel)
        - 🖼️ Image galleries for inspections
        - 📋 Document version control
        - 💾 File storage management
        
        **Enhanced Reporting**
        - 📊 PDF report generation
        - 📧 Email reports functionality
        - 📅 Scheduled automated reports
        - 📈 Advanced analytics dashboards
        - 📉 Custom report builder
        
        **Mobile Optimization**
        - 📱 Mobile-first responsive design improvements
        - 📷 Camera integration for inspections
        - 🗺️ GPS location auto-capture
        - 📴 Offline mode capabilities
        - 🔄 Background sync when online
        """)
    
    # Medium-term enhancements (3-6 months)
    with st.expander("📅 **Medium-term Enhancements** (3-6 Months)", expanded=False):
        st.markdown("""
        ### Phase 2: Advanced Features
        
        **Work Order Enhancements**
        - 🔗 Link work orders to inspection defects
        - ⏰ Work order scheduling optimization
        - 📧 Email notifications for assignments
        - 💬 Comments and collaboration features
        - 📊 Resource allocation and planning
        - ⏱️ Time tracking for technicians
        
        **Preventive Maintenance**
        - 📆 Automated PM schedule generation
        - 🔔 Maintenance due date alerts
        - 📋 PM checklist templates
        - 📈 PM compliance tracking
        - 🔄 Recurring work order creation
        
        **Inventory Management**
        - 📦 Parts and materials tracking
        - 🏪 Warehouse/stock locations
        - 📉 Low stock alerts
        - 💰 Parts cost tracking
        - 📊 Usage history and analytics
        
        **Advanced Analytics**
        - 📊 Predictive maintenance analytics
        - 💹 Cost trend analysis
        - 📈 Asset lifecycle modeling
        - 🎯 KPI dashboards
        - 📉 Failure rate analysis
        """)
    
    # Long-term enhancements (6-12 months)
    with st.expander("📅 **Long-term Enhancements** (6-12 Months)", expanded=False):
        st.markdown("""
        ### Phase 3: Enterprise Features
        
        **Integration Capabilities**
        - 🔌 REST API for third-party integration
        - 📡 IoT sensor data integration
        - 🗺️ GIS system integration
        - 💼 ERP system connectivity
        - 📊 Business intelligence tool integration
        
        **Advanced Asset Management**
        - 📸 AI-powered defect detection from photos
        - 🤖 Automated condition assessment
        - 📊 Asset performance benchmarking
        - 💰 Total cost of ownership (TCO) analysis
        - 🔄 Asset replacement planning
        
        **Workflow Automation**
        - ⚙️ Custom workflow designer
        - 📧 Automated email escalations
        - 🔔 Multi-level approval processes
        - 🤖 Rule-based work order creation
        - 📋 Template-based task automation
        
        **Collaboration Features**
        - 💬 In-app messaging system
        - 👥 Team collaboration boards
        - 📝 Shared notes and annotations
        - 🔔 Real-time notifications
        - 📹 Video call integration for remote support
        
        **Compliance & Standards**
        - ✅ ISO 55000 compliance tracking
        - 📋 Regulatory requirement management
        - 🏆 Best practice templates
        - 📊 Compliance reporting
        - 🔍 Audit trail management
        """)
    
    # Innovative features
    with st.expander("🌟 **Innovative Features** (Future Vision)", expanded=False):
        st.markdown("""
        ### Phase 4: Next-Generation Capabilities
        
        **Artificial Intelligence & Machine Learning**
        - 🤖 AI-powered maintenance recommendations
        - 📊 Predictive failure analysis
        - 🎯 Optimal maintenance scheduling
        - 💡 Smart resource allocation
        - 📈 Anomaly detection in asset performance
        
        **Advanced Visualization**
        - 🏗️ 3D asset modeling
        - 🥽 AR/VR inspection tools
        - 🗺️ Digital twin technology
        - 📊 Interactive heat maps
        - 🎨 Advanced data visualization
        
        **Mobile & Field Operations**
        - 📱 Native mobile apps (iOS/Android)
        - 🔊 Voice-to-text for reports
        - 🗺️ Offline map caching
        - 📡 Real-time location tracking
        - 🤝 Contractor portal access
        
        **Sustainability & Green Features**
        - 🌱 Carbon footprint tracking
        - ♻️ Sustainability metrics
        - 💚 Green maintenance practices
        - 📊 Environmental impact reporting
        - 🎯 ESG compliance tracking
        
        **Advanced Reporting**
        - 📊 Custom dashboard builder
        - 📈 Executive summary reports
        - 🎯 Performance scorecards
        - 📉 What-if scenario modeling
        - 🔮 Forecasting and projections
        """)
    
    st.divider()
    
    # Feedback section
    st.markdown("### 💭 Have a Feature Request?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **We want to hear from you!**
        
        Your feedback helps shape the future of this system. If you have ideas for new features or improvements, please contact your system administrator or project team.
        """)
    
    with col2:
        st.success("""
        **Stay Updated**
        
        Check this page regularly for updates on new features and enhancements. We're constantly working to improve your experience!
        """)
    
    # Version History
    st.divider()
    st.markdown("### 📜 Version History")
    
    with st.expander("View Release Notes"):
        st.markdown("""
        **Version 1.0.0** (Current)
        - Initial release
        - Core asset management functionality
        - Work order creation and tracking
        - Inspection management
        - Basic reporting and analytics
        - Google Earth integration
        - User management
        - Asset hierarchy configuration
        
        **Coming in Version 1.1.0** (Q1 2025)
        - User authentication
        - File attachments
        - Enhanced mobile interface
        - PDF report generation
        
        **Planned for Version 2.0.0** (Q2 2025)
        - Preventive maintenance scheduler
        - Inventory management
        - Advanced analytics
        - API integration capabilities
        """)

