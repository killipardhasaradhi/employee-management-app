import streamlit as st
import random
import smtplib
import pandas as pd
from datetime import date
from email.mime.text import MIMEText
from supabase import create_client
from streamlit_geolocation import streamlit_geolocation
from geopy.distance import geodesic

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

for key in ["otp_sent", "generated_otp", "verified_email", "show_host_reg", "show_attendance_list"]:
    if key not in st.session_state: st.session_state[key] = False

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

# ---------------------------------------------------------
# STAGE 2: MAIN PORTAL (AUTOMATIC ROUTING)
# ---------------------------------------------------------
else:
    active_email = st.session_state.verified_email
    
    try:
        host_check = supabase.table("companies").select("*").eq("host_email", active_email).execute().data
    except Exception:
        host_check = []

    try:
        emp_records = supabase.table("employees").select("*").eq("email", active_email).execute().data
    except Exception:
        emp_records = []

    # --- 1. SUPER ADMIN VIEW ---
    if active_email == SUPER_ADMIN_EMAIL:
        st.title("📱 PS DIGITAL")
        if st.button("Logout"):
            st.session_state.verified_email = None
            st.rerun()
        st.markdown("---")
        st.success("👑 Super Admin Dashboard")
        
        companies = supabase.table("companies").select("*").execute().data or []
        employees = supabase.table("employees").select("company_name").execute().data or []
        
        emp_counts = {}
        for emp in employees:
            c_name = emp.get("company_name")
            if c_name:
                emp_counts[c_name] = emp_counts.get(c_name, 0) + 1
        
        for comp in companies:
            comp["employee_count"] = emp_counts.get(comp.get("company_name"), 0)
            
        st.metric("Total Companies Registered", len(companies))
        st.dataframe(companies)

        st.markdown("---")
        st.subheader("🗑️ Remove / Delete Company")
        company_names = [c.get("company_name") for c in companies if c.get("company_name")]
        
        if company_names:
            comp_to_remove = st.selectbox("Select Company to Remove", options=company_names)
            if st.button("❌ Remove Company", type="primary"):
                try:
                    # Remove company record
                    supabase.table("companies").delete().eq("company_name", comp_to_remove).execute()
                    # Clean up associated employees, attendance, and notices
                    try: supabase.table("employees").delete().eq("company_name", comp_to_remove).execute()
                    except Exception: pass
                    try: supabase.table("attendance").delete().eq("company_name", comp_to_remove).execute()
                    except Exception: pass
                    try: supabase.table("company_notices").delete().eq("company_name", comp_to_remove).execute()
                    except Exception: pass
                    
                    st.success(f"Company '{comp_to_remove}' and associated data removed successfully!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Failed to remove company: {err}")
        else:
            st.info("No companies currently registered.")

    # --- 2. HOST DASHBOARD ---
    elif host_check:
        comp = host_check[0]
        c_name = comp.get("company_name", "Company Portal")
        st.markdown(f'<div class="company-header">🏢 {c_name}</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        col1.write(f"Logged in as Host: **{comp.get('host_name')}**")
        if col2.button("Logout"):
            st.session_state.verified_email = None
            st.rerun()
        st.markdown("---")

        menu = st.selectbox("Select Action", [
            "📊 Attendance Summary", 
            "📍 Fix Shop Location", 
            "👥 Employee Directory", 
            "📢 Post Notice", 
            "📅 Declare Holiday"
        ])

        if menu == "📊 Attendance Summary":
            sel_date = st.date_input("Select Date", value=date.today())
            
            try:
                emps = supabase.table("employees").select("*").eq("company_name", c_name).execute().data or []
            except Exception:
                emps = supabase.table("employees").select("*").execute().data or []
                
            try:
                att = supabase.table("attendance").select("*").eq("company_name", c_name).eq("attendance_date", str(sel_date)).execute().data or []
            except Exception:
                att = supabase.table("attendance").select("*").eq("attendance_date", str(sel_date)).execute().data or []
                
            present_emails = {a.get("employee_email") for a in att}
            present_list = [e for e in emps if e.get("email") in present_emails]
            absent_list = [e for e in emps if e.get("email") not in present_emails]
            
            st.subheader(f"Attendance Stats for {sel_date}")
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Total Employees", len(emps))
            m_col2.metric("✅ Total Present", len(present_list))
            m_col3.metric("❌ Total Absent", len(absent_list))
            
            if att:
                df = pd.DataFrame(att)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Export Attendance Report to CSV", csv, f"Attendance_{c_name}_{sel_date}.csv", "text/csv")

            st.markdown("---")
            if st.button("👁️ Show / Hide Detailed Present & Absent List"):
                st.session_state.show_attendance_list = not st.session_state.show_attendance_list
            
            if st.session_state.show_attendance_list:
                st.subheader("✅ Present Staff List")
                if present_list:
                    for e in present_list: st.write(f"• **{e.get('name')}** ({e.get('email')})")
                else: st.info("No present records found for this date.")

                st.subheader("❌ Absent Staff List")
                if absent_list:
                    for e in absent_list: st.write(f"• **{e.get('name')}** ({e.get('email')})")
                else: st.info("No absent staff for this date.")

        elif menu == "📍 Fix Shop Location":
            st.subheader("📍 Configure Official Shop / Office GPS Location")
            current_lat = comp.get("latitude")
            current_lng = comp.get("longitude")

            if current_lat and current_lng:
                st.success(f"Current Saved Location: Lat {current_lat}, Long {current_lng}")
            else:
                st.warning("No location set yet! Employees can mark attendance from anywhere until you fix your shop location.")

            st.write("Click below while physically inside your shop to capture and lock the location:")
            host_loc = streamlit_geolocation()
            
            if host_loc and host_loc.get("latitude"):
                st.info(f"Captured Location: Latitude `{host_loc['latitude']}`, Longitude `{host_loc['longitude']}`")
                if st.button("🔒 Save This Location as Shop GPS"):
                    supabase.table("companies").update({
                        "latitude": host_loc["latitude"],
                        "longitude": host_loc["longitude"]
                    }).eq("company_name", c_name).execute()
                    st.success("Shop location fixed successfully!")
                    st.rerun()

        elif menu == "👥 Employee Directory":
            try:
                st.dataframe(supabase.table("employees").select("*").eq("company_name", c_name).execute().data or [])
            except Exception:
                st.dataframe(supabase.table("employees").select("*").execute().data or [])

        elif menu == "📢 Post Notice":
            msg = st.text_area("Write Notice Message")
            if st.button("Publish Notice"):
                supabase.table("company_notices").insert({"company_name": c_name, "notice_text": msg.strip()}).execute()
                st.success("Notice published!")

        elif menu == "📅 Declare Holiday":
            h_date = st.date_input("Holiday Date")
            h_title = st.text_input("Holiday Title / Reason")
            if st.button("Save Holiday"):
                supabase.table("company_notices").insert({"company_name": c_name, "holiday_date": str(h_date), "holiday_title": h_title.strip()}).execute()
                st.success("Holiday declared!")

    # --- 3. EMPLOYEE DASHBOARD ---
    elif emp_records:
        emp = emp_records[0]
        c_name = emp.get("company_name", "Company Portal")
        st.markdown(f'<div class="company-header">🏢 {c_name}</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        col1.write(f"Logged in as Employee: **{emp.get('name')}**")
        if col2.button("Logout"):
            st.session_state.verified_email = None
            st.rerun()
        st.markdown("---")

        comp_info = supabase.table("companies").select("*").eq("company_name", c_name).execute().data
        shop_lat = comp_info[0].get("latitude") if comp_info else None
        shop_lng = comp_info[0].get("longitude") if comp_info else None

        st.subheader("📅 Daily Attendance")
        cur_date_str = str(date.today())
        
        check_att = supabase.table("attendance").select("*").eq("company_name", c_name).eq("employee_email", active_email).eq("attendance_date", cur_date_str).execute().data

        if check_att:
            st.success(f"✅ Marked Present for Today ({cur_date_str})")
        else:
            st.info("📍 Fetching your current location... Please enable browser location permissions.")
            emp_loc = streamlit_geolocation()

            if emp_loc and emp_loc.get("latitude"):
                user_coords = (emp_loc["latitude"], emp_loc["longitude"])
                
                if shop_lat and shop_lng:
                    shop_coords = (shop_lat, shop_lng)
                    distance_meters = geodesic(user_coords, shop_coords).meters
                    
                    st.write(f"Distance from shop: **{round(distance_meters, 1)} meters**")

                    if distance_meters <= 100:
                        if st.button("✋ Mark Present", type="primary"):
                            supabase.table("attendance").insert({
                                "company_name": c_name,
                                "employee_email": active_email,
                                "employee_name": emp.get("name"),
                                "attendance_date": cur_date_str,
                                "status": "Present",
                                "latitude": emp_loc["latitude"],
                                "longitude": emp_loc["longitude"]
                            }).execute()
                            st.success("Attendance marked successfully!")
                            st.rerun()
                    else:
                        st.error("❌ You are too far from the shop location to mark attendance. You must be within 100 meters.")
                else:
                    if st.button("✋ Mark Present", type="primary"):
                        supabase.table("attendance").insert({
                            "company_name": c_name,
                            "employee_email": active_email,
                            "employee_name": emp.get("name"),
                            "attendance_date": cur_date_str,
                            "status": "Present",
                            "latitude": emp_loc["latitude"],
                            "longitude": emp_loc["longitude"]
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
            if st.button("⬅️ Back"):
                st.session_state.show_host_reg = False
                st.rerun()

        else:
            st.warning("No employee profile found. Please register below:")
            
            if st.button("👔 Are you the Host / Owner of a company? Click here to Register Company"):
                st.session_state.show_host_reg = True
                st.rerun()

            st.markdown("---")
            assigned_id = generate_unique_emp_id()
            
            with st.form("emp_form"):
                st.subheader("Add Employee Profile")
                biz_input = st.text_input("Enter Your Company Name *").strip()
                st.text_input("Assigned Employee Number", value=assigned_id, disabled=True)
                name = st.text_input("Full Name *")
                dept = st.text_input("Department")
                pos = st.text_input("Position")
                phone = st.text_input("Phone Number")

                if st.form_submit_button("Save Profile"):
                    if name.strip() and biz_input:
                        supabase.table("employees").insert({
                            "employee_no": assigned_id,
                            "company_name": biz_input,
                            "name": name.strip(), 
                            "department": dept.strip(), 
                            "position": pos.strip(),
                            "phone": phone.strip(), 
                            "email": active_email
                        }).execute()
                        st.success("Profile saved successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill in required fields marked with *.")
