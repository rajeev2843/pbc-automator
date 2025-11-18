import streamlit as st
import pandas as pd
from datetime import datetime
from database import *
from gemini_ai import *
from utils import *
import io

# Initialize database
init_database()

# Page config
st.set_page_config(
    page_title="Smart Audit Room",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply styling
apply_custom_styling()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "landing"

# ============================================================================
# LANDING PAGE
# ============================================================================

def show_landing_page():
    # Clean Layout without Cards
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown('<h1 style="font-size: 3.5rem; color: #4F46E5;">Smart Audit Room</h1>', unsafe_allow_html=True)
        st.markdown("### Automate Your PBC Process with AI")
        st.write("Transform your audit workflow. Generate PBC lists from Trial Balance instantly, track submissions, and verify documents with AI.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚀 Get Started", key="hero_signup", use_container_width=True):
                st.session_state.current_page = "signup"
                st.rerun()
        with c2:
            if st.button("🔐 Sign In", key="hero_signin", use_container_width=True):
                st.session_state.current_page = "signin"
                st.rerun()
    
    with col2:
        st.info("**Designed for CAs**\n\nStreamline audit documentation and client communication in one secure platform.")

# ============================================================================
# AUTHENTICATION PAGES
# ============================================================================

def show_signup_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## Create Account")
        st.markdown("<div style='background: white; padding: 30px; border-radius: 12px; border: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
        
        role = st.radio("I am a:", ["Chartered Accountant", "Client"], horizontal=True)
        role_enum = UserRole.CA if role == "Chartered Accountant" else UserRole.CLIENT
        
        full_name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        confirm_pass = st.text_input("Confirm Password", type="password")
        
        firm_name = None
        mem_no = None
        company_name = None
        gstin = None
        ca_code = None

        if role_enum == UserRole.CA:
            firm_name = st.text_input("Firm Name")
            mem_no = st.text_input("Membership Number")
        else:
            company_name = st.text_input("Company Name")
            gstin = st.text_input("GSTIN")
            ca_code = st.text_input("CA Invite Code (Ask your CA)")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Sign Up", use_container_width=True):
            if not email or not password or not full_name:
                st.error("Please fill all required fields")
            elif password != confirm_pass:
                st.error("Passwords do not match")
            else:
                db = get_session()
                try:
                    if db.query(User).filter(User.email == email).first():
                        st.error("Email already registered")
                    else:
                        user = User(
                            email=email,
                            password_hash=hash_password(password),
                            full_name=full_name,
                            role=role_enum,
                            company_name=firm_name if role_enum == UserRole.CA else company_name
                        )
                        db.add(user)
                        db.flush()
                        
                        if role_enum == UserRole.CA:
                            profile = CAProfile(
                                user_id=user.user_id,
                                firm_name=firm_name,
                                membership_no=mem_no,
                                invite_code=generate_invite_code()
                            )
                            db.add(profile)
                        else:
                            ca_profile = db.query(CAProfile).filter(CAProfile.invite_code == ca_code).first()
                            client_profile = ClientProfile(
                                user_id=user.user_id,
                                company_name=company_name,
                                gstin=gstin,
                                ca_id=ca_profile.ca_id if ca_profile else None
                            )
                            db.add(client_profile)
                        
                        db.commit()
                        st.success("Account created! Please sign in.")
                        st.session_state.current_page = "signin"
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                finally:
                    db.close()
                    
        if st.button("Already have an account? Sign In", type="secondary", use_container_width=True):
            st.session_state.current_page = "signin"
            st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)

def show_signin_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## Sign In")
        st.markdown("<div style='background: white; padding: 30px; border-radius: 12px; border: 1px solid #E2E8F0;'>", unsafe_allow_html=True)
        
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Sign In", use_container_width=True):
            db = get_session()
            user = db.query(User).filter(User.email == email).first()
            
            if user and verify_password(password, user.password_hash):
                login_user(user.user_id, user.role)
                st.rerun()
            else:
                st.error("Invalid credentials")
            db.close()
            
        if st.button("Don't have an account? Sign Up", type="secondary", use_container_width=True):
            st.session_state.current_page = "signup"
            st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================================
# CA DASHBOARD
# ============================================================================

def show_ca_dashboard():
    db = get_session()
    user = db.query(User).filter(User.user_id == st.session_state.user_id).first()
    ca_profile = user.ca_profile
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👨‍💼 {user.full_name}")
        st.caption(f"{ca_profile.firm_name}")
        st.divider()
        
        page = st.radio("Menu", ["Dashboard", "My Clients", "Start Audit", "Review Documents"])
        
        st.divider()
        st.success(f"🔑 Invite Code:\n**{ca_profile.invite_code}**")
        if st.button("Logout"):
            logout_user()

    if page == "Dashboard":
        st.title("Practice Overview")
        
        clients_count = len(ca_profile.clients)
        projects = ca_profile.audit_projects
        pending_reviews = sum(1 for p in projects for item in p.pbc_items if item.status == PBCStatus.SUBMITTED)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='metric-card'><h3>Clients</h3><h1>{clients_count}</h1></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-card'><h3>Active Audits</h3><h1>{len(projects)}</h1></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='metric-card'><h3>Pending Reviews</h3><h1>{pending_reviews}</h1></div>", unsafe_allow_html=True)

    elif page == "Start Audit":
        st.title("🚀 Start New Audit")
        st.markdown("Create a new audit project and generate PBC requirements automatically.")
        
        with st.container():
            clients = ca_profile.clients
            if not clients:
                st.warning("No clients found. Share your invite code to add clients.")
            else:
                client_opts = {c.company_name: c.client_id for c in clients}
                selected_client = st.selectbox("Select Client", list(client_opts.keys()))
                
                proj_name = st.text_input("Project Name", value="Statutory Audit FY 2024-25")
                
                st.markdown("### Upload Trial Balance")
                
                # --- SAMPLE FILE DOWNLOAD ---
                sample_csv = "Account Name,Debit,Credit\nSales,0,500000\nRent Expense,12000,0\nSalary,50000,0\nBank HDFC,100000,0"
                st.download_button(
                    label="📥 Download Sample CSV Template",
                    data=sample_csv,
                    file_name="sample_trial_balance.csv",
                    mime="text/csv"
                )
                # -----------------------------
                
                uploaded_tb = st.file_uploader("Drag and drop file here", type=['xlsx', 'csv'])
                
                if st.button("Generate AI PBC List", use_container_width=True):
                    if uploaded_tb and proj_name:
                        with st.spinner("🤖 AI is analyzing Trial Balance..."):
                            if uploaded_tb.name.endswith('.csv'):
                                df = pd.read_csv(uploaded_tb)
                            else:
                                df = pd.read_excel(uploaded_tb)
                            
                            new_project = AuditProject(
                                ca_id=ca_profile.ca_id,
                                client_id=client_opts[selected_client],
                                project_name=proj_name,
                                financial_year="2024-25"
                            )
                            db.add(new_project)
                            db.commit()
                            
                            pbc_items = generate_pbc_from_trial_balance(df)
                            
                            for idx, item in enumerate(pbc_items):
                                new_item = PBCItem(
                                    project_id=new_project.project_id,
                                    item_number=idx+1,
                                    category=item['category'],
                                    item_description=item['description'],
                                    why_needed=item['why_needed'],
                                    priority=item['priority'],
                                    ai_generated=True
                                )
                                db.add(new_item)
                            db.commit()
                            st.success(f"Audit created with {len(pbc_items)} AI-generated requirements!")
    
    elif page == "Review Documents":
        st.title("🔍 Document Review")
        # (Existing Review Logic - Same as before)
        projects = ca_profile.audit_projects
        proj_opts = {p.project_name: p.project_id for p in projects}
        sel_proj = st.selectbox("Select Audit Project", list(proj_opts.keys())) if proj_opts else None
        
        if sel_proj:
            proj = db.query(AuditProject).get(proj_opts[sel_proj])
            pending_items = [item for item in proj.pbc_items if item.status == PBCStatus.SUBMITTED]
            
            if not pending_items:
                st.success("All caught up! No pending reviews.")
            else:
                for item in pending_items:
                    with st.expander(f"📄 {item.category}: {item.item_description}"):
                        doc = item.documents[-1]
                        st.markdown(f"**File:** {doc.filename} | **Size:** {format_file_size(doc.file_size)}")
                        st.info(f"**AI Analysis:**\n{doc.ai_analysis}")
                        
                        c1, c2 = st.columns(2)
                        if c1.button("✅ Approve", key=f"app_{doc.doc_id}"):
                            item.status = PBCStatus.VERIFIED
                            db.commit()
                            st.rerun()
                        if c2.button("❌ Reject", key=f"rej_{doc.doc_id}"):
                            item.status = PBCStatus.REJECTED
                            db.commit()
                            st.rerun()

    db.close()

# ============================================================================
# CLIENT DASHBOARD
# ============================================================================

def show_client_dashboard():
    db = get_session()
    user = db.query(User).filter(User.user_id == st.session_state.user_id).first()
    client_profile = user.client_profile
    
    with st.sidebar:
        st.markdown(f"### 🏢 {user.company_name}")
        if client_profile.linked_ca:
            st.caption(f"Auditor: {client_profile.linked_ca.firm_name}")
        else:
            st.warning("No Auditor Linked")
        st.divider()
        if st.button("Logout"):
            logout_user()

    projects = client_profile.audit_projects
    if not projects:
        st.info("No active audits. Your CA will create a project.")
    else:
        proj = projects[-1]
        st.title(f"📂 {proj.project_name}")
        
        total = len(proj.pbc_items)
        completed = sum(1 for i in proj.pbc_items if i.status == PBCStatus.VERIFIED)
        progress = int((completed/total)*100) if total > 0 else 0
        st.progress(progress)
        st.caption(f"Audit Progress: {progress}%")
        
        filter_status = st.selectbox("Show Items", ["Pending", "Submitted", "Verified", "All"])
        items = proj.pbc_items
        if filter_status != "All":
            items = [i for i in items if i.status.value == filter_status]
        
        for item in items:
            with st.expander(f"{item.item_description} {status_badge(item.status.value)}"):
                st.write(f"**Reason:** {item.why_needed}")
                if item.status in [PBCStatus.PENDING, PBCStatus.REJECTED]:
                    uf = st.file_uploader("Upload", key=f"up_{item.pbc_id}")
                    if uf and st.button("Submit", key=f"sub_{item.pbc_id}"):
                        # Document Upload Logic (Same as before)
                        with st.spinner("AI Analyzing..."):
                            bytes_data = uf.read()
                            analysis = analyze_uploaded_document(bytes_data, uf.name, item.item_description)
                            new_doc = PBCDocument(
                                pbc_id=item.pbc_id, filename=uf.name, file_size=len(bytes_data),
                                file_type=uf.type, uploaded_by=user.user_id,
                                ai_analysis=str(analysis.get('summary', ''))
                            )
                            db.add(new_doc)
                            item.status = PBCStatus.SUBMITTED
                            db.commit()
                            st.success("Uploaded!")
                            st.rerun()
    db.close()

def main():
    if not st.session_state.authenticated:
        if st.session_state.current_page == "landing":
            show_landing_page()
        elif st.session_state.current_page == "signin":
            show_signin_page()
        elif st.session_state.current_page == "signup":
            show_signup_page()
    else:
        if st.session_state.role == UserRole.CA:
            show_ca_dashboard()
        else:
            show_client_dashboard()

if __name__ == "__main__":
    main()
    
    
