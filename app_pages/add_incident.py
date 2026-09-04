import streamlit as st
from database import queries as q
from datetime import datetime

def app():
    st.title("➕ Add Incident")
    st.markdown("### Create New Incident")

    with st.form("incident_form"):
        title = st.text_input("Title*", max_chars=200)
        description = st.text_area("Description", height=150)
        col1, col2 = st.columns(2)
        with col1:
            categories = q.execute_query("SELECT category_id, category_name FROM IncidentCategories ORDER BY category_name")
            category_name = st.selectbox("Category*", categories["category_name"])
            category_id = categories[categories["category_name"] == category_name]["category_id"].iloc[0]
        with col2:
            systems = q.execute_query("SELECT system_id, system_name FROM Systems WHERE is_active=1 ORDER BY system_name")
            system_name = st.selectbox("System*", systems["system_name"])
            system_id = systems[systems["system_name"] == system_name]["system_id"].iloc[0]

        col3, col4 = st.columns(2)
        with col3:
            priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"], index=2)
        with col4:
            sla_hours = st.number_input("SLA Hours", min_value=1, max_value=72, value=8)

        employees = q.execute_query("SELECT employee_id, full_name FROM Employees WHERE is_active=1 ORDER BY full_name")
        employee_name = st.selectbox("Assigned Employee*", employees["full_name"])
        assigned_employee_id = employees[employees["full_name"] == employee_name]["employee_id"].iloc[0]

        submit = st.form_submit_button("Create Incident")

    if submit:
        if not title:
            st.error("Title is required.")
        elif not category_id or not system_id or not assigned_employee_id:
            st.error("Please fill all required fields.")
        else:
            try:
                incident_id = q.create_incident(
                    title=title,
                    description=description,
                    category_id=category_id,
                    system_id=system_id,
                    assigned_employee_id=assigned_employee_id,
                    priority=priority,
                    sla_hours=sla_hours
                )
                st.success(f"Incident #{incident_id} created successfully.")
                st.balloons()
            except Exception as e:
                st.error(f"Error creating incident: {e}")