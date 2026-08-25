import streamlit as st
import random
import smtplib
from datetime import date, datetime, timedelta
from email.mime.text import MIMEText
from supabase import create_client

# ---------------------------------------------------------
# PAGE CONFIG & STYLES
# ---------------------------------------------------------
st.set_page_config(page_title="PS DIGITAL", page_icon="📱", layout="centered")

st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"],
    div[data-testid="stToolbar"], div[data-testid="stDecoration"], div[data-testid="stStatusWidget"],
    div[data-testid="stAppViewerHost"], [data-testid="manage-app-button"] {
        display: none !important; visibility: hidden !important;
    }
    .main .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    .company-header {
        background: linear-gradient(135deg, #FF512F 0%, #DD2476 100%);
        color: #FFFFFF; padding: 16px 24px; border-radius: 12px;
        text-align: center; font-family: 'Trebuchet MS', sans-serif;
        font-size: 26px; font-weight: 800; letter-spacing: 1px;
        box-shadow: 0px 4px 15px rgba(221, 36, 118, 0.35);
        margin-top: 10px; margin-bottom: 20px; text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CREDENTIALS CONFIGURATION
# ---------------------------------------------------------
SUPABASE_URL = "https://tqxbeudrvkinuujojasx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxeGJldWRydmtpbnV1am9qYXN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc1NDQ5NzcsImV4cCI6MjEwMzEyMDk3N30.UC0UDV-vTsSnw8Ff2Jrp9DAfhhhpIkz1iY5eDtimU78"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SUPER_ADMIN_EMAIL = "pardhukilli273@gmail.com"
SENDER_EMAIL = "pardhukilli273@gmail.com"
SENDER_PASSWORD = "fneh pjig gqum vtmv"

if "otp_sent" not in st.session_state: st.session_state.otp_sent = False
if "generated_otp" not in st.session_state: st.session_state.generated_otp = None
if "verified_email" not in st.session_state: st.session_state.verified_email = None
if "selected_date" not in st.session_state: st.session_state.selected_date = date.today()
if "show_host_reg" not in st.session_state: st.session_state.show_host_reg = False

def send_otp_email(target_email, otp_code):
    try:
        msg = MIMEText(f"Your verification code for PS DIGITAL Platform is: {otp_code}")
        msg['Subject'] = 'PS DIGITAL - Email Verification Code'
        msg['From'] = SENDER_EMAIL
        msg['To'] = target_email
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, target_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error sending email: {e}")
        return False

def generate_unique_emp_id():
    response = supabase.table("employees").select("employee_no").execute()
    existing_ids = {str(row.get("employee_no")).strip() for row in (response.data or []) if row.get("employee_no")}
    for _ in range(1000):
        rand_id = str(random.randint(1, 1000))
        if rand_id not in existing_ids: return rand_id
    return str(random.randint(1001, 9999))

# ---------------------------------------------------------
# STAGE 1: LOGIN & OTP VERIFICATION
# ---------------------------------------------------------
if not st.session_state.verified_email:
    st.title("📱 PS DIGITAL")
    st.caption("ENTERPRISE MULTI-HOST MANAGEMENT & ATTENDANCE SYSTEM")
    user_email = st.text_input("Enter Email Address to Access Portal").strip().lower()

    if user_email and not st.session_state.otp_sent:
        if st.button("Send Verification Code"):
            otp = str(random.randint(100000, 999999))
            if send_otp_email(user_email, otp):
                st.session_state.generated_otp = otp
                st.session_state.otp_sent = True
                st.session_state.temp_email = user_email
                st.success(f"Verification code sent to {user_email}!")
                st.rerun()

    if st.session_state.otp_sent:
        st.info(f"Enter the 6-digit code sent to **{st.session_state.temp_email}**")
        input_otp = st.text_input("6-Digit Verification Code", max_chars=6)

        if st.button("Verify & Login"):
            if input_otp == st.session_state.generated_otp:
                st.session_state.verified_email = st.session_state.temp_email
                st.session_state.otp_sent = False
                st.rerun()
            else:
                st.error("Invalid Code!")
        if st.button("Resend Code / Change Email"):
            st.session_state.otp_sent = False
            st.rerun()

# ---------------------------------------------------------
# STAGE 2: MAIN PORTAL (AUTOMATIC ROUTING)
# ---------------------------------------------------------
else:
    active_email = st.session_state.verified_email
    host_check = supabase.table("companies").select("*").eq("host_email", active_email).execute().data
    emp_records = supabase.table("employees").select("*").eq("email", active_email).execute().data

    # --- 1. SUPER ADMIN VIEW ---
    if active_email == SUPER_ADMIN_EMAIL:
        st.title("📱 PS DIGITAL")
        if st.button("Logout"):
            st.session_state.verified_email = None
            st.rerun()
        st.markdown("---")
        st.success("👑 Main Platform Super Admin Dashboard")
        companies = supabase.table("companies").select("*").execute().data or []
        st.metric("Total Companies Registered", len(companies))
        st.dataframe(companies)

    # --- 2. HOST DASHBOARD ---
    elif host_check:
        comp = host_check[0]
        c_name = comp.get("company_name")
        st.markdown(f'<div class="company-header">🏢 {c_name}</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        col1.write(f"Logged in as Host: **{comp.get('host_name')}**")
        if col2.button("Logout"):
            st.session_state.verified_email = None
            st.rerun()
        st.markdown("---")

        menu = st.selectbox("Select Action", ["📊 Attendance Summary", "👥 Employee Directory", "📢 Post Notice", "📅 Declare Holiday"])

        if menu == "📊 Attendance Summary":
            sel_date = st.date_input("Select Date", value=date.today())
            emps = supabase.table("employees").select("*").eq("company_name", c_name).execute().data or []
            att = supabase.table("attendance").select("*").eq("company_name", c_name).eq("attendance_date", str(sel_date)).execute().data or []
            present_emails = {a.get("employee_email") for a in att}
            
            st.metric("Total Staff", len(emps))
            st.subheader("✅ Present List")
            for e in emps:
                if e.get("email") in present_emails: st.write(f"• **{e.get('name')}**")
            st.subheader("❌ Absent List")
            for e in emps:
                if e.get("email") not in present_emails: st.write(f"• **{e.get('name')}**")

        elif menu == "👥 Employee Directory":
            st.dataframe(supabase.table("employees").select("*").eq("company_name", c_name).execute().data or [])

        elif menu == "📢 Post Notice":
            msg = st.text_area("Write Notice Message")
            if st.button("Publish Notice"):
                supabase.table("company_notices").insert({"company_name": c_name, "notice_text": msg.strip()}).execute()
                st.success("Notice published!")

        elif menu == "📅 Declare Holiday":
            h_date = st.date_input("Holiday Date")
            h_title = st.text_input("Holiday Title")
            if st.button("Save Holiday"):
                supabase.table("company_notices").insert({"company_name": c_name, "holiday_date": str(h_date), "holiday_title": h_title.strip()}).execute()
                st.success("Holiday saved!")

    # --- 3. EMPLOYEE DASHBOARD ---
    elif emp_records:
        emp = emp_records[0]
        c_name = emp.get("company_name")
        st.markdown(f'<div class="company-header">🏢 {c_name}</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        col1.write(f"Logged in as Employee: **{emp.get('name')}**")
        if col2.button("Logout"):
            st.session_state.verified_email = None
            st.rerun()
        st.markdown("---")

        notices = supabase.table("company_notices").select("*").eq("company_name", c_name).order("created_at", desc=True).execute().data or []
        if notices and notices[0].get("notice_text"):
            st.info(f"📢 **Latest Notice:** {notices[0].get('notice_text')}")

        st.subheader("📅 Attendance")
        cur_date_str = str(date.today())
        check_att = supabase.table("attendance").select("*").eq("company_name", c_name).eq("employee_email", active_email).eq("attendance_date", cur_date_str).execute().data

        if check_att:
            st.success(f"✅ Marked Present for Today ({cur_date_str})")
        else:
            if st.button("✋ Mark I Came Today (Present)", type="primary"):
                supabase.table("attendance").insert({
                    "company_name": c_name, "employee_email": active_email,
                    "employee_name": emp.get("name"), "attendance_date": cur_date_str, "status": "Present"
                }).execute()
                st.success("Attendance marked!")
                st.rerun()

    # --- 4. NEW USER ONBOARDING ---
    else:
        st.title("📱 PS DIGITAL")
        if st.button("Logout"):
            st.session_state.verified_email = None
            st.rerun()
        st.markdown("---")

        all_comps = [c.get("company_name") for c in (supabase.table("companies").select("company_name").execute().data or [])]

        if st.session_state.show_host_reg:
            st.subheader("🏢 Register Your Company as Host")
            with st.form("host_form"):
                new_c_name = st.text_input("Company / Shop Name *").strip()
                h_name = st.text_input("Host Full Name *")
                h_phone = st.text_input("Host Phone Number")
                if st.form_submit_button("Create Company & Become Host"):
                    if new_c_name and h_name:
                        supabase.table("companies").insert({
                            "company_name": new_c_name, "host_name": h_name,
                            "host_email": active_email, "host_phone": h_phone
                        }).execute()
                        st.session_state.show_host_reg = False
                        st.rerun()
            if st.button("⬅️ Back to Employee Joining Form"):
                st.session_state.show_host_reg = False
                st.rerun()

        else:
            st.warning("No employee profile found. Join your company below:")
            assigned_id = generate_unique_emp_id()
            with st.form("emp_form"):
                st.subheader("Add Employee Profile")
                biz_input = st.selectbox("Select Your Company *", options=all_comps) if all_comps else st.text_input("Company Name *")
                st.text_input("Assigned Employee Number", value=assigned_id, disabled=True)
                name = st.text_input("Full Name *")
                dept = st.text_input("Department")
                pos = st.text_input("Position")
                phone = st.text_input("Phone Number")
                salary = st.text_input("Salary")

                if st.form_submit_button("Save Profile"):
                    if name.strip() and biz_input:
                        supabase.table("employees").insert({
                            "company_name": biz_input, "employee_no": assigned_id,
                            "name": name, "department": dept, "position": pos,
                            "phone": phone, "email": active_email, "salary": salary
                        }).execute()
                        st.rerun()
            st.markdown("---")
            if st.button("👔 Are you the Host / Owner of a company? Click here"):
                st.session_state.show_host_reg = True
                st.rerun()
