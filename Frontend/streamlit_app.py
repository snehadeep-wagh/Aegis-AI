import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime, timedelta
from google.cloud import storage
from google.cloud import bigquery
import os

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="AI Loan Portal",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- GOOGLE CLOUD STORAGE SETUP ----------
def initialize_gcs():
    """Initialize Google Cloud Storage client using Application Default Credentials"""
    try:
        client = storage.Client()
        return client
    except Exception as e:
        st.error(f"❌ Failed to initialize GCS client: {str(e)}")
        st.info("💡 Make sure you're running in GCP Cloud Shell or have set up credentials")
        return None

def initialize_bigquery():
    """Initialize BigQuery client using Application Default Credentials"""
    try:
        client = bigquery.Client()
        return client
    except Exception as e:
        st.error(f"❌ Failed to initialize BigQuery client: {str(e)}")
        st.info("💡 Make sure you're running in GCP Cloud Shell or have set up credentials")
        return None

def upload_to_gcs(client, bucket_name, file_data, file_name, user_folder, loan_type):
    """Upload file to GCS bucket with organized folder structure"""
    try:
        bucket = client.bucket(bucket_name)
        
        # Create folder structure: user/{username}/{loan_type}/{timestamp}_{filename}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        blob_path = f"user/{user_folder}/{loan_type}/{timestamp}_{file_name}"
        blob = bucket.blob(blob_path)
        
        # Upload file
        file_data.seek(0)  # Reset file pointer
        blob.upload_from_file(file_data, content_type=file_data.type)
        
        return {
            "success": True,
            "path": blob_path,
            "public_url": blob.public_url if blob.public_url else f"gs://{bucket_name}/{blob_path}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def save_to_bigquery(client, dataset_id, table_id, user_data):
    """Save user loan data to BigQuery"""
    try:
        # Use the full table reference
        table_ref = client.dataset(dataset_id).table(table_id)
        
        # Prepare rows for insertion - convert all values to strings for string columns
        rows_to_insert = [{
            "User_Name": str(user_data["username"]),
            "Loan_Type": str(user_data["loan_type"]),
            "Loan_Amt": str(float(user_data["loan_amount"])),  # Store as string
            "Score": str(int(user_data["risk_score"])),  # Store as string
            "Loan_Status": str(user_data["loan_status"])
        }]
        
        # Insert data
        errors = client.insert_rows_json(table_ref, rows_to_insert)
        
        if errors:
            return {
                "success": False,
                "error": str(errors)
            }
        else:
            return {
                "success": True,
                "message": f"✅ Data saved to BigQuery: {dataset_id}.{table_id}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def get_bigquery_data(client):
    """Fetch data from BigQuery table and convert data types"""
    try:
        # Use bracket escaping for table name with hyphen
        query = """
            SELECT 
                User_Name,
                Loan_Type,
                Loan_Amt,
                Score,
                Loan_Status
            FROM `hack-team-promptops.UserData.User-Info`
            ORDER BY User_Name
        """
        st.info("📊 Fetching data from BigQuery using SQL...")
        df = client.query(query).to_dataframe()
        
        if not df.empty:
            # Convert data types - handle string values
            # Convert Score to numeric, handling any errors
            df['Risk_Score'] = pd.to_numeric(df['Score'], errors='coerce').fillna(0).astype(int)
            
            # Convert Loan_Amt to numeric
            df['Loan_Amt_Num'] = pd.to_numeric(df['Loan_Amt'], errors='coerce').fillna(0)
            
            # Drop the original columns and rename
            df = df.drop(columns=['Score', 'Loan_Amt'])
            df = df.rename(columns={
                'Loan_Amt_Num': 'Loan_Amt',
                'Risk_Score': 'Risk_Score'
            })
            
            # Reorder columns
            df = df[['User_Name', 'Loan_Type', 'Loan_Amt', 'Risk_Score', 'Loan_Status']]
            
            st.info(f"📊 Found {len(df)} records in BigQuery")
            return df
        else:
            st.info("📊 BigQuery table exists but has no records yet.")
            return df
            
    except Exception as e:
        st.error(f"❌ Error fetching data from BigQuery: {str(e)}")
        st.info("💡 Make sure the table `UserData.User-Info` exists in your project.")
        return None

def logout():
    """Logout function to clear session state"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: #f0f2f6;
        padding: 0px !important;
    }
    
    .stApp {
        background: #f0f2f6;
    }
    
    /* Glassmorphism cards */
    .glass-card {
        background: rgba(255,255,255,0.85);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 24px;
        border: 1px solid rgba(255,255,255,0.3);
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.08);
        padding: 1.8rem;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 48px rgba(31, 38, 135, 0.15);
    }
    
    /* Login container */
    .login-wrapper {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    
    .login-box {
        background: rgba(255,255,255,0.95);
        backdrop-filter: blur(20px);
        border-radius: 32px;
        padding: 3.5rem 3rem;
        max-width: 440px;
        width: 100%;
        box-shadow: 0 25px 80px rgba(0,0,0,0.25);
    }
    
    .login-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    
    .login-subtitle {
        text-align: center;
        color: #7b8da6;
        font-weight: 400;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }
    
    /* Loan cards */
    .loan-card-modern {
        background: white;
        border-radius: 20px;
        padding: 2rem 1.2rem;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        cursor: pointer;
        border: 2px solid transparent;
        position: relative;
        overflow: hidden;
        min-height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.04);
    }
    
    .loan-card-modern::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .loan-card-modern:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    
    .loan-card-modern:hover::before {
        opacity: 1;
    }
    
    .loan-icon {
        font-size: 3.6rem;
        margin-bottom: 0.6rem;
    }
    
    .loan-name {
        font-weight: 700;
        font-size: 1.2rem;
        color: #1a2332;
        margin-bottom: 0.2rem;
    }
    
    .loan-desc {
        color: #8a9bb5;
        font-size: 0.85rem;
        font-weight: 400;
    }
    
    /* Document rows */
    .doc-item {
        background: white;
        border-radius: 14px;
        padding: 0.9rem 1.2rem;
        margin-bottom: 0.7rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        border: 1px solid #eef2f7;
        transition: all 0.3s ease;
    }
    
    .doc-item:hover {
        border-color: #667eea;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.08);
    }
    
    .doc-name {
        font-weight: 500;
        color: #1a2332;
        flex: 2;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    
    .doc-status-badge {
        padding: 0.25rem 0.9rem;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    
    .doc-status-badge.uploaded {
        background: #e8f5e9;
        color: #2e7d32;
    }
    
    .doc-status-badge.pending {
        background: #fff3e0;
        color: #e65100;
    }
    
    .doc-status-badge.cloud-uploaded {
        background: #e3f2fd;
        color: #0d47a1;
    }
    
    /* Risk score circular */
    .risk-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        background: conic-gradient(#667eea var(--score), #eef2f7 var(--score));
        position: relative;
    }
    
    .risk-circle-inner {
        width: 90px;
        height: 90px;
        border-radius: 50%;
        background: white;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    
    .risk-number {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1a2332;
        line-height: 1;
    }
    
    .risk-label {
        font-size: 0.7rem;
        color: #8a9bb5;
        font-weight: 500;
        letter-spacing: 0.5px;
    }
    
    /* Admin stats */
    .stat-card {
        background: white;
        border-radius: 18px;
        padding: 1.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.03);
        border: 1px solid #eef2f7;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.06);
        border-color: #667eea;
    }
    
    .stat-number {
        font-size: 2.4rem;
        font-weight: 800;
        color: #1a2332;
        line-height: 1.2;
    }
    
    .stat-label {
        color: #8a9bb5;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .stat-icon {
        font-size: 2rem;
        opacity: 0.8;
    }
    
    /* Buttons */
    .btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3) !important;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4) !important;
    }
    
    .btn-secondary {
        background: white !important;
        color: #667eea !important;
        border: 2px solid #667eea !important;
        border-radius: 50px !important;
        padding: 0.5rem 1.8rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .btn-secondary:hover {
        background: #667eea !important;
        color: white !important;
    }
    
    /* Header */
    .header-modern {
        background: rgba(255,255,255,0.9);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 0.8rem 2rem;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border: 1px solid rgba(255,255,255,0.3);
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
    }
    
    .header-title {
        font-weight: 800;
        font-size: 1.4rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .user-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 1rem;
    }
    
    .logout-btn {
        background: #f0f2f6;
        border: none;
        border-radius: 50px;
        padding: 0.4rem 1.2rem;
        font-weight: 600;
        color: #667eea;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .logout-btn:hover {
        background: #fee2e2;
        color: #dc2626;
    }
    
    /* Detail view */
    .detail-section {
        background: white;
        border-radius: 20px;
        padding: 1.8rem;
        margin-bottom: 1.2rem;
        border: 1px solid #eef2f7;
        box-shadow: 0 4px 16px rgba(0,0,0,0.03);
    }
    
    .detail-section h4 {
        color: #1a2332;
        font-weight: 700;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    
    .transaction-item {
        display: flex;
        justify-content: space-between;
        padding: 0.6rem 0;
        border-bottom: 1px solid #f0f2f6;
    }
    
    .transaction-item:last-child {
        border-bottom: none;
    }
    
    .transaction-amount {
        font-weight: 600;
    }
    
    .transaction-amount.credit {
        color: #2e7d32;
    }
    
    .transaction-amount.debit {
        color: #c62828;
    }
    
    .badge-risk {
        padding: 0.3rem 1.2rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.8rem;
        letter-spacing: 0.3px;
    }
    
    .badge-risk.low {
        background: #e8f5e9;
        color: #2e7d32;
    }
    
    .badge-risk.medium {
        background: #fff3e0;
        color: #e65100;
    }
    
    .badge-risk.high {
        background: #ffebee;
        color: #c62828;
    }
    
    /* Misc */
    .divider {
        border: none;
        height: 1px;
        background: linear-gradient(to right, transparent, #e0e5ec, transparent);
        margin: 1.5rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    
    .stButton > button {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* File uploader styling */
    .uploaded-file {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 0.3rem 0.8rem;
        font-size: 0.85rem;
        color: #1a2332;
    }
</style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE INIT ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None
if "selected_loan" not in st.session_state:
    st.session_state.selected_loan = None
if "documents" not in st.session_state:
    st.session_state.documents = {}
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "risk_score" not in st.session_state:
    st.session_state.risk_score = None
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "selected_applicant" not in st.session_state:
    st.session_state.selected_applicant = None
if "gcs_upload_status" not in st.session_state:
    st.session_state.gcs_upload_status = {}
if "uploaded_to_cloud" not in st.session_state:
    st.session_state.uploaded_to_cloud = False
if "loan_amount" not in st.session_state:
    st.session_state.loan_amount = 0
if "bq_saved" not in st.session_state:
    st.session_state.bq_saved = False
if "bq_data" not in st.session_state:
    st.session_state.bq_data = None

# ---------- MOCK DATA ----------
LOAN_TYPES = {
    "Home Loan": {"icon": "🏠", "desc": "Up to ₹5 Cr • 8.5% p.a.", "color": "#667eea"},
    "Car Loan": {"icon": "🚗", "desc": "Up to ₹50 L • 9.2% p.a.", "color": "#f093fb"},
    "Gold Loan": {"icon": "💎", "desc": "Up to ₹2 Cr • 7.8% p.a.", "color": "#f6d365"},
    "Personal Loan": {"icon": "💳", "desc": "Up to ₹25 L • 10.5% p.a.", "color": "#4facfe"},
}

DOCUMENT_TEMPLATES = {
    "Home Loan": ["PAN Card", "Aadhaar Card", "Income Tax Returns (3 yrs)", "Bank Statements (6 months)", "Property Documents"],
    "Car Loan": ["PAN Card", "Aadhaar Card", "Income Tax Returns", "Bank Statements (6 months)", "Vehicle Invoice"],
    "Gold Loan": ["PAN Card", "Aadhaar Card", "Gold Purity Certificate", "Identity Proof", "Address Proof"],
    "Personal Loan": ["PAN Card", "Aadhaar Card", "Salary Slips (3 months)", "Bank Statements (6 months)", "Employment Proof"],
}

# ---------- LOGIN PAGE ----------
def login_page():
    st.markdown("""
    <div class='login-wrapper'>
        <div class='login-box'>
            <div style='text-align: center; margin-bottom: 0.5rem;'>
                <span style='font-size: 3.5rem;'>🏦</span>
            </div>
            <div class='login-title'>AI Loan Portal</div>
            <div class='login-subtitle'>Secure • Intelligent • Fast</div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username", label_visibility="collapsed")
        password = st.text_input("Password", type="password", placeholder="Enter your password", label_visibility="collapsed")
        
        col1, col2 = st.columns(2)
        with col1:
            user_btn = st.form_submit_button("👤 User", use_container_width=True)
        with col2:
            admin_btn = st.form_submit_button("🛡️ Admin", use_container_width=True)
        
        if user_btn or admin_btn:
            if username and password:
                st.session_state.logged_in = True
                st.session_state.role = "user" if user_btn else "admin"
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Please fill all fields.")
    
    st.markdown("""
        <div style='text-align:center; margin-top: 1.5rem; color: #8a9bb5; font-size: 0.8rem;'>
            Demo: any username/password
        </div>
    </div></div>
    """, unsafe_allow_html=True)

# ---------- USER DASHBOARD ----------
def user_dashboard():
    # Initialize GCS and BigQuery clients
    gcs_client = initialize_gcs()
    bq_client = initialize_bigquery()
    
    # Header with working logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 0.8rem;'>
            <span style='font-size: 1.6rem;'>🏦</span>
            <span class='header-title'>AI Loan Portal</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 1rem; justify-content: flex-end;'>
            <span style='color: #1a2332; font-weight: 500;'>👋 {st.session_state.username}</span>
            <div class='user-avatar'>{st.session_state.username[0].upper()}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Logout button using Streamlit
        if st.button("🚪 Logout", key="user_logout", use_container_width=True):
            logout()
    
    if st.session_state.selected_loan is None:
        # Show loan cards
        st.markdown("<h3 style='color: #1a2332; font-weight: 700; margin-bottom: 0.3rem;'>Choose Your Loan</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #8a9bb5; margin-bottom: 2rem;'>Select a loan type to begin your application</p>", unsafe_allow_html=True)
        
        cols = st.columns(4)
        for idx, (loan, data) in enumerate(LOAN_TYPES.items()):
            with cols[idx]:
                card_html = f"""
                <div class='loan-card-modern' style='border-bottom: 4px solid {data["color"]};'>
                    <div class='loan-icon'>{data["icon"]}</div>
                    <div class='loan-name'>{loan}</div>
                    <div class='loan-desc'>{data["desc"]}</div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                if st.button(f"Apply Now", key=f"select_{idx}", use_container_width=True):
                    st.session_state.selected_loan = loan
                    st.session_state.documents = {doc: None for doc in DOCUMENT_TEMPLATES[loan]}
                    st.session_state.submitted = False
                    st.session_state.risk_score = None
                    st.session_state.analysis = None
                    st.session_state.gcs_upload_status = {}
                    st.session_state.uploaded_to_cloud = False
                    st.session_state.loan_amount = 0
                    st.session_state.bq_saved = False
                    st.rerun()
    else:
        # Show document upload
        loan = st.session_state.selected_loan
        docs = DOCUMENT_TEMPLATES[loan]
        
        # Back button
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.selected_loan = None
                st.rerun()
        
        st.markdown(f"""
        <div class='glass-card' style='margin-bottom: 1.5rem;'>
            <div style='display: flex; align-items: center; gap: 1rem;'>
                <span style='font-size: 2.5rem;'>{LOAN_TYPES[loan]["icon"]}</span>
                <div>
                    <h3 style='color: #1a2332; font-weight: 700; margin: 0;'>{loan}</h3>
                    <p style='color: #8a9bb5; margin: 0; font-size: 0.9rem;'>Please upload all required documents for AI verification</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ---------- TASK 1: Add Loan Amount Field ----------
        st.markdown("""
        <div style='background: white; border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem; border: 1px solid #eef2f7;'>
            <h4 style='color: #1a2332; font-weight: 600; margin-bottom: 0.5rem;'>💰 Loan Details</h4>
        """, unsafe_allow_html=True)
        
        # Loan amount input
        loan_amount = st.number_input(
            "Enter Loan Amount (₹)",
            min_value=10000,
            max_value=50000000,
            value=st.session_state.loan_amount if st.session_state.loan_amount > 0 else 100000,
            step=10000,
            format="%d",
            key="loan_amount_input"
        )
        st.session_state.loan_amount = loan_amount
        
        # Display loan amount in Indian format
        if loan_amount > 0:
            loan_in_lakhs = loan_amount / 100000
            loan_in_crores = loan_amount / 10000000
            display_text = f"₹{loan_amount:,}"
            if loan_in_crores >= 1:
                display_text += f" ({loan_in_crores:.2f} Cr)"
            elif loan_in_lakhs >= 1:
                display_text += f" ({loan_in_lakhs:.2f} L)"
            st.info(f"💰 Loan Amount: **{display_text}**")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Document rows
        all_uploaded = True
        for doc in docs:
            col1, col2, col3 = st.columns([2.5, 1.2, 1.5])
            with col1:
                st.markdown(f"<div class='doc-name'>📄 {doc}</div>", unsafe_allow_html=True)
            with col2:
                if st.session_state.documents.get(doc) is not None:
                    if doc in st.session_state.gcs_upload_status and st.session_state.gcs_upload_status[doc].get("success"):
                        st.markdown("<span class='doc-status-badge cloud-uploaded'>☁️ Cloud Uploaded</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span class='doc-status-badge uploaded'>✅ Uploaded</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='doc-status-badge pending'>⏳ Pending</span>", unsafe_allow_html=True)
            with col3:
                if st.session_state.documents.get(doc) is None:
                    uploaded_file = st.file_uploader("", type=["pdf", "png", "jpg", "jpeg"], key=f"upload_{doc}", label_visibility="collapsed")
                    if uploaded_file is not None:
                        st.session_state.documents[doc] = uploaded_file
                        st.rerun()
                else:
                    if st.button("✖ Remove", key=f"remove_{doc}"):
                        st.session_state.documents[doc] = None
                        if doc in st.session_state.gcs_upload_status:
                            del st.session_state.gcs_upload_status[doc]
                        st.rerun()
            if st.session_state.documents.get(doc) is None:
                all_uploaded = False
        
        # Submit button - upload to GCS, verify, and save to BigQuery
        col1, col2, col3 = st.columns([2, 1.5, 1])
        with col2:
            if st.button("🚀 Submit for AI Verification", disabled=not all_uploaded or st.session_state.loan_amount <= 0, use_container_width=True):
                if st.session_state.loan_amount <= 0:
                    st.error("❌ Please enter a valid loan amount.")
                elif gcs_client is None:
                    st.error("❌ Google Cloud Storage client not initialized. Please check your credentials.")
                    st.info("💡 In Cloud Shell, run: gcloud auth application-default login")
                else:
                    with st.spinner("📤 Uploading documents to Google Cloud Storage..."):
                        bucket_name = "document-agent-storage"
                        all_uploads_successful = True
                        upload_errors = []
                        
                        # Upload each document to GCS
                        for doc_name, file_obj in st.session_state.documents.items():
                            if file_obj is not None and doc_name not in st.session_state.gcs_upload_status:
                                # Reset file pointer to beginning
                                file_obj.seek(0)
                                
                                # Upload to GCS
                                result = upload_to_gcs(
                                    gcs_client,
                                    bucket_name,
                                    file_obj,
                                    file_obj.name,
                                    st.session_state.username,
                                    loan
                                )
                                
                                if result["success"]:
                                    st.session_state.gcs_upload_status[doc_name] = {
                                        "success": True,
                                        "path": result["path"],
                                        "public_url": result.get("public_url", "")
                                    }
                                else:
                                    all_uploads_successful = False
                                    upload_errors.append(f"{doc_name}: {result['error']}")
                                    st.session_state.gcs_upload_status[doc_name] = {
                                        "success": False,
                                        "error": result["error"]
                                    }
                        
                        if all_uploads_successful:
                            st.session_state.uploaded_to_cloud = True
                            st.success("✅ All documents uploaded to Google Cloud Storage successfully!")
                            
                            # Now perform AI verification
                            with st.spinner("🤖 AI is verifying documents..."):
                                time.sleep(2)
                                st.session_state.risk_score = random.randint(15, 85)
                                risk_level = "Low" if st.session_state.risk_score < 40 else "Medium" if st.session_state.risk_score < 70 else "High"
                                
                                # Determine loan status based on risk score
                                if st.session_state.risk_score < 40:
                                    loan_status = "Approved"
                                elif st.session_state.risk_score < 70:
                                    loan_status = "Under Review"
                                else:
                                    loan_status = "Rejected"
                                
                                st.session_state.analysis = f"""
                                ✅ **Document Verification:** All {len(docs)} documents verified successfully and stored in cloud.
                                📁 **Storage Location:** gs://document-agent-storage/user/{st.session_state.username}/{loan}/
                                📊 **Risk Assessment:** {risk_level} risk profile identified.
                                💰 **Transaction History:** Stable income pattern with no defaults in last 24 months.
                                📈 **Analytics:** Application is {'strong' if st.session_state.risk_score < 50 else 'moderate'}.
                                """
                                
                                # ---------- TASK 2: Save to BigQuery ----------
                                if bq_client is not None:
                                    try:
                                        # Use your exact dataset and table names
                                        dataset_id = "UserData"
                                        table_id = "User-Info"  # Using hyphen as per your query
                                        
                                        # Create dataset if it doesn't exist
                                        try:
                                            bq_client.get_dataset(dataset_id)
                                        except Exception:
                                            dataset = bigquery.Dataset(f"{bq_client.project}.{dataset_id}")
                                            dataset.location = "US"
                                            bq_client.create_dataset(dataset, exists_ok=True)
                                            st.info(f"📊 Dataset '{dataset_id}' created successfully!")
                                        
                                        # Create table if it doesn't exist with proper schema
                                        table_ref = bq_client.dataset(dataset_id).table(table_id)
                                        try:
                                            bq_client.get_table(table_ref)
                                            st.info(f"📊 Table '{dataset_id}.{table_id}' exists. Inserting data...")
                                        except Exception:
                                            # Table doesn't exist, create it
                                            schema = [
                                                bigquery.SchemaField("User_Name", "STRING", mode="REQUIRED"),
                                                bigquery.SchemaField("Loan_Type", "STRING", mode="REQUIRED"),
                                                bigquery.SchemaField("Loan_Amt", "STRING", mode="REQUIRED"),
                                                bigquery.SchemaField("Score", "STRING", mode="REQUIRED"),
                                                bigquery.SchemaField("Loan_Status", "STRING", mode="REQUIRED"),
                                            ]
                                            table = bigquery.Table(table_ref, schema=schema)
                                            bq_client.create_table(table)
                                            st.info(f"📊 Table '{dataset_id}.{table_id}' created successfully!")
                                        
                                        # Save to BigQuery - convert all to strings
                                        bq_result = save_to_bigquery(
                                            bq_client,
                                            dataset_id,
                                            table_id,
                                            {
                                                "username": st.session_state.username,
                                                "loan_type": loan,
                                                "loan_amount": float(st.session_state.loan_amount),
                                                "risk_score": int(st.session_state.risk_score),
                                                "loan_status": loan_status
                                            }
                                        )
                                        
                                        if bq_result["success"]:
                                            st.session_state.bq_saved = True
                                            st.success(f"✅ Data successfully saved to BigQuery: {dataset_id}.{table_id}")
                                            st.info(f"📊 Query: SELECT * FROM `{bq_client.project}.{dataset_id}.{table_id}`")
                                        else:
                                            st.warning(f"⚠️ BigQuery save issue: {bq_result['error']}")
                                    except Exception as e:
                                        st.warning(f"⚠️ BigQuery operation issue: {str(e)}")
                                        st.info("💡 Make sure you have BigQuery enabled and proper permissions.")
                                else:
                                    st.warning("⚠️ BigQuery client not initialized. Data will not be saved to BigQuery.")
                                
                                st.session_state.submitted = True
                                st.rerun()
                        else:
                            st.error(f"❌ Failed to upload some documents to GCS: {', '.join(upload_errors)}")
        
        # Show results if submitted
        if st.session_state.submitted and st.session_state.risk_score is not None:
            st.markdown("<hr class='divider'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #1a2332; font-weight: 700;'>📊 AI Verification Results</h4>", unsafe_allow_html=True)
            
            # Show cloud storage info
            if st.session_state.uploaded_to_cloud:
                st.success(f"📁 Documents stored in: `gs://document-agent-storage/user/{st.session_state.username}/{loan}/`")
            
            # Show BigQuery info
            if st.session_state.bq_saved:
                st.success("📊 Data saved to BigQuery: `UserData.User-Info` table")
                st.info("🔍 Run this query to check: `SELECT * FROM `hack-team-promptops.UserData.User-Info``")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                risk_level = "Low" if st.session_state.risk_score < 40 else "Medium" if st.session_state.risk_score < 70 else "High"
                risk_class = "low" if st.session_state.risk_score < 40 else "medium" if st.session_state.risk_score < 70 else "high"
                
                # Determine loan status
                if st.session_state.risk_score < 40:
                    loan_status = "✅ Approved"
                    status_color = "#2e7d32"
                elif st.session_state.risk_score < 70:
                    loan_status = "⏳ Under Review"
                    status_color = "#e65100"
                else:
                    loan_status = "❌ Rejected"
                    status_color = "#c62828"
                
                st.markdown(f"""
                <div style='background: white; border-radius: 20px; padding: 1.8rem; text-align: center; border: 1px solid #eef2f7;'>
                    <div style='position: relative; display: inline-block;'>
                        <div class='risk-circle' style='--score: {st.session_state.risk_score}%;'>
                            <div class='risk-circle-inner'>
                                <div class='risk-number'>{st.session_state.risk_score}</div>
                                <div class='risk-label'>Risk Score</div>
                            </div>
                        </div>
                    </div>
                    <div style='margin-top: 0.8rem;'>
                        <span class='badge-risk {risk_class}'>{risk_level} Risk</span>
                    </div>
                    <div style='margin-top: 0.8rem; padding-top: 0.8rem; border-top: 1px solid #f0f2f6;'>
                        <div style='font-size: 0.9rem; color: #8a9bb5;'>Loan Status</div>
                        <div style='font-size: 1.3rem; font-weight: 700; color: {status_color};'>{loan_status}</div>
                    </div>
                    <div style='margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid #f0f2f6;'>
                        <div style='font-size: 0.9rem; color: #8a9bb5;'>Loan Amount</div>
                        <div style='font-size: 1.1rem; font-weight: 700; color: #1a2332;'>₹{st.session_state.loan_amount:,}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div style='background: white; border-radius: 20px; padding: 1.8rem; border: 1px solid #eef2f7; height: 100%;'>
                    <div style='color: #1a2332; line-height: 2; font-size: 0.95rem;'>
                        {st.session_state.analysis}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ---------- ADMIN DASHBOARD ----------
def admin_dashboard():
    # Header with working logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 0.8rem;'>
            <span style='font-size: 1.6rem;'>🏦</span>
            <span class='header-title'>Admin Dashboard</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 1rem; justify-content: flex-end;'>
            <span style='color: #1a2332; font-weight: 500;'>🛡️ {st.session_state.username}</span>
            <div class='user-avatar' style='background: linear-gradient(135deg, #f093fb, #f5576c);'>{st.session_state.username[0].upper()}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Logout button using Streamlit
        if st.button("🚪 Logout", key="admin_logout", use_container_width=True):
            logout()
    
    # Initialize BigQuery client
    bq_client = initialize_bigquery()
    
    # Check if viewing application detail
    if st.session_state.selected_applicant is not None:
        show_application_detail()
        return
    
    # Fetch data from BigQuery with better error handling
    if bq_client is not None:
        with st.spinner("🔄 Fetching data from BigQuery..."):
            df = get_bigquery_data(bq_client)
            if df is not None and not df.empty:
                st.session_state.bq_data = df
                st.success(f"✅ Successfully loaded {len(df)} records from BigQuery")
            elif df is not None and df.empty:
                st.session_state.bq_data = None
                st.info("📊 BigQuery table exists but has no records yet.")
            else:
                st.session_state.bq_data = None
                st.warning("⚠️ Could not fetch data from BigQuery. Please check the table exists.")
    else:
        st.session_state.bq_data = None
        st.warning("⚠️ BigQuery client not initialized. Please check your credentials.")
    
    # Stats row - Calculate from BigQuery data
    st.markdown("<h3 style='color: #1a2332; font-weight: 700; margin-bottom: 0.3rem;'>📊 Overview</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8a9bb5; margin-bottom: 1.5rem;'>Monitor all loan applications and AI analytics</p>", unsafe_allow_html=True)
    
    if st.session_state.bq_data is not None and not st.session_state.bq_data.empty:
        df = st.session_state.bq_data
        total_applications = len(df)
        verified = len(df[df['Loan_Status'] == 'Approved'])
        pending = len(df[df['Loan_Status'] == 'Under Review'])
        rejected = len(df[df['Loan_Status'] == 'Rejected'])
        
        col1, col2, col3, col4 = st.columns(4)
        stats = [
            {"icon": "📋", "number": total_applications, "label": "Total Applications", "color": "#667eea"},
            {"icon": "✅", "number": verified, "label": "Approved", "color": "#2e7d32"},
            {"icon": "⏳", "number": pending, "label": "Under Review", "color": "#e65100"},
            {"icon": "❌", "number": rejected, "label": "Rejected", "color": "#c62828"},
        ]
        
        for idx, stat in enumerate(stats):
            with col1 if idx == 0 else col2 if idx == 1 else col3 if idx == 2 else col4:
                st.markdown(f"""
                <div class='stat-card'>
                    <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
                        <div>
                            <div class='stat-number'>{stat["number"]}</div>
                            <div class='stat-label'>{stat["label"]}</div>
                        </div>
                        <div class='stat-icon'>{stat["icon"]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        col1, col2, col3, col4 = st.columns(4)
        stats = [
            {"icon": "📋", "number": 0, "label": "Total Applications", "color": "#667eea"},
            {"icon": "✅", "number": 0, "label": "Approved", "color": "#2e7d32"},
            {"icon": "⏳", "number": 0, "label": "Under Review", "color": "#e65100"},
            {"icon": "❌", "number": 0, "label": "Rejected", "color": "#c62828"},
        ]
        
        for idx, stat in enumerate(stats):
            with col1 if idx == 0 else col2 if idx == 1 else col3 if idx == 2 else col4:
                st.markdown(f"""
                <div class='stat-card'>
                    <div style='display: flex; justify-content: space-between; align-items: flex-start;'>
                        <div>
                            <div class='stat-number'>{stat["number"]}</div>
                            <div class='stat-label'>{stat["label"]}</div>
                        </div>
                        <div class='stat-icon'>{stat["icon"]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Applications table - Display data from BigQuery
    st.markdown("<h4 style='color: #1a2332; font-weight: 700; margin: 1.5rem 0 1rem 0;'>📋 Recent Applications</h4>", unsafe_allow_html=True)
    
    if st.session_state.bq_data is not None and not st.session_state.bq_data.empty:
        df = st.session_state.bq_data
        
        # Create clickable table rows
        for idx, row in df.iterrows():
            risk_score = row['Risk_Score']
            risk_class = "low" if risk_score < 40 else "medium" if risk_score < 70 else "high"
            
            col1, col2, col3, col4, col5, col6 = st.columns([1.2, 1.2, 1.2, 0.8, 1.2, 0.8])
            
            with col1:
                st.markdown(f"**{row['User_Name']}**")
            with col2:
                st.markdown(f"{row['Loan_Type']}")
            with col3:
                st.markdown(f"₹{row['Loan_Amt']:,.0f}")
            with col4:
                st.markdown(f"<span class='badge-risk {risk_class}'>{risk_score}</span>", unsafe_allow_html=True)
            with col5:
                status = row['Loan_Status']
                if status == "Approved":
                    st.markdown(f"✅ {status}")
                elif status == "Under Review":
                    st.markdown(f"⏳ {status}")
                else:
                    st.markdown(f"❌ {status}")
            with col6:
                # Store the index or user name to handle detail view
                if st.button("View Details", key=f"view_bq_{idx}", use_container_width=True):
                    st.session_state.selected_applicant = idx
                    st.session_state.selected_applicant_data = row.to_dict()
                    st.rerun()
            st.markdown("<hr style='margin: 0.2rem 0; border-color: #f0f2f6;'>", unsafe_allow_html=True)
    else:
        st.info("📊 No applications found in BigQuery. Submit some loan applications to see data here.")
    
    # BigQuery Data Viewer Section
    st.markdown("""
    <hr class='divider'>
    <div style='background: white; border-radius: 20px; padding: 1.8rem; border: 1px solid #eef2f7; margin-top: 1.5rem;'>
        <h4 style='color: #1a2332; font-weight: 700; margin-bottom: 1rem;'>📊 Complete BigQuery Data</h4>
        <p style='color: #8a9bb5; margin-bottom: 1rem;'>Full dataset from BigQuery table: <code>UserData.User-Info</code></p>
    """, unsafe_allow_html=True)
    
  #  if st.session_state.bq_data is not None and not st.session_state.bq_data.empty:
   #     st.dataframe(st.session_state.bq_data, use_container_width=True, hide_index=True)
    #    st.caption(f"📊 Total records: {len(st.session_state.bq_data)}")
        
        # Add refresh button
     #   if st.button("🔄 Refresh Data", use_container_width=True):
      #      with st.spinner("🔄 Refreshing data from BigQuery..."):
       #         df = get_bigquery_data(bq_client)
        #        if df is not None:
         #           st.session_state.bq_data = df
           #          st.rerun()
    #else:
     #   st.info("📊 No data found in BigQuery table. Submit some loan applications to populate data.")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # AI Analytics Summary
    if st.session_state.bq_data is not None and not st.session_state.bq_data.empty:
        df = st.session_state.bq_data
        approval_rate = (len(df[df['Loan_Status'] == 'Approved']) / len(df) * 100) if len(df) > 0 else 0
        avg_risk = df['Risk_Score'].mean() if not df.empty else 0
        most_popular = df['Loan_Type'].mode().iloc[0] if not df.empty else "N/A"
        
        st.markdown("""
        <hr class='divider'>
        <div style='background: white; border-radius: 20px; padding: 1.8rem; border: 1px solid #eef2f7; margin-top: 1.5rem;'>
            <h4 style='color: #1a2332; font-weight: 700; margin-bottom: 1rem;'>🤖 AI Analytics Summary</h4>
            <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1.5rem;'>
                <div>
                    <div style='color: #8a9bb5; font-size: 0.85rem;'>Approval Rate</div>
                    <div style='font-size: 1.8rem; font-weight: 800; color: #1a2332;'>{approval_rate:.1f}%</div>
                </div>
                <div>
                    <div style='color: #8a9bb5; font-size: 0.85rem;'>Avg Risk Score</div>
                    <div style='font-size: 1.8rem; font-weight: 800; color: #1a2332;'>{avg_risk:.1f}</div>
                </div>
                <div>
                    <div style='color: #8a9bb5; font-size: 0.85rem;'>Most Popular</div>
                    <div style='font-size: 1.8rem; font-weight: 800; color: #1a2332;'>{most_popular}</div>
                </div>
            </div>
            <div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #f0f2f6;'>
                <div style='color: #8a9bb5; font-size: 0.85rem;'>Document Verification Success Rate</div>
                <div style='height: 8px; background: #f0f2f6; border-radius: 50px; margin-top: 0.5rem; overflow: hidden;'>
                    <div style='height: 100%; width: 89%; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 50px;'></div>
                </div>
                <div style='display: flex; justify-content: space-between; margin-top: 0.3rem;'>
                    <span style='color: #8a9bb5; font-size: 0.8rem;'>89% success rate</span>
                    <span style='color: #667eea; font-size: 0.8rem; font-weight: 600;'>AI Verified</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <hr class='divider'>
        <div style='background: white; border-radius: 20px; padding: 1.8rem; border: 1px solid #eef2f7; margin-top: 1.5rem;'>
            <h4 style='color: #1a2332; font-weight: 700; margin-bottom: 1rem;'>🤖 AI Analytics Summary</h4>
            <p style='color: #8a9bb5;'>No data available for analytics. Submit applications to generate insights.</p>
        </div>
        """, unsafe_allow_html=True)

def show_application_detail():
    """Show detailed view of selected application from BigQuery"""
    if st.session_state.selected_applicant_data:
        applicant = st.session_state.selected_applicant_data
    else:
        # Fallback to mock data if needed
        applicant = {
            "User_Name": "Unknown",
            "Loan_Type": "Unknown",
            "Loan_Amt": 0,
            "Risk_Score": 0,
            "Loan_Status": "Unknown"
        }
    
    # Back button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.selected_applicant = None
            st.session_state.selected_applicant_data = None
            st.rerun()
    
    st.markdown(f"""
    <div style='display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem;'>
        <div style='width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg, #667eea, #764ba2); display: flex; align-items: center; justify-content: center; color: white; font-size: 1.8rem; font-weight: 700;'>
            {applicant['User_Name'][0].upper() if applicant['User_Name'] != 'Unknown' else '?'}
        </div>
        <div>
            <h2 style='color: #1a2332; font-weight: 800; margin: 0;'>{applicant['User_Name']}</h2>
            <div style='display: flex; gap: 1.5rem; color: #8a9bb5;'>
                <span>{applicant['Loan_Type']}</span>
                <span>•</span>
                <span>₹{applicant['Loan_Amt']:,.0f}</span>
                <span>•</span>
                <span>Status: {applicant['Loan_Status']}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        # Risk Score Card
        risk_score = applicant['Risk_Score']
        risk_class = "low" if risk_score < 40 else "medium" if risk_score < 70 else "high"
        risk_label = "Low" if risk_score < 40 else "Medium" if risk_score < 70 else "High"
        
        st.markdown(f"""
        <div class='detail-section'>
            <h4>📊 Risk & Credit Profile</h4>
            <div style='text-align: center; padding: 0.5rem 0;'>
                <div style='position: relative; display: inline-block;'>
                    <div class='risk-circle' style='--score: {risk_score}%;'>
                        <div class='risk-circle-inner'>
                            <div class='risk-number'>{risk_score}</div>
                            <div class='risk-label'>Risk Score</div>
                        </div>
                    </div>
                </div>
                <div style='margin-top: 0.8rem;'>
                    <span class='badge-risk {risk_class}'>{risk_label} Risk</span>
                </div>
            </div>
            <hr style='border-color: #f0f2f6; margin: 1rem 0;'>
            <div style='display: flex; justify-content: space-between; padding: 0.3rem 0;'>
                <span style='color: #8a9bb5;'>Loan Amount</span>
                <span style='font-weight: 700; color: #1a2332;'>₹{applicant['Loan_Amt']:,.0f}</span>
            </div>
            <div style='display: flex; justify-content: space-between; padding: 0.3rem 0;'>
                <span style='color: #8a9bb5;'>Application Status</span>
                <span style='font-weight: 600;'>{applicant['Loan_Status']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Transaction History (Mock data since we don't have transaction history in BigQuery)
        st.markdown(f"""
        <div class='detail-section'>
            <h4>💰 Transaction History</h4>
            <p style='color: #8a9bb5; font-size: 0.9rem;'>Transaction history is not available in BigQuery for this demo.</p>
            <div style='background: #f8f9fa; border-radius: 12px; padding: 1rem; margin-top: 0.5rem;'>
                <p style='color: #1a2332; font-size: 0.9rem;'>📊 <strong>Credit Score:</strong> {random.randint(650, 800)}</p>
                <p style='color: #1a2332; font-size: 0.9rem;'>📈 <strong>Repayment Capacity:</strong> {'Strong' if risk_score < 50 else 'Moderate' if risk_score < 70 else 'Needs Review'}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # AI Analysis
        risk_label = "Low" if risk_score < 40 else "Medium" if risk_score < 70 else "High"
        st.markdown(f"""
        <div class='detail-section' style='background: linear-gradient(135deg, #f8f9ff, #f0f2ff); border-color: #667eea;'>
            <h4>🤖 AI Analysis</h4>
            <div style='color: #1a2332; line-height: 1.8; font-size: 0.95rem;'>
                <div>✅ <strong>Document Verification:</strong> All documents verified</div>
                <div>📊 <strong>Risk Assessment:</strong> {risk_label} risk profile</div>
                <div>📈 <strong>Repayment Capacity:</strong> {'Strong' if risk_score < 50 else 'Moderate' if risk_score < 70 else 'Needs Review'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ---------- MAIN APP ----------
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        if st.session_state.role == "admin":
            admin_dashboard()
        else:
            user_dashboard()

if __name__ == "__main__":
    main()