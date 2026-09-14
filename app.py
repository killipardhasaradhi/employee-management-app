import streamlit as st
import random
import smtplib
import pandas as pd
from io import BytesIO
from datetime import date, datetime, timedelta, time as dtime
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
st.set_page_config(page_title="PS DIGITAL", page_icon="🏢", layout="centered")

# ---------------------------------------------------------
# VIBRANT PROFESSIONAL THEME & HAMBURGER MENU CSS
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

    header, footer, [data-testid="stHeader"], [data-testid="stSidebar"] {
        visibility: hidden !important;
        height: 0px !important;
        display: none !important;
    }

    .main .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
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
        font-size: 26px !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricLabel"] p {
        color: #A1A1AA !important;
        font-size: 11px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        font-weight: 700 !important;
    }

    /* 5. Modern Form Inputs - BRIGHT, high-contrast typed text */
    div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="select"],
    div[data-baseweb="base-input"],
    div[data-testid="stTextInput"] div[data-baseweb],
    div[data-testid="stTextArea"] div[data-baseweb],
    div[data-testid="stNumberInput"] div[data-baseweb],
    div[data-testid="stDateInput"] div[data-baseweb],
    div[data-testid="stTimeInput"] div[data-baseweb] {
        background-color: #17171F !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
    }
    div[data-baseweb="input"]:focus-within, div[data-baseweb="textarea"]:focus-within,
    div[data-baseweb="select"]:focus-within {
        border: 1px solid #818CF8 !important;
        box-shadow: 0 0 0 3px rgba(129,140,248,0.15) !important;
    }
    input, textarea,
    div[data-baseweb="input"], div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"], div[data-baseweb="base-input"] > div,
    div[data-baseweb="textarea"], div[data-baseweb="textarea"] > div,
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextInput"] > div,
    div[data-testid="stTextInput"] div,
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stTextArea"] > div,
    div[data-testid="stDateInput"] input,
    div[data-testid="stDateInput"] > div,
    div[data-testid="stTimeInput"] input,
    div[data-testid="stTimeInput"] > div,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stNumberInput"] > div {
        background-color: #17171F !important;
    }
    input, textarea,
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea,
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stDateInput"] input,
    div[data-testid="stTimeInput"] input,
    div[data-testid="stNumberInput"] input {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        caret-color: #F472B6 !important;
        font-size: 15.5px !important;
        font-weight: 700 !important;
    }
    input::placeholder, textarea::placeholder {
        color: #A1A1AA !important;
        -webkit-text-fill-color: #A1A1AA !important;
        opacity: 1 !important;
        font-weight: 400 !important;
    }
    input:-webkit-autofill,
    input:-webkit-autofill:hover,
    input:-webkit-autofill:focus,
    input:-webkit-autofill:active {
        -webkit-text-fill-color: #FFFFFF !important;
        -webkit-box-shadow: 0 0 0px 1000px #17171F inset !important;
        box-shadow: 0 0 0px 1000px #17171F inset !important;
        transition: background-color 9999s ease-in-out 0s !important;
        caret-color: #FFFFFF !important;
    }
    div[data-baseweb="select"] {
        background-color: #17171F !important;
    }
    div[data-baseweb="select"] * {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    label p, label span {
        color: #A1A1AA !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }

    /* 6. Buttons - gradient primary, professional secondary
       (covers both regular st.button AND st.form_submit_button) */
    button[kind="primary"], button[kind="primaryFormSubmit"] {
        background: linear-gradient(90deg, #6366F1, #EC4899) !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        border: none !important;
        height: 48px !important;
        box-shadow: 0 6px 18px rgba(99,102,241,0.35) !important;
        transition: transform 0.15s ease !important;
    }
    button[kind="primary"] p, button[kind="primaryFormSubmit"] p,
    button[kind="primary"] div, button[kind="primaryFormSubmit"] div {
        color: #FFFFFF !important;
    }
    button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover {
        transform: translateY(-1px) !important;
    }
    button[kind="secondary"], button[kind="secondaryFormSubmit"] {
        background-color: #17171F !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 12px !important;
        height: 48px !important;
    }
    button[kind="secondary"] p, button[kind="secondaryFormSubmit"] p,
    button[kind="secondary"] div, button[kind="secondaryFormSubmit"] div {
        color: #FFFFFF !important;
    }

    [data-testid="stDownloadButton"] button {
        background: linear-gradient(90deg, #10B981, #059669) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        height: 48px !important;
        box-shadow: 0 6px 18px rgba(16,185,129,0.30) !important;
    }

    [data-testid="stDataFrame"] {
        border-radius: 14px !important;
        overflow: hidden !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }

    /* 7. HAMBURGER MENU BUTTON */
    .nav-burger-marker + div [data-testid="stButton"] button {
        background: #17171F !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        height: 42px !important;
        padding: 0 !important;
        color: #FFFFFF !important;
    }

    /* 8. VERTICAL DROPDOWN MENU PANEL (opens line-by-line under the hamburger) */
    div[data-testid="stVerticalBlock"]:has(> div .nav-menu-marker) {
        background: linear-gradient(145deg, #17171F, #131318) !important;
        border: 1px solid rgba(255,255,255,0.10) !important;
        border-radius: 16px !important;
        padding: 8px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 14px 34px rgba(0, 0, 0, 0.45) !important;
        gap: 4px !important;
    }
    div[data-testid="stVerticalBlock"]:has(> div .nav-menu-marker) [data-testid="stButton"] button {
        justify-content: flex-start !important;
        text-align: left !important;
        padding-left: 18px !important;
        font-size: 14.5px !important;
        letter-spacing: 0.3px !important;
        height: 46px !important;
    }
    div[data-testid="stVerticalBlock"]:has(> div .nav-menu-marker) button[kind="secondary"] {
        background: transparent !important;
        border: none !important;
        border-bottom: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 10px !important;
        color: #D4D4D8 !important;
        box-shadow: none !important;
    }
    div[data-testid="stVerticalBlock"]:has(> div .nav-menu-marker) button[kind="primary"] {
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# CREDENTIALS CONFIGURATION (Streamlit secrets, with fallback)
# ---------------------------------------------------------
def _get_secret(key, fallback=None):
    try:
        return st.secrets[key]
    except Exception:
        return fallback


_USING_FALLBACK_SECRETS = False
SUPABASE_URL = _get_secret("SUPABASE_URL")
SUPABASE_KEY = _get_secret("SUPABASE_KEY")
SUPER_ADMIN_EMAIL = _get_secret("SUPER_ADMIN_EMAIL")
SENDER_EMAIL = _get_secret("SENDER_EMAIL")
SENDER_PASSWORD = _get_secret("SENDER_PASSWORD")

if not all([SUPABASE_URL, SUPABASE_KEY, SUPER_ADMIN_EMAIL, SENDER_EMAIL, SENDER_PASSWORD]):
    _USING_FALLBACK_SECRETS = True
    # NOTE: These fallback values only exist so the app keeps working until
    # you configure real Streamlit secrets. Rotate these credentials and move
    # them to .streamlit/secrets.toml (or the Streamlit Cloud "Secrets" panel)
    # as soon as possible -- see DEPLOYMENT_NOTES.md.
    SUPABASE_URL = SUPABASE_URL or "https://tqxbeudrvkinuujojasx.supabase.co"
    SUPABASE_KEY = SUPABASE_KEY or "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxeGJldWRydmtpbnV1am9qYXN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc1NDQ5NzcsImV4cCI6MjEwMzEyMDk3N30.UC0UDV-vTsSnw8Ff2Jrp9DAfhhhpIkz1iY5eDtimU78"
    SUPER_ADMIN_EMAIL = SUPER_ADMIN_EMAIL or "pardhukilli273@gmail.com"
    SENDER_EMAIL = SENDER_EMAIL or "psdigitalmanagementsystem@gmail.com"
    SENDER_PASSWORD = SENDER_PASSWORD or "nmaz vapa mvur hnir"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

OTP_COOLDOWN_SECONDS = 60
OTP_EXPIRY_SECONDS = 300  # 5 minutes

SESSION_KEYS = [
    "otp_sent", "generated_otp", "verified_email", "show_host_reg",
    "show_attendance_list", "emp_coords", "temp_email", "assigned_emp_id",
    "otp_generated_time", "otp_last_sent_time", "last_attendance_time",
]
for k in SESSION_KEYS:
    if k not in st.session_state:
        st.session_state[k] = False


def send_otp_email(target_email, otp_code):
    try:
        msg = MIMEText(f"Your verification code for PS DIGITAL Platform is: {otp_code}\n\nThis code expires in 5 minutes.")
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


def generate_unique_emp_id(existing_ids=None):
    """Generate a 4-digit employee id that isn't already in use."""
    if existing_ids is None:
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
# CACHED READ HELPERS (reduces redundant Supabase calls)
# ---------------------------------------------------------
@st.cache_data(ttl=30, show_spinner=False)
def cached_all_companies():
    return supabase.table("companies").select("*").execute().data or []


@st.cache_data(ttl=30, show_spinner=False)
def cached_all_employees_slim():
    return supabase.table("employees").select("company_name").execute().data or []


def clear_admin_caches():
    cached_all_companies.clear()
    cached_all_employees_slim.clear()


# ---------------------------------------------------------
# ATTENDANCE ANALYTICS HELPERS
# ---------------------------------------------------------
def get_employee_attendance_trend(company_name, email, days=30):
    start = (date.today() - timedelta(days=days - 1)).isoformat()
    try:
        recs = supabase.table("attendance").select("attendance_date").eq(
            "company_name", company_name).eq("employee_email", email).gte("attendance_date", start).execute().data or []
    except Exception:
        recs = []
    present_dates = {r.get("attendance_date") for r in recs}
    date_range = [(date.today() - timedelta(days=i)) for i in range(days - 1, -1, -1)]
    df = pd.DataFrame({
        "Day": [d.strftime("%d %b") for d in date_range],
        "Present": [1 if d.isoformat() in present_dates else 0 for d in date_range],
    })
    return df, len(present_dates)


def get_company_attendance_trend(company_name, days=30):
    start = (date.today() - timedelta(days=days - 1)).isoformat()
    try:
        recs = supabase.table("attendance").select("attendance_date").eq(
            "company_name", company_name).gte("attendance_date", start).execute().data or []
    except Exception:
        recs = []
    counts = {}
    for r in recs:
        d = r.get("attendance_date")
        counts[d] = counts.get(d, 0) + 1
    date_range = [(date.today() - timedelta(days=i)) for i in range(days - 1, -1, -1)]
    df = pd.DataFrame({
        "Day": [d.strftime("%d %b") for d in date_range],
        "Present Count": [counts.get(d.isoformat(), 0) for d in date_range],
    })
    return df


# ---------------------------------------------------------
# ATTENDANCE STATUS / LATE TRACKING HELPERS
# ---------------------------------------------------------
def compute_attendance_status(comp, marked_time_str):
    """Compares the marked time (HH:MM:SS) against the company's configured
    shift start time + grace period, if configured. Falls back to 'Present'
    if no shift policy has been set."""
    shift_start = comp.get("shift_start_time") if comp else None
    grace = comp.get("late_grace_minutes") if comp else None
    if not shift_start:
        return "Present"
    try:
        grace = int(grace) if grace is not None else 15
        shift_h, shift_m = [int(x) for x in str(shift_start).split(":")[:2]]
        marked_h, marked_m, *_ = [int(x) for x in marked_time_str.split(":")]
        shift_minutes = shift_h * 60 + shift_m + grace
        marked_minutes = marked_h * 60 + marked_m
        return "Late" if marked_minutes > shift_minutes else "Present"
    except Exception:
        return "Present"


def safe_insert_attendance(payload):
    """Inserts an attendance row. If optional columns (marked_time) don't exist
    yet in the DB (migration not run), retries without them so the core
    check-in flow never breaks."""
    try:
        supabase.table("attendance").insert(payload).execute()
        return True
    except Exception:
        reduced = {k: v for k, v in payload.items() if k not in ("marked_time",)}
        try:
            supabase.table("attendance").insert(reduced).execute()
            return True
        except Exception as e2:
            st.error(f"Could not save attendance: {e2}")
            return False


# ---------------------------------------------------------
# MULTI-ADMIN HELPERS (graceful no-op if company_admins table absent)
# ---------------------------------------------------------
def get_host_company_for_email(email):
    """Returns the company record this email administers, checking both the
    primary host_email column and the optional company_admins table."""
    try:
        primary = supabase.table("companies").select("*").eq("host_email", email).execute().data
    except Exception:
        primary = []
    if primary:
        return primary
    try:
        link = supabase.table("company_admins").select("*").eq("email", email).execute().data
        if link:
            comp_name = link[0].get("company_name")
            return supabase.table("companies").select("*").eq("company_name", comp_name).execute().data
    except Exception:
        pass
    return []


def get_company_admins(company_name):
    try:
        return supabase.table("company_admins").select("*").eq("company_name", company_name).execute().data or []
    except Exception:
        return []


# ---------------------------------------------------------
# BULK EMPLOYEE IMPORT HELPER
# ---------------------------------------------------------
def bulk_import_employees(df, company_name):
    """Expects columns: name, email (required); department, position, phone (optional).
    Skips rows missing name/email or already existing (by email)."""
    added, skipped, errors = 0, 0, []
    try:
        existing = supabase.table("employees").select("employee_no,email").eq("company_name", company_name).execute().data or []
    except Exception:
        existing = []
    existing_emails = {e.get("email") for e in existing if e.get("email")}
    existing_ids = {str(e.get("employee_no")) for e in existing if e.get("employee_no")}

    df.columns = [c.strip().lower() for c in df.columns]
    df = df.fillna("")

    def _clean(val):
        return str(val).strip()

    for _, row in df.iterrows():
        name = _clean(row.get("name", ""))
        email = _clean(row.get("email", "")).lower()
        if not name or not email or email in existing_emails:
            skipped += 1
            continue
        new_id = generate_unique_emp_id(existing_ids)
        existing_ids.add(new_id)
        try:
            supabase.table("employees").insert({
                "employee_no": new_id,
                "company_name": company_name,
                "name": name,
                "department": _clean(row.get("department", "")),
                "position": _clean(row.get("position", "")),
                "phone": _clean(row.get("phone", "")),
                "email": email,
            }).execute()
            existing_emails.add(email)
            added += 1
        except Exception as e:
            errors.append(f"{email}: {e}")
    return added, skipped, errors


# ---------------------------------------------------------
# HAMBURGER DROPDOWN MENU (vertical, line-by-line navigation)
# ---------------------------------------------------------
NAV_ICONS = {
    "DASHBOARD": "📊", "DIRECTORY": "📁", "REMOVE COMP": "🗑️",
    "HOME": "🏠", "ATTENDANCE": "🗓️", "LOCATION": "📍", "STAFF": "👥",
    "NOTICES": "📢", "SETTINGS": "⚙️", "LEAVE": "🌴",
    "ATTEND": "✋", "GEOFENCE": "🧭", "PROFILE": "👤",
}


def render_menu(nav_key, options, default=None):
    """Renders a hamburger (☰) button that opens a vertical, line-by-line menu.
    Returns the currently active option (unchanged values, for use in if/elif checks)."""
    open_key = f"{nav_key}_menu_open"
    active_key = f"{nav_key}_menu_active"
    if open_key not in st.session_state:
        st.session_state[open_key] = False
    if active_key not in st.session_state or st.session_state[active_key] not in options:
        st.session_state[active_key] = default or options[0]

    st.markdown('<div class="nav-burger-marker"></div>', unsafe_allow_html=True)
    top_l, top_r = st.columns([5, 1])
    with top_l:
        current_icon = NAV_ICONS.get(st.session_state[active_key], "•")
        st.markdown(
            f'<div style="padding-top:8px; color:#D4D4D8; font-weight:700; font-size:14px;">'
            f'{current_icon} {st.session_state[active_key].title()}</div>',
            unsafe_allow_html=True,
        )
    with top_r:
        if st.button("☰", key=f"{nav_key}_burger", use_container_width=True):
            st.session_state[open_key] = not st.session_state[open_key]
            st.rerun()

    if st.session_state[open_key]:
        menu_box = st.container()
        with menu_box:
            st.markdown('<div class="nav-menu-marker"></div>', unsafe_allow_html=True)
            for opt in options:
                icon = NAV_ICONS.get(opt, "•")
                is_active = st.session_state[active_key] == opt
                if st.button(
                    f"{icon}  {opt.title()}", key=f"{nav_key}_item_{opt}",
                    use_container_width=True, type="primary" if is_active else "secondary",
                ):
                    st.session_state[active_key] = opt
                    st.session_state[open_key] = False
                    st.rerun()

    return st.session_state[active_key]


# ---------------------------------------------------------
# PDF GENERATION HELPERS
# ---------------------------------------------------------
BRAND_COLOR = rl_colors.HexColor("#4338CA")
BRAND_LIGHT = rl_colors.HexColor("#EEF2FF")
GRID_COLOR = rl_colors.HexColor("#E4E4E7")


def generate_attendance_receipt_pdf(company_name, employee_name, employee_id, department,
                                     position, att_date, status, lat=None, lng=None, distance=None,
                                     marked_at=None):
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


def generate_attendance_report_pdf(company_name, report_date, present_list, absent_list, on_leave_list=None):
    on_leave_list = on_leave_list or []
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=50, bottomMargin=50, leftMargin=40, rightMargin=40)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("ReportTitle", parent=styles["Title"], textColor=BRAND_COLOR,
                                  alignment=TA_CENTER, fontSize=18, spaceAfter=2)
    sub_style = ParagraphStyle("ReportSub", parent=styles["Normal"], alignment=TA_CENTER,
                                textColor=rl_colors.HexColor("#71717A"), fontSize=10)
    section_style = ParagraphStyle("SectionHeader", parent=styles["Heading2"], textColor=BRAND_COLOR, fontSize=13)

    total = len(present_list) + len(absent_list) + len(on_leave_list)
    story = [
        Paragraph(company_name or "Company", title_style),
        Paragraph(f"Daily Attendance Report &mdash; {report_date}", sub_style),
        Spacer(1, 10),
        Paragraph(
            f"Total Staff: {total}  |  Present: {len(present_list)}  |  "
            f"Absent: {len(absent_list)}  |  On Leave: {len(on_leave_list)}",
            sub_style,
        ),
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

    if on_leave_list:
        story.append(Paragraph("On Leave", section_style))
        story.append(Spacer(1, 6))
        story.append(build_table(on_leave_list, "On Leave", rl_colors.HexColor("#D97706")))
        story.append(Spacer(1, 18))

    story.append(Paragraph("Absent", section_style))
    story.append(Spacer(1, 6))
    story.append(build_table(absent_list, "Absent", rl_colors.HexColor("#DC2626")) if absent_list
                 else Paragraph("No employees absent.", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# ---------------------------------------------------------
# SECURITY NOTICE (shown until real Streamlit secrets are configured)
# ---------------------------------------------------------
if _USING_FALLBACK_SECRETS:
    st.warning(
        "⚠️ Running on fallback credentials embedded in code. Move these to "
        "Streamlit secrets and rotate them — see DEPLOYMENT_NOTES.md.",
        icon="⚠️",
    )

# ---------------------------------------------------------
# STAGE 1: LOGIN & OTP VERIFICATION
# ---------------------------------------------------------
if not st.session_state.verified_email:
    st.markdown("""
        <div class="app-brand-header">
            <div>
                <div class="app-title">PS DIGITAL</div>
                <div class="app-subtitle">ENTERPRISE ATTENDANCE PORTAL</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.write("### Sign In to Account")
    user_email = st.text_input("Enter Email Address", placeholder="name@company.com").strip().lower()

    if user_email and not st.session_state.otp_sent:
        cooldown_remaining = 0
        if st.session_state.otp_last_sent_time:
            elapsed = (datetime.now() - st.session_state.otp_last_sent_time).total_seconds()
            cooldown_remaining = max(0, int(OTP_COOLDOWN_SECONDS - elapsed))

        if cooldown_remaining > 0:
            st.info(f"⏳ Please wait {cooldown_remaining}s before requesting another code.")
        else:
            if st.button("Send Access Code", use_container_width=True, type="primary"):
                with st.spinner("Sending verification code..."):
                    otp = str(random.randint(100000, 999999))
                    sent = send_otp_email(user_email, otp)
                if sent:
                    st.session_state.generated_otp = otp
                    st.session_state.otp_sent = True
                    st.session_state.temp_email = user_email
                    st.session_state.otp_generated_time = datetime.now()
                    st.session_state.otp_last_sent_time = datetime.now()
                    st.success(f"Verification code sent to {user_email}")
                    st.rerun()

    if st.session_state.otp_sent:
        st.info(f"Enter the 6-digit verification code sent to {st.session_state.temp_email}")
        input_otp = st.text_input("Verification Code", max_chars=6, placeholder="123456")

        if st.button("Verify & Continue", use_container_width=True, type="primary"):
            expired = False
            if st.session_state.otp_generated_time:
                age = (datetime.now() - st.session_state.otp_generated_time).total_seconds()
                expired = age > OTP_EXPIRY_SECONDS

            if expired:
                st.error("This code has expired. Please request a new one.")
                st.session_state.otp_sent = False
                st.rerun()
            elif input_otp == st.session_state.generated_otp:
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

    with st.spinner("Loading your workspace..."):
        host_check = get_host_company_for_email(active_email)
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

        admin_nav = render_menu("admin", ["DASHBOARD", "DIRECTORY", "REMOVE COMP"])
        companies = cached_all_companies()
        employees = cached_all_employees_slim()

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
                        with st.spinner("Deleting company and all related data..."):
                            supabase.table("companies").delete().eq("company_name", comp_to_remove).execute()
                            supabase.table("employees").delete().eq("company_name", comp_to_remove).execute()
                            supabase.table("attendance").delete().eq("company_name", comp_to_remove).execute()
                            supabase.table("company_notices").delete().eq("company_name", comp_to_remove).execute()
                            try:
                                supabase.table("company_admins").delete().eq("company_name", comp_to_remove).execute()
                                supabase.table("leave_requests").delete().eq("company_name", comp_to_remove).execute()
                            except Exception:
                                pass
                        clear_admin_caches()
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
        brand_color = comp.get("brand_color") or "#818CF8"
        st.markdown(f"""
            <div class="app-brand-header">
                <div>
                    <div class="app-title" style="background: linear-gradient(90deg, {brand_color}, #F472B6 60%, #38BDF8); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">{c_name}</div>
                    <div class="app-subtitle">HOST WORKSPACE</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        host_nav = render_menu("host", ["HOME", "ATTENDANCE", "LEAVE", "LOCATION", "STAFF", "NOTICES", "SETTINGS"])

        if host_nav == "HOME":
            st.markdown(f"""
                <div class="hero-card">
                    <h3>Host Dashboard</h3>
                    <p>Welcome back, <b>{comp.get('host_name')}</b></p>
                </div>
            """, unsafe_allow_html=True)

            with st.spinner("Loading dashboard..."):
                emps = supabase.table("employees").select("*").eq("company_name", c_name).execute().data or []
                today_att = supabase.table("attendance").select("*").eq("company_name", c_name).eq("attendance_date", str(date.today())).execute().data or []
            m1, m2 = st.columns(2)
            m1.metric("Total Staff", len(emps))
            m2.metric("Present Today", len(today_att))

            st.markdown("##### 📈 30-Day Attendance Trend")
            trend_df = get_company_attendance_trend(c_name, days=30)
            st.line_chart(trend_df.set_index("Day"))

        elif host_nav == "ATTENDANCE":
            st.subheader("📊 Daily Attendance Summary")
            sel_date = st.date_input("Select Date", value=date.today())
            with st.spinner("Loading attendance..."):
                emps = supabase.table("employees").select("*").eq("company_name", c_name).execute().data or []
                att = supabase.table("attendance").select("*").eq("company_name", c_name).eq("attendance_date", str(sel_date)).execute().data or []
                try:
                    leave_recs = supabase.table("leave_requests").select("*").eq(
                        "company_name", c_name).eq("status", "Approved").lte(
                        "start_date", str(sel_date)).gte("end_date", str(sel_date)).execute().data or []
                except Exception:
                    leave_recs = []

            present_emails = {a.get("employee_email") for a in att}
            on_leave_emails = {l.get("employee_email") for l in leave_recs} - present_emails
            present_list = [e for e in emps if e.get("email") in present_emails]
            on_leave_list = [e for e in emps if e.get("email") in on_leave_emails]
            absent_list = [e for e in emps if e.get("email") not in present_emails and e.get("email") not in on_leave_emails]

            c_w, c_x, c_y, c_z = st.columns(4)
            c_w.metric("Staff", len(emps))
            c_x.metric("Present", len(present_list))
            c_y.metric("On Leave", len(on_leave_list))
            c_z.metric("Absent", len(absent_list))

            dl_col1, dl_col2 = st.columns(2)
            if att:
                df = pd.DataFrame(att)
                csv = df.to_csv(index=False).encode('utf-8')
                with dl_col1:
                    st.download_button("⬇️ CSV Report", csv, f"Attendance_{c_name}_{sel_date}.csv", "text/csv", use_container_width=True, key="host_csv_dl")
            with dl_col2:
                report_pdf = generate_attendance_report_pdf(c_name, str(sel_date), present_list, absent_list, on_leave_list)
                st.download_button("📄 PDF Report", report_pdf, f"Attendance_{c_name}_{sel_date}.pdf", "application/pdf", use_container_width=True, key="host_pdf_dl")

        elif host_nav == "LEAVE":
            st.subheader("🌴 Leave Requests")
            try:
                pending = supabase.table("leave_requests").select("*").eq("company_name", c_name).eq("status", "Pending").order("requested_at", desc=True).execute().data or []
                decided = supabase.table("leave_requests").select("*").eq("company_name", c_name).neq("status", "Pending").order("requested_at", desc=True).execute().data or []
            except Exception:
                st.info("Leave management isn't set up yet. Run the database migration (see DEPLOYMENT_NOTES.md) to enable this feature.")
                pending, decided = [], []

            if pending:
                st.write("#### Pending Requests")
                for req in pending:
                    with st.container():
                        st.markdown(f"""
                            <div class="hero-card">
                                <h3>{req.get('employee_name')}</h3>
                                <p>{req.get('start_date')} → {req.get('end_date')}</p>
                                <p>{req.get('reason') or 'No reason provided.'}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        ap_col, rj_col = st.columns(2)
                        with ap_col:
                            if st.button("✅ Approve", key=f"approve_leave_{req.get('id')}", use_container_width=True, type="primary"):
                                supabase.table("leave_requests").update({"status": "Approved"}).eq("id", req.get("id")).execute()
                                st.toast("Leave approved.")
                                st.rerun()
                        with rj_col:
                            if st.button("❌ Reject", key=f"reject_leave_{req.get('id')}", use_container_width=True):
                                supabase.table("leave_requests").update({"status": "Rejected"}).eq("id", req.get("id")).execute()
                                st.toast("Leave rejected.")
                                st.rerun()
            else:
                st.info("No pending leave requests.")

            if decided:
                st.write("#### Recent Decisions")
                st.dataframe(decided, use_container_width=True)

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
            with st.spinner("Loading staff..."):
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

            st.markdown("---")
            st.write("### 📥 Bulk Import Staff (CSV)")
            st.caption("CSV columns: name, email (required); department, position, phone (optional).")
            csv_file = st.file_uploader("Upload CSV", type=["csv"], key="bulk_staff_csv")
            if csv_file is not None:
                try:
                    import_df = pd.read_csv(csv_file)
                    st.dataframe(import_df.head(10), use_container_width=True)
                    if st.button("Import Employees", type="primary", use_container_width=True):
                        with st.spinner("Importing employees..."):
                            added, skipped, errors = bulk_import_employees(import_df, c_name)
                        st.success(f"Imported {added} employee(s). Skipped {skipped} (missing data or duplicate email).")
                        if errors:
                            st.warning("Some rows failed:\n" + "\n".join(errors[:10]))
                        st.rerun()
                except Exception as e:
                    st.error(f"Could not read CSV: {e}")

        elif host_nav == "NOTICES":
            st.subheader("📢 Post Announcement")
            msg = st.text_area("Notice Details")
            if st.button("Publish Announcement", type="primary", use_container_width=True):
                if msg.strip():
                    supabase.table("company_notices").insert({"company_name": c_name, "notice_text": msg.strip()}).execute()
                    st.toast("Notice published!")
                    st.rerun()
                else:
                    st.warning("Notice text cannot be empty.")

        elif host_nav == "SETTINGS":
            st.subheader("⚙️ Host Account Settings")
            st.write("### 👤 Edit Host Profile")
            with st.form("host_edit_profile"):
                h_name_edit = st.text_input("Host Name", value=comp.get("host_name", ""))
                h_phone_edit = st.text_input("Phone Number", value=comp.get("host_phone", ""))
                if st.form_submit_button("Save Changes", use_container_width=True):
                    with st.spinner("Saving..."):
                        supabase.table("companies").update({
                            "host_name": h_name_edit.strip(),
                            "host_phone": h_phone_edit.strip()
                        }).eq("host_email", active_email).execute()
                    st.toast("Profile updated!")
                    st.rerun()

            st.markdown("---")
            st.write("### 🎨 Branding")
            new_color = st.color_picker("Accent Color", value=comp.get("brand_color") or "#818CF8")
            if st.button("Save Brand Color", use_container_width=True):
                try:
                    supabase.table("companies").update({"brand_color": new_color}).eq("company_name", c_name).execute()
                    st.toast("Brand color updated!")
                    st.rerun()
                except Exception:
                    st.error("Branding isn't set up yet. Run the database migration (see DEPLOYMENT_NOTES.md).")

            st.markdown("---")
            st.write("### ⏰ Attendance Policy")
            try:
                default_shift = dtime(9, 0)
                if comp.get("shift_start_time"):
                    hh, mm = [int(x) for x in str(comp["shift_start_time"]).split(":")[:2]]
                    default_shift = dtime(hh, mm)
            except Exception:
                default_shift = dtime(9, 0)
            shift_time = st.time_input("Shift Start Time", value=default_shift)
            grace_minutes = st.number_input("Late Grace Period (minutes)", min_value=0, max_value=120,
                                             value=int(comp.get("late_grace_minutes") or 15))
            if st.button("Save Attendance Policy", use_container_width=True):
                try:
                    supabase.table("companies").update({
                        "shift_start_time": shift_time.strftime("%H:%M"),
                        "late_grace_minutes": grace_minutes,
                    }).eq("company_name", c_name).execute()
                    st.toast("Attendance policy saved!")
                    st.rerun()
                except Exception:
                    st.error("Attendance policy fields aren't set up yet. Run the database migration (see DEPLOYMENT_NOTES.md).")

            st.markdown("---")
            st.write("### 👥 Team Admins")
            st.caption("Anyone added here can also manage this company (in addition to the primary host email).")
            admins = get_company_admins(c_name)
            if admins:
                for a in admins:
                    a_col1, a_col2 = st.columns([4, 1])
                    a_col1.write(a.get("email"))
                    if a_col2.button("Remove", key=f"remove_admin_{a.get('id', a.get('email'))}"):
                        try:
                            supabase.table("company_admins").delete().eq("company_name", c_name).eq("email", a.get("email")).execute()
                            st.rerun()
                        except Exception:
                            st.error("Could not remove admin.")
            else:
                st.caption("No additional admins yet.")
            new_admin_email = st.text_input("Add admin by email", key="new_admin_email").strip().lower()
            if st.button("Add Admin", use_container_width=True):
                if new_admin_email:
                    try:
                        supabase.table("company_admins").insert({"company_name": c_name, "email": new_admin_email}).execute()
                        st.toast("Admin added!")
                        st.rerun()
                    except Exception:
                        st.error("Multi-admin isn't set up yet. Run the database migration (see DEPLOYMENT_NOTES.md).")

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

        try:
            comp_info_all = supabase.table("companies").select("*").eq("company_name", c_name).execute().data
        except Exception:
            comp_info_all = []
        comp_record = comp_info_all[0] if comp_info_all else {}
        brand_color = comp_record.get("brand_color") or "#818CF8"

        st.markdown(f"""
            <div class="app-brand-header">
                <div>
                    <div class="app-title" style="background: linear-gradient(90deg, {brand_color}, #F472B6 60%, #38BDF8); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;">{c_name}</div>
                    <div class="app-subtitle">MEMBER PORTAL</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        emp_nav = render_menu("emp", ["ATTEND", "GEOFENCE", "LEAVE", "NOTICES", "PROFILE"])

        try:
            notices = supabase.table("company_notices").select("*").eq("company_name", c_name).order("created_at", desc=True).execute().data or []
        except Exception:
            notices = []

        comp_lat = comp_record.get("latitude")
        comp_lng = comp_record.get("longitude")
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
                status_label = record.get("status", "Present")
                if status_label == "Late":
                    st.warning(f"🕒 Marked **Late** for Today ({cur_date_str})")
                else:
                    st.success(f"✅ Marked Present for Today ({cur_date_str})")

                rec_lat, rec_lng = record.get("latitude"), record.get("longitude")
                rec_dist = None
                if rec_lat is not None and rec_lng is not None and comp_lat and comp_lng:
                    rec_dist = geodesic((rec_lat, rec_lng), (comp_lat, comp_lng)).meters

                with st.spinner("Preparing your receipt..."):
                    pdf_bytes = generate_attendance_receipt_pdf(
                        company_name=c_name, employee_name=emp.get("name"), employee_id=emp.get("employee_no"),
                        department=emp.get("department"), position=emp.get("position"),
                        att_date=cur_date_str, status=status_label,
                        lat=rec_lat, lng=rec_lng, distance=rec_dist,
                        marked_at=record.get("marked_time") or st.session_state.get("last_attendance_time"),
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

                    def _mark_attendance(dist_val=None):
                        marked_time_str = datetime.now().strftime("%H:%M:%S")
                        status_val = compute_attendance_status(comp_record, marked_time_str)
                        payload = {
                            "company_name": c_name, "employee_email": active_email,
                            "employee_name": emp.get("name"), "attendance_date": cur_date_str,
                            "status": status_val, "latitude": user_lat, "longitude": user_lng,
                            "marked_time": marked_time_str,
                        }
                        with st.spinner("Marking attendance..."):
                            ok = safe_insert_attendance(payload)
                        if ok:
                            st.session_state.emp_coords = False
                            st.session_state.last_attendance_time = marked_time_str
                            st.success("Attendance marked!" if status_val == "Present" else "Attendance marked — you're a bit late today.")
                            st.rerun()

                    if comp_lat and comp_lng:
                        dist = geodesic((user_lat, user_lng), (comp_lat, comp_lng)).meters
                        st.write(f"Distance to Office: **{round(dist, 1)} meters**")

                        if dist <= 100:
                            if st.button("✋ Submit Attendance", type="primary", use_container_width=True, key="submit_att_geo"):
                                _mark_attendance(dist)
                        else:
                            st.error("❌ Too far from office premises (Must be within 100m).")
                    else:
                        if st.button("✋ Submit Attendance", type="primary", use_container_width=True, key="submit_att_nogeo"):
                            _mark_attendance()

            st.markdown("---")
            st.markdown("##### 📈 Your Last 30 Days")
            trend_df, present_count = get_employee_attendance_trend(c_name, active_email, days=30)
            tcol1, tcol2 = st.columns(2)
            tcol1.metric("Days Present (30d)", present_count)
            tcol2.metric("Attendance Rate", f"{round(present_count / 30 * 100)}%")
            st.bar_chart(trend_df.set_index("Day"))

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

        elif emp_nav == "LEAVE":
            st.subheader("🌴 Request Time Off")
            with st.form("leave_request_form"):
                lc1, lc2 = st.columns(2)
                start_d = lc1.date_input("Start Date", value=date.today())
                end_d = lc2.date_input("End Date", value=date.today())
                reason = st.text_area("Reason (optional)")
                if st.form_submit_button("Submit Request", use_container_width=True):
                    if end_d < start_d:
                        st.error("End date cannot be before start date.")
                    else:
                        try:
                            supabase.table("leave_requests").insert({
                                "company_name": c_name, "employee_email": active_email,
                                "employee_name": emp.get("name"), "start_date": str(start_d),
                                "end_date": str(end_d), "reason": reason.strip(), "status": "Pending",
                            }).execute()
                            st.toast("Leave request submitted!")
                            st.rerun()
                        except Exception:
                            st.error("Leave requests aren't set up yet. Ask your admin to run the database migration (see DEPLOYMENT_NOTES.md).")

            st.markdown("---")
            st.write("### Your Requests")
            try:
                my_requests = supabase.table("leave_requests").select("*").eq("employee_email", active_email).order("requested_at", desc=True).execute().data or []
            except Exception:
                my_requests = []
            if my_requests:
                for req in my_requests:
                    badge_class = {"Pending": "badge-warning", "Approved": "badge-success", "Rejected": "badge-danger"}.get(req.get("status"), "badge-warning")
                    st.markdown(
                        f"<div class='hero-card'><p>{req.get('start_date')} → {req.get('end_date')}</p>"
                        f"<span class='{badge_class}'>{req.get('status')}</span></div>",
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No leave requests yet.")

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
                        with st.spinner("Saving..."):
                            supabase.table("employees").update({
                                "name": new_name.strip(),
                                "department": new_dept.strip(),
                                "position": new_pos.strip(),
                                "phone": new_phone.strip()
                            }).eq("email", active_email).execute()
                        st.toast("Profile details updated!")
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
                    <div class="app-title">PS DIGITAL</div>
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
                        with st.spinner("Creating your company profile..."):
                            supabase.table("companies").insert({
                                "company_name": new_c_name, "host_name": h_name,
                                "host_email": active_email, "host_phone": h_phone
                            }).execute()
                            try:
                                supabase.table("company_admins").insert({"company_name": new_c_name, "email": active_email}).execute()
                            except Exception:
                                pass
                        clear_admin_caches()
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
                        with st.spinner("Saving your profile..."):
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
