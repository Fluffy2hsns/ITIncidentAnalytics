import streamlit as st
import pandas as pd
from database import queries as q
from utils import formatting as fmt

def app():
    st.title("🎫 Incidents")
    st.markdown("### All Incidents")

    # Фильтры
    with st.expander("Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            search = st.text_input("Search", placeholder="Title or description")
        with col2:
            priority = st.selectbox("Priority", ["All", "Low", "Medium", "High", "Critical"], index=0)
        with col3:
            status = st.selectbox("Status", ["All", "New", "Assigned", "In Progress", "Resolved", "Closed"], index=0)

        col4, col5, col6 = st.columns(3)
        with col4:
            categories = q.execute_query("SELECT category_id, category_name FROM IncidentCategories ORDER BY category_name")
            cat_options = ["All"] + list(categories["category_name"])
            cat_name = st.selectbox("Category", cat_options)
            category_id = None
            if cat_name != "All":
                category_id = categories[categories["category_name"] == cat_name]["category_id"].iloc[0]
        with col5:
            systems = q.execute_query("SELECT system_id, system_name FROM Systems ORDER BY system_name")
            sys_options = ["All"] + list(systems["system_name"])
            sys_name = st.selectbox("System", sys_options)
            system_id = None
            if sys_name != "All":
                system_id = systems[systems["system_name"] == sys_name]["system_id"].iloc[0]
        with col6:
            departments = q.execute_query("SELECT department_id, department_name FROM Departments ORDER BY department_name")
            dep_options = ["All"] + list(departments["department_name"])
            dep_name = st.selectbox("Department", dep_options)
            department_id = None
            if dep_name != "All":
                department_id = departments[departments["department_name"] == dep_name]["department_id"].iloc[0]

    filters = {
        'search': search,
        'priority': None if priority == "All" else priority,
        'status': None if status == "All" else status,
        'category_id': category_id,
        'system_id': system_id,
        'department_id': department_id,
    }

    df = q.get_all_incidents(filters)

    if df.empty:
        st.info("No incidents found.")
        return

    # Таблица
    st.dataframe(
        df,
        column_config={
            "incident_id": "ID",
            "title": "Title",
            "category_name": "Category",
            "system_name": "System",
            "priority": "Priority",
            "status": "Status",
            "assigned_employee": "Assigned Employee",
            "created_at": "Created",
            "resolved_at": "Resolved",
            "sla_hours": "SLA (h)"
        },
        hide_index=True,
        use_container_width=True
    )

    # Выбор инцидента для деталей
    st.markdown("---")
    st.subheader("Incident Details")
    incident_id = st.number_input("Enter Incident ID", min_value=1, step=1)
    if st.button("Show Details"):
        details = q.get_incident_details(incident_id)
        if details:
            st.markdown(f"### Incident #{details['incident_id']}")
            st.write(f"**Title:** {details['title']}")
            st.write(f"**Description:** {details.get('description', 'No description')}")
            st.write(f"**Category:** {details['category']}")
            st.write(f"**System:** {details['system']}")
            st.write(f"**Priority:** {details['priority']}")
            st.write(f"**Assigned:** {details['employee']}")
            st.write(f"**Department:** {details['department']}")
            st.write(f"**Status:** {details['status']}")
            st.write(f"**Created:** {details['created_at']}")
            st.write(f"**First Response:** {details.get('first_response_at', 'N/A')}")
            st.write(f"**Resolved:** {details.get('resolved_at', 'N/A')}")
            st.write(f"**SLA Hours:** {details['sla_hours']}")

            # История
            st.markdown("#### History")
            history = q.get_incident_history(incident_id)
            if not history.empty:
                for _, row in history.iterrows():
                    st.text(f"{row['changed_at']} | {row['old_status']} → {row['new_status']} | by {row['changed_by']} | {row.get('comment','')}")
            else:
                st.info("No history found.")

            # Изменение статуса
            st.markdown("#### Change Status")
            new_status = st.selectbox("New Status", ["New", "Assigned", "In Progress", "Resolved", "Closed"])
            comment = st.text_input("Comment", "")
            # changed_by: предположим, выбираем текущего пользователя (здесь заглушка)
            employees = q.execute_query("SELECT employee_id, full_name FROM Employees WHERE is_active=1 ORDER BY full_name")
            emp_options = {row['full_name']: row['employee_id'] for _, row in employees.iterrows()}
            changed_by_name = st.selectbox("Changed by", list(emp_options.keys()))
            changed_by = emp_options[changed_by_name]
            if st.button("Update Status"):
                try:
                    q.update_incident_status(incident_id, new_status, changed_by, comment)
                    st.success("Status updated and history recorded.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error updating status: {e}")
        else:
            st.warning("Incident not found.")