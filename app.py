# app.py - RetailPulse AI (Complete Full-Stack Version)
# Generalized Multi-Tenant AI Retail SaaS Platform with AI Integration

import streamlit as st
import pandas as pd
import json
import time
import io
import random
from datetime import datetime, timedelta
from PIL import Image
import base64
from typing import Dict, Any, List, Optional, Union
import traceback

# ==================== BACKEND IMPORTS & CONFIGURATION ====================
# Try to import actual backend libraries, fallback to mock mode
try:
    import google.generativeai as genai
    from supabase import create_client
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    st.sidebar.warning("⚠️ Backend libraries not installed. Running in mock mode.")

# ==================== APPLICATION CONFIGURATION ====================
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

# ==================== SECTOR-SPECIFIC CONFIGURATIONS ====================
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

# ==================== BACKEND CONNECTION MANAGEMENT ====================
@st.cache_resource
def init_connections():
    """
    Initialize Gemini AI and Supabase connections with fallback to mock mode
    Returns: (gemini_model, supabase_client, connection_status)
    """
    connection_status = {
        "gemini_available": False,
        "supabase_available": False,
        "mode": "mock"
    }
    
    gemini_model = None
    supabase_client = None
    
    try:
        # Check if backend libraries are available
        if not BACKEND_AVAILABLE:
            st.info("Running in mock mode. Install google-generativeai and supabase for full functionality.")
            return None, None, connection_status
        
        # Initialize Gemini AI
        try:
            if "GEMINI_API_KEY" in st.secrets:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                
                # ✅ USE CORRECT MODEL NAME FOR 2.5 FLASH-LITE:
                # Option 1: Gemini 2.5 Flash-Lite (Fast & Efficient - 90% profit margin)
                gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')
                
                # Option 2: Gemini 3 Flash (if you have early access)
                # gemini_model = genai.GenerativeModel('gemini-3.0-flash-exp')
                
                # Option 3: Fallback to latest stable
                # gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                # Test connection
                try:
                    response = gemini_model.generate_content("Test connection")
                    connection_status["gemini_available"] = True
                    st.success("✅ Gemini AI 2.5 Flash-Lite connected successfully")
                except Exception as model_error:
                    # Try fallback model
                    st.warning(f"⚠️ 2.5 Flash-Lite not available: {str(model_error)}")
                    st.info("Trying fallback model...")
                    gemini_model = genai.GenerativeModel('gemini-1.5-flash-latest')
                    response = gemini_model.generate_content("Test")
                    connection_status["gemini_available"] = True
                    st.success("✅ Gemini AI connected with fallback model")
                    
            else:
                st.info("ℹ️ GEMINI_API_KEY not found in secrets. Using mock AI mode.")
        except Exception as e:
            st.warning(f"⚠️ Gemini AI initialization failed: {str(e)}")
            # Try alternative model
            try:
                gemini_model = genai.GenerativeModel('gemini-pro')
                connection_status["gemini_available"] = True
                st.success("✅ Gemini AI connected with legacy model")
            except:
                pass
        
        # Initialize Supabase
        try:
            if "SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets:
                supabase_url = st.secrets["SUPABASE_URL"]
                supabase_key = st.secrets["SUPABASE_KEY"]
                supabase_client = create_client(supabase_url, supabase_key)
                connection_status["supabase_available"] = True
                st.success("✅ Supabase connected successfully")
            else:
                st.info("ℹ️ Supabase credentials not found in secrets. Using mock database.")
        except Exception as e:
            st.warning(f"⚠️ Supabase initialization failed: {str(e)}")
        
        # Determine mode
        if connection_status["gemini_available"] or connection_status["supabase_available"]:
            connection_status["mode"] = "live"
        else:
            connection_status["mode"] = "mock"
            
    except Exception as e:
        st.error(f"❌ Connection initialization error: {str(e)}")
        connection_status["mode"] = "mock"
    
    return gemini_model, supabase_client, connection_status
