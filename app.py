# app.py - RetailPulse AI (Fixed Version)
# Generalized Multi-Tenant AI Retail SaaS Platform

import streamlit as st
import pandas as pd

# ==================== CONFIGURATION ====================
class AppStep:
    """Application steps for navigation"""
    WELCOME = 1
    ONBOARDING = 2
    PRICING = 3
    DASHBOARD = 4


# Business sectors as strings
GROCERY = "Grocery"
PHARMACY = "Pharmacy"
APPAREL = "Apparel"
ELECTRONICS = "Electronics"

# Pricing plans as strings
BASIC_PLAN = "Basic"
AI_PRO_PLAN = "AI Pro"

# Sector-specific feature mappings
SECTOR_FEATURES = {
    GROCERY: {
        "basic": ["Inventory Tracking", "Basic Analytics", "3 User Accounts"],
        "ai_pro": ["AI Demand Forecasting", "Tezi Mandi Integration", 
                  "Smart Reordering", "10 User Accounts"]
    },
    PHARMACY: {
        "basic": ["Inventory Tracking", "Basic Analytics", "3 User Accounts"],
        "ai_pro": ["Expiry Tracker AI", "Compliance Monitoring", 
                  "Prescription Pattern Analysis", "10 User Accounts"]
    },
    APPAREL: {
        "basic": ["Inventory Tracking", "Basic Analytics", "3 User Accounts"],
        "ai_pro": ["Trend Forecasting AI", "Size Optimization", 
                  "Visual Search", "10 User Accounts"]
    },
    ELECTRONICS: {
        "basic": ["Inventory Tracking", "Basic Analytics", "3 User Accounts"],
        "ai_pro": ["Warranty Tracker AI", "Cross-sell Recommendations", 
                  "Price Optimization", "10 User Accounts"]
    }
}

# Icons for sidebar based on sector
SECTOR_ICONS = {
    GROCERY: "🛒",
    PHARMACY: "💊",
    APPAREL: "👕",
    ELECTRONICS: "📱"
}

# ==================== MOCK DATABASE LAYER ====================
def save_user_profile(data):
    """Mock function simulating database save"""
    print(f"[MOCK DB] Saving user profile: {data}")
    return {
        "success": True,
        "user_id": "user_" + str(hash(str(data)))[:8],
        "data": data
    }


# ==================== INITIALIZATION ====================
def initialize_session_state():
    """Initialize all required session state variables"""
    if 'current_step' not in st.session_state:
        st.session_state.current_step = AppStep.WELCOME
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    if 'user_sector' not in st.session_state:
        st.session_state.user_sector = None
    if 'selected_plan' not in st.session_state:
        st.session_state.selected_plan = None


def reset_application():
    """Reset application to initial state"""
    keys_to_keep = ['_streamlit_rerun_count']
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    st.rerun()


# ==================== UI COMPONENTS ====================
def render_welcome_step():
    """Step 1: Welcome/Login page"""
    st.title("🛍️ RetailPulse AI")
    st.subheader("Intelligent Retail Management Platform")
    
    # Create a centered container
    with st.container():
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### Welcome to RetailPulse AI")
            st.markdown("Transform your retail business with AI-powered insights. Get started with your phone number below.")
            st.markdown("---")
            
            # Phone input
            phone_number = st.text_input(
                "📱 Enter your phone number",
                placeholder="+1 (555) 123-4567",
                key="login_phone"
            )
            
            # Continue button
            if st.button("Continue", type="primary", use_container_width=True):
                if phone_number and len(phone_number.strip()) > 5:
                    st.session_state.user_profile['phone'] = phone_number.strip()
                    st.session_state.current_step = AppStep.ONBOARDING
                    st.rerun()
                else:
                    st.error("📱 Please enter a valid phone number")
            
            st.markdown("---")
            st.caption("Demo: Use any phone number format to continue")


