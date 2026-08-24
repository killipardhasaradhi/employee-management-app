import streamlit as st
from supabase import create_client

# Supabase Database Connection
SUPABASE_URL = "https://tqxbeudrvkinuujojasx.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxeGJldWRydmtpbnV1am9qYXN4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc1NDQ5NzcsImV4cCI6MjEwMzEyMDk3N30.UC0UDV-vTsSnw8Ff2Jrp9DAfhhhpIkz1iY5eDtimU78"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="PS DIGITAL", page_icon="📱")

st.title("📱 PS DIGITAL")
st.caption("EMPLOYEE MANAGEMENT SYSTEM")

# Sidebar navigation
role = st.sidebar.radio("Select Portal Role", ["Employee Portal", "Admin Dashboard (Host)"])

if role == "Admin Dashboard (Host)":
    st.header("👑 Admin Dashboard")
    search_query = st.text_input("Search by Name or Employee No")
    
    # Fetch all data from database
    response = supabase.table("employees").select("*").execute()
    data = response.data

    if data:
        if search_query:
            # Filter results by search keyword
            filtered = [
                emp for emp in data 
                if search_query.lower() in emp.get("name", "").lower() 
                or search_query.lower() in emp.get("employee_no", "").lower()
            ]
            st.metric("Total Records Found", len(filtered))
            st.dataframe(filtered)
        else:
            st.metric("Total Employees", len(data))
            st.dataframe(data)
    else:
        st.info("No employee records found in the database.")

elif role == "Employee Portal":
    st.header("👤 Employee Profile View")
    user_email = st.text_input("Enter your registered Email Address").strip().lower()

    if user_email:
        # Check if employee exists
        response = supabase.table("employees").select("*").eq("email", user_email).execute()
        records = response.data

        if records:
            emp = records[0]
            st.success(f"Welcome back, {emp.get('name')}!")
            
            with st.form("edit_employee_form"):
                st.subheader("Edit Your Details")
                emp_no = st.text_input("Employee Number", value=emp.get("employee_no") or "", disabled=True)
                name = st.text_input("Full Name", value=emp.get("name") or "")
                dept = st.text_input("Department", value=emp.get("department") or "")
                pos = st.text_input("Position", value=emp.get("position") or "")
                phone = st.text_input("Phone Number", value=emp.get("phone") or "")
                salary = st.text_input("Salary", value=emp.get("salary") or "")

                submit_update = st.form_submit_button("Update My Details")
                
                if submit_update:
                    supabase.table("employees").update({
                        "name": name,
                        "department": dept,
                        "position": pos,
                        "phone": phone,
                        "salary": salary
                    }).eq("email", user_email).execute()
                    st.success("Your details were updated successfully!")
        else:
            st.warning("No profile found for this email. Register below:")
            with st.form("new_employee_form"):
                st.subheader("Add New Profile")
                emp_no = st.text_input("Employee Number *")
                name = st.text_input("Full Name *")
                dept = st.text_input("Department")
                pos = st.text_input("Position")
                phone = st.text_input("Phone Number")
                salary = st.text_input("Salary")

                submit_new = st.form_submit_button("Save Profile")

                if submit_new:
                    if not emp_no or not name:
                        st.error("Employee Number and Full Name are required!")
                    else:
                        try:
                            supabase.table("employees").insert({
                                "employee_no": emp_no,
                                "name": name,
                                "department": dept,
                                "position": pos,
                                "phone": phone,
                                "email": user_email,
                                "salary": salary
                            }).execute()
                            st.success("Profile saved successfully!")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error("Error saving profile. Check if Employee Number already exists.")