# ==================== AI PROCESSING ENGINE ====================
def get_sector_system_prompt(sector: str) -> str:
    """Generate sector-specific system prompt for Gemini AI"""
    base_prompt = """You are a Retail Data Extraction Assistant. Extract purchase details from the input and return STRICT JSON format.

REQUIRED OUTPUT FORMAT (JSON ONLY, NO MARKDOWN):
{
    "items": [
        {"name": "item name", "qty": quantity, "price": unit_price}
    ],
    "total_amount": total_price
}

RULES:
1. Extract ALL items mentioned
2. If quantity not specified, assume 1
3. If price not specified, estimate reasonable market price
4. Calculate total_amount as sum(qty * price)
5. Round prices to 2 decimal places
6. Return ONLY the JSON object, no other text
"""
    
    sector_specific = {
        GROCERY: """
ADDITIONAL GROCERY RULES:
- Focus on weights (kg, g, lbs) and units
- Distinguish between loose and packaged items
- Note if items are perishable
- Common units: kg, liters, pieces, dozens
- Example: "2 kg apples at $3/kg" → {"name": "apples", "qty": 2, "price": 3.0}
""",
        PHARMACY: """
ADDITIONAL PHARMACY RULES:
- Focus on medicine/salt names, not brand names
- Check for expiry date mentions
- Flag if medicine requires prescription
- Common units: tablets, strips, bottles, mg/ml
- Example: "2 strips of paracetamol at $5 each" → {"name": "paracetamol", "qty": 2, "price": 5.0}
""",
        APPAREL: """
ADDITIONAL APPAREL RULES:
- Focus on sizes (S, M, L, XL), colors, brands
- Note if items are discounted or on sale
- Distinguish between different clothing types
- Example: "3 medium t-shirts at $15 each" → {"name": "t-shirt (medium)", "qty": 3, "price": 15.0}
""",
        ELECTRONICS: """
ADDITIONAL ELECTRONICS RULES:
- Focus on specifications, brands, models
- Note warranty periods if mentioned
- Distinguish between accessories and main devices
- Example: "1 smartphone at $999" → {"name": "smartphone", "qty": 1, "price": 999.0}
"""
    }
    
    return base_prompt + sector_specific.get(sector, "")

def generate_mock_ai_response(sector: str, input_type: str = "text") -> Dict[str, Any]:
    """Generate realistic mock AI response based on sector"""
    mock_responses = {
        GROCERY: {
            "items": [
                {"name": "Organic Apples", "qty": 2.0, "price": 3.99},
                {"name": "Whole Wheat Bread", "qty": 1.0, "price": 2.49},
                {"name": "Fresh Milk (1L)", "qty": 2.0, "price": 1.99},
                {"name": "Brown Eggs (12pcs)", "qty": 1.0, "price": 3.49}
            ],
            "total_amount": 16.94
        },
        PHARMACY: {
            "items": [
                {"name": "Paracetamol 500mg", "qty": 1.0, "price": 5.99},
                {"name": "Vitamin C Tablets", "qty": 1.0, "price": 8.49},
                {"name": "Hand Sanitizer", "qty": 2.0, "price": 3.25},
                {"name": "Bandages (10pcs)", "qty": 1.0, "price": 4.99}
            ],
            "total_amount": 25.97
        },
        APPAREL: {
            "items": [
                {"name": "Cotton T-Shirt (Medium)", "qty": 3.0, "price": 14.99},
                {"name": "Denim Jeans (32)", "qty": 1.0, "price": 49.99},
                {"name": "Running Shoes", "qty": 1.0, "price": 79.99}
            ],
            "total_amount": 154.95
        },
        ELECTRONICS: {
            "items": [
                {"name": "Wireless Earbuds", "qty": 1.0, "price": 89.99},
                {"name": "Phone Case", "qty": 2.0, "price": 12.99},
                {"name": "USB-C Cable", "qty": 3.0, "price": 8.49}
            ],
            "total_amount": 142.94
        }
    }
    
    response = mock_responses.get(sector, mock_responses[GROCERY])
    
    # Add some random variation
    for item in response["items"]:
        item["price"] = round(item["price"] * random.uniform(0.95, 1.05), 2)
    response["total_amount"] = round(sum(item["qty"] * item["price"] for item in response["items"]), 2)
    
    return response

