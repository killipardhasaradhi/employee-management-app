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
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="PS DIGITAL", layout="centered")

# ---------------------------------------------------------
# HIGH-END MODERN DARK THEME & FIXED BOTTOM NAVIGATION CSS
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* 1. Reset Body & Core Canvas */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #09090B !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        color: #FAFAFA !important;
    }

    /* Hide standard headers, footers, and sidebars */
    header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] {
        visibility: hidden !important;
        height: 0px !important;
        display: none !important;
    }

    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 110px !important; /* Clears fixed bottom bar */
        max-width: 550px !important;
    }

    /* 2. Top App Branding Header */
    .app-brand-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 16px;
        border-bottom: 1px solid #27272A;
        margin-bottom: 20px;
    }
    .app-title {
        font-size: 24px;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #FFFFFF !important;
    }
    .app-subtitle {
        color: #A1A1AA !important;
        font-size: 13px;
        font-weight: 500;
    }

    /* 3. Cards & Containers */
    .hero-card {
        background: #18181B !important;
        border: 1px solid #27272A !important;
        border-radius: 16px !important;
        padding: 20px !important;
        margin-bottom: 16px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
    }
    .hero-card h3 {
        color: #FFFFFF !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        margin-bottom: 6px !important;
    }
    .hero-card p, .hero-card span, .hero-card b {
        color: #A1A1AA !important;
        font-size: 14px !important;
    }

    .location-box {
        background-color: #0F172A !important;
        border: 1px dashed #3B82F6 !important;
        border-radius: 14px !important;
        padding: 18px !important;
        text-align: center !important;
        margin-top: 12px !important;
        margin-bottom: 16px !important;
    }
    .location-box h4 {
        color: #60A5FA !important;
        font-weight: 700 !important;
        margin-bottom: 4px !important;
    }
    .location-box p {
        color: #93C5FD !important;
        font-size: 13px !important;
    }

    /* 4. Streamlit Metric Overrides */
    [data-testid="stMetricValue"] div {
        color: #FFFFFF !important;
        font-size: 30px !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricLabel"] p {
        color: #A1A1AA !important;
        font-size: 12px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        font-weight: 700 !important;
    }

    /* 5. Modern Form Inputs */
    div[data-baseweb="input"] {
        background-color: #18181B !important;
        border: 1px solid #27272A !important;
        border-radius: 12px !important;
    }
    input {
        color: #FFFFFF !important;
        font-size: 15px !important;
    }
    label p, label span {
        color: #A1A1AA !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }

    /* 6. Buttons */
    button[kind="primary"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        border: none !important;
        height: 48px !important;
    }
    button[kind="secondary"] {
        background-color: #18181B !important;
        color: #FFFFFF !important;
        border: 1px solid #27272A !important;
        border-radius: 12px !important;
        height: 48px !important;
    }

    /* 7. FIXED BOTTOM NAVIGATION BAR */
    div[data-testid="stRadio"] {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        width: 100vw !important;
        background-color: #09090B !important;
        border-top: 1px solid #27272A !important;
        padding: 10px 0px 18px 0px !important;
        z-index: 999999 !important;
        margin: 0 !important;
    }
    div[data-testid="stRadio"] > div {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-around !important;
        align-items: center !important;
        max-width: 500px !important;
        margin: 0 auto !important;
    }
    div[data-testid="stRadio"] label > div:first-child {
        display: none !important; /* Hide radio circle */
    }
    div[data-testid="stRadio"] label {
        background-color: transparent !important;
        color: #71717A !important;
        font-size: 11px !important;
        font-weight: 800 !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
        padding: 6px 12px !important;
        cursor: pointer !important;
        border-bottom: 2px solid transparent !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stRadio"] label:has(input:checked) {
        color: #FFFFFF !important;
        border-bottom: 2px solid #FFFFFF !important;
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

SESSION_KEYS = ["otp_sent", "generated_otp", "verified_email", "show_host_reg", "show_attendance_list", "emp_coords"]
for k in SESSION_KEYS:
    if k not in st.session_state:
        st.session_state[k] = False
def send_otp_email(target_email, otp_code):
       try;
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
    st.markdown("""
        <div class="app-brand-header">
            <div>
                <div class="app-title">LockIn PS</div>
                <div class="app-subtitle">ENTERPRISE ATTENDANCE PORTAL</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.write("### Sign In to Account")
    user_email = st.text_input("Enter Email Address", placeholder="name@company.com").strip().lower()

    if user_email and not st.session_state.otp_sent:
        if st.button("Send Access Code", use_container_width=True, type="primary"):
            otp = str(random.randint(100000, 999999))
            if send_otp_email(user_email, otp):
                st.session_state.generated_otp = otp
                st.session_state.otp_sent = True
                st.session_state.temp_email = user_email
                st.success(f"Verification code sent to {user_email}")
                st.rerun()

    if st.session_state.otp_sent:
        st.info(f"Enter the 6-digit verification code sent to {st.session_state.temp_email}")
        input_otp = st.text_input("Verification Code", max_chars=6, placeholder="123456")

        if st.button("Verify & Continue", use_container_width=True, type="primary"):
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

    # =========================================================
    # 1. SUPER ADMIN DASHBOARD
    # =========================================================
    if active_email == SUPER_ADMIN_EMAIL:
        st.markdown("""
            <div class="app-brand-header">
                <div class="app-title">Admin Console</div>
                <div class="app-subtitle">SUPER ADMIN CONTROL</div>
            </div>
        """, unsafe_allow_html=True)

        admin_nav = st.radio("", ["DASHBOARD", "DIRECTORY", "REMOVE COMP"], horizontal=True, label_visibility="collapsed")
        
        companies = supabase.table("companies").select("*").execute().data or []
        employees = supabase.table("employees").select("company_name").execute().data or []

        if admin_nav == "DASHBOARD":
            st.markdown("""<div class="hero-card"><h3>Super Admin Management</h3><p>Control platform hosts, global parameters, and client operations.</p></div>""", unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            col_a.metric("Total Companies", len(companies))
            col_b.metric("Total Users", len(employees))

        elif admin_nav == "DIRECTORY":
            st.subheader("Registered Companies")
            st.dataframe(companies, use_container_width=True)

        elif admin_nav == "REMOVE COMP":
            st.subheader(" Delete Company Profile")
            company_names = [c.get("company_name") for c in companies if c.get("company_name")]
            if company_names:
                comp_to_remove = st.selectbox("Select Company to Remove", options=company_names)
                if st.button("❌ Remove Company", type="primary", use_container_width=True):
                    try:
                        supabase.table("companies").delete().eq("company_name", comp_to_remove).execute()
                        supabase.table("employees").delete().eq("company_name", comp_to_remove).execute()
                        supabase.table("attendance").delete().eq("company_name", comp_to_remove).execute()
                        supabase.table("company_notices").delete().eq("company_name", comp_to_remove).execute()
                        st.success(f"Company '{comp_to_remove}' deleted!")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Error: {err}")
            else:
                st.info("No registered companies found.")

    # =========================================================
    # 2. HOST DASHBOARD
    # =========================================================
    elif host_check:
        comp = host_check[0]
        c_name = comp.get("company_name", "Company Portal")

        st.markdown(f"""
            <div class="app-brand-header">
                <div>
                    <div class="app-title">{c_name}</div>
                    <div class="app-subtitle">HOST WORKSPACE</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Bottom Bar Navigation
        host_nav = st.radio("", ["HOME", "ATTENDANCE", "LOCATION", "STAFF", "NOTICES", "SETTINGS"], horizontal=True, label_visibility="collapsed")

        if host_nav == "HOME":
            st.markdown(f"""
                <div class="hero-card">
                    <h3>Host Dashboard</h3>
                    <p>Welcome back, <b>{comp.get('host_name')}</b></p>
                </div>
            """, unsafe_allow_html=True)
            
            emps = supabase.table("employees").select("*").eq("company_name", c_name).execute().data or []
            today_att = supabase.table("attendance").select("*").eq("company_name", c_name).eq("attendance_date", str(date.today())).execute().data or []
            
            m1, m2 = st.columns(2)
            m1.metric("Total Staff", len(emps))
            m2.metric("Present Today", len(today_att))

        elif host_nav == "ATTENDANCE":
            st.subheader("📊 Daily Attendance Summary")
            sel_date = st.date_input("Select Date", value=date.today())
            
            emps = supabase.table("employees").select("*").eq("company_name", c_name).execute().data or []
            att = supabase.table("attendance").select("*").eq("company_name", c_name).eq("attendance_date", str(sel_date)).execute().data or []
            
            present_emails = {a.get("employee_email") for a in att}
            present_list = [e for e in emps if e.get("email") in present_emails]
            absent_list = [e for e in emps if e.get("email") not in present_emails]
            
            c_x, c_y, c_z = st.columns(3)
            c_x.metric("Staff", len(emps))
            c_y.metric("Present", len(present_list))
            c_z.metric("Absent", len(absent_list))
            
            if att:
                df = pd.DataFrame(att)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download Report (CSV)", csv, f"Attendance_{c_name}_{sel_date}.csv", "text/csv", use_container_width=True)

        elif host_nav == "LOCATION":
            st.subheader(" Office GPS Boundary")
            current_lat, current_lng = comp.get("latitude"), comp.get("longitude")

            if current_lat and current_lng:
                st.success(f"GPS Coordinates Active: `{current_lat}, {current_lng}`")
                st.map(pd.DataFrame({'lat': [current_lat], 'lon': [current_lng]}), zoom=15)
            else:
                st.warning("No GPS Boundary configured.")

            st.markdown("""
                <div class="location-box">
                    <h4> Configure GPS Lock</h4>
                    <p>Trigger scanner below to lock official office coordinates.</p>
                </div>
            """, unsafe_allow_html=True)
            
            host_loc = streamlit_geolocation()
            if host_loc and host_loc.get("latitude"):
                if st.button("🔒 Lock Coordinates", type="primary", use_container_width=True):
                    supabase.table("companies").update({
                        "latitude": host_loc["latitude"],
                        "longitude": host_loc["longitude"]
                    }).eq("company_name", c_name).execute()
                    st.success("Location locked successfully!")
                    st.rerun()

        elif host_nav == "STAFF":
            st.subheader(" Employee Directory & Management")
            emps = supabase.table("employees").select("*").eq("company_name", c_name).execute().data or []
            
            if emps:
                st.dataframe(emps, use_container_width=True)
                st.markdown("---")
                st.write("### ❌ Remove Employee")
                emp_options = {f"{e.get('name')} ({e.get('email')})": e.get("email") for e in emps}
                selected_emp_label = st.selectbox("Select Staff Member", options=list(emp_options.keys()))
                
                if st.button("Remove Selected Employee", type="primary", use_container_width=True):
                    target_email = emp_options[selected_emp_label]
                    supabase.table("employees").delete().eq("company_name", c_name).eq("email", target_email).execute()
                    st.success(f"Removed employee successfully!")
                    st.rerun()
            else:
                st.info("No employees registered under this company.")

        elif host_nav == "NOTICES":
            st.subheader("📢 Post Announcement")
            msg = st.text_area("Notice Details")
            if st.button("Publish Announcement", type="primary", use_container_width=True):
                if msg.strip():
                    supabase.table("company_notices").insert({"company_name": c_name, "notice_text": msg.strip()}).execute()
                    st.success("Notice published!")

        elif host_nav == "SETTINGS":
            st.subheader("⚙️ Host Account Settings")
            st.write("### 👤 Edit Host Profile")
            with st.form("host_edit_profile"):
                h_name_edit = st.text_input("Host Name", value=comp.get("host_name", ""))
                h_phone_edit = st.text_input("Phone Number", value=comp.get("host_phone", ""))
                if st.form_submit_button("Save Changes", use_container_width=True):
                    supabase.table("companies").update({
                        "host_name": h_name_edit.strip(),
                        "host_phone": h_phone_edit.strip()
                    }).eq("host_email", active_email).execute()
                    st.success("Profile updated!")
                    st.rerun()

            st.markdown("---")
            col_so, col_del = st.columns(2)
            with col_so:
                if st.button("🚪 Sign Out", use_container_width=True):
                    st.session_state.verified_email = None
                    st.rerun()
            with col_del:
                confirm_host_del = st.checkbox("Confirm deletion")
                if st.button("❌ Delete Profile", type="primary", use_container_width=True, disabled=not confirm_host_del):
                    supabase.table("companies").delete().eq("host_email", active_email).execute()
                    st.session_state.verified_email = None
                    st.rerun()

    # =========================================================
    # 3. EMPLOYEE DASHBOARD
    # =========================================================
    elif emp_records:
        emp = emp_records[0]
        c_name = emp.get("company_name", "Company Portal")

        st.markdown(f"""
            <div class="app-brand-header">
                <div>
                    <div class="app-title">{c_name}</div>
                    <div class="app-subtitle">MEMBER PORTAL</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Bottom Bar Navigation
        emp_nav = st.radio("", ["ATTEND", "GEOFENCE", "NOTICES", "PROFILE"], horizontal=True, label_visibility="collapsed")

        try:
            notices = supabase.table("company_notices").select("*").eq("company_name", c_name).order("created_at", desc=True).execute().data or []
        except Exception:
            notices = []

        comp_info = supabase.table("companies").select("*").eq("company_name", c_name).execute().data
        comp_lat = comp_info[0].get("latitude") if comp_info else None
        comp_lng = comp_info[0].get("longitude") if comp_info else None
        cur_date_str = str(date.today())

      if emp_nav == "ATTEND":
           st.markdown(f"""
                <div class="hero-card">
                    <h3>Welcome back, {emp.get("name")}!</h3>
                    <p>Dept: <b>{emp.get("department", "General")}</b> | ID: <b>{emp.get("employee_no")}</b></p>
                </div>
            """, unsafe_allow_html=True)

            check_att = supabase.table("attendance").select("*").eq("company_name", c_name).eq("employee_email", active_email).eq("attendance_date", cur_date_str).execute().data

            if check_att:
                st.success(f"✅ Marked Present for Today ({cur_date_str})")
                else:st.markdown("""
                    <div class="location-box">
                        <h4>GPS Verification Terminal</h4>
                        <p>Verify position within 100 meters of office premises.</p>
                    </div>
                """, unsafe_allow_html=True)
                
                loc_data =streamlit_geolocation()
                if loc_data and loc_data.get("latitude"):
                    st.session_state.emp_coords = (loc_data["latitude"], loc_data["longitude"])

                if st.session_state.emp_coords:
                    user_lat, user_lng = st.session_state.emp_coords
                    st.success(f"Captured: `{round(user_lat, 4)}, {round(user_lng, 4)}`")
  if comp_lat and comp_lng:
                        dist = geodesic((user_lat, user_lng), (comp_lat, comp_lng)).meters
                        st.write(f"Distance to Office: **{round(dist, 1)} meters**")

                        if dist <= 100:
                            if st.button("✋ Submit Attendance", type="primary", use_container_width=True):
                                supabase.table("attendance").insert({
                                    "company_name": c_name, "employee_email": active_email,
                                    "employee_name": emp.get("name"), "attendance_date": cur_date_str,
                                    "status": "Present", "latitude": user_lat, "longitude": user_lng
                                }).execute()
                                st.session_state.emp_coords = False
                                st.success("Attendance marked!")
                                st.rerun()
                        else:
                            st.error("❌ Too far from office premises (Must be within 100m).")
                    else:
                        if st.button("✋ Submit Attendance", type="primary", use_container_width=True):
                            supabase.table("attendance").insert({
                                "company_name": c_name, "employee_email": active_email,
                                "employee_name": emp.get("name"), "attendance_date": cur_date_str,
                                "status": "Present", "latitude": user_lat, "longitude": user_lng
                            }).execute()
                            st.session_state.emp_coords = False
                            st.success("Attendance marked!")
                            st.rerun()

        elif emp_nav == "GEOFENCE":
            st.subheader(" Geofence Map Verification")
            if st.session_state.emp_coords:
                u_lat, u_lng = st.session_state.emp_coords
                pts = [{'lat': u_lat, 'lon': u_lng}]
                if comp_lat and comp_lng:
                    pts.append({'lat': comp_lat, 'lon': comp_lng})
                st.map(pd.DataFrame(pts), zoom=15)
            else:
                st.info("Capture your location on the Attendance tab to view map coordinates.")

        elif emp_nav == "NOTICES":
            st.subheader("📢 Company Bulletin Board")
            notice_list = [n for n in notices if n.get("notice_text")]
            if notice_list:
                for item in notice_list:
                    st.info(f"• {item.get('notice_text')}")
            else:
                st.caption("No notices available.")

        elif emp_nav == "PROFILE":
            st.subheader("⚙️ Settings & Profile")
            st.write("### 👤 Edit Profile Details")
            with st.form("edit_emp_profile_form"):
                new_name = st.text_input("Full Name", value=emp.get("name", ""))
                new_dept = st.text_input("Department", value=emp.get("department", ""))
                new_pos = st.text_input("Position / Role", value=emp.get("position", ""))
                new_phone = st.text_input("Phone Number", value=emp.get("phone", ""))
                
                if st.form_submit_button(" Save Profile Changes", use_container_width=True):
                    if new_name.strip():
                        supabase.table("employees").update({
                            "name": new_name.strip(),
                            "department": new_dept.strip(),
                            "position": new_pos.strip(),
                            "phone": new_phone.strip()
                        }).eq("email", active_email).execute()
                        st.success("Profile details updated!")
                        st.rerun()
                    else:
                        st.error("Full Name cannot be empty.")

            st.markdown("---")
            col_logout, col_delete = st.columns(2)
            
            with col_logout:
                if st.button(" Sign Out", use_container_width=True):
                    st.session_state.verified_email = None
                    st.session_state.emp_coords = False
                    st.rerun()
with col_delete:
                confirm_del = st.checkbox("Confirm deletion")
                if st.button("❌ Delete Profile", type="primary", use_container_width=True, disabled=not confirm_del):
                    supabase.table("employees").delete().eq("email", active_email).execute()
                    st.session_state.verified_email = None
                    st.session_state.emp_coords = False
                    st.success("Your profile has been removed.")
                    st.rerun()

    # =========================================================
    # 4. NEW USER ONBOARDING
    # =========================================================
    else:
        st.markdown("""
            <div class="app-brand-header">
                <div>
                    <div class="app-title">LockIn PS</div>
                    <div class="app-subtitle">ACCOUNT ONBOARDING</div>
                </div>
            </div>
        """, unsafe_allow_html=True)if st.button("Sign Out"):
            st.session_state.verified_email = None
            st.rerun()

        if st.session_state.show_host_reg:
            st.subheader("🏢 Register Company Profile")
            with st.form("host_form"):new_c_name = st.text_input("Company Name *").strip().upper()
                h_name = st.text_input("Host Name *")
                h_phone = st.text_input("Phone Number")
                if st.form_submit_button("Create Host Account"):
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
            st.info("No active profile linked to this email address.")
            
            if st.button(" Register as Company Host / Owner", use_container_width=True):
                st.session_state.show_host_reg = True
                st.rerun()

            st.markdown("---")
            assigned_id = generate_unique_emp_id()
            
            with st.form("emp_form"):
                st.subheader("Join Company as Employee")
                biz_input = st.text_input("Company Name *").strip().upper()
                st.text_input("Generated Employee ID", value=assigned_id, disabled=True)
                name = st.text_input("Full Name *")
                dept = st.text_input("Department")
                pos = st.text_input("Position")
                phone = st.text_input("Phone Number")

                 if st.form_submit_button("Save Employee Profile"):
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
                        st.success("Profile saved!")
                        st.rerun()
                    else:
                        st.error("Please complete all required fields (*).")