def render_onboarding_step():
    """Step 2: Onboarding form"""
    st.title("📋 Business Onboarding")
    
    with st.container():
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown("### Tell us about your business")
            
            # Shop name input
            shop_name = st.text_input(
                "🏪 Shop Name *",
                placeholder="e.g., City Mart, Medico Pharmacy",
                key="shop_name"
            )
            
            # Business sector dropdown
            sector_options = [GROCERY, PHARMACY, APPAREL, ELECTRONICS]
            
            selected_sector = st.selectbox(
                "📊 Business Sector *",
                options=sector_options,
                index=0,
                key="business_sector"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Button container
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("← Back", use_container_width=True):
                    st.session_state.current_step = AppStep.WELCOME
                    st.rerun()
            
            with col_btn2:
                if st.button("Continue to Plans →", type="primary", use_container_width=True):
                    if shop_name and selected_sector:
                        # Save onboarding data
                        st.session_state.user_profile.update({
                            'shop_name': shop_name,
                            'sector': selected_sector
                        })
                        st.session_state.user_sector = selected_sector
                        st.session_state.current_step = AppStep.PRICING
                        st.rerun()
                    else:
                        st.error("❗ Please fill in all required fields (*)")


def render_pricing_step():
    """Step 3: Pricing/Plan selection"""
    st.title("💰 Choose Your Plan")
    
    sector = st.session_state.user_sector
    sector_name = sector if sector else "Retail"
    
    st.markdown(f"### Tailored for your {sector_name} business")
    st.markdown("---")
    
    # Two-column pricing cards
    col1, col2 = st.columns(2, gap="large")
    
    # Basic Plan Card
    with col1:
        with st.container(border=True, height=450):
            st.markdown(f"## {BASIC_PLAN}")
            st.markdown("### $29/month")
            st.markdown("---")
            
            # Get features for current sector
            features = SECTOR_FEATURES.get(sector, SECTOR_FEATURES[GROCERY])
            for feature in features['basic']:
                st.markdown(f"✓ {feature}")
            
            st.markdown("---")
            if st.button(
                "Select Basic", 
                key="select_basic",
                use_container_width=True,
                type="secondary"
            ):
                st.session_state.selected_plan = BASIC_PLAN
                st.session_state.current_step = AppStep.DASHBOARD
                save_user_profile(st.session_state.user_profile)
                st.rerun()
    
    # AI Pro Plan Card
    with col2:
        with st.container(border=True, height=450):
            st.markdown(f"## {AI_PRO_PLAN}")
            st.markdown("### $99/month")
            st.markdown("---")
            
            # Get features for current sector
            features = SECTOR_FEATURES.get(sector, SECTOR_FEATURES[GROCERY])
            for feature in features['ai_pro']:
                st.markdown(f"🚀 {feature}")
            
            # Add sector-specific highlight
            if sector == GROCERY:
                st.info("**Includes:** Tezi Mandi Integration")
            elif sector == PHARMACY:
                st.info("**Includes:** Expiry Tracker AI")
            elif sector == APPAREL:
                st.info("**Includes:** Trend Forecasting AI")
            elif sector == ELECTRONICS:
                st.info("**Includes:** Warranty Tracker AI")
            
            st.markdown("---")
            if st.button(
                "Select AI Pro", 
                type="primary",
                key="select_ai_pro",
                use_container_width=True
            ):
                st.session_state.selected_plan = AI_PRO_PLAN
                st.session_state.current_step = AppStep.DASHBOARD
                save_user_profile(st.session_state.user_profile)
                st.rerun()
    
    # Back button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Onboarding", use_container_width=True):
        st.session_state.current_step = AppStep.ONBOARDING
        st.rerun()


def render_sidebar():
    """Dynamic sidebar based on user sector"""
    with st.sidebar:
        # Display different content based on current step
        if st.session_state.current_step == AppStep.DASHBOARD:
            sector = st.session_state.user_sector
            sector_icon = SECTOR_ICONS.get(sector, "🛍️")
            
            st.title(f"{sector_icon} RetailPulse AI")
            st.markdown("---")
            
            st.markdown(f"**Welcome to**")
            st.markdown(f"### {st.session_state.user_profile.get('shop_name', 'Your Shop')}")
            st.markdown(f"*{sector} • {st.session_state.selected_plan}*")
            st.markdown("---")
            
            # Menu items
            menu_items = ["📊 Dashboard", "📦 Inventory", "📈 Analytics", "🤖 AI Insights"]
            
            # Add sector-specific menu items
            if sector == GROCERY:
                menu_items.append("🛒 Tezi Mandi")
            elif sector == PHARMACY:
                menu_items.append("💊 Expiry Tracker")
            elif sector == APPAREL:
                menu_items.append("👕 Style Advisor")
            elif sector == ELECTRONICS:
                menu_items.append("🔧 Warranty Manager")
            
            menu_items.append("⚙️ Settings")
            
            # Display menu
            for item in menu_items:
                st.button(item, use_container_width=True)
            
            st.markdown("---")
            
            # Reset button
            if st.button("🔄 Reset Account", type="secondary", use_container_width=True):
                reset_application()
        else:
            # Simple sidebar for other steps
            st.title("🛍️ RetailPulse AI")
            st.markdown("---")
            st.markdown("### Getting Started")
            st.markdown("1. Login with phone")
            st.markdown("2. Business details")
            st.markdown("3. Choose plan")
            st.markdown("4. Access dashboard")


def render_dashboard():
    """Step 4: Main Dashboard (Sector-specific)"""
    sector = st.session_state.user_sector
    sector_icon = SECTOR_ICONS.get(sector, "🛍️")
    shop_name = st.session_state.user_profile.get('shop_name', 'Your Shop')
    
    st.title(f"{sector_icon} {shop_name} Dashboard")
    st.markdown(f"*{sector} • {st.session_state.selected_plan} Plan*")
    
    # Dashboard metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Today's Sales", "$2,847", "+12%")
    
    with col2:
        st.metric("Inventory Value", "$18,459", "-3%")
    
    with col3:
        st.metric("Customer Visits", "147", "+8%")
    
    with col4:
        st.metric("AI Predictions", "94%", "Accuracy")
    
    st.markdown("---")
    
    # Main content area
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 Key Metrics")
        
        # Sector-specific metrics
        if sector == GROCERY:
            st.info("**Fresh Produce Turnover:** 2.3 days")
            st.info("**Tezi Mandi Savings:** $423 this month")
            st.info("**Waste Reduction:** 18% improved")
        
        elif sector == PHARMACY:
            st.info("**Expiry Risk:** Low (2 items)")
            st.info("**Prescription Accuracy:** 99.8%")
            st.info("**Compliance Score:** 98/100")
        
        elif sector == APPAREL:
            st.info("**Top Size:** Medium (35% sales)")
            st.info("**Return Rate:** 4.2%")
            st.info("**Trend Match:** 87% accuracy")
        
        elif sector == ELECTRONICS:
            st.info("**Warranty Claims:** 3 this month")
            st.info("**Cross-sell Rate:** 22%")
            st.info("**Repair Time:** 1.8 days avg")
        
        else:
            st.info("**Sales Growth:** +12% MoM")
            st.info("**Inventory Turnover:** 45 days")
            st.info("**Customer Satisfaction:** 4.7/5")
    
    with col_right:
        st.subheader("🤖 AI Insights")
        
        # AI insights based on sector and plan
        if st.session_state.selected_plan == AI_PRO_PLAN:
            if sector == GROCERY:
                st.success("**AI Recommendation:** Stock up on organic vegetables - predicted 35% demand increase next week.")
                st.success("**Tezi Mandi Alert:** Best prices on tomatoes tomorrow.")
            
            elif sector == PHARMACY:
                st.success("**AI Alert:** 2 medications expiring next week. Consider promotional pricing.")
                st.success("**Prescription Pattern:** Higher demand for allergy meds detected.")
            
            elif sector == APPAREL:
                st.success("**Trend Forecast:** Pastel colors trending upward. Consider increasing stock.")
                st.success("**Size Optimization:** Medium sizes understocked by 15%.")
            
            elif sector == ELECTRONICS:
                st.success("**Warranty Alert:** 5 products reaching warranty end this month.")
                st.success("**Price Optimization:** Recommended 8% price reduction on older model headphones.")
        else:
            st.warning("**Upgrade to AI Pro** for advanced insights and sector-specific features!")
            st.info("Basic plan includes essential tracking and analytics.")
    
    # Recent transactions
    st.markdown("---")
    st.subheader("📋 Recent Transactions")
    
    # Sample data based on sector
    if sector == GROCERY:
        data = pd.DataFrame({
            "Item": ["Organic Apples", "Whole Wheat Bread", "Fresh Milk"],
            "Quantity": [15, 8, 12],
            "Amount": ["$45", "$24", "$36"],
            "Time": ["10:30 AM", "11:15 AM", "11:45 AM"]
        })
    elif sector == PHARMACY:
        data = pd.DataFrame({
            "Item": ["Vitamin C", "Pain Reliever", "Allergy Meds"],
            "Quantity": [5, 3, 7],
            "Amount": ["$75", "$27", "$98"],
            "Time": ["09:45 AM", "10:20 AM", "11:05 AM"]
        })
    elif sector == APPAREL:
        data = pd.DataFrame({
            "Item": ["Denim Jacket", "Cotton T-Shirt", "Running Shoes"],
            "Quantity": [2, 5, 1],
            "Amount": ["$120", "$75", "$85"],
            "Time": ["12:15 PM", "12:45 PM", "01:30 PM"]
        })
    elif sector == ELECTRONICS:
        data = pd.DataFrame({
            "Item": ["Wireless Earbuds", "Phone Case", "Charger Cable"],
            "Quantity": [3, 7, 4],
            "Amount": ["$297", "$70", "$36"],
            "Time": ["10:00 AM", "10:45 AM", "11:30 AM"]
        })
    else:
        data = pd.DataFrame({
            "Item": ["Sample Item 1", "Sample Item 2", "Sample Item 3"],
            "Quantity": [10, 5, 8],
            "Amount": ["$100", "$50", "$80"],
            "Time": ["10:00 AM", "11:00 AM", "12:00 PM"]
        })
    
    st.dataframe(data, use_container_width=True, hide_index=True)


# ==================== MAIN APPLICATION ====================
def main():
    """Main application router"""
    # Page configuration
    st.set_page_config(
        page_title="RetailPulse AI",
        page_icon="🛍️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main content router
    current_step = st.session_state.get('current_step', AppStep.WELCOME)
    
    if current_step == AppStep.WELCOME:
        render_welcome_step()
    
    elif current_step == AppStep.ONBOARDING:
        render_onboarding_step()
    
    elif current_step == AppStep.PRICING:
        render_pricing_step()
    
    elif current_step == AppStep.DASHBOARD:
        render_dashboard()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2025 RetailPulse AI v2.0")
    st.sidebar.caption("Demo Application")


if __name__ == "__main__":
    main()