def process_retail_input(
    user_input: Union[str, bytes, Image.Image], 
    sector: str,
    input_type: str = "text"
) -> Dict[str, Any]:
    """
    Process retail input (text, image, or voice) using AI or mock data
    
    Args:
        user_input: Text string, image bytes, or PIL Image
        sector: Business sector
        input_type: "text", "image", or "voice"
    
    Returns:
        Dictionary with extracted items and total amount
    """
    try:
        # Initialize connections
        gemini_model, _, connection_status = init_connections()
        
        # If in mock mode or Gemini not available, use mock data
        if connection_status["mode"] == "mock" or not connection_status["gemini_available"]:
            st.info("🤖 Using mock AI (demo mode)")
            time.sleep(1)  # Simulate processing time
            return generate_mock_ai_response(sector, input_type)
        
        # Prepare content based on input type
        content_parts = []
        
        # Add system prompt
        system_prompt = get_sector_system_prompt(sector)
        content_parts.append(system_prompt)
        
        # Add user input based on type
        if input_type == "text":
            content_parts.append(f"Extract purchase details from: {user_input}")
        elif input_type == "image":
            if isinstance(user_input, Image.Image):
                content_parts.append("Extract purchase details from this receipt/image:")
                content_parts.append(user_input)
            else:
                content_parts.append(f"Image provided (bytes length: {len(user_input)})")
        elif input_type == "voice":
            content_parts.append(f"Transcribed voice input: {user_input}")
        
        # Generate response with Gemini
        generation_config = {
            "temperature": 0.1,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 500,
        }
        
        response = gemini_model.generate_content(
            content_parts,
            generation_config=generation_config
        )
        
        # Try to parse JSON from response
        try:
            # Extract JSON from response text
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
            
            result = json.loads(response_text)
            
            # Validate structure
            if "items" not in result or "total_amount" not in result:
                st.warning("⚠️ AI response format invalid, using mock data")
                return generate_mock_ai_response(sector, input_type)
            
            # Ensure proper data types
            for item in result["items"]:
                if not all(key in item for key in ["name", "qty", "price"]):
                    st.warning("⚠️ Item format invalid, using mock data")
                    return generate_mock_ai_response(sector, input_type)
                
                # Convert to proper types
                try:
                    item["qty"] = float(item["qty"])
                    item["price"] = float(item["price"])
                except (ValueError, TypeError):
                    st.warning("⚠️ Quantity/price conversion failed, using mock data")
                    return generate_mock_ai_response(sector, input_type)
            
            result["total_amount"] = float(result["total_amount"])
            
            # Add metadata
            result["processing_mode"] = "ai"
            result["sector"] = sector
            result["timestamp"] = datetime.now().isoformat()
            
            return result
            
        except json.JSONDecodeError as e:
            st.error(f"❌ Failed to parse AI response: {str(e)}")
            st.info("Response text was:")
            st.code(response_text[:200] + "...")
            return generate_mock_ai_response(sector, input_type)
            
    except Exception as e:
        st.error(f"❌ Processing error: {str(e)}")
        return {"error": str(e), "items": [], "total_amount": 0.0}

# ==================== DATABASE LAYER ====================
def sync_to_supabase(data: Dict[str, Any], table_name: str = "purchases") -> Dict[str, Any]:
    """
    Sync data to Supabase or mock database
    
    Args:
        data: Data to sync
        table_name: Table name (purchases, users, inventory, ai_insights)
    
    Returns:
        Dictionary with sync result
    """
    try:
        _, supabase_client, connection_status = init_connections()
        
        # If in mock mode or Supabase not available, use mock sync
        if connection_status["mode"] == "mock" or not connection_status["supabase_available"]:
            # Generate mock response
            mock_id = f"mock_{int(time.time())}_{random.randint(1000, 9999)}"
            
            # Store in session state for demo
            if "mock_purchases" not in st.session_state:
                st.session_state.mock_purchases = []
            
            data_to_store = {
                "id": mock_id,
                "items": data.get("items", []),
                "total_amount": data.get("total_amount", 0),
                "sector": data.get("sector", "Unknown"),
                "created_at": datetime.now().isoformat(),
                "shop_name": st.session_state.user_profile.get("shop_name", "Unknown Shop"),
                "user_id": st.session_state.user_profile.get("user_id", "mock_user")
            }
            
            st.session_state.mock_purchases.append(data_to_store)
            
            return {
                "success": True,
                "message": "✅ Data saved (mock mode)",
                "id": mock_id,
                "data": data_to_store
            }
        
        # Prepare data for Supabase
        db_data = {
            "items": json.dumps(data.get("items", [])),
            "total_amount": float(data.get("total_amount", 0)),
            "sector": data.get("sector", "Unknown"),
            "shop_name": st.session_state.user_profile.get("shop_name", "Unknown Shop"),
            "user_id": st.session_state.user_profile.get("user_id", "demo_user"),
            "processing_mode": data.get("processing_mode", "unknown"),
            "metadata": json.dumps({
                "item_count": len(data.get("items", [])),
                "timestamp": data.get("timestamp", datetime.now().isoformat())
            })
        }
        
        # Insert into Supabase
        response = supabase_client.table(table_name).insert(db_data).execute()
        
        if hasattr(response, 'data') and response.data:
            return {
                "success": True,
                "message": f"✅ Data synced to {table_name}",
                "id": response.data[0].get("id"),
                "data": response.data[0]
            }
        else:
            return {
                "success": False,
                "error": "No data returned from Supabase",
                "message": "Using mock storage instead"
            }
            
    except Exception as e:
        st.error(f"❌ Database error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Using mock storage"
        }

