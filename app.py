import streamlit as st
import random
import smtplib
import pandas as pd
from io import BytesIO
from datetime import date, datetime
from email.mime.text import MIMEText
from supabase import create_client
from streamlit_geolocation import streamlit_geolocation
from geopy.distance import geodesic
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors as rl_colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="PS DIGITAL", layout="centered")

# ---------------------------------------------------------
# VIBRANT PROFESSIONAL THEME & FLOATING PILL NAVIGATION CSS
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* 1. Reset Body & Core Canvas with subtle color glow */
    html, body, [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 15% -10%, rgba(99,102,241,0.20), transparent 45%),
            radial-gradient(circle at 100% 0%, rgba(236,72,153,0.16), transparent 40%),
            radial-gradient(circle at 50% 100%, rgba(16,185,129,0.10), transparent 40%),
            #0A0A0F !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        color: #F4F4F5 !important;
    }

    /* Hide standard headers, footers, and sidebars */
    header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] {
        visibility: hidden !important;
        height: 0px !important;
        display: none !important;
    }

    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 120px !important; /* Clears floating nav bar */
        max-width: 560px !important;
    }

    /* 2. Top App Branding Header with gradient title */
    .app-brand-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 18px;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 22px;
    }
    .app-title {
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #818CF8, #F472B6 60%, #38BDF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .app-subtitle {
        color: #A1A1AA !important;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* 3. Cards & Containers */
    .hero-card {
        background: linear-gradient(145deg, #17171F 0%, #131318 100%) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-left: 4px solid #818CF8 !important;
        border-radius: 16px !important;
        padding: 20px 22px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35) !important;
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
        background: linear-gradient(145deg, rgba(56,189,248,0.14), rgba(14,165,233,0.05)) !important;
        border: 1px dashed #38BDF8 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        text-align: center !important;
        margin-top: 12px !important;
        margin-bottom: 18px !important;
    }
    .location-box h4 {
        color: #38BDF8 !important;
        font-weight: 700 !important;
        margin-bottom: 4px !important;
    }
    .location-box p {
        color: #7DD3FC !important;
        font-size: 13px !important;
    }

    /* Utility colorful status badges for markdown content */
    .badge-success { display:inline-block; padding:4px 12px; border-radius:999px; background:rgba(16,185,129,0.15); color:#34D399; font-weight:700; font-size:12px; }
    .badge-warning { display:inline-block; padding:4px 12px; border-radius:999px; background:rgba(245,158,11,0.15); color:#FBBF24; font-weight:700; font-size:12px; }
    .badge-danger  { display:inline-block; padding:4px 12px; border-radius:999px; background:rgba(244,63,94,0.15); color:#FB7185; font-weight:700; font-size:12px; }

    /* 4. Streamlit Metric Overrides - colorful gradient values */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #17171F, #131318) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 14px !important;
        padding: 14px 10px !important;
    }
    [data-testid="stMetricValue"] div {
        background: linear-gradient(90deg, #818CF8, #38BDF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 28px !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricLabel"] p {
        color: #A1A1AA !important;
        font-size: 11px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        font-weight: 700 !important;
    }

    /* 5. Modern Form Inputs */
    div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"] {
        background-color: #17171F !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 12px !important;
    }
    div[data-baseweb="input"]:focus-within, div[data-baseweb="textarea"]:focus-within {
        border: 1px solid #818CF8 !important;
        box-shadow: 0 0 0 3px rgba(129,140,248,0.15) !important;
    }
    input, textarea {
        color: #FFFFFF !important;
        font-size: 15px !important;
    }
    label p, label span {
        color: #A1A1AA !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }

    /* 6. Buttons - gradient primary, professional secondary */
    button[kind="primary"] {
        background: linear-gradient(90deg, #6366F1, #EC4899) !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        border: none !important;
        height: 48px !important;
        box-shadow: 0 6px 18px rgba(99,102,241,0.35) !important;
        transition: transform 0.15s ease !important;
    }
    button[kind="primary"]:hover {
        transform: translateY(-1px) !important;
    }
    button[kind="secondary"] {
        background-color: #17171F !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 12px !important;
        height: 48px !important;
    }

    /* Download buttons - emerald accent so PDFs stand out */
    [data-testid="stDownloadButton"] button {
        background: linear-gradient(90deg, #10B981, #059669) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        height: 48px !important;
        box-shadow: 0 6px 18px rgba(16,185,129,0.30) !important;
    }

    /* Dataframe / table polish */
    [data-testid="stDataFrame"] {
        border-radius: 14px !important;
        overflow: hidden !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }

    /* 7. FLOATING CAPSULE BOTTOM NAVIGATION */
    div[data-testid="stRadio"] {
        position: fixed !important;
        bottom: 16px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: calc(100vw - 32px) !important;
        max-width: 520px !important;
        background: rgba(19, 19, 24, 0.92) !important;
        backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 999px !important;
        padding: 6px !important;
        z-index: 999999 !important;
        margin: 0 !important;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5) !important;
    }
    div[data-testid="stRadio"] > div {
        display: flex !important;
        flex-direction: row !important;
        justify-content: space-between !important;
        align-items: center !important;
        gap: 4px !important;
    }
    div[data-testid="stRadio"] label > div:first-child {
        display: none !important; /* Hide radio circle */
    }
    div[data-testid="stRadio"] label {
        flex: 1 !important;
        text-align: center !important;
        background-color: transparent !important;
        color: #A1A1AA !important;
        font-size: 10.5px !important;
        font-weight: 800 !important;
        letter-spacing: 0.6px !important;
        text-transform: uppercase !important;
        padding: 10px 6px !important;
        border-radius: 999px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        margin: 0 !important;
    }
    div[data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(90deg, #6366F1, #EC4899) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(99,102,241,0.4) !important;
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
SENDER_EMAIL = "psdigitalmanagementsystem@gmail.com"
SENDER_PASSWORD = "nmaz vapa mvur hnir"

SESSION_KEYS = [
    "otp_sent", "generated_otp", "verified_email", "show_host_reg",
    "show_attendance_list", "emp_coords", "temp_email", "assigned_emp_id",
]
for k in SESSION_KEYS:
    if k not in st.session_state:
        st.session_state[k] = False


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
    """Generate a 4-digit employee id that isn't already in use."""
    existing_ids = set()
    try:
        existing = supabase.table("employees").select("employee_no").execute().data or []
        existing_ids = {str(e.get("employee_no")) for e in existing}
    except Exception:
        pass
    while True:
        new_id = str(random.randint(1001, 9999))
        if new_id not in existing_ids:
            return new_id


# ---------------------------------------------------------
# PDF GENERATION HELPERS
# ---------------------------------------------------------
BRAND_COLOR = rl_colors.HexColor("#4338CA")
BRAND_LIGHT = rl_colors.HexColor("#EEF2FF")
GRID_COLOR = rl_colors.HexColor("#E4E4E7")


def generate_attendance_receipt_pdf(company_name, employee_name, employee_id, department,
                                     position, att_date, status, lat=None, lng=None, distance=None,
                                     marked_at=None):
    """Builds a one-page attendance confirmation receipt PDF and returns it as bytes."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, bottomMargin=50, leftMargin=50, rightMargin=50)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("ReceiptTitle", parent=styles["Title"], textColor=BRAND_COLOR,
                                  alignment=TA_CENTER, fontSize=20, spaceAfter=2)
    sub_style = ParagraphStyle("ReceiptSub", parent=styles["Normal"], alignment=TA_CENTER,
                                textColor=rl_colors.HexColor("#71717A"), fontSize=10)
    footer_style = ParagraphStyle("ReceiptFooter", parent=styles["Normal"], alignment=TA_CENTER,
                                   fontSize=8, textColor=rl_colors.HexColor("#A1A1AA"))

    story = [
        Paragraph("PS DIGITAL", title_style),
        Paragraph("Attendance Confirmation Receipt", sub_style),
        Spacer(1, 18),
    ]

    rows = [
        ["Company", company_name or "-"],
        ["Employee Name", employee_name or "-"],
        ["Employee ID", str(employee_id) if employee_id else "-"],
        ["Department", department or "-"],
        ["Position", position or "-"],
        ["Date", str(att_date)],
        ["Status", status or "Present"],
    ]
    if marked_at:
        rows.append(["Time Marked", str(marked_at)])
    if lat is not None and lng is not None:
        rows.append(["GPS Coordinates", f"{round(lat, 5)}, {round(lng, 5)}"])
    if distance is not None:
        rows.append(["Distance from Office", f"{round(distance, 1)} meters"])

    table = Table(rows, colWidths=[160, 300])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), BRAND_LIGHT),
        ("TEXTCOLOR", (0, 0), (0, -1), BRAND_COLOR),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, GRID_COLOR),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(table)
    story.append(Spacer(1, 28))
    story.append(Paragraph("This is a system-generated attendance receipt from the PS DIGITAL Attendance Portal.", footer_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_attendance_report_pdf(company_name, report_date, present_list, absent_list):
    """Builds a company-wide daily attendance report PDF and returns it as bytes."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, bottomMargin=50, leftMargin=40, rightMargin=40)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("ReportTitle", parent=styles["Title"], textColor=BRAND_COLOR,
                                  alignment=TA_CENTER, fontSize=18, spaceAfter=2)
    sub_style = ParagraphStyle("ReportSub", parent=styles["Normal"], alignment=TA_CENTER,
                                textColor=rl_colors.HexColor("#71717A"), fontSize=10)
    section_style = ParagraphStyle("SectionHeader", parent=styles["Heading2"], textColor=BRAND_COLOR, fontSize=13)

    story = [
        Paragraph(company_name or "Company", title_style),
        Paragraph(f"Daily Attendance Report &mdash; {report_date}", sub_style),
        Spacer(1, 10),
        Paragraph(f"Total Staff: {len(present_list) + len(absent_list)}  |  Present: {len(present_list)}  |  Absent: {len(absent_list)}", sub_style),
        Spacer(1, 20),
    ]

    header_row = ["#", "Name", "Department", "Position", "Status"]

    def build_table(people, status_label, status_color):
        data = [header_row]
        for i, p in enumerate(people, start=1):
            data.append([str(i), p.get("name", "-"), p.get("department", "-"), p.get("position", "-"), status_label])
        t = Table(data, colWidths=[25, 140, 110, 110, 65])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, GRID_COLOR),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [rl_colors.white, rl_colors.HexColor("#FAFAFA")]),
            ("TEXTCOLOR", (4, 1), (4, -1), status_color),
            ("FONTNAME", (4, 1), (4, -1), "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        return t

    story.append(Paragraph("Present", section_style))
    story.append(Spacer(1, 6))
    story.append(build_table(present_list, "Present", rl_colors.HexColor("#059669")) if present_list
                 else Paragraph("No employees present.", styles["Normal"]))
    story.append(Spacer(1, 18))

    story.append(Paragraph("Absent", section_style))
    story.append(Spacer(1, 6))
    story.append(build_table(absent_list, "Absent", rl_colors.HexColor("#DC2626")) if absent_list
                 else Paragraph("No employees absent.", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


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
            st.subheader("Delete Company Profile")
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
            dl_col1, dl_col2 = st.columns(2)
            if att:
                df = pd.DataFrame(att)
                csv = df.to_csv(index=False).encode('utf-8')
                with dl_col1:
                    st.download_button("⬇️ CSV Report", csv, f"Attendance_{c_name}_{sel_date}.csv", "text/csv", use_container_width=True, key="host_csv_dl")
            with dl_col2:
                report_pdf = generate_attendance_report_pdf(c_name, str(sel_date), present_list, absent_list)
                st.download_button("📄 PDF Report", report_pdf, f"Attendance_{c_name}_{sel_date}.pdf", "application/pdf", use_container_width=True, key="host_pdf_dl")

        elif host_nav == "LOCATION":
            st.subheader("Office GPS Boundary")
            current_lat, current_lng = comp.get("latitude"), comp.get("longitude")
            if current_lat and current_lng:
                st.success(f"GPS Coordinates Active: `{current_lat}, {current_lng}`")
                st.map(pd.DataFrame({'lat': [current_lat], 'lon': [current_lng]}), zoom=15)
            else:
                st.warning("No GPS Boundary configured.")

            st.markdown("""
                <div class="location-box">
                    <h4>Configure GPS Lock</h4>
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
            st.subheader("Employee Directory & Management")
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
                    st.success("Removed employee successfully!")
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
                else:
                    st.warning("Notice text cannot be empty.")

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
                if st.button("🚪 Sign Out", use_container_width=True, key="host_signout"):
                    st.session_state.verified_email = None
                    st.rerun()
            with col_del:
                confirm_host_del = st.checkbox("Confirm deletion")
                if st.button("❌ Delete Profile", type="primary", use_container_width=True, disabled=not confirm_host_del, key="host_delete"):
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
                record = check_att[0]
                st.success(f"✅ Marked Present for Today ({cur_date_str})")

                rec_lat, rec_lng = record.get("latitude"), record.get("longitude")
                rec_dist = None
                if rec_lat is not None and rec_lng is not None and comp_lat and comp_lng:
                    rec_dist = geodesic((rec_lat, rec_lng), (comp_lat, comp_lng)).meters

                pdf_bytes = generate_attendance_receipt_pdf(
                    company_name=c_name, employee_name=emp.get("name"), employee_id=emp.get("employee_no"),
                    department=emp.get("department"), position=emp.get("position"),
                    att_date=cur_date_str, status=record.get("status", "Present"),
                    lat=rec_lat, lng=rec_lng, distance=rec_dist,
                    marked_at=st.session_state.get("last_attendance_time"),
                )
                st.download_button(
                    "📄 Download Attendance PDF", data=pdf_bytes,
                    file_name=f"Attendance_{emp.get('name', 'Employee').replace(' ', '_')}_{cur_date_str}.pdf",
                    mime="application/pdf", use_container_width=True, key="dl_att_pdf",
                )
            else:
                st.markdown("""
                    <div class="location-box">
                        <h4>GPS Verification Terminal</h4>
                        <p>Verify position within 100 meters of office premises.</p>
                    </div>
                """, unsafe_allow_html=True)

                loc_data = streamlit_geolocation()
                if loc_data and loc_data.get("latitude"):
                    st.session_state.emp_coords = (loc_data["latitude"], loc_data["longitude"])

                if st.session_state.emp_coords:
                    user_lat, user_lng = st.session_state.emp_coords
                    st.success(f"Captured: `{round(user_lat, 4)}, {round(user_lng, 4)}`")
                    if comp_lat and comp_lng:
                        dist = geodesic((user_lat, user_lng), (comp_lat, comp_lng)).meters
                        st.write(f"Distance to Office: **{round(dist, 1)} meters**")

                        if dist <= 100:
                            if st.button("✋ Submit Attendance", type="primary", use_container_width=True, key="submit_att_geo"):
                                supabase.table("attendance").insert({
                                    "company_name": c_name, "employee_email": active_email,
                                    "employee_name": emp.get("name"), "attendance_date": cur_date_str,
                                    "status": "Present", "latitude": user_lat, "longitude": user_lng
                                }).execute()
                                st.session_state.emp_coords = False
                                st.session_state.last_attendance_time = datetime.now().strftime("%H:%M:%S")
                                st.success("Attendance marked!")
                                st.rerun()
                        else:
                            st.error("❌ Too far from office premises (Must be within 100m).")
                    else:
                        if st.button("✋ Submit Attendance", type="primary", use_container_width=True, key="submit_att_nogeo"):
                            supabase.table("attendance").insert({
                                "company_name": c_name, "employee_email": active_email,
                                "employee_name": emp.get("name"), "attendance_date": cur_date_str,
                                "status": "Present", "latitude": user_lat, "longitude": user_lng
                            }).execute()
                            st.session_state.emp_coords = False
                            st.session_state.last_attendance_time = datetime.now().strftime("%H:%M:%S")
                            st.success("Attendance marked!")
                            st.rerun()

        elif emp_nav == "GEOFENCE":
            st.subheader("Geofence Map Verification")
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

                if st.form_submit_button("Save Profile Changes", use_container_width=True):
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
                if st.button("Sign Out", use_container_width=True, key="emp_signout"):
                    st.session_state.verified_email = None
                    st.session_state.emp_coords = False
                    st.rerun()

            with col_delete:
                confirm_del = st.checkbox("Confirm deletion")
                if st.button("❌ Delete Profile", type="primary", use_container_width=True, disabled=not confirm_del, key="emp_delete"):
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
        """, unsafe_allow_html=True)

        if st.button("Sign Out", key="onboarding_signout"):
            st.session_state.verified_email = None
            st.rerun()

        if st.session_state.show_host_reg:
            st.subheader("🏢 Register Company Profile")
            with st.form("host_form"):
                new_c_name = st.text_input("Company Name *").strip().upper()
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
                    else:
                        st.error("Company Name and Host Name are required.")

            if st.button("⬅️ Back", key="host_reg_back"):
                st.session_state.show_host_reg = False
                st.rerun()

        else:
            st.info("No active profile linked to this email address.")

            if st.button("Register as Company Host / Owner", use_container_width=True, key="reg_host_btn"):
                st.session_state.show_host_reg = True
                st.rerun()

            st.markdown("---")

            if not st.session_state.assigned_emp_id:
                st.session_state.assigned_emp_id = generate_unique_emp_id()
            assigned_id = st.session_state.assigned_emp_id

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
                        st.session_state.assigned_emp_id = False
                        st.success("Profile saved!")
                        st.rerun()
                    else:
                        st.error("Please complete all required fields (*).")
