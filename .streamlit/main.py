# Note: This is Part 1 - Contains imports, landing page, signup, signin, and CA dashboard setup
# Copy all parts sequentially to build complete main.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import *
from gemini_ai import *
from utils import *
from tb_mapper import TrialBalanceToPBCMapper
import io
import json
from io import BytesIO

# Initialize database
init_database()

# Page config
st.set_page_config(
    page_title="Smart Audit Room - PBC Automator",
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
# HELPER FUNCTIONS FOR TB MAPPER INTEGRATION
# ============================================================================

def generate_pbc_description(pbc_category: str, ledgers_df: pd.DataFrame) -> str:
    """Generate PBC description based on category and ledgers"""
    
    ledger_names = ", ".join(ledgers_df['Original_Ledger_Name'].head(3).tolist())
    if len(ledgers_df) > 3:
        ledger_names += f" and {len(ledgers_df) - 3} more"
    
    category_descriptions = {
        "Fixed Assets": f"Fixed asset register with details of {ledger_names}. Include purchase invoices, depreciation schedule, and disposal records.",
        "Bank": f"Bank statements and reconciliations for {ledger_names}. Include bank confirmation letters.",
        "Cash": "Cash book, petty cash records, and cash count certificates as on year-end.",
        "Inventories": f"Stock statement with valuation details for {ledger_names}. Include physical verification reports.",
        "Trade Receivables": f"Debtors list with ageing for {ledger_names}. Include confirmation letters and subsequent collection details.",
        "Trade Payables": f"Creditors list with ageing for {ledger_names}. Include confirmation letters and MSME classification.",
        "Loans": f"Loan agreements, sanction letters, and repayment schedules for {ledger_names}.",
        "GST": "GST returns (GSTR-1, GSTR-3B), GST reconciliation, and ITC working papers.",
        "Sales": "Sales register, invoices, and supporting documents. Include GST reconciliation.",
        "Expenses": f"Expense vouchers and supporting documents for {ledger_names}.",
        "Salary": "Salary sheets, PF/ESI challans, and Form 16 for employees.",
    }
    
    for key, desc in category_descriptions.items():
        if key.lower() in pbc_category.lower():
            return desc
    
    return f"Supporting documents and schedules for {pbc_category}. Includes ledger extracts and vouchers."


def generate_why_needed(pbc_category: str) -> str:
    """Generate why needed explanation"""
    
    explanations = {
        "Fixed Assets": "To verify existence, ownership, valuation and completeness of fixed assets as per AS-10/Ind AS 16",
        "Bank": "To confirm existence and accuracy of bank balances and reconcile book balances with bank statements",
        "Cash": "To verify existence of cash and ensure proper controls over cash handling",
        "Inventories": "To verify existence, ownership, condition and valuation of inventory as per AS-2/Ind AS 2",
        "Trade Receivables": "To confirm existence, recoverability and completeness of receivables",
        "Trade Payables": "To verify completeness and accuracy of liabilities and MSME compliance",
        "Loans": "To verify terms, conditions, repayment schedule and compliance with loan covenants",
        "GST": "To verify GST compliance and ensure accurate reporting of input and output tax",
        "Sales": "To verify revenue recognition, cut-off and ensure completeness of sales",
        "Expenses": "To verify nature, authorization and proper accounting of expenses",
        "Salary": "To verify employee costs and compliance with statutory requirements",
    }
    
    for key, explanation in explanations.items():
        if key.lower() in pbc_category.lower():
            return explanation
    
    return f"To verify, validate and ensure proper accounting treatment of {pbc_category}"


def determine_priority(pbc_category: str, debit: float, credit: float) -> str:
    """Determine priority based on category and amounts"""
    
    amount = max(abs(debit), abs(credit))
    
    high_priority = ["bank", "cash", "sales", "revenue", "receivable", "payable", "loan", "borrowing"]
    if any(hp in pbc_category.lower() for hp in high_priority):
        return "High"
    
    if amount > 1000000:
        return "High"
    
    if amount > 100000:
        return "Medium"
    
    return "Low"


def get_major_category(pbc_category: str) -> str:
    """Get major category for grouping"""
    
    category_lower = pbc_category.lower()
    
    if any(term in category_lower for term in ['fixed asset', 'intangible', 'capital wip', 'ppe']):
        return 'Fixed Assets'
    elif 'inventor' in category_lower or any(term in category_lower for term in ['raw material', 'wip', 'finished', 'stock']):
        return 'Inventories'
    elif 'receivable' in category_lower or 'debtor' in category_lower:
        return 'Trade Receivables'
    elif any(term in category_lower for term in ['cash', 'bank']):
        return 'Cash & Bank'
    elif 'payable' in category_lower or 'creditor' in category_lower:
        return 'Trade Payables'
    elif any(term in category_lower for term in ['share capital', 'equity', 'reserve', 'retained']):
        return 'Equity'
    elif 'borrowing' in category_lower or 'loan' in category_lower:
        return 'Borrowings'
    elif any(term in category_lower for term in ['gst', 'tds', 'tax']):
        return 'Statutory Compliance'
    elif any(term in category_lower for term in ['sales', 'revenue', 'income']):
        return 'Revenue'
    elif any(term in category_lower for term in ['expense', 'cost', 'depreciation']):
        return 'Expenses'
    else:
        return 'Other'


# ============================================================================
# LANDING PAGE (Same as original)
# ============================================================================

# [Copy the entire show_landing_page() function from your original main.py]

# ============================================================================
# SIGNUP PAGE (Same as original)
# ============================================================================

# [Copy the entire show_signup_page() function from your original main.py]

# ============================================================================
# SIGNIN PAGE (Same as original)
# ============================================================================

# [Copy the entire show_signin_page() function from your original main.py]

# ============================================================================
# CA DASHBOARD
# ============================================================================

def show_ca_dashboard():
    db = get_session()
    
    user = db.query(User).filter(User.user_id == st.session_state.user_id).first()
    ca_profile = db.query(CAProfile).filter(CAProfile.user_id == st.session_state.user_id).first()
    
    if not ca_profile:
        st.error("CA Profile not found")
        db.close()
        return
    
    with st.sidebar:
        st.markdown(f"<h3 style='color: #E2E8F0;'>👨‍💼 {user.full_name}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: #E2E8F0; font-weight: 700; font-size: 16px;'>{ca_profile.firm_name}</p>", unsafe_allow_html=True)
        st.markdown(f"**ICAI Membership:** {ca_profile.membership_no}")
        if hasattr(ca_profile, 'firm_registration_no') and ca_profile.firm_registration_no:
            st.markdown(f"**Firm Registration:** {ca_profile.firm_registration_no}")
        
        with st.expander("🔗 Your Invite Code"):
            st.code(ca_profile.invite_code, language=None)
            if st.button("📋 Copy Code", key="copy_invite_sidebar", use_container_width=True):
                st.toast("✅ Copied to clipboard!")
        
        st.divider()
        
        menu = st.radio(
            "Navigation",
            ["📊 Dashboard", "📁 Projects", "➕ New Project", "👥 My Clients", "⚙️ Settings"],
            label_visibility="collapsed"
        )
            
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
    
    if menu == "📊 Dashboard":
        show_ca_dashboard_home(db, ca_profile)
    elif menu == "📁 Projects":
        show_ca_projects(db, ca_profile)
    elif menu == "➕ New Project":
        show_ca_new_project(db, ca_profile)
    elif menu == "👥 My Clients":
        show_ca_clients(db, ca_profile)
    elif menu == "⚙️ Settings":
        show_ca_settings(db, ca_profile)
    
    db.close()


# [Copy show_ca_dashboard_home() and show_ca_projects() from original]


def show_ca_new_project(db, ca_profile):
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    st.markdown("# ➕ Create New Audit Project")
    st.markdown("---")
    
    clients = db.query(ClientProfile).filter(ClientProfile.ca_id == ca_profile.ca_id).all()
    
    if not clients:
        st.warning("⚠️ You don't have any clients yet. Clients must sign up and link to your firm using your invite code.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    with st.form("new_project_form"):
        st.markdown("### 📋 Project Details")
        
        client_options = {f"{c.company_name} ({c.gstin or 'No GSTIN'})": c.client_id for c in clients}
        selected_client_name = st.selectbox("Select Client *", options=list(client_options.keys()))
        selected_client_id = client_options[selected_client_name]
        
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input("Project Name *", placeholder="e.g., Statutory Audit FY 2024-25")
            audit_type = st.selectbox("Audit Type *", ["Statutory Audit", "Tax Audit", "Internal Audit", "GST Audit", "Stock Audit"])
        with col2:
            financial_year = st.text_input("Financial Year *", placeholder="e.g., 2024-25")
            accounting_std = st.selectbox("Accounting Standard *", ["Indian GAAP", "Ind AS"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📊 Upload Trial Balance")
        
        col_info1, col_info2 = st.columns([2, 2])
        with col_info1:
            st.markdown("Upload Trial Balance to auto-generate PBC list using AI")
        with col_info2:
            sample_df = pd.DataFrame({
                'Account Name': ['Cash in Hand', 'Bank - SBI Current Account', 'Sales Revenue', 'Rent Expense', 'Trade Payables'],
                'Debit': [50000, 250000, 0, 35000, 0],
                'Credit': [0, 0, 500000, 0, 75000]
            })
            
            csv = sample_df.to_csv(index=False)
            st.download_button(
                label="📥 Sample CSV",
                data=csv,
                file_name="sample_trial_balance.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_sample_csv"
            )
        
        tb_file = st.file_uploader(
            "Trial Balance (Excel/CSV)",
            type=['xlsx', 'xls', 'csv'],
            help="Upload Trial Balance with columns: Account Name, Debit, Credit"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("🚀 Create Project & Generate PBC", use_container_width=True)
        
        if submit:
            if not all([project_name, financial_year, tb_file]):
                st.error("❌ Please fill all required fields and upload Trial Balance")
            else:
                try:
                    if tb_file.name.endswith('.csv'):
                        tb_df = pd.read_csv(tb_file)
                    else:
                        tb_df = pd.read_excel(tb_file)
                    
                    required_cols = ['Account Name', 'Debit', 'Credit']
                    if not all(col in tb_df.columns for col in required_cols):
                        st.error(f"❌ Trial Balance must have columns: {', '.join(required_cols)}")
                    else:
                        with st.spinner("🤖 Creating project and generating PBC list with AI Mapper..."):
                            new_project = AuditProject(
                                ca_id=ca_profile.ca_id,
                                client_id=selected_client_id,
                                project_name=project_name,
                                financial_year=financial_year,
                                audit_type=audit_type,
                                status="Active"
                            )
                            db.add(new_project)
                            db.flush()
                            
                            tb_record = TrialBalance(
                                project_id=new_project.project_id,
                                filename=tb_file.name,
                                total_debit=float(tb_df['Debit'].sum()),
                                total_credit=float(tb_df['Credit'].sum()),
                                account_count=len(tb_df)
                            )
                            db.add(tb_record)
                            
                            # USE TB MAPPER
                            mapper_audit_type = "Tax" if audit_type == "Tax Audit" else "Stat"
                            mapper = TrialBalanceToPBCMapper(
                                audit_type=mapper_audit_type,
                                accounting_standard=accounting_std
                            )
                            
                            mapping_result = mapper.process_trial_balance(
                                df=tb_df,
                                ledger_column='Account Name',
                                debit_column='Debit',
                                credit_column='Credit',
                                threshold=60
                            )
                            
                            summary = mapper.generate_pbc_summary(mapping_result)
                            
                            pbc_categories = mapping_result[
                                mapping_result['PBC_Category'] != 'UNMAPPED - Manual Review Required'
                            ]['PBC_Category'].unique()
                            
                            pbc_item_number = 1
                            for pbc_category in pbc_categories:
                                category_ledgers = mapping_result[
                                    mapping_result['PBC_Category'] == pbc_category
                                ]
                                
                                total_debit = category_ledgers['Debit_Amount'].sum() if 'Debit_Amount' in category_ledgers.columns else 0
                                total_credit = category_ledgers['Credit_Amount'].sum() if 'Credit_Amount' in category_ledgers.columns else 0
                                
                                description = generate_pbc_description(pbc_category, category_ledgers)
                                why_needed = generate_why_needed(pbc_category)
                                priority = determine_priority(pbc_category, total_debit, total_credit)
                                
                                pbc_item = PBCItem(
                                    project_id=new_project.project_id,
                                    item_number=pbc_item_number,
                                    category=get_major_category(pbc_category),
                                    item_description=description,
                                    why_needed=why_needed,
                                    priority=priority,
                                    status=PBCStatus.PENDING,
                                    ai_generated=True
                                )
                                db.add(pbc_item)
                                pbc_item_number += 1
                            
                            db.commit()
                            
                            st.success(f"✅ Project created successfully!")
                            st.balloons()
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Total Ledgers", summary['total_ledgers'])
                            with col2:
                                st.metric("PBC Items Generated", len(pbc_categories))
                            with col3:
                                st.metric("Success Rate", f"{summary['success_rate']}%")
                            
                            st.info(f"✓ {summary['high_confidence']} High Confidence | {summary['medium_confidence']} Medium | {summary['low_confidence']} Need Review")
                            
                            import time
                            time.sleep(3)
                            st.session_state.selected_project = new_project.project_id
                            st.rerun()
                
                except Exception as e:
                    db.rollback()
                    st.error(f"❌ Error: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)


# [Copy show_ca_clients() and show_ca_settings() from original]


# ============================================================================
# CLIENT DASHBOARD (Same as original - all functions)
# ============================================================================

# [Copy all client functions from original main.py]


# ============================================================================
# MAIN APPLICATION ROUTER
# ============================================================================

def main():
    if not st.session_state.authenticated:
        if st.session_state.current_page == "landing":
            show_landing_page()
        elif st.session_state.current_page == "signup":
            show_signup_page()
        elif st.session_state.current_page == "signin":
            show_signin_page()
    else:
        if st.session_state.role == "ca":
            show_ca_dashboard()
        elif st.session_state.role == "client":
            show_client_dashboard()

if __name__ == "__main__":
    main()
