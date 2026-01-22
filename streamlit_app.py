import streamlit as st
import streamlit_authenticator as stauth
import requests
import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from collections import defaultdict

# Load environment variables
load_dotenv()

# --- RATE LIMITING FOR LOGIN ATTEMPTS ---
login_attempts = defaultdict(list)

def check_login_rate_limit():
    """Limit to 3 failed login attempts per hour by IP"""
    if 'client_ip' not in st.session_state:
        # Try to get real IP from headers (works with most reverse proxies)
        try:
            st.session_state.client_ip = st.context.headers.get("X-Forwarded-For", "unknown").split(",")[0]
        except:
            st.session_state.client_ip = "unknown"
    
    client_ip = st.session_state.client_ip
    now = datetime.now()
    
    # Clean old attempts (older than 1 hour)
    login_attempts[client_ip] = [
        attempt_time for attempt_time in login_attempts[client_ip]
        if (now - attempt_time).total_seconds() < 3600
    ]
    
    # Check if limit exceeded
    if len(login_attempts[client_ip]) >= 3:
        st.error("🔒 Too many failed login attempts. Please try again in 1 hour.")
        st.stop()

def log_failed_login():
    """Log a failed login attempt"""
    client_ip = st.session_state.get('client_ip', 'unknown')
    login_attempts[client_ip].append(datetime.now())

# --- 1. CONFIGURATION & AUTH SETUP ---
API_URL = os.getenv("API_URL", "http://localhost:8010")
ADMIN_KEY = os.getenv("ADMIN_API_KEY", "your_super_secret_key_here")
BACKUP_DIR = "./backups"
MY_DATA_DIR = "./my_data"
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(MY_DATA_DIR, exist_ok=True)

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

# --- 2. CHECK RATE LIMIT BEFORE LOGIN ---
check_login_rate_limit()

# --- 3. RENDER LOGIN ---
authenticator.login(location='main')

