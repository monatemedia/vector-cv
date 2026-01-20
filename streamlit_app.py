import streamlit as st
import streamlit_authenticator as stauth
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- 1. CONFIGURATION & AUTH SETUP ---
API_URL = "http://localhost:8010"

st.set_page_config(
    page_title="Resume Synthesizer",
    page_icon="📄",
    layout="wide"
)

# Fetch credentials from your .env file
user_name = os.getenv("AUTH_USERNAME", "user")
user_password = os.getenv("AUTH_PASSWORD", "password")
full_name = os.getenv("AUTH_NAME", "Admin User")

# Define credentials dictionary
credentials = {
    "usernames": {
        user_name: {
            "name": full_name,
            "password": user_password
        }
    }
}

# Hash passwords in-place
stauth.Hasher.hash_passwords(credentials)

# Initialize Authenticator
authenticator = stauth.Authenticate(
    credentials,
    os.getenv("COOKIE_NAME", "resume_synthesizer_auth"),
    os.getenv("COOKIE_KEY", "some_very_random_secret_string"),
    cookie_expiry_days=30
)

# --- 2. RENDER LOGIN ---
# This call handles the session state internally
authenticator.login(location='main')

# --- 3. AUTHENTICATION LOGIC ---
# Use session_state to check status (most reliable for v0.4.0+)
if st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
elif st.session_state["authentication_status"]:

    # --- 4. CUSTOM CSS ---
    st.markdown("""
    <style>
        .main-header { font-size: 2.5rem; font-weight: bold; color: #1f77b4; margin-bottom: 1rem; }
        .sub-header { font-size: 1.5rem; font-weight: bold; color: #2c3e50; margin-top: 2rem; margin-bottom: 1rem; }
        .success-box { padding: 1rem; border-radius: 0.5rem; background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
        .info-box { padding: 1rem; border-radius: 0.5rem; background-color: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; }
    </style>
    """, unsafe_allow_html=True)

    # --- 5. SIDEBAR NAVIGATION & LOGOUT ---
    st.sidebar.markdown(f"# 📄 Welcome, {st.session_state['name']}")
    
    # 1. Define the page first so it's always available to the logic below
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Dashboard", "👤 Personal Info", "💼 Experience", "🎨 Style Guidelines", "📝 Applications"]
    )

    st.sidebar.markdown("---")

    # 2. Handle Logout
    authenticator.logout('Logout', 'sidebar')
    
    # 3. If logout was just clicked, the status changes. 
    # We check this to prevent the rest of the script from running with 'None' credentials.
    if st.session_state["authentication_status"] is not True:
        st.rerun()

    # --- 6. API HELPER FUNCTIONS ---
    def api_get(endpoint):
        try:
            response = requests.get(f"{API_URL}{endpoint}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return None

    def api_post(endpoint, data):
        try:
            response = requests.post(f"{API_URL}{endpoint}", json=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return None

    def api_delete(endpoint):
        try:
            response = requests.delete(f"{API_URL}{endpoint}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return None

    # --- 7. PAGE CONTENT ---

    if page == "🏠 Dashboard":
        st.markdown('<div class="main-header">📊 Dashboard</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        experiences = api_get("/api/experience-blocks")
        applications = api_get("/api/applications")
        
        with col1:
            st.metric("Experience Blocks", len(experiences) if experiences else 0)
        with col2:
            st.metric("Total Applications", len(applications) if applications else 0)
        with col3:
            applied_count = len([a for a in (applications or []) if a.get('status') == 'applied'])
            st.metric("Applied", applied_count)
        
        st.markdown("---")
        st.markdown('<div class="sub-header">🚀 Quick Start Guide</div>', unsafe_allow_html=True)
        st.markdown("1. Add **Personal Info**\n2. Add **Experience Blocks**\n3. Define **Style Guidelines**\n4. Create **Applications**")

    elif page == "👤 Personal Info":
        st.markdown('<div class="main-header">👤 Personal Information</div>', unsafe_allow_html=True)
        existing_info = api_get("/api/personal-info")
        with st.form("personal_info_form"):
            p_name = st.text_input("Full Name *", value=existing_info.get('name', '') if existing_info else '')
            email = st.text_input("Email", value=existing_info.get('email', '') if existing_info else '')
            summary = st.text_area("Professional Summary", value=existing_info.get('summary', '') if existing_info else '', height=150)
            if st.form_submit_button("💾 Save Personal Info"):
                data = {"name": p_name, "email": email, "summary": summary}
                if api_post("/api/personal-info", data):
                    st.success("✅ Saved!")
                    st.rerun()

    elif page == "💼 Experience":
        st.markdown('<div class="main-header">💼 Experience Blocks</div>', unsafe_allow_html=True)
        with st.expander("➕ Add New Experience Block", expanded=True):
            with st.form("experience_form", clear_on_submit=True):
                title = st.text_input("Job Title / Project Name *")
                content = st.text_area("Description *", height=200)
                tags_input = st.text_input("Skills (comma-separated) *")
                if st.form_submit_button("💾 Add Experience"):
                    tags = [tag.strip() for tag in tags_input.split(',')]
                    data = {"title": title, "content": content, "metadata_tags": tags}
                    if api_post("/api/experience-blocks", data):
                        st.success("✅ Added!")
                        st.rerun()
        
        experiences = api_get("/api/experience-blocks")
        if experiences:
            for exp in experiences:
                with st.expander(f"{exp['title']}"):
                    st.write(exp['content'])
                    if st.button("🗑️ Delete", key=f"del_{exp['id']}"):
                        api_delete(f"/api/experience-blocks/{exp['id']}")
                        st.rerun()

    elif page == "🎨 Style Guidelines":
        st.markdown('<div class="main-header">🎨 Style Guidelines</div>', unsafe_allow_html=True)
        with st.form("style_form"):
            g_name = st.text_input("Guideline Name")
            g_desc = st.text_area("Description")
            if st.form_submit_button("💾 Save Guideline"):
                api_post("/api/style-guidelines", {"name": g_name, "description": g_desc, "is_active": "true"})
                st.rerun()

    elif page == "📝 Applications":
        st.markdown('<div class="main-header">📝 Applications</div>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["➕ Create", "📋 View"])
        with tab1:
            with st.form("app_form"):
                comp = st.text_input("Company")
                pos = st.text_input("Position")
                desc = st.text_area("Job Description")
                if st.form_submit_button("🚀 Generate"):
                    api_post("/api/applications", {"company_name": comp, "job_title": pos, "raw_spec": desc})
                    st.rerun()
        with tab2:
            apps = api_get("/api/applications")
            if apps:
                for a in apps:
                    with st.expander(f"{a['job_title']} at {a['company_name']}"):
                        st.write(f"Status: {a['status']}")
                        if st.checkbox("View CV", key=f"v_{a['id']}"):
                            st.text_area("CV", a['generated_cv'], height=300)