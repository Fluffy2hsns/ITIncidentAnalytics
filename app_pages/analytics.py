import streamlit as st
import pandas as pd
import plotly.express as px
from database import queries as q
from utils import calculations as calc

def app():
    st.title("📈 Analytics")
    st.markdown("### Advanced Incident Analytics")

    # Период
    col1, col2 = st.columns(2)
    with col1:
        date_from = st.date_input("From", value=pd.to_datetime('2025-01-01'))
    with col2:
        date_to = st.date_input("To", value=pd.to_datetime('today'))

    filters = {'date_from': date_from, 'date_to': date_to + pd.Timedelta(days=1)}

    # Динамика инцидентов
    st.subheader("Incidents Over Time")
    df = q.get_incidents_by_month(filters)
    if not df.empty:
        df['date'] = pd.to_datetime(df['year'].astype(str) + '-' + df['month'].astype(str) + '-01')
        fig = px.line(df, x='date', y='count', markers=True)
        st.plotly_chart(fig, use_container_width=True)

    # Распределение приоритетов
    st.subheader("Priority Distribution")
    df = q.get_incidents_by_priority(filters)
    if not df.empty:
        fig = px.pie(df, names='priority', values='count', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    # Категории
    st.subheader("Incidents by Category")
    df = q.get_incidents_by_category(filters)
    if not df.empty:
        fig = px.bar(df, x='category_name', y='count')
        st.plotly_chart(fig, use_container_width=True)

    # Проблемные системы
    st.subheader("Top 10 Problematic Systems")
    df = q.get_top_problematic_systems(filters, top_n=10)
    if not df.empty:
        fig = px.bar(df, x='system_name', y='incident_count')
        st.plotly_chart(fig, use_container_width=True)

    # Производительность сотрудников
    st.subheader("Employee Performance")
    emp_perf = q.execute_query("""
        SELECT e.full_name,
               COUNT(i.incident_id) AS total_incidents,
               AVG(DATEDIFF(MINUTE, i.created_at, i.resolved_at))/60.0 AS avg_resolution_hours,
               SUM(CASE WHEN v.sla_status = 'Breached' THEN 1 ELSE 0 END) AS sla_breaches
        FROM Incidents i
        JOIN Employees e ON i.assigned_employee_id = e.employee_id
        LEFT JOIN View_SLAStatus v ON i.incident_id = v.incident_id
        WHERE i.created_at BETWEEN ? AND ?
        GROUP BY e.full_name
        ORDER BY total_incidents DESC
    """, params=[date_from, date_to])
    if not emp_perf.empty:
        st.dataframe(emp_perf, hide_index=True)

    # Среднее время решения по категориям
    st.subheader("Average Resolution Time by Category")
    avg_cat = q.execute_query("""
        SELECT c.category_name, AVG(DATEDIFF(MINUTE, i.created_at, i.resolved_at))/60.0 AS avg_hours
        FROM Incidents i
        JOIN IncidentCategories c ON i.category_id = c.category_id
        WHERE i.resolved_at IS NOT NULL AND i.created_at BETWEEN ? AND ?
        GROUP BY c.category_name
        ORDER BY avg_hours DESC
    """, params=[date_from, date_to])
    if not avg_cat.empty:
        fig = px.bar(avg_cat, x='category_name', y='avg_hours')
        st.plotly_chart(fig, use_container_width=True)

    # SLA Compliance по отделам
    st.subheader("SLA Compliance by Department")
    sla_dep = q.execute_query("""
        SELECT d.department_name,
               ROUND(100.0 * SUM(CASE WHEN v.sla_status = 'Met' THEN 1 ELSE 0 END) / 
                     NULLIF(SUM(CASE WHEN v.sla_status IN ('Met','Breached') THEN 1 ELSE 0 END), 0), 2) AS compliance_percent
        FROM Incidents i
        JOIN Employees e ON i.assigned_employee_id = e.employee_id
        JOIN Departments d ON e.department_id = d.department_id
        LEFT JOIN View_SLAStatus v ON i.incident_id = v.incident_id
        WHERE i.created_at BETWEEN ? AND ?
        GROUP BY d.department_name
    """, params=[date_from, date_to])
    if not sla_dep.empty:
        fig = px.bar(sla_dep, x='department_name', y='compliance_percent', range_y=[0,100])
        st.plotly_chart(fig, use_container_width=True)