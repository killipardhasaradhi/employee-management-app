import streamlit as st
import random
import smtplib
from email.mime.text import MIMEText
from supabase import create_client

# ---------------------------------------------------------
# CLEAN WEB PAGE STYLING (Hides Streamlit UI & Manage App)
# ---------------------------------------------------------
st.set_page_config(page_title="PS DIGITAL - Enterprise Platform", page_icon="📱", layout="centered")

clean_page_css = """
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] {
        display: none !important;
        visibility: hidden !important;
    }
    div[data-testid="stToolbar"], 
    div[data-testid="stDecoration"], 
    div[data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
    }
    div[data-testid="stAppViewerHost"],
    [data-testid="manage-app-button"],
    button[title="Manage app"],
    .viewerBadge_container__1t5dn,
    div[class*="viewerBadge"],
    div[class*="stAppViewerHost"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
    </style>
"""
st.markdown(clean_page_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# CONFIGURATION (UPDATE YOUR CREDENTIALS HERE)
# ---------------------------------------------------------
SUPABASE_URL = "https://tqxbeudrvkinuujojasx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxeGJldWRydmtpbnV1am9qYXN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc1NDQ5NzcsImV4cCI6MjEwMzEyMDk3N30.UC0UDV-vTsSnw8Ff2Jrp9DAfhhhpIkz1iY5eDtimU78"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 👑 YOUR EMAIL (Super Admin / Platform Owner)
SUPER_ADMIN_EMAIL = "pardhukilli273@gmail.com"

# Gmail SMTP Settings for sending OTPs
SENDER_EMAIL = "pardhukilli273@gmail.com"
SENDER_PASSWORD = "fneh pjig gqum vtmv"    # 16-character Gmail App Password

# Session states initialization
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = None
if "verified_email" not in st.session_state:
    st.session_state.verified_email = None

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
    existing_ids = set()
    if response.data:
        for row in response.data:
            if row.get("employee_no"):
                existing_ids.add(str(row.get("employee_no")).strip())
    
    for _ in range(1000):
        rand_id = str(random.randint(1, 1000))
        if rand_id not in existing_ids:
            return rand_id
    return str(random.randint(1001, 9999))

# ---------------------------------------------------------
# APP INTERFACE
# ---------------------------------------------------------
st.title("📱 PS DIGITAL")
st.caption("ENTERPRISE MULTI-HOST MANAGEMENT SYSTEM")

# STAGE 1 & 2: EMAIL VERIFICATION VIA OTP
if not st.session_state.verified_email:
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
                st.success("Email verified successfully!")
                st.rerun()
            else:
                st.error("Invalid Code! Please check your email and try again.")
        
        if st.button("Resend Code / Change Email"):
            st.session_state.otp_sent = False
            st.rerun()

# STAGE 3: LOGGED IN PORTAL
else:
    active_email = st.session_state.verified_email
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"Logged in: **{active_email}**")
    with col2:
        if st.button("Logout"):
            st.session_state.verified_email = None
            st.rerun()

    st.markdown("---")

    # =========================================================
    # 👑 1. SUPER ADMIN VIEW (YOU)
    # =========================================================
    if active_email == SUPER_ADMIN_EMAIL:
        st.success("👑 Logged in as Main Platform Super Admin")
        st.header("Master Company & Host Directory")

        companies_res = supabase.table("companies").select("*").execute()
        companies = companies_res.data or []

        if companies:
            master_data = []
            for comp in companies:
                c_name = comp.get("company_name")
                # Count total employees registered under this company
                emp_count_res = supabase.table("employees").select("id", count="exact").eq("business_name", c_name).execute()
                emp_count = emp_count_res.count if emp_count_res.count is not None else len(emp_count_res.data or [])

                master_data.append({
                    "Company / Shop Name": c_name,
                    "Host Name": comp.get("host_name"),
                    "Host Email": comp.get("host_email"),
                    "Host Phone": comp.get("host_phone"),
                    "Total Employees": emp_count
                })

            st.metric("Total Companies Onboarded", len(master_data))
            st.dataframe(master_data)
        else:
            st.info("No hosts or companies registered yet.")

    # =========================================================
    # 🏢 2. HOST & EMPLOYEE SELECTION
    # =========================================================
    else:
        role = st.radio("Select Login Mode", ["Host / Company Owner", "Employee View"], horizontal=True)

        # -----------------------------------------------------
        # HOST / COMPANY OWNER PORTAL
        # -----------------------------------------------------
        if role == "Host / Company Owner":
            st.header("🏢 Host Management Portal")

            # Check if this email is already a registered host
            host_check = supabase.table("companies").select("*").eq("host_email", active_email).execute()
            
            if host_check.data:
                company_info = host_check.data[0]
                comp_name = company_info.get("company_name")
                st.success(f"Welcome back Host: **{company_info.get('host_name')}** ({comp_name})")
                
                st.subheader(f"Employee Dashboard for {comp_name}")
                
                search_query = st.text_input("Search staff by Name or Employee No")
                emp_res = supabase.table("employees").select("*").eq("business_name", comp_name).execute()
                emp_data = emp_res.data or []

                if emp_data:
                    if search_query:
                        filtered = [
                            e for e in emp_data 
                            if search_query.lower() in str(e.get("name", "")).lower() 
                            or search_query.lower() in str(e.get("employee_no", "")).lower()
                        ]
                        st.metric("Search Results", len(filtered))
                        st.dataframe(filtered)
                    else:
                        st.metric("Total Staff Registered", len(emp_data))
                        st.dataframe(emp_data)
                else:
                    st.info(f"No employee records registered under '{comp_name}' yet.")

            else:
                st.warning("First-time setup: Register your company to become a Host!")
                with st.form("host_registration_form"):
                    st.subheader("Register Your Company / Shop")
                    new_comp_name = st.text_input("Company / Shop Name *").strip()
                    h_name = st.text_input("Host Full Name *")
                    h_phone = st.text_input("Host Phone Number")

                    submit_host = st.form_submit_button("Create Company & Become Host")

                    if submit_host:
                        if not new_comp_name or not h_name:
                            st.error("Company Name and Host Full Name are required!")
                        else:
                            try:
                                supabase.table("companies").insert({
                                    "company_name": new_comp_name,
                                    "host_name": h_name,
                                    "host_email": active_email,
                                    "host_phone": h_phone
                                }).execute()
                                st.success(f"Company '{new_comp_name}' registered successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error registering company. The company name might already exist: {e}")

        # -----------------------------------------------------
        # EMPLOYEE PORTAL
        # -----------------------------------------------------
        else:
            st.header("👤 Employee Profile View")
            records = supabase.table("employees").select("*").eq("email", active_email).execute().data

            if records:
                emp = records[0]
                st.success(f"Welcome back, {emp.get('name')}!")
                
                with st.form("edit_employee_form"):
                    st.subheader("Edit Your Details")
                    st.text_input("Company Name", value=str(emp.get("business_name") or ""), disabled=True)
                    st.text_input("Employee Number", value=str(emp.get("employee_no") or ""), disabled=True)
                    name = st.text_input("Full Name *", value=str(emp.get("name") or ""))
                    dept = st.text_input("Department", value=str(emp.get("department") or ""))
                    pos = st.text_input("Position", value=str(emp.get("position") or ""))
                    phone = st.text_input("Phone Number", value=str(emp.get("phone") or ""))
                    salary = st.text_input("Salary", value=str(emp.get("salary") or ""))

                    submit_update = st.form_submit_button("Update My Details")
                    
                    if submit_update:
                        if not name.strip():
                            st.error("Full Name cannot be empty!")
                        else:
                            try:
                                supabase.table("employees").update({
                                    "name": name,
                                    "department": dept,
                                    "position": pos,
                                    "phone": phone,
                                    "salary": salary
                                }).eq("email", active_email).execute()
                                st.success("Your details were updated successfully!")
                            except Exception as e:
                                st.error(f"Failed to update details: {e}")
            else:
                st.warning("No profile found for this email. Join your company below:")
                
                # Fetch available companies for helpful dropdown/validation
                all_comps = [c.get("company_name") for c in (supabase.table("companies").select("company_name").execute().data or [])]
                
                assigned_id = generate_unique_emp_id()
                
                with st.form("new_employee_form"):
                    st.subheader("Add New Employee Profile")
                    
                    if all_comps:
                        biz_input = st.selectbox("Select Your Company / Shop *", options=all_comps)
                    else:
                        biz_input = st.text_input("Company / Shop Name *")
                        
                    emp_no = st.text_input("Assigned Employee Number", value=assigned_id, disabled=True)
                    name = st.text_input("Full Name *")
                    dept = st.text_input("Department")
                    pos = st.text_input("Position")
                    phone = st.text_input("Phone Number")
                    salary = st.text_input("Salary")

                    submit_new = st.form_submit_button("Save Profile")

                    if submit_new:
                        if not name.strip() or not biz_input:
                            st.error("Company Name and Full Name are required!")
                        else:
                            try:
                                supabase.table("employees").insert({
                                    "business_name": biz_input,
                                    "employee_no": assigned_id,
                                    "name": name,
                                    "department": dept,
                                    "position": pos,
                                    "phone": phone,
                                    "email": active_email,
                                    "salary": salary
                                }).execute()
                                st.success(f"Profile saved under '{biz_input}'! Employee No: #{assigned_id}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error saving profile: {e}")
