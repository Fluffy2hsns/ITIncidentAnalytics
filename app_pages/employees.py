import streamlit as st
from database import queries as q
from utils import calculations as calc
import pandas as pd

def app():
    st.title("👥 Employees")
    st.markdown("### Employee Directory and Performance")

    employees_df = q.execute_query("""
        SELECT e.employee_id, e.full_name, e.position, d.department_name, e.email, e.is_active
        FROM Employees e
        LEFT JOIN Departments d ON e.department_id = d.department_id
        ORDER BY e.full_name
    """)

    st.dataframe(employees_df, hide_index=True)

    st.markdown("---")
    st.subheader("Employee Performance")
    emp_id = st.number_input("Enter Employee ID", min_value=1, step=1, key="emp_perf_id")
    if st.button("Show Performance"):
        emp_id = int(emp_id)

        emp_info = q.execute_query("""
            SELECT e.full_name, e.position, d.department_name
            FROM Employees e
            LEFT JOIN Departments d ON e.department_id = d.department_id
            WHERE e.employee_id = ?
        """, params=[emp_id])

        if emp_info.empty:
            st.warning("Employee not found.")
        else:
            emp = emp_info.iloc[0]
            st.markdown(f"### {emp['full_name']}")
            st.write(f"**Position:** {emp['position']}")
            st.write(f"**Department:** {emp['department_name']}")

            # Метрики
            total_inc = q.execute_query(
                "SELECT COUNT(*) AS total FROM Incidents WHERE assigned_employee_id = ?",
                params=[emp_id]
            )['total'].iloc[0]

            resolved_inc = q.execute_query(
                "SELECT COUNT(*) AS total FROM Incidents WHERE assigned_employee_id = ? AND resolved_at IS NOT NULL",
                params=[emp_id]
            )['total'].iloc[0]

            avg_res = q.execute_query("""
                SELECT AVG(DATEDIFF(MINUTE, created_at, resolved_at))/60.0 AS avg_hours
                FROM Incidents WHERE assigned_employee_id = ? AND resolved_at IS NOT NULL
            """, params=[emp_id])['avg_hours'].iloc[0]

            sla_breach = q.execute_query("""
                SELECT COUNT(*) AS total FROM View_SLAStatus v
                JOIN Incidents i ON v.incident_id = i.incident_id
                WHERE i.assigned_employee_id = ? AND v.sla_status = 'Breached'
            """, params=[emp_id])['total'].iloc[0]

            critical = q.execute_query(
                "SELECT COUNT(*) AS total FROM Incidents WHERE assigned_employee_id = ? AND priority = 'Critical'",
                params=[emp_id]
            )['total'].iloc[0]

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Total Incidents", total_inc)
            col2.metric("Resolved", resolved_inc)
            col3.metric("Avg Resolution", calc.format_hours(avg_res))
            col4.metric("SLA Breaches", sla_breach)
            col5.metric("Critical Incidents", critical)