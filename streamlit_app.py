import streamlit as st
import requests
import json
from datetime import datetime

# Configuration
API_URL = "http://localhost:8010"

st.set_page_config(
    page_title="Resume Synthesizer",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("# 📄 Resume Synthesizer")
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "👤 Personal Info", "💼 Experience", "🎨 Style Guidelines", "📝 Applications"]
)

# Helper functions
def api_get(endpoint):
    try:
        response = requests.get(f"{API_URL}{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

def api_post(endpoint, data):
    try:
        response = requests.post(f"{API_URL}{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

def api_delete(endpoint):
    try:
        response = requests.delete(f"{API_URL}{endpoint}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return None

# Dashboard Page
if page == "🏠 Dashboard":
    st.markdown('<div class="main-header">📊 Dashboard</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    # Get stats
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
    
    # Quick Start Guide
    st.markdown('<div class="sub-header">🚀 Quick Start Guide</div>', unsafe_allow_html=True)
    st.markdown("""
    1. **Add Personal Info**: Fill in your basic contact information
    2. **Add Experience Blocks**: Add your work history, projects, and achievements
    3. **Set Style Guidelines** (Optional): Define how you want your CV formatted
    4. **Create Application**: Paste a job description and generate tailored CV + Cover Letter
    """)
    
    # Recent Applications
    if applications:
        st.markdown('<div class="sub-header">📋 Recent Applications</div>', unsafe_allow_html=True)
        for app in applications[:5]:
            with st.expander(f"{app['job_title']} at {app['company_name']} - {app['status']}"):
                st.write(f"**Created:** {app['created_at']}")
                st.write(f"**Status:** {app['status']}")

# Personal Info Page
elif page == "👤 Personal Info":
    st.markdown('<div class="main-header">👤 Personal Information</div>', unsafe_allow_html=True)
    
    # Try to load existing info
    existing_info = api_get("/api/personal-info")
    
    with st.form("personal_info_form"):
        name = st.text_input("Full Name *", value=existing_info.get('name', '') if existing_info else '')
        email = st.text_input("Email", value=existing_info.get('email', '') if existing_info else '')
        phone = st.text_input("Phone", value=existing_info.get('phone', '') if existing_info else '')
        location = st.text_input("Location", value=existing_info.get('location', '') if existing_info else '')
        linkedin = st.text_input("LinkedIn URL", value=existing_info.get('linkedin', '') if existing_info else '')
        github = st.text_input("GitHub URL", value=existing_info.get('github', '') if existing_info else '')
        portfolio = st.text_input("Portfolio URL", value=existing_info.get('portfolio', '') if existing_info else '')
        summary = st.text_area("Professional Summary", value=existing_info.get('summary', '') if existing_info else '', 
                              height=150)
        
        submitted = st.form_submit_button("💾 Save Personal Info")
        
        if submitted:
            data = {
                "name": name,
                "email": email,
                "phone": phone,
                "location": location,
                "linkedin": linkedin,
                "github": github,
                "portfolio": portfolio,
                "summary": summary
            }
            result = api_post("/api/personal-info", data)
            if result:
                st.success("✅ Personal information saved successfully!")
                st.rerun()

# Experience Page
elif page == "💼 Experience":
    st.markdown('<div class="main-header">💼 Experience Blocks</div>', unsafe_allow_html=True)
    
    st.info("💡 Add all your work experiences, projects, and achievements. The system will automatically select the most relevant ones for each job application.")
    
    # Add new experience
    with st.expander("➕ Add New Experience Block", expanded=True):
        with st.form("experience_form", clear_on_submit=True):
            title = st.text_input("Job Title / Project Name *")
            company = st.text_input("Company / Organization")
            content = st.text_area(
                "Description *",
                height=200,
                help="Describe your responsibilities, achievements, and impact. Use specific metrics where possible."
            )
            tags_input = st.text_input(
                "Skills/Keywords (comma-separated) *",
                help="e.g., Laravel, PHP, Docker, PostgreSQL"
            )
            
            submitted = st.form_submit_button("💾 Add Experience Block")
            
            if submitted:
                if not title or not content or not tags_input:
                    st.error("Please fill in all required fields!")
                else:
                    tags = [tag.strip() for tag in tags_input.split(',')]
                    data = {
                        "title": title,
                        "company": company,
                        "content": content,
                        "metadata_tags": tags
                    }
                    result = api_post("/api/experience-blocks", data)
                    if result:
                        st.success("✅ Experience block added successfully!")
                        st.rerun()
    
    # Display existing experiences
    st.markdown('<div class="sub-header">📚 Your Experience Library</div>', unsafe_allow_html=True)
    experiences = api_get("/api/experience-blocks")
    
    if experiences:
        for exp in experiences:
            with st.expander(f"{exp['title']} {f'at {exp.get('company', '')}' if exp.get('company') else ''}"):
                st.write(f"**Content:** {exp['content']}")
                st.write(f"**Skills:** {', '.join(exp.get('metadata_tags', []))}")
                st.write(f"**Added:** {exp['created_at']}")
                
                if st.button(f"🗑️ Delete", key=f"del_{exp['id']}"):
                    result = api_delete(f"/api/experience-blocks/{exp['id']}")
                    if result:
                        st.success("Deleted!")
                        st.rerun()
    else:
        st.info("No experience blocks yet. Add your first one above!")

# Style Guidelines Page
elif page == "🎨 Style Guidelines":
    st.markdown('<div class="main-header">🎨 Style Guidelines</div>', unsafe_allow_html=True)
    
    st.info("💡 Define how you want your CV and cover letter formatted. These rules will be applied to all generated documents.")
    
    # Add new guideline
    with st.expander("➕ Add New Style Guideline", expanded=True):
        with st.form("style_form", clear_on_submit=True):
            name = st.text_input("Guideline Name *", help="e.g., 'Keep CV to 2 pages'")
            description = st.text_area(
                "Description *",
                help="Describe the rule in detail"
            )
            
            submitted = st.form_submit_button("💾 Add Style Guideline")
            
            if submitted:
                if not name or not description:
                    st.error("Please fill in all fields!")
                else:
                    data = {
                        "name": name,
                        "description": description,
                        "rules": {},
                        "is_active": "true"
                    }
                    result = api_post("/api/style-guidelines", data)
                    if result:
                        st.success("✅ Style guideline added!")
                        st.rerun()
    
    # Display existing guidelines
    st.markdown('<div class="sub-header">📋 Active Guidelines</div>', unsafe_allow_html=True)
    guidelines = api_get("/api/style-guidelines")
    
    if guidelines:
        for guideline in guidelines:
            st.markdown(f"**{guideline['name']}**")
            st.write(guideline['description'])
            st.markdown("---")
    else:
        st.info("No style guidelines yet. The system will use default formatting.")

# Applications Page
elif page == "📝 Applications":
    st.markdown('<div class="main-header">📝 Job Applications</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["➕ Create New", "📋 View All"])
    
    with tab1:
        st.info("💡 Paste the job description below and let AI generate a tailored CV and cover letter!")
        
        with st.form("application_form"):
            company_name = st.text_input("Company Name *")
            job_title = st.text_input("Job Title *")
            job_url = st.text_input("Job URL (optional)")
            raw_spec = st.text_area(
                "Job Description *",
                height=300,
                help="Paste the complete job description here"
            )
            
            submitted = st.form_submit_button("🚀 Generate Application Materials")
            
            if submitted:
                if not company_name or not job_title or not raw_spec:
                    st.error("Please fill in all required fields!")
                else:
                    with st.spinner("🔮 AI is crafting your perfect application... This may take 30-60 seconds."):
                        data = {
                            "company_name": company_name,
                            "job_title": job_title,
                            "job_url": job_url,
                            "raw_spec": raw_spec
                        }
                        result = api_post("/api/applications", data)
                        
                        if result:
                            st.success("✅ Application materials generated successfully!")
                            st.balloons()
                            
                            # Display results
                            st.markdown('<div class="sub-header">📄 Generated CV</div>', unsafe_allow_html=True)
                            st.text_area("CV", value=result['generated_cv'], height=400)
                            
                            st.markdown('<div class="sub-header">📧 Generated Cover Letter</div>', unsafe_allow_html=True)
                            st.text_area("Cover Letter", value=result['generated_cover_letter'], height=300)
                            
                            st.markdown('<div class="sub-header">🎯 Skills Gap Analysis</div>', unsafe_allow_html=True)
                            skills_gap = result['skills_gap_report']
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("**✅ Matching Skills:**")
                                for skill in skills_gap.get('matching_skills', []):
                                    st.write(f"• {skill}")
                            
                            with col2:
                                st.write("**⚠️ Missing Skills:**")
                                for skill in skills_gap.get('missing_skills', []):
                                    st.write(f"• {skill}")
                            
                            st.write("**💡 Recommendations:**")
                            for rec in skills_gap.get('recommendations', []):
                                st.write(f"• {rec}")
                            
                            st.rerun()
    
    with tab2:
        applications = api_get("/api/applications")
        
        if applications:
            # Status filter
            status_filter = st.selectbox(
                "Filter by status",
                ["All", "draft", "applied", "interviewing", "rejected", "offer", "accepted"]
            )
            
            filtered_apps = applications
            if status_filter != "All":
                filtered_apps = [a for a in applications if a['status'] == status_filter]
            
            for app in filtered_apps:
                with st.expander(f"{app['job_title']} at {app['company_name']} - {app['status'].upper()}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Created:** {app['created_at']}")
                        if app.get('applied_date'):
                            st.write(f"**Applied:** {app['applied_date']}")
                        if app.get('job_url'):
                            st.write(f"**URL:** {app['job_url']}")
                    
                    with col2:
                        new_status = st.selectbox(
                            "Update Status",
                            ["draft", "applied", "interviewing", "rejected", "offer", "accepted"],
                            index=["draft", "applied", "interviewing", "rejected", "offer", "accepted"].index(app['status']),
                            key=f"status_{app['id']}"
                        )
                        
                        if st.button("Update", key=f"update_{app['id']}"):
                            requests.patch(
                                f"{API_URL}/api/applications/{app['id']}/status",
                                params={"status": new_status}
                            )
                            st.success("Status updated!")
                            st.rerun()
                    
                    st.markdown("---")
                    
                    # Show generated materials
                    show_cv = st.checkbox("Show CV", key=f"cv_{app['id']}")
                    if show_cv and app.get('generated_cv'):
                        st.text_area("CV", value=app['generated_cv'], height=300, key=f"cv_text_{app['id']}")
                    
                    show_cover = st.checkbox("Show Cover Letter", key=f"cover_{app['id']}")
                    if show_cover and app.get('generated_cover_letter'):
                        st.text_area("Cover Letter", value=app['generated_cover_letter'], height=200, key=f"cover_text_{app['id']}")
                    
                    show_gap = st.checkbox("Show Skills Gap", key=f"gap_{app['id']}")
                    if show_gap and app.get('skills_gap_report'):
                        st.json(app['skills_gap_report'])
        else:
            st.info("No applications yet. Create your first one in the 'Create New' tab!")