def get_historical_purchases(limit: int = 10) -> List[Dict[str, Any]]:
    """Get historical purchases from Supabase or mock data"""
    try:
        _, supabase_client, connection_status = init_connections()
        
        if connection_status["mode"] == "live" and connection_status["supabase_available"]:
            # Get from Supabase
            shop_name = st.session_state.user_profile.get("shop_name", "")
            response = supabase_client.table("purchases")\
                .select("*")\
                .eq("shop_name", shop_name)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            if hasattr(response, 'data'):
                return response.data
        else:
            # Get from mock data
            if "mock_purchases" in st.session_state:
                return st.session_state.mock_purchases[-limit:]
    
    except Exception as e:
        st.warning(f"⚠️ Could not fetch historical data: {str(e)}")
    
    return []

# ==================== MOCK DATABASE LAYER (Original) ====================
def save_user_profile(data):
    """Mock function simulating database save - preserved from original"""
    print(f"[MOCK DB] Saving user profile: {data}")
    # Generate user ID for mock
    data["user_id"] = "user_" + str(hash(str(data)))[:8]
    return {
        "success": True,
        "user_id": data["user_id"],
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
    if 'ai_scans' not in st.session_state:
        st.session_state.ai_scans = []
    if 'show_scanner' not in st.session_state:
        st.session_state.show_scanner = False
    if 'processing_result' not in st.session_state:
        st.session_state.processing_result = None

def reset_application():
    """Reset application to initial state"""
    keys_to_keep = ['_streamlit_rerun_count']
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    st.rerun()

# ==================== UI COMPONENTS (Original - Preserved) ====================
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

# ==================== NEW AI SCANNER COMPONENT ====================
def render_ai_scanner():
    """AI Scanner component for receipt/input processing"""
    st.markdown("---")
    st.subheader("🤖 AI Receipt Scanner")
    
    # Scanner mode selection
    scanner_mode = st.radio(
        "Choose scanning method:",
        ["📝 Text Input", "📸 Camera/Image", "🎤 Voice (Mock)"],
        horizontal=True,
        key="scanner_mode"
    )
    
    processing_result = None
    
    if scanner_mode == "📝 Text Input":
        # Text input for purchase description
        purchase_text = st.text_area(
            "Enter purchase description:",
            placeholder="e.g., 'Bought 2 kg apples at $3/kg, 1 liter milk for $2.5, and 3 bread loaves at $1.5 each'",
            height=100
        )
        
        if st.button("🚀 Process with AI", type="primary", use_container_width=True):
            if purchase_text:
                with st.spinner("🤖 AI is analyzing your purchase..."):
                    processing_result = process_retail_input(purchase_text, st.session_state.user_sector, "text")
                    st.session_state.processing_result = processing_result
            else:
                st.warning("Please enter a purchase description")
    
    elif scanner_mode == "📸 Camera/Image":
        # Camera and image upload
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Option 1: Take a photo**")
            camera_input = st.camera_input("Capture receipt", key="camera_capture")
            
            if camera_input:
                image = Image.open(camera_input)
                st.image(image, caption="Captured Image", use_container_width=True)
                
                if st.button("📸 Process This Image", use_container_width=True):
                    with st.spinner("🤖 AI is analyzing the image..."):
                        processing_result = process_retail_input(image, st.session_state.user_sector, "image")
                        st.session_state.processing_result = processing_result
        
        with col2:
            st.markdown("**Option 2: Upload an image**")
            uploaded_file = st.file_uploader(
                "Upload receipt/image",
                type=["jpg", "jpeg", "png"],
                key="file_uploader"
            )
            
            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_container_width=True)
                
                if st.button("📤 Process Uploaded Image", use_container_width=True):
                    with st.spinner("🤖 AI is analyzing the image..."):
                        processing_result = process_retail_input(image, st.session_state.user_sector, "image")
                        st.session_state.processing_result = processing_result
    
    elif scanner_mode == "🎤 Voice (Mock)":
        # Mock voice input (since st.audio_input doesn't exist)
        st.info("🎤 Voice input is in mock mode. Streamlit doesn't have native audio recording yet.")
        
        voice_options = [
            "I bought 3 t-shirts for $15 each and 2 jeans for $45 each",
            "Purchased 5 kg rice at $2/kg, 2 liters oil for $5 each",
            "Got 2 strips of paracetamol at $6 each and 1 vitamin C bottle for $12",
            "Bought 1 smartphone for $999 and 3 phone cases at $15 each"
        ]
        
        selected_voice = st.selectbox(
            "Select a sample voice input:",
            voice_options,
            key="voice_sample"
        )
        
        if st.button("🎤 Process Voice Input", type="primary", use_container_width=True):
            with st.spinner("🤖 AI is processing voice input..."):
                processing_result = process_retail_input(selected_voice, st.session_state.user_sector, "voice")
                st.session_state.processing_result = processing_result
    
    # Display processing result
    if st.session_state.processing_result:
        processing_result = st.session_state.processing_result
        
        if "error" in processing_result:
            st.error(f"❌ Error: {processing_result['error']}")
        else:
            st.success("✅ Purchase successfully extracted!")
            
            # Display results in columns
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.markdown("**📋 Extracted Items**")
                items_df = pd.DataFrame(processing_result["items"])
                if not items_df.empty:
                    items_df["total"] = items_df["qty"] * items_df["price"]
                    st.dataframe(
                        items_df.style.format({
                            "qty": "{:.2f}",
                            "price": "${:.2f}",
                            "total": "${:.2f}"
                        }),
                        use_container_width=True,
                        hide_index=True
                    )
            
            with col_right:
                st.markdown("**💰 Summary**")
                st.metric("Total Amount", f"${processing_result['total_amount']:.2f}")
                st.metric("Number of Items", len(processing_result["items"]))
                
                # Save to database button
                if st.button("💾 Save to Database", type="secondary", use_container_width=True):
                    with st.spinner("Saving to database..."):
                        save_result = sync_to_supabase(processing_result)
                        
                        if save_result.get("success"):
                            st.success(save_result["message"])
                            st.session_state.ai_scans.append({
                                "result": processing_result,
                                "save_result": save_result,
                                "timestamp": datetime.now().isoformat()
                            })
                            
                            # Show saved data
                            with st.expander("📊 View Saved Data"):
                                st.json(save_result.get("data", {}))
                        else:
                            st.error(f"Failed to save: {save_result.get('message', 'Unknown error')}")
            
            # Test AI button (for demonstration)
            if st.button("🧪 Test Another Sample", type="secondary"):
                st.session_state.processing_result = None
                st.rerun()