# --- 4. AUTHENTICATION LOGIC ---
if st.session_state["authentication_status"] is False:
    log_failed_login()
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
elif st.session_state["authentication_status"]:

    # --- 5. CUSTOM CSS ---
    st.markdown("""
    <style>
        .main-header { font-size: 2.5rem; font-weight: bold; color: #1f77b4; margin-bottom: 1rem; }
        .sub-header { font-size: 1.5rem; font-weight: bold; color: #2c3e50; margin-top: 2rem; margin-bottom: 1rem; }
        .success-box { padding: 1rem; border-radius: 0.5rem; background-color: #d4edda; border: 1px solid #c3e6cb; color: #155724; }        
        .info-box { padding: 1rem; border-radius: 0.5rem; background-color: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; }
        .warning-box { padding: 1rem; border-radius: 0.5rem; background-color: #fff3cd; border: 1px solid #ffeeba; color: #856404; }
    </style>
    """, unsafe_allow_html=True)

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
            headers = {"Authorization": f"Bearer {ADMIN_KEY}"}
            response = requests.post(f"{API_URL}{endpoint}", json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return None

    def api_put(endpoint, data):
        try:
            headers = {"Authorization": f"Bearer {ADMIN_KEY}"}
            response = requests.put(f"{API_URL}{endpoint}", json=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return None

    def api_delete(endpoint):
        try:
            headers = {"Authorization": f"Bearer {ADMIN_KEY}"}
            response = requests.delete(f"{API_URL}{endpoint}", headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"API Error: {str(e)}")
            return None

    # --- 7. BACKUP FUNCTIONS ---
    def export_to_json_file():
        """Export data via API and save to file"""
        try:
            data = api_get("/api/export-data")
            if not data:
                return None
            
            # Create timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"my_data.json.backup-{timestamp}"
            filepath = os.path.join(BACKUP_DIR, filename)
            
            # Save to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return filepath
        except Exception as e:
            st.error(f"Backup failed: {str(e)}")
            return None

    def list_backups():
        """List all available backup files"""
        backup_files = sorted(
            [f for f in os.listdir(BACKUP_DIR) if f.startswith("my_data.json.backup-")],
            reverse=True
        )
        return backup_files

    def import_from_json_file(filepath):
        """Import data from JSON file via API"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Send to API
            result = api_post("/api/import-data", data)
            
            if result:
                st.success(f"✅ Imported {result.get('imported_blocks', 0)} experience blocks")
                return True
            return False
        except Exception as e:
            st.error(f"Import failed: {str(e)}")
            return False

    def validate_json_structure(data):
        """Validate JSON has required structure"""
        required_keys = ["personal_info", "experience_blocks"]
        if not all(key in data for key in required_keys):
            return False, f"Missing required keys: {', '.join([k for k in required_keys if k not in data])}"
        
        # Validate personal_info
        if not isinstance(data["personal_info"], dict):
            return False, "personal_info must be an object"
        
        if "name" not in data["personal_info"]:
            return False, "personal_info must contain 'name' field"
        
        # Validate experience_blocks
        if not isinstance(data["experience_blocks"], list):
            return False, "experience_blocks must be an array"
        
        for i, block in enumerate(data["experience_blocks"]):
            if not isinstance(block, dict):
                return False, f"experience_blocks[{i}] must be an object"
            
            required_block_keys = ["title", "content", "tags"]
            missing = [k for k in required_block_keys if k not in block]
            if missing:
                return False, f"experience_blocks[{i}] missing: {', '.join(missing)}"
        
        return True, "Valid structure"

    def compare_backups(backup1_path, backup2_path):
        """Compare two backup files and show differences"""
        try:
            with open(backup1_path, 'r') as f1, open(backup2_path, 'r') as f2:
                data1 = json.load(f1)
                data2 = json.load(f2)
            
            differences = []
            
            # Compare personal info
            if data1["personal_info"] != data2["personal_info"]:
                differences.append("Personal info has changed")
            
            # Compare experience blocks count
            count1 = len(data1["experience_blocks"])
            count2 = len(data2["experience_blocks"])
            if count1 != count2:
                differences.append(f"Experience blocks: {count1} → {count2}")
            
            # Compare block titles
            titles1 = set(b["title"] for b in data1["experience_blocks"])
            titles2 = set(b["title"] for b in data2["experience_blocks"])
            
            added = titles2 - titles1
            removed = titles1 - titles2
            
            if added:
                differences.append(f"Added blocks: {', '.join(added)}")
            if removed:
                differences.append(f"Removed blocks: {', '.join(removed)}")
            
            return differences if differences else ["No differences found"]
        
        except Exception as e:
            return [f"Comparison failed: {str(e)}"]

    # --- 8. SIDEBAR NAVIGATION & LOGOUT ---
    st.sidebar.markdown(f"# 📄 Welcome, {st.session_state['name']}")

    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Dashboard", "👤 Personal Info", "💼 Experience", "🎨 Style Guidelines", 
         "📝 Applications", "💾 Backup Manager", "📊 Analytics"]
    )

    st.sidebar.markdown("---")
    authenticator.logout('Logout', 'sidebar')

    if st.session_state["authentication_status"] is not True:
        st.rerun()

    # --- 9. PAGE CONTENT ---

    if page == "🏠 Dashboard":
        st.markdown('<div class="main-header">📊 Dashboard</div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        experiences = api_get("/api/experience-blocks")
        applications = api_get("/api/applications")

        with col1:
            st.metric("Experience Blocks", len(experiences) if experiences else 0)
        with col2:
            st.metric("Total Applications", len(applications) if applications else 0)
        with col3:
            applied_count = len([a for a in (applications or []) if a.get('status') == 'applied'])
            st.metric("Applied", applied_count)
        with col4:
            backups = list_backups()
            st.metric("Backups", len(backups))

        st.markdown("---")
        st.markdown('<div class="sub-header">🚀 Quick Start Guide</div>', unsafe_allow_html=True)
        st.markdown("1. Add **Personal Info**\n2. Add **Experience Blocks**\n3. Define **Style Guidelines**\n4. Create **Applications**")
        
        # Recent activity
        if applications:
            st.markdown("---")
            st.markdown("### Recent Applications")
            recent_apps = sorted(applications, key=lambda x: x['created_at'], reverse=True)[:5]
            for app in recent_apps:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{app['job_title']}** at {app['company_name']}")
                with col2:
                    st.write(f"Status: {app['status']}")
                with col3:
                    created_date = datetime.fromisoformat(app['created_at'].replace('Z', '+00:00'))
                    st.write(created_date.strftime("%Y-%m-%d"))

    elif page == "👤 Personal Info":
        st.markdown('<div class="main-header">👤 Personal Information</div>', unsafe_allow_html=True)
        existing_info = api_get("/api/personal-info")
        with st.form("personal_info_form"):
            p_name = st.text_input("Full Name *", value=existing_info.get('name', '') if existing_info else '')
            email = st.text_input("Email", value=existing_info.get('email', '') if existing_info else '')
            phone = st.text_input("Phone", value=existing_info.get('phone', '') if existing_info else '')
            location = st.text_input("Location", value=existing_info.get('location', '') if existing_info else '')
            
            col1, col2, col3 = st.columns(3)
            with col1:
                linkedin = st.text_input("LinkedIn", value=existing_info.get('linkedin', '') if existing_info else '')
            with col2:
                github = st.text_input("GitHub", value=existing_info.get('github', '') if existing_info else '')
            with col3:
                portfolio = st.text_input("Portfolio", value=existing_info.get('portfolio', '') if existing_info else '')
            
            summary = st.text_area("Professional Summary", value=existing_info.get('summary', '') if existing_info else '', height=150)
            
            if st.form_submit_button("💾 Save Personal Info"):
                data = {
                    "name": p_name,
                    "email": email,
                    "phone": phone,
                    "location": location,
                    "linkedin": linkedin,
                    "github": github,
                    "portfolio": portfolio,
                    "summary": summary
                }
                if api_post("/api/personal-info", data):
                    st.success("✅ Saved!")
                    st.rerun()

    elif page == "💼 Experience":
        st.markdown('<div class="main-header">💼 Experience Blocks</div>', unsafe_allow_html=True)
        
        # Filters
        with st.expander("🔍 Filter & Search"):
            col1, col2, col3 = st.columns(3)
            with col1:
                filter_type = st.selectbox(
                    "Block Type",
                    ["All", "pillar_project", "supporting_project", "employment", "education", "skills_summary"]
                )
            with col2:
                filter_priority = st.selectbox("Priority", ["All", "1", "2", "3", "4", "5"])
            with col3:
                search_term = st.text_input("Search", placeholder="Title, company, or content...")
        
        # Add/Edit Experience Block
        if 'editing_block_id' not in st.session_state:
            st.session_state.editing_block_id = None
        
        # Determine if we're editing
        is_editing = st.session_state.editing_block_id is not None
        edit_block = None
        
        if is_editing:
            # Fetch the block being edited
            edit_block = api_get(f"/api/experience-blocks/{st.session_state.editing_block_id}")
            expander_title = f"✏️ Edit: {edit_block['title']}" if edit_block else "➕ Add New Experience Block"
        else:
            expander_title = "➕ Add New Experience Block"
        
        with st.expander(expander_title, expanded=True):
            with st.form("experience_form", clear_on_submit=not is_editing):
                if edit_block:
                    title = st.text_input("Job Title / Project Name *", value=edit_block.get('title', ''))
                    company = st.text_input("Company Name", value=edit_block.get('company', ''))
                    content = st.text_area("Description *", value=edit_block.get('content', ''), height=200)
                    tags_input = st.text_input("Skills (comma-separated) *", value=', '.join(edit_block.get('metadata_tags', [])))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        current_type = edit_block.get('block_type', 'supporting_project')
                        type_options = ["pillar_project", "supporting_project", "employment", "education", "skills_summary"]
                        type_index = type_options.index(current_type) if current_type in type_options else 1
                        block_type = st.selectbox("Block Type", type_options, index=type_index)
                    with col2:
                        current_priority = edit_block.get('priority', '3')
                        priority_index = int(current_priority) - 1 if current_priority.isdigit() else 2
                        priority = st.selectbox("Priority", ["1", "2", "3", "4", "5"], index=priority_index)
                else:
                    title = st.text_input("Job Title / Project Name *")
                    company = st.text_input("Company Name")
                    content = st.text_area("Description *", height=200)
                    tags_input = st.text_input("Skills (comma-separated) *")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        block_type = st.selectbox(
                            "Block Type",
                            ["pillar_project", "supporting_project", "employment", "education", "skills_summary"],
                            index=1
                        )
                    with col2:
                        priority = st.selectbox("Priority", ["1", "2", "3", "4", "5"], index=2)
                
                col1, col2 = st.columns(2)
                with col1:
                    submit_label = "💾 Update Experience" if is_editing else "💾 Add Experience"
                    if st.form_submit_button(submit_label):
                        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                        data = {
                            "title": title,
                            "company": company,
                            "content": content,
                            "metadata_tags": tags,
                            "block_type": block_type,
                            "priority": priority
                        }
                        
                        if is_editing:
                            if api_put(f"/api/experience-blocks/{st.session_state.editing_block_id}", data):
                                st.success("✅ Updated!")
                                st.session_state.editing_block_id = None
                                st.rerun()
                        else:
                            if api_post("/api/experience-blocks", data):
                                st.success("✅ Added!")
                                st.rerun()
                
                with col2:
                    if is_editing and st.form_submit_button("❌ Cancel Edit"):
                        st.session_state.editing_block_id = None
                        st.rerun()

        # Build query parameters
        params = []
        if filter_type != "All":
            params.append(f"block_type={filter_type}")
        if filter_priority != "All":
            params.append(f"priority={filter_priority}")
        if search_term:
            params.append(f"search={search_term}")
        
        query_string = "&".join(params)
        endpoint = f"/api/experience-blocks?{query_string}" if query_string else "/api/experience-blocks"
        
        experiences = api_get(endpoint)
        if experiences:
            st.markdown("---")
            st.markdown(f"### Existing Experience Blocks ({len(experiences)})")
            for exp in experiences:
                with st.expander(f"{exp['title']} ({exp.get('block_type', 'N/A')}) - Priority: {exp.get('priority', 'N/A')}"):
                    st.write(f"**Company:** {exp.get('company', 'N/A')}")
                    st.write(f"**Tags:** {', '.join(exp.get('metadata_tags', []))}")
                    st.write(exp['content'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✏️ Edit", key=f"edit_{exp['id']}"):
                            st.session_state.editing_block_id = exp['id']
                            st.rerun()
                    with col2:
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
        
        # Filter by status
        with st.expander("🔍 Filter Applications"):
            status_filter = st.selectbox(
                "Status",
                ["All", "draft", "applied", "interviewing", "rejected", "offer", "accepted"]
            )
        
        tab1, tab2 = st.tabs(["➕ Create", "📋 View & Manage"])
        
        with tab1:
            with st.form("app_form"):
                comp = st.text_input("Company")
                pos = st.text_input("Position")
                desc = st.text_area("Job Description", height=300)
                if st.form_submit_button("🚀 Generate"):
                    api_post("/api/applications", {"company_name": comp, "job_title": pos, "raw_spec": desc})
                    st.rerun()
        
        with tab2:
            # Fetch applications with filter
            endpoint = "/api/applications"
            if status_filter != "All":
                endpoint += f"?status={status_filter}"
            
            apps = api_get(endpoint)
            if apps:
                for a in apps:
                    with st.expander(f"{a['job_title']} at {a['company_name']} ({a['status']})"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Created:** {datetime.fromisoformat(a['created_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')}")
                            if a.get('applied_date'):
                                st.write(f"**Applied:** {datetime.fromisoformat(a['applied_date'].replace('Z', '+00:00')).strftime('%Y-%m-%d')}")
                        
                        with col2:
                            # Update status
                            new_status = st.selectbox(
                                "Update Status",
                                ["draft", "applied", "interviewing", "rejected", "offer", "accepted"],
                                index=["draft", "applied", "interviewing", "rejected", "offer", "accepted"].index(a['status']),
                                key=f"status_{a['id']}"
                            )
                            if new_status != a['status']:
                                if st.button("💾 Update Status", key=f"update_status_{a['id']}"):
                                    update_data = {"status": new_status}
                                    if new_status == "applied" and not a.get('applied_date'):
                                        update_data["applied_date"] = datetime.utcnow().isoformat()
                                    api_put(f"/api/applications/{a['id']}", update_data)
                                    st.rerun()
                        
                        # Notes
                        notes = st.text_area("Notes", value=a.get('notes', ''), key=f"notes_{a['id']}")
                        if notes != a.get('notes', ''):
                            if st.button("💾 Save Notes", key=f"save_notes_{a['id']}"):
                                api_put(f"/api/applications/{a['id']}", {"notes": notes})
                                st.rerun()
                        
                        if st.checkbox("View CV", key=f"v_{a['id']}"):
                            st.text_area("CV", a['generated_cv'], height=300, key=f"cv_text_{a['id']}")

    elif page == "💾 Backup Manager":
        st.markdown('<div class="main-header">💾 Backup Manager</div>', unsafe_allow_html=True)
        
        tab1, tab2, tab3, tab4 = st.tabs(["📤 Export", "📥 Import", "🗂️ Manage Backups", "🔄 Compare"])
        
        with tab1:
            st.markdown("### Export Current Data")
            st.info("Create a timestamped backup of all your current data from the database.")
            
            if st.button("📤 Create Backup Now", type="primary"):
                with st.spinner("Creating backup..."):
                    filepath = export_to_json_file()
                    if filepath:
                        st.success(f"✅ Backup created: {os.path.basename(filepath)}")
                        
                        # Offer download
                        with open(filepath, 'r') as f:
                            st.download_button(
                                label="⬇️ Download Backup",
                                data=f.read(),
                                file_name=os.path.basename(filepath),
                                mime="application/json"
                            )
        
        with tab2:
            st.markdown("### Import from Backup")
            st.markdown('<div class="warning-box">⚠️ <strong>Warning:</strong> Importing will update existing data in the database. Blocks with matching titles will be updated.</div>', unsafe_allow_html=True)
            
            # Option 1: Select from existing backups
            backups = list_backups()
            if backups:
                st.markdown("#### Select from Existing Backups")
                selected_backup = st.selectbox("Choose a backup:", backups)
                
                # Preview option
                if st.checkbox("Preview backup content"):
                    try:
                        with open(os.path.join(BACKUP_DIR, selected_backup), 'r') as f:
                            preview_data = json.load(f)
                        st.json(preview_data)
                    except Exception as e:
                        st.error(f"Failed to preview: {str(e)}")
                
                if st.button("📥 Import Selected Backup"):
                    with st.spinner("Importing..."):
                        filepath = os.path.join(BACKUP_DIR, selected_backup)
                        if import_from_json_file(filepath):
                            st.success("✅ Import complete!")
                            st.rerun()
            
            st.markdown("---")
            
            # Option 2: Upload new backup file
            st.markdown("#### Upload Backup File")
            uploaded_file = st.file_uploader("Upload a JSON backup file", type=['json'])
            if uploaded_file is not None:
                # Validate structure
                try:
                    upload_data = json.load(uploaded_file)
                    is_valid, message = validate_json_structure(upload_data)
                    
                    if is_valid:
                        st.success(f"✅ {message}")
                        
                        # Preview
                        if st.checkbox("Preview uploaded data"):
                            st.json(upload_data)
                        
                        if st.button("📥 Import Uploaded File"):
                            with st.spinner("Importing..."):
                                # Save uploaded file temporarily
                                temp_path = os.path.join(BACKUP_DIR, f"temp_{uploaded_file.name}")
                                uploaded_file.seek(0)  # Reset file pointer
                                with open(temp_path, 'wb') as f:
                                    f.write(uploaded_file.getbuffer())
                                
                                # Import from temp file
                                if import_from_json_file(temp_path):
                                    st.success("✅ Import complete!")
                                    st.rerun()
                                
                                # Clean up temp file
                                if os.path.exists(temp_path):
                                    os.remove(temp_path)
                    else:
                        st.error(f"❌ Invalid structure: {message}")
                
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON file")
        
        with tab3:
            st.markdown("### Manage Existing Backups")
            backups = list_backups()
            
            if not backups:
                st.info("No backups found. Create your first backup in the Export tab.")
            else:
                st.write(f"Found {len(backups)} backup(s):")
                
                for backup in backups:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        # Extract timestamp from filename
                        timestamp_str = backup.replace("my_data.json.backup-", "")
                        try:
                            dt = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                            display_name = dt.strftime("%Y-%m-%d %H:%M:%S")
                        except:
                            display_name = backup
                        st.write(f"📄 {display_name}")
                    
                    with col2:
                        filepath = os.path.join(BACKUP_DIR, backup)
                        with open(filepath, 'r') as f:
                            st.download_button(
                                label="⬇️",
                                data=f.read(),
                                file_name=backup,
                                mime="application/json",
                                key=f"download_{backup}"
                            )
                    
                    with col3:
                        if st.button("🗑️", key=f"delete_{backup}"):
                            try:
                                os.remove(filepath)
                                st.success(f"Deleted {backup}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to delete: {str(e)}")
        with tab4:
                st.markdown("### Compare Backups")
                st.info("Select two backups to see what changed between them.")
                
                backups = list_backups()
                if len(backups) < 2:
                    st.warning("You need at least 2 backups to compare.")
                else:
                    col1, col2 = st.columns(2)
                    with col1:
                        backup1 = st.selectbox("First backup (older)", backups, key="compare1")
                    with col2:
                        backup2 = st.selectbox("Second backup (newer)", [b for b in backups if b != backup1], key="compare2")
                    
                    if st.button("🔄 Compare Backups"):
                        if backup1 and backup2:
                            path1 = os.path.join(BACKUP_DIR, backup1)
                            path2 = os.path.join(BACKUP_DIR, backup2)
                            differences = compare_backups(path1, path2)
                            
                            st.markdown("#### Differences Found:")
                            for diff in differences:
                                st.write(f"- {diff}")

                    elif page == "📊 Analytics":
                        st.markdown('<div class="main-header">📊 Analytics Dashboard</div>', unsafe_allow_html=True)
                        
                        applications = api_get("/api/applications")
                        experiences = api_get("/api/experience-blocks")
                        
                        if applications and experiences:
                            # Application statistics
                            st.markdown("### Application Statistics")
                            col1, col2, col3 = st.columns(3)
                            
                            status_counts = {}
                            for app in applications:
                                status = app.get('status', 'draft')
                                status_counts[status] = status_counts.get(status, 0) + 1
                            
                            with col1:
                                st.metric("Total Applications", len(applications))
                            with col2:
                                success_rate = (status_counts.get('offer', 0) + status_counts.get('accepted', 0)) / len(applications) * 100
                                st.metric("Success Rate", f"{success_rate:.1f}%")
                            with col3:
                                interview_rate = status_counts.get('interviewing', 0) / len(applications) * 100 if len(applications) > 0 else 0
                                st.metric("Interview Rate", f"{interview_rate:.1f}%")
                            
                            # Status breakdown
                            st.markdown("### Status Breakdown")
                            status_data = {status: count for status, count in status_counts.items()}
                            st.bar_chart(status_data)
                            
                            # Skills analysis
                            st.markdown("### Skills Analysis")
                            st.info("Track which skills appear most frequently in your applications")
                            
                            # Count skill mentions
                            skill_counts = {}
                            for exp in experiences:
                                if exp.get('metadata_tags'):
                                    for tag in exp['metadata_tags']:
                                        skill_counts[tag] = skill_counts.get(tag, 0) + 1
                            
                            # Show top skills
                            if skill_counts:
                                sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                                skill_chart_data = {skill: count for skill, count in sorted_skills}
                                st.bar_chart(skill_chart_data)
                            
                            # Application timeline
                            st.markdown("### Application Timeline")
                            timeline_data = {}
                            for app in applications:
                                created_date = datetime.fromisoformat(app['created_at'].replace('Z', '+00:00')).strftime('%Y-%m')
                                timeline_data[created_date] = timeline_data.get(created_date, 0) + 1
                            
                            st.line_chart(timeline_data)
                        else:
                            st.info("Not enough data yet. Create some applications to see analytics.")