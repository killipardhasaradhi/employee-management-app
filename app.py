import streamlit as st
import random
import smtplib
from datetime import date, datetime, timedelta
from email.mime.text import MIMEText
from supabase import create_client

# ---------------------------------------------------------
# PAGE CONFIGURATION & CUSTOM CSS
# ---------------------------------------------------------
st.set_page_config(page_title="PS DIGITAL - Multi-Host ERP", page_icon="📱", layout="centered")

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

    /* Vibrant & Beautiful Company Name Header */
    .company-header {
        background: linear-gradient(135deg, #FF512F 0%, #DD2476 100%);
        color: #FFFFFF;
        padding: 16px 24px;
        border-radius: 12px;
        text-align: center;
        font-family: 'Trebuchet MS', sans-serif;
        font-size: 26px;
        font-weight: 800;
        letter-spacing: 1px;
        box-shadow: 0px 4px 15px rgba(221, 36, 118, 0.35);
        margin-top: 10px;
        margin-bottom: 20px;
        text-transform: uppercase;
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

# 👑 YOUR EMAIL (Platform Owner)
SUPER_ADMIN_EMAIL = "pardhukilli273@gmail.com"

# Gmail SMTP Settings for OTP
SENDER_EMAIL = "pardhukilli273@gmail.com"
SENDER_PASSWORD = "fneh pjig gqum vtmv"    # 16-character Gmail App Password

# Initialize session states
if "otp_sent" not in st.session_state:
    st.session_state.otp_sent = False
if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = None
if "verified_email" not in st.session_state:
    st.session_state.verified_email = None
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()
if "show_host_reg" not in st.session_state:
    st.session_state.show_host_reg = False

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
# STAGE 1 & 2: LOGIN VIA OTP (SHOWS PS DIGITAL HEADER)
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
                st.success("Email verified successfully!")
                st.rerun()
            else:
                st.error("Invalid Code! Please check your email and try again.")
        
        if st.button("Resend Code / Change Email"):
            st.session_state.otp_sent = False
            st.rerun()

# ---------------------------------------------------------
# STAGE 3: LOGGED IN PORTAL (AUTOMATIC ROUTING)
# ---------------------------------------------------------
else:
    active_email = st.session_state.verified_email
    
    # Check if active email is registered as a Host or Employee
    host_check = supabase.table("companies").select("*").eq("host_email", active_email).execute().data
    emp_records = supabase.table("employees").select("*").eq("email", active_email).execute().data

    # --- 1. SUPER ADMIN VIEW ---
    if active_email == SUPER_ADMIN_EMAIL:
        st.title("📱 PS DIGITAL")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Logged in: **{active_email}**")
        with col2:
            if st.button("Logout"):
                st.session_state.verified_email = None
                st.rerun()

        st.markdown("---")
        st.success("👑 Main Platform Super Admin Dashboard")
        companies_res = supabase.table("companies").select("*").execute()
        companies = companies_res.data or []

        if companies:
            master_data = []
            for comp in companies:
                c_name = comp.get("company_name")
                emp_count_res = supabase.table("employees").select("id", count="exact").eq("company_name", c_name).execute()
                emp_count = emp_count_res.count if emp_count_res.count is not None else len(emp_count_res.data or [])

                master_data.append({
                    "Company Name": c_name,
                    "Host Name": comp.get("host_name"),
                    "Host Email": comp.get("host_email"),
                    "Host Phone": comp.get("host_phone"),
                    "Total Staff Count": emp_count
                })

            st.metric("Total Companies Registered", len(master_data))
            st.dataframe(master_data)
        else:
            st.info("No companies registered yet.")

    # --- 2. HOST DASHBOARD ---
    elif host_check:
        company_info = host_check[0]
        comp_name = company_info.get("company_name")

        # HEADER IS ONLY COMPANY NAME
        st.markdown(f'<div class="company-header">🏢 {comp_name}</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Logged in as Host: **{company_info.get('host_name')}** ({active_email})")
        with col2:
            if st.button("Logout"):
                st.session_state.verified_email = None
                st.rerun()

        st.markdown("---")

        host_menu = st.selectbox("Select Action", [
            "📊 Today's Attendance Summary",
            "👥 Employee Directory",
            "📢 Publish Company Notice",
            "📅 Declare Holiday"
        ])

        # MENU 1: TODAY'S ATTENDANCE SUMMARY
        if host_menu == "📊 Today's Attendance Summary":
            st.subheader("Attendance Dashboard")
            selected_date = st.date_input("Select Date", value=date.today())
            
            all_emps = supabase.table("employees").select("*").eq("company_name", comp_name).execute().data or []
            total_count = len(all_emps)
            
            att_res = supabase.table("attendance").select("*").eq("company_name", comp_name).eq("attendance_date", str(selected_date)).execute().data or []
            present_emails = {a.get("employee_email") for a in att_res}
            present_count = len(present_emails)
            absent_count = total_count - present_count

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Staff", total_count)
            c2.metric("Present Today", present_count)
            c3.metric("Absent Today", absent_count)

            st.markdown("---")
            col_p, col_a = st.columns(2)
            
            with col_p:
                st.subheader("✅ Present List")
                present_list = [e for e in all_emps if e.get("email") in present_emails]
                if present_list:
                    for p in present_list:
                        st.write(f"• **{p.get('name')}** (#{p.get('employee_no')})")
                else:
                    st.caption("No attendance recorded for this date.")

            with col_a:
                st.subheader("❌ Absent List")
                absent_list = [e for e in all_emps if e.get("email") not in present_emails]
                if absent_list:
                    for a in absent_list:
                        st.write(f"• **{a.get('name')}** (#{a.get('employee_no')})")
                else:
                    st.caption("All staff members present!")

        # MENU 2: EMPLOYEE DIRECTORY
        elif host_menu == "👥 Employee Directory":
            st.subheader("Employee Details")
            search_query = st.text_input("Search staff by Name or Employee No")
            all_emps = supabase.table("employees").select("*").eq("company_name", comp_name).execute().data or []

            if search_query:
                filtered = [
                    e for e in all_emps 
                    if search_query.lower() in str(e.get("name", "")).lower() 
                    or search_query.lower() in str(e.get("employee_no", "")).lower()
                ]
                st.dataframe(filtered)
            else:
                st.dataframe(all_emps)

        # MENU 3: PUBLISH NOTICE
        elif host_menu == "📢 Publish Company Notice":
            st.subheader("Post Notice for Employees")
            notice_msg = st.text_area("Write Notice Message")
            if st.button("Publish Notice"):
                if notice_msg.strip():
                    supabase.table("company_notices").insert({
                        "company_name": comp_name,
                        "notice_text": notice_msg.strip()
                    }).execute()
                    st.success("Notice published to employee portal!")
                else:
                    st.error("Notice text cannot be empty.")

        # MENU 4: DECLARE HOLIDAY
        elif host_menu == "📅 Declare Holiday":
            st.subheader("Add Official Holiday")
            h_date = st.date_input("Select Holiday Date")
            h_title = st.text_input("Holiday Occasion / Title")
            if st.button("Save Holiday"):
                if h_title.strip():
                    supabase.table("company_notices").insert({
                        "company_name": comp_name,
                        "holiday_date": str(h_date),
                        "holiday_title": h_title.strip()
                    }).execute()
                    st.success(f"Holiday '{h_title}' set for {h_date}!")
                else:
                    st.error("Please enter a title for the holiday.")

    # --- 3. EXISTING EMPLOYEE DASHBOARD ---
    elif emp_records:
        emp = emp_records[0]
        comp_name = emp.get("company_name")
        emp_name = emp.get("name")
        
        # HEADER IS ONLY COMPANY NAME
        st.markdown(f'<div class="company-header">🏢 {comp_name}</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Logged in as Employee: **{emp_name}** ({active_email})")
        with col2:
            if st.button("Logout"):
                st.session_state.verified_email = None
                st.rerun()

        st.markdown("---")

        # --- 📢 NOTICE BOARD DISPLAY ---
        notices = supabase.table("company_notices").select("*").eq("company_name", comp_name).order("created_at", desc=True).execute().data or []
        active_notices = [n for n in notices if n.get("notice_text")]
        if active_notices:
            st.info(f"📢 **Latest Company Notice:**\n\n{active_notices[0].get('notice_text')}")

        # --- 📅 CALENDAR & ATTENDANCE SECTION ---
        st.subheader("📅 Attendance Calendar")

        col_prev, col_curr, col_next = st.columns([1, 2, 1])
        with col_prev:
            if st.button("⬅️ Previous Day"):
                st.session_state.selected_date -= timedelta(days=1)
                st.rerun()
        with col_curr:
            view_date = st.date_input("Current Date Focus", value=st.session_state.selected_date)
            st.session_state.selected_date = view_date
        with col_next:
            if st.button("Next Day ➡️"):
                st.session_state.selected_date += timedelta(days=1)
                st.rerun()

        cur_date_str = str(st.session_state.selected_date)
        today_str = str(date.today())

        holidays = [n for n in notices if n.get("holiday_date") == cur_date_str]
        if holidays:
            st.warning(f"🎉 **Holiday Notice:** {holidays[0].get('holiday_title')}")

        check_att = supabase.table("attendance").select("*").eq("company_name", comp_name).eq("employee_email", active_email).eq("attendance_date", cur_date_str).execute().data

        if check_att:
            st.success(f"✅ Marked Present for {cur_date_str}")
        else:
            if cur_date_str == today_str:
                if st.button("✋ Mark I Came Today (Present)", type="primary"):
                    try:
                        supabase.table("attendance").insert({
                            "company_name": comp_name,
                            "employee_email": active_email,
                            "employee_name": emp_name,
                            "attendance_date": cur_date_str,
                            "status": "Present"
                        }).execute()
                        st.success("Attendance marked successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error marking attendance: {e}")
            else:
                st.info(f"Attendance status for {cur_date_str}: Not Marked / Absent")

        # --- ⚙️ EDIT PROFILE FORM ---
        with st.expander("Edit My Profile Details"):
            with st.form("edit_emp_details"):
                st.text_input("Company Name", value=str(comp_name), disabled=True)
                st.text_input("Employee Number", value=str(emp.get("employee_no") or ""), disabled=True)
                updated_name = st.text_input("Full Name *", value=str(emp_name))
                dept = st.text_input("Department", value=str(emp.get("department") or ""))
                pos = st.text_input("Position", value=str(emp.get("position") or ""))
                phone = st.text_input("Phone Number", value=str(emp.get("phone") or ""))
                salary = st.text_input("Salary", value=str(emp.get("salary") or ""))

                if st.form_submit_button("Update Details"):
                    supabase.table("employees").update({
                        "name": updated_name,
                        "department": dept,
                        "position": pos,
                        "phone": phone,
                        "salary": salary
                    }).eq("email", active_email).execute()
                    st.success("Details updated!")
                    st.rerun()

    # --- 4. NEW USER ONBOARDING (EMPLOYEE OR HOST SELECTION) ---
    else:
        st.title("📱 PS DIGITAL")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Logged in: **{active_email}**")
        with col2:
            if st.button("Logout"):
                st.session_state.verified_email = None
                st.rerun()

        st.markdown("---")

        all_comps = [c.get("company_name") for c in (supabase.table("companies").select("company_name").execute().data or [])]

        if st.session_state.show_host_reg:
            st.subheader("🏢 Register Your Company as a Host / Owner")
            with st.form("host_registration_form"):
                new_comp_name = st.text_input("Company / Shop Name *").strip()
                h_name = st.text_input("Host Full Name *")
                h_phone = st.text_input("Host Phone Number")

                submit_host = st.form_submit_button("Create Company & Become Host")

                if submit_host:
                    if not new_comp_name or not h_name:
                        st.error("Company Name and Host Name are required!")
                    else:
                        try:
                            supabase.table("companies").insert({
                                "company_name": new_comp_name,
                                "host_name": h_name,
                                "host_email": active_email,
                                "host_phone": h_phone
                            }).execute()
                            st.success(f"Company '{new_comp_name}' registered successfully!")
                            st.session_state.show_host_reg = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error registering company: {e}")

            if st.button("⬅️ Back to Employee Joining Form"):
                st.session_state.show_host_reg = False
                st.rerun()

        else:
            st.warning("No employee profile found for this email. Join your company below:")
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
                                "company_name": biz_input,
                                "employee_no": assigned_id,
                            