# ==================== ENHANCED DASHBOARD ====================
def render_dashboard():
    """Step 4: Main Dashboard with AI Scanner integration"""
    sector = st.session_state.user_sector
    sector_icon = SECTOR_ICONS.get(sector, "🛍️")
    shop_name = st.session_state.user_profile.get('shop_name', 'Your Shop')
    
    # Dashboard header with scanner toggle
    col_header1, col_header2 = st.columns([3, 1])
    
    with col_header1:
        st.title(f"{sector_icon} {shop_name} Dashboard")
        st.markdown(f"*{sector} • {st.session_state.selected_plan} Plan*")
    
    with col_header2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📱 Toggle AI Scanner", use_container_width=True):
            st.session_state.show_scanner = not st.session_state.get('show_scanner', False)
            st.rerun()
    
    # Dashboard metrics - with real/simulated data
    st.markdown("---")
    st.subheader("📊 Live Metrics")
    
    # Get historical data for metrics
    historical_data = get_historical_purchases(limit=20)
    
    # Calculate metrics from historical data
    if historical_data:
        total_sales = sum(item.get("total_amount", 0) for item in historical_data)
        avg_sale = total_sales / len(historical_data) if len(historical_data) > 0 else 0
        item_count = sum(len(item.get("items", [])) for item in historical_data)
    else:
        # Fallback to mock metrics
        total_sales = 2847 + random.randint(-200, 200)
        avg_sale = 89 + random.randint(-10, 10)
        item_count = 147
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Today's Sales", f"${total_sales:,.2f}", "+12%")
    
    with col2:
        st.metric("Avg. Transaction", f"${avg_sale:,.2f}", "+5%")
    
    with col3:
        st.metric("Items Processed", item_count, "+8%")
    
    with col4:
        # Connection status indicator
        _, _, connection_status = init_connections()
        status_icon = "🟢" if connection_status["mode"] == "live" else "🟡"
        status_text = "Live" if connection_status["mode"] == "live" else "Demo"
        st.metric("AI Status", f"{status_icon} {status_text}")
    
    # Show AI Scanner if toggled
    if st.session_state.get('show_scanner', False):
        render_ai_scanner()
    
    # Main content area
    st.markdown("---")
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 Key Metrics")
        
        # Sector-specific metrics (enhanced with real data)
        if sector == GROCERY:
            st.info(f"**Fresh Produce Turnover:** 2.3 days")
            st.info(f"**Total Items Processed:** {item_count}")
            st.info(f"**Avg. Transaction Value:** ${avg_sale:.2f}")
        
        elif sector == PHARMACY:
            st.info(f"**Transactions Today:** {len(historical_data)}")
            st.info(f"**Total Sales:** ${total_sales:.2f}")
            st.info(f"**Avg. Items per Sale:** {item_count/len(historical_data):.1f}" if historical_data else "**Ready to scan!**")
        
        elif sector == APPAREL:
            st.info(f"**Items in Inventory:** {item_count * 10}")
            st.info(f"**Sales Trend:** +12% WoW")
            st.info(f"**Return Rate:** 4.2%")
        
        elif sector == ELECTRONICS:
            st.info(f"**Warranty Items:** {item_count}")
            st.info(f"**Cross-sell Rate:** 22%")
            st.info(f"**Avg. Ticket:** ${avg_sale:.2f}")
        
        else:
            st.info(f"**Sales Growth:** +12% MoM")
            st.info(f"**Inventory Turnover:** 45 days")
            st.info(f"**Customer Satisfaction:** 4.7/5")
        
        # Show recent scans if available
        if st.session_state.ai_scans:
            st.markdown("---")
            st.subheader("🕐 Recent Scans")
            for i, scan in enumerate(st.session_state.ai_scans[-3:], 1):
                result = scan.get("result", {})
                with st.expander(f"Scan {i}: {len(result.get('items', []))} items"):
                    st.metric("Total", f"${result.get('total_amount', 0):.2f}")
                    for item in result.get('items', []):
                        st.write(f"• {item.get('name')}: {item.get('qty')} × ${item.get('price'):.2f}")
    
    with col_right:
        st.subheader("🤖 AI Insights")
        
        # Connection status info
        _, _, connection_status = init_connections()
        
        if connection_status["mode"] == "live":
            if st.session_state.selected_plan == AI_PRO_PLAN:
                # AI Pro insights
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
                
                # Test AI button
                if st.button("🧪 Test AI Processing", type="secondary", use_container_width=True):
                    with st.spinner("Testing AI with sample data..."):
                        test_input = "2 kg apples at $3 per kg and 1 bread for $2.5"
                        test_result = process_retail_input(test_input, sector, "text")
                        st.info(f"AI Test Result: {len(test_result.get('items', []))} items, Total: ${test_result.get('total_amount', 0):.2f}")
            else:
                st.warning("**Upgrade to AI Pro** for advanced insights and sector-specific features!")
                st.info("Basic plan includes essential tracking and analytics.")
        else:
            st.info("**Demo Mode Active**")
            st.info("Connect your Gemini AI and Supabase credentials for live AI features.")
            if st.button("🔄 Test Demo AI", use_container_width=True):
                with st.spinner("Running demo AI..."):
                    test_result = generate_mock_ai_response(sector)
                    st.success(f"Demo AI Result: {len(test_result.get('items', []))} items extracted")
    
    # Recent transactions/historical data
    st.markdown("---")
    st.subheader("📋 Transaction History")
    
    if historical_data:
        # Create dataframe from historical data
        history_list = []
        for transaction in historical_data[-10:]:  # Last 10 transactions
            items = transaction.get("items", [])
            if isinstance(items, str):
                try:
                    items = json.loads(items)
                except:
                    items = []
            
            for item in items:
                history_list.append({
                    "Date": transaction.get("created_at", "")[:10],
                    "Item": item.get("name", ""),
                    "Qty": item.get("qty", 0),
                    "Price": f"${item.get('price', 0):.2f}",
                    "Total": f"${item.get('qty', 0) * item.get('price', 0):.2f}"
                })
        
        if history_list:
            history_df = pd.DataFrame(history_list)
            st.dataframe(history_df, use_container_width=True, hide_index=True)
        else:
            st.info("No transaction details available in history.")
    else:
        # Fallback to mock data
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
        st.caption("*Sample data - connect to Supabase for real transaction history*")

# ==================== ENHANCED SIDEBAR ====================
def render_sidebar():
    """Dynamic sidebar based on user sector with backend status"""
    with st.sidebar:
        # Show connection status at top
        _, _, connection_status = init_connections()
        
        if connection_status["mode"] == "live":
            status_color = "🟢"
            status_text = "Live Mode"
        else:
            status_color = "🟡"
            status_text = "Demo Mode"
        
        st.caption(f"{status_color} {status_text}")
        
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
            
            # Enhanced menu items with AI scanner
            menu_items = ["📊 Dashboard", "📦 Inventory", "📈 Analytics", "🤖 AI Scanner"]
            
            # Add sector-specific menu items
            if sector == GROCERY:
                menu_items.append("🛒 Tezi Mandi")
            elif sector == PHARMACY:
                menu_items.append("💊 Expiry Tracker")
            elif sector == APPAREL:
                menu_items.append("👕 Style Advisor")
            elif sector == ELECTRONICS:
                menu_items.append("🔧 Warranty Manager")
            
            menu_items.extend(["💾 Database", "⚙️ Settings"])
            
            # Display menu with handlers
            for item in menu_items:
                if st.button(item, use_container_width=True):
                    if item == "🤖 AI Scanner":
                        st.session_state.show_scanner = not st.session_state.get('show_scanner', False)
                        st.rerun()
                    elif item == "💾 Database":
                        # Show database info
                        with st.expander("Database Info", expanded=False):
                            st.write("**Connection Status:**", connection_status)
                            if st.session_state.get('ai_scans'):
                                st.write(f"**Scans in Session:** {len(st.session_state.ai_scans)}")
                            if st.session_state.get('mock_purchases'):
                                st.write(f"**Mock Transactions:** {len(st.session_state.mock_purchases)}")
            
            st.markdown("---")
            
            # Quick actions
            st.markdown("**Quick Actions**")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📱 Scan", use_container_width=True):
                    st.session_state.show_scanner = True
                    st.rerun()
            
            with col2:
                if st.button("🔄 Refresh", use_container_width=True):
                    st.rerun()
            
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
            
            # Show backend status
            with st.expander("Backend Status", expanded=False):
                st.write("**Mode:**", connection_status["mode"])
                st.write("**Gemini AI:**", "✅ Connected" if connection_status["gemini_available"] else "❌ Not connected")
                st.write("**Supabase:**", "✅ Connected" if connection_status["supabase_available"] else "❌ Not connected")

# ==================== MAIN APPLICATION ====================
def main():
    """Main application router"""
    # Page configuration
    st.set_page_config(
        page_title="RetailPulse AI",
        page_icon="🛍️",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/yourusername/retailpulse-ai',
            'Report a bug': 'https://github.com/yourusername/retailpulse-ai/issues',
            'About': "# RetailPulse AI\nIntelligent Retail Management Platform"
        }
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize connections (cached)
    init_connections()
    
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
    st.sidebar.caption("©️ 2025 RetailPulse AI v3.0")
    st.sidebar.caption("AI-Powered Retail Management")

# ==================== RUN APPLICATION ====================
if __name__ == "__main__":
    main()
