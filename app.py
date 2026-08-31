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
# PAGE CONFIG & CUSTOM STYLING
# ---------------------------------------------------------
st.set_page_config(page_title="PS DIGITAL", page_icon="📱", layout="centered")

st.markdown("""
    <style>
    #MainMenu, header, footer, [data-testid="stHeader"], [data-testid="stSidebar"],
    div[data-testid="stToolbar"], div[data-testid="stDecoration"], div[data-testid="stStatusWidget"],
    div[data-testid="stAppViewerHost"], [data-testid="manage-app-button"] {
        display: none !important; visibility: hidden !important;
    }
    .main .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
    
    /* Main Header Banner */
    .main-header {
        background: linear-gradient(135deg, #FF512F 0%, #DD2476 100%);
        color: #FFFFFF !important; padding: 20px; border-radius: 14px;
        text-align: center; font-family: 'Trebuchet MS', sans-serif;
        font-size: 26px; font-weight: 800; letter-spacing: 1px;
        box-shadow: 0px 4px 15px rgba(221, 36, 118, 0.3);
        margin-bottom: 20px; text-transform: uppercase;
    }

    /* Input Field & Caption High Contrast Fixes */
    div[data-testid="stCaptionContainer"] {
        color: #1E293B !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
    }

    label, p, span, h1, h2, h3, h4, h5, h6 {
        color: #0F172A !important;
    }

    /* Style Text Inputs for High Legibility */
    div[data-baseweb="input"] {
        background-color: #F1F5F9 !important;
        border: 2px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }
    
    input {
        color: #0F172A !important;
        font-weight: 600 !important;
    }

    /* Hero Card Text & Titles */
    .hero-card {
        background-color: #F8FAFC !important;
        border-left: 5px solid #DD2476;
        padding: 16px; 
        border-radius: 8px;
        margin-bottom: 15px;
        box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.05);
    }

    .hero-card, .hero-card h3, .hero-card p, .hero-card b {
        color: #000000 !important;
        font-weight: 800 !important;
    }
    
    /* Dashboard Metrics & Labels */
    [data-testid="stMetricLabel"] p, 
    [data-testid="stMetricValue"] div {
        color: #000000 !important;
        font-weight: 800 !important;
    }
    
    .location-box {
        background-color: #EFF6FF !important;
        color: #1E3A8A !important;
        border: 2px dashed #3B82F6;
        padding: 20px; border-radius: 12px;
        text-align: center; margin-top: 10px; margin-bottom: 15px;
    }
    .location-box h4, .location-box p {
        color: #1E3A8A !important;
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

for key in ["otp_sent", "generated_otp", "verified_email", "show_host_reg", "show_attendance_list", "emp_coords"]:
    if key not in st.session_state:
        st.session_state[key] = False

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
    st.markdown("""<div class="main-header">📱 PS DIGITAL</div>""", unsafe_allow_html=True)
    st.caption("**ENTERPRISE MULTI-HOST MANAGEMENT & ATTENDANCE SYSTEM**")
    st.markdown("**Enter Email Address to Access Portal**")
    user_email = st.text_input("Enter Email Address to Access Portal", label_visibility="collapsed").strip().lower()
    if user_email and not st.session_state.otp_sent:
        if st.button("Send Verification Code", use_container_width=True):
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

        if st.button("Verify & Login", use_container_width=True):
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
        st.markdown("""<div class="main-header">👑 Super Admin Portal</div>""", unsafe_allow_html=True)
        
        c1, c2 = st.columns([3, 1])
        c1.write(f"Logged in as: **{SUPER_ADMIN_EMAIL}**")
        if c2.button("Logout"):
            st.session_state.verified_email = None
            st.rerun()
            
        st.markdown("---")
        
        admin_menu = st.selectbox("📌 Select Module / Feature", [
            "1. 🏠 Admin Home Dashboard",
            "2. 🏢 Registered Companies Directory",
            "3. 🗑️ Remove / Delete Company"
        ])

        companies = supabase.table("companies").select("*").execute().data or []
        employees = supabase.table("employees").select("company_name").execute().data or []

        emp_counts = {}
        for emp in employees:
            cn = emp.get("company_name")
            if cn:
                emp_counts[cn] = emp_counts.get(cn, 0) + 1

        for comp in companies:
            comp["employee_count"] = emp_counts.get(comp.get("company_name"), 0)

        if admin_menu.startswith("1."):
            st.markdown("""<div class="hero-card"><h3> Welcome, System Super Admin</h3><p>Manage enterprise clients, system data, and company removal from this hub.</p></div>""", unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            col_a.metric("Total Companies", len(companies))
            col_b.metric("Total Platform Users", len(employees))

        elif admin_menu.startswith("2."):
            st.subheader("🏢 Registered Companies")
            st.dataframe(companies, use_container_width=True)

        elif admin_menu.startswith("3."):
            st.subheader("🗑️ Delete Company Profile")
            company_names = [c.get("company_name") for c in companies if c.get("company_name")]
            if company_names:
                comp_to_remove = st.selectbox("Select Company to Remove", options=company_names)
                if st.button("❌ Permanently Remove Company", type="primary", use_container_width=True):
                    try:
                        supabase.table("companies").delete().eq("company_name", comp_to_remove).execute()
                        try:
                            supabase.table("employees").delete().eq("company_name", comp_to_remove).execute()
                        except Exception:
                            pass
                        try:
                            supabase.table("attendance").delete().eq("company_name", comp_to_remove).execute()
                        except Exception:
                            pass
                        try:
                            supabase.table("company_notices").delete().eq("company_name", comp_to_remove).execute()
                        except Exception:
                            pass
                        st.success(f"Company '{comp_to_remove}' and associated data removed!")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Error removing company: {err}")
            else:
                st.info("No companies registered.")

    # =========================================================
    # 2. HOST DASHBOARD
    # =========================================================
    elif host_check:
        comp = host_check[0]
        c_name = comp.get("company_name", "Company Portal")
        st.markdown(f"""<div class="main-header">🏢 {c_name}</div>""", unsafe_allow_html=True)
        
        c1, c2 = st.columns([3, 1])
        c1.write(f"Host: **{comp.get('host_name')}**")
        if c2.button("Logout"):
            st.session_state.verified_email = None
            st.rerun()
        st.markdown("---")

        host_menu = st.selectbox("📌 Select Menu Option", [
            "1. 🏠 Home Overview",
            "2. 📊 Daily Attendance Summary & Export",
            "3. 📍 Fix Company Location (GPS)",
            "4. 👥 Employee Directory",
            "5. 📢 Post Announcement Notice",
            "6. 📅 Declare Company Holiday"
        ])

        # 1. Host Home
        if host_menu.startswith("1."):
            st.markdown(f"""
                <div class="hero-card">
                    <h3>🏢 {c_name} Host Workspace</h3>
                    <p>Use the navigation menu above to check attendance, set up company GPS boundaries, and issue notices.</p>
                </div>
            """, unsafe_allow_html=True)
            
            emps = supabase.table("employees").select("*").eq("company_name", c_name).execute().data or []
            today_att = supabase.table("attendance").select("*").eq("company_name", c_name).eq("attendance_date", str(date.today())).execute().data or []
            
            m1, m2 = st.columns(2)
            m1.metric("Registered Employees", len(emps))
            m2.metric("Present Today", len(today_att))

        # 2. Attendance Summary
        elif host_menu.startswith("2."):
            st.subheader("📊 Attendance Summary & Reports")
            sel_date = st.date_input("Select Attendance Date", value=date.today())
            
            emps = supabase.table("employees").select("*").eq("company_name", c_name).execute().data or []
            att = supabase.table("attendance").select("*").eq("company_name", c_name).eq("attendance_date", str(sel_date)).execute().data or []
            
            present_emails = {a.get("employee_email") for a in att}
            present_list = [e for e in emps if e.get("email") in present_emails]
            absent_list = [e for e in emps if e.get("email") not in present_emails]
            
            col_x, col_y, col_z = st.columns(3)
            col_x.metric("Total Staff", len(emps))
            col_y.metric("Present", len(present_list))
            col_z.metric("Absent", len(absent_list))
            
            if att:
                df = pd.DataFrame(att)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Export Attendance Report (CSV)", csv, f"Attendance_{c_name}_{sel_date}.csv", "text/csv", use_container_width=True)

            st.markdown("---")
            if st.button("👁️ Toggle Present/Absent Breakdown", use_container_width=True):
                st.session_state.show_attendance_list = not st.session_state.show_attendance_list
            
            if st.session_state.show_attendance_list:
                st.write("### ✅ Present Staff")
                for e in present_list:
                    st.write(f"• **{e.get('name')}** ({e.get('email')})")
                st.write("### ❌ Absent Staff")
                for e in absent_list:
                    st.write(f"• **{e.get('name')}** ({e.get('email')})")

        # 3. Fix Location
        elif host_menu.startswith("3."):
            st.subheader("📍 Official Company Location Setup")
            current_lat, current_lng = comp.get("latitude"), comp.get("longitude")

            if current_lat and current_lng:
                st.success(f"Active GPS Lock: Latitude `{current_lat}`, Longitude `{current_lng}`")
                st.map(pd.DataFrame({'lat': [current_lat], 'lon': [current_lng]}), zoom=15)
                st.markdown(f"🗺️ [Open Saved Location in Google Maps](https://www.google.com/maps?q={current_lat},{current_lng})")
            else:
                st.warning("No location configured! Employees can currently mark attendance from anywhere.")

            st.markdown("""
                <div class="location-box">
                    <h4>📍 Location Lock Terminal</h4>
                    <p>Stand at your main office or shop door and trigger the GPS scanner below to store company coordinates.</p>
                </div>
            """, unsafe_allow_html=True)
            
            host_loc = streamlit_geolocation()
            if host_loc and host_loc.get("latitude"):
                st.info(f"Captured GPS: `{host_loc['latitude']}, {host_loc['longitude']}`")
                if st.button("🔒 Lock Location Coordinates", type="primary", use_container_width=True):
                    supabase.table("companies").update({
                        "latitude": host_loc["latitude"],
                        "longitude": host_loc["longitude"]
                    }).eq("company_name", c_name).execute()
                    st.success("Company location updated successfully!")
                    st.rerun()

        # 4. Directory
        elif host_menu.startswith("4."):
            st.subheader("👥 Employee Directory")
            emps = supabase.table("employees").select("*").eq("company_name", c_name).execute().data or []
            st.dataframe(emps, use_container_width=True)

        # 5. Post Notice
        elif host_menu.startswith("5."):
            st.subheader("📢 Post Announcement")
            msg = st.text_area("Notice Message")
            if st.button("Publish Notice", type="primary", use_container_width=True):
                supabase.table("company_notices").insert({"company_name": c_name, "notice_text": msg.strip()}).execute()
                st.success("Notice published!")

        # 6. Declare Holiday
        elif host_menu.startswith("6."):
            st.subheader("📅 Declare Holiday")
            h_date = st.date_input("Holiday Date")
            h_title = st.text_input("Holiday Occasion / Reason")
            if st.button("Save Holiday", type="primary", use_container_width=True):
                supabase.table("company_notices").insert({"company_name": c_name, "holiday_date": str(h_date), "holiday_title": h_title.strip()}).execute()
                st.success("Holiday registered!")

    # =========================================================
    # 3. EMPLOYEE DASHBOARD
    # =========================================================
    elif emp_records:
        emp = emp_records[0]
        c_name = emp.get("company_name", "Company Portal")
        st.markdown(f"""<div class="main-header">🏢 {c_name}</div>""", unsafe_allow_html=True)
        
        c1, c2 = st.columns([3, 1])
        c1.write(f"Logged in: **{emp.get('name')}**")
        if c2.button("Logout"):
            st.session_state.verified_email = None
            st.rerun()
        st.markdown("---")

        emp_menu = st.selectbox("📌 Select View Option", [
            "1. 🏠 Home Page & Quick Attendance",
            "2. 📍 Detailed Geofence Location Verification",
            "3. 📢 Company Notices & Announcements",
            "4. 🗓️ Company Holidays Calendar"
        ])

        try:
            notices = supabase.table("company_notices").select("*").eq("company_name", c_name).order("created_at", desc=True).execute().data or []
        except Exception:
            notices = []

        comp_info = supabase.table("companies").select("*").eq("company_name", c_name).execute().data
        comp_lat = comp_info[0].get("latitude") if comp_info else None
        comp_lng = comp_info[0].get("longitude") if comp_info else None
        cur_date_str = str(date.today())

        # 1. Home & Attendance
        if emp_menu.startswith("1."):
            st.markdown(f"""
                <div class="hero-card">
                    <h3>Welcome back, {emp.get("name")}!</h3>
                    <p>Department: <b>{emp.get("department", "General")}</b> | Employee No: <b>{emp.get("employee_no")}</b></p>
                </div>
            """, unsafe_allow_html=True)

            latest_notice = [n for n in notices if n.get("notice_text")]
            if latest_notice:
                st.info(f"📢 **Latest Notice:** {latest_notice[0].get('notice_text')}")

            st.subheader("📅 Today's Attendance")
            check_att = supabase.table("attendance").select("*").eq("company_name", c_name).eq("employee_email", active_email).eq("attendance_date", cur_date_str).execute().data

            if check_att:
                st.success(f"✅ Marked Present for Today ({cur_date_str})")
            else:
                st.write("Scan your location below to register daily attendance:")
                
                st.markdown("""
                    <div class="location-box">
                        <h4>📍 GPS Location Verification Terminal</h4>
                        <p>Click below to verify that you are within 100 meters of company premises.</p>
                    </div>
                """, unsafe_allow_html=True)
                
                loc_data = streamlit_geolocation()
                if loc_data and loc_data.get("latitude"):
                    st.session_state.emp_coords = (loc_data["latitude"], loc_data["longitude"])

                if st.session_state.emp_coords:
                    user_lat, user_lng = st.session_state.emp_coords
                    st.success(f"Captured Position: `{round(user_lat, 4)}, {round(user_lng, 4)}`")

                    if comp_lat and comp_lng:
                        dist = geodesic((user_lat, user_lng), (comp_lat, comp_lng)).meters
                        st.write(f"Distance to company: **{round(dist, 1)} meters**")

                        if dist <= 100:
                            if st.button("✋ Submit Attendance (Present)", type="primary", use_container_width=True):
                                supabase.table("attendance").insert({
                                    "company_name": c_name, "employee_email": active_email,
                                    "employee_name": emp.get("name"), "attendance_date": cur_date_str,
                                    "status": "Present", "latitude": user_lat, "longitude": user_lng
                                }).execute()
                                st.session_state.emp_coords = False
                                st.success("Attendance registered!")
                                st.rerun()
                        else:
                            st.error("❌ Too far from company premises (Must be within 100m).")
                    else:
                        if st.button("✋ Submit Attendance (Present)", type="primary", use_container_width=True):
                            supabase.table("attendance").insert({
                                "company_name": c_name, "employee_email": active_email,
                                "employee_name": emp.get("name"), "attendance_date": cur_date_str,
                                "status": "Present", "latitude": user_lat, "longitude": user_lng
                            }).execute()
                            st.session_state.emp_coords = False
                            st.success("Attendance registered!")
                            st.rerun()

        # 2. Detailed Location View
        elif emp_menu.startswith("2."):
            st.subheader("📍 Geofence Map Verification")
            if st.session_state.emp_coords:
                u_lat, u_lng = st.session_state.emp_coords
                st.markdown(f"🗺️ [**Open Position in Google Maps App**](https://www.google.com/maps?q={u_lat},{u_lng})")
                pts = [{'lat': u_lat, 'lon': u_lng}]
                if comp_lat and comp_lng:
                    pts.append({'lat': comp_lat, 'lon': comp_lng})
                st.map(pd.DataFrame(pts), zoom=15)
            else:
                st.info("Capture your location on the Home page to view map details.")

        # 3. Notices
        elif emp_menu.startswith("3."):
            st.subheader("📢 Company Notice Board")
            notice_list = [n for n in notices if n.get("notice_text")]
            if notice_list:
                for item in notice_list:
                    st.info(f"• {item.get('notice_text')}")
            else:
                st.caption("No notices posted.")

        # 4.Holidays
        elif emp_menu.startswith("4."):
            st.subheader("🗓️ Holidays Calendar")
            holidays = [n for n in notices if n.get("holiday_date")]
            if holidays:
                for h in holidays:
                    st.warning(f"📌 **{h.get('holiday_date')}**: {h.get('holiday_title', 'Holiday')}")
            else:
                st.caption("No upcoming company holidays listed.")

    # =========================================================
    # 4. NEW USER ONBOARDING
    # =========================================================
    else:
        st.markdown("""<div class="main-header">📱 PS DIGITAL</div>""", unsafe_allow_html=True)
        if st.button("Logout"):
            st.session_state.verified_email = None
            st.rerun()
            st.markdown("---")

        if st.session_state.show_host_reg:
            st.subheader("🏢 Register Company Profile")
            with st.form("host_form"):
                new_c_name = st.text_input("Company Name *").strip()
                h_name = st.text_input("Host Name *")
                h_phone = st.text_input("Phone Number")
                if st.form_submit_button("Register Company Host Profile"):
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
            st.warning("No profile associated with this account. Please select an option:")
            
            if st.button("👔 Register as Company Host / Owner", use_container_width=True):
                st.session_state.show_host_reg = True
                st.rerun()

            st.markdown("---")
            assigned_id = generate_unique_emp_id()
            
            with st.form("emp_form"):
                st.subheader("Add Employee Profile")
                biz_input = st.text_input("Company Name *").strip()
                st.text_input("Assigned Employee ID", value=assigned_id, disabled=True)
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
                        st.success("Profile saved successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill in required fields marked with *.")
