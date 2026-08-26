import streamlit as st
import random
import smtplib
import pandas as pd
from datetime import date, datetime
from email.mime.text import MIMEText
from supabase import create_client
from streamlit_geolocation import streamlit_geolocation
from geopy.distance import geodesic
import io

# PDF Generation Tool
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# ---------------------------------------------------------
# PAGE CONFIG & STYLES
# ---------------------------------------------------------
st.set_page_config(page_title="PS DIGITAL Enterprise", page_icon="📱", layout="centered")
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
# ENVIRONMENT & SECRETS CONFIGURATION
# ---------------------------------------------------------
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://tqxbeudrvkinuujojasx.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxeGJldWRydmtpbnV1am9qYXN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc1NDQ5NzcsImV4cCI6MjEwMzEyMDk3N30.UC0UDV-vTsSnw8Ff2Jrp9DAfhhhpIkz1iY5eDtimU78")
SUPER_ADMIN_EMAIL = st.secrets.get("SUPER_ADMIN_EMAIL", "pardhukilli273@gmail.com")
SENDER_EMAIL = st.secrets.get("SENDER_EMAIL", "psdigitalmanagementsystem@gmail.com")
SENDER_PASSWORD = st.secrets.get("SENDER_PASSWORD", "vtny yryt ufig kelq")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("⚠️ Missing Supabase credentials! Please configure Streamlit Secrets.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------------------------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------------------------------
for key in ["otp_sent", "generated_otp", "verified_email", "show_host_reg", "show_attendance_list"]:
    if key not in st.session_state:
        st.session_state[key] = False

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------
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

def generate_payslip_pdf(company_name, emp_name, emp_id, month, year, base_salary, days_present, net_pay):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"<b>{company_name}</b>", styles['Title']))
    story.append(Paragraph(f"Payslip for {month} {year}", styles['Heading2']))
    story.append(Spacer(1, 12))

    data = [
        ["Employee Name", emp_name, "Employee ID", emp_id],
        ["Days Present", str(days_present), "Base Salary", f"${base_salary:,.2f}"],
        ["Calculated Net Pay", f"${net_pay:,.2f}", "Payment Status", "Processed"]
    ]
    t = Table(data, colWidths=[120, 140, 120, 140])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer

# ---------------------------------------------------------
# STAGE 1: AUTHENTICATION (OTP LOGIC)
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
# STAGE 2: APPLICATION ROUTING
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

    # --- 1. SUPER ADMIN DASHBOARD ---
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
                    supabase.table("companies").delete().eq("company_name", comp_to_remove).execute()
                    for table in ["employees", "attendance", "company_notices", "leave_requests"]:
                        try:
                            supabase.table(table).delete().eq("company_name", comp_to_remove).execute()
                        except Exception:
                            pass
                    
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
            "📝 Manage Leave Requests",
            "💵 Payroll & Payslips",
            "📍 Fix Shop Location", 
            "👥 Employee Directory", 
            "📢 Post Notice", 
            "📅 Declare Holiday"
        ])
        
        if menu == "📊 Attendance Summary":
            sel_date = st.date_input("Select Date", value=date.today())
            emps = supabase.table("employees").select("*").eq("company_name", c_name).execute().data or []
            att = supabase.table("attendance").select("*").eq("company_name", c_name).eq("attendance_date", str(sel_date)).execute().data or []
                
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
                    for e in present_list:
                        st.write(f"• **{e.get('name')}** ({e.get('email')})")
                else:
                    st.info("No present records found for this date.")
                st.subheader("❌ Absent Staff List")
                if absent_list:
                    for e in absent_list:
                        st.write(f"• **{e.get('name')}** ({e.get('email')})")
                else:
                    st.info("No absent staff for this date.")

        elif menu == "📝 Manage Leave Requests":
            st.subheader("Pending Leave Requests")
            leaves = supabase.table("leave_requests").select("*").eq("company_name", c_name).eq("status", "Pending").execute().data or []
            if leaves:
                for req in leaves:
                    st.write(f"**{req.get('employee_name')}** requested leave for **{req.get('leave_date')}**")
                    st.caption(f"Reason: {req.get('reason')}")
                    c_app, c_rej = st.columns(2)
                    if c_app.button(f"Approve #{req.get('id')}"):
                        supabase.table("leave_requests").update({"status": "Approved"}).eq("id", req.get("id")).execute()
                        st.success("Approved!")
                        st.rerun()
                    if c_rej.button(f"Reject #{req.get('id')}"):
                        supabase.table("leave_requests").update({"status": "Rejected"}).eq("id", req.get("id")).execute()
                        st.info("Rejected!")
                        st.rerun()
                    st.markdown("---")
            else:
                st.info("No pending leave requests.")

        elif menu == "💵 Payroll & Payslips":
            st.subheader("Generate Monthly Employee Payslip")
            emps = supabase.table("employees").select("*").eq("company_name", c_name).execute().data or []
            if emps:
                emp_dict = {e.get('name'): e for e in emps}
                selected_emp_name = st.selectbox("Select Employee", list(emp_dict.keys()))
                selected_emp = emp_dict[selected_emp_name]
                
                col_m, col_y = st.columns(2)
                month = col_m.selectbox("Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
                year = col_y.number_input("Year", value=2026, min_value=2024, max_value=2030)
                
                base_sal = st.number_input("Base Monthly Salary ($)", value=3000, step=100)
                days_present = st.number_input("Days Present in Month", value=22, min_value=0, max_value=31)
                
                net_pay = (base_sal / 22) * days_present if days_present <= 22 else base_sal
                st.write(f"Calculated Net Salary: **${net_pay:,.2f}**")
                
                pdf_bytes = generate_payslip_pdf(c_name, selected_emp_name, selected_emp.get("employee_no"), month, year, base_sal, days_present, net_pay)
                st.download_button("📄 Download PDF Payslip", data=pdf_bytes, file_name=f"Payslip_{selected_emp_name}_{month}_{year}.pdf", mime="application/pdf")
            else:
                st.info("No registered employees found.")

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
            st.dataframe(supabase.table("employees").select("*").eq("company_name", c_name).execute().data or [])

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
        
        emp_menu = st.selectbox("Navigation", ["📍 Attendance", "📝 Request Leave", "📢 Notices & Holidays"])
        
        if emp_menu == "📍 Attendance":
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

        elif emp_menu == "📝 Request Leave":
            st.subheader("Submit Leave Request")
            l_date = st.date_input("Leave Date")
            l_reason = st.text_area("Reason for Leave")
            if st.button("Submi
