import streamlit as st
import pandas as pd
import plotly.express as px
from database import queries as q
from utils import calculations as calc
from utils import formatting as fmt
from datetime import date, timedelta

def app():
    st.title("📊 Dashboard")
    st.markdown("### IT Incident Management & Analytics")

    # Фильтры
    with st.expander("Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            date_from = st.date_input("From", value=date.today() - timedelta(days=365))
        with col2:
            date_to = st.date_input("To", value=date.today())
        with col3:
            priority = st.selectbox("Priority", ["All", "Low", "Medium", "High", "Critical"], index=0)

        col4, col5, col6 = st.columns(3)
        with col4:
            status = st.selectbox("Status", ["All", "New", "Assigned", "In Progress", "Resolved", "Closed"], index=0)
        with col5:
            categories = q.execute_query("SELECT category_id, category_name FROM IncidentCategories ORDER BY category_name")
            cat_options = ["All"] + list(categories["category_name"])
            cat_name = st.selectbox("Category", cat_options)
            category_id = None
            if cat_name != "All":
                category_id = int(categories[categories["category_name"] == cat_name]["category_id"].iloc[0])
        with col6:
            systems = q.execute_query("SELECT system_id, system_name FROM Systems ORDER BY system_name")
            sys_options = ["All"] + list(systems["system_name"])
            sys_name = st.selectbox("System", sys_options)
            system_id = None
            if sys_name != "All":
                system_id = int(systems[systems["system_name"] == sys_name]["system_id"].iloc[0])

        col7, col8 = st.columns(2)
        with col7:
            departments = q.execute_query("SELECT department_id, department_name FROM Departments ORDER BY department_name")
            dep_options = ["All"] + list(departments["department_name"])
            dep_name = st.selectbox("Department", dep_options)
            department_id = None
            if dep_name != "All":
                department_id = int(departments[departments["department_name"] == dep_name]["department_id"].iloc[0])

    filters = {
        'date_from': date_from,
        'date_to': date_to + timedelta(days=1),  # включительно
        'priority': None if priority == "All" else priority,
        'status': None if status == "All" else status,
        'category_id': category_id,
        'system_id': system_id,
        'department_id': department_id,
    }

    # KPI
    total = q.get_kpi_total_incidents(filters)
    open_inc = q.get_kpi_open_incidents(filters)
    critical = q.get_kpi_critical_incidents(filters)
    sla_compliance = q.get_kpi_sla_compliance(filters)
    avg_res = q.get_kpi_avg_resolution_time(filters)

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Incidents", total)
    col2.metric("Open Incidents", open_inc)
    col3.metric("Critical Incidents", critical)
    col4.metric("SLA Compliance", f"{sla_compliance:.1f}%")
    col5.metric("Avg Resolution", calc.format_hours(avg_res))

    st.markdown("---")

    # Графики
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Incidents by Month")
        df = q.get_incidents_by_month(filters)
        if not df.empty:
            df['date'] = pd.to_datetime(df['year'].astype(str) + '-' + df['month'].astype(str) + '-01')
            fig = px.line(df, x='date', y='count', markers=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data for selected filters")

    with col2:
        st.subheader("Incidents by Priority")
        df = q.get_incidents_by_priority(filters)
        if not df.empty:
            fig = px.pie(df, names='priority', values='count', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Incidents by Category")
        df = q.get_incidents_by_category(filters)
        if not df.empty:
            fig = px.bar(df, x='category_name', y='count', orientation='v')
            st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("Incidents by Status")
        df = q.get_incidents_by_status(filters)
        if not df.empty:
            fig = px.pie(df, names='status', values='count', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

    col5, col6 = st.columns(2)
    with col5:
        st.subheader("Top 5 Problematic Systems")
        df = q.get_top_problematic_systems(filters)
        if not df.empty:
            fig = px.bar(df, x='system_name', y='incident_count', orientation='v')
            st.plotly_chart(fig, use_container_width=True)

    with col6:
        st.subheader("Incidents by Department")
        df = q.get_incidents_by_department(filters)
        if not df.empty:
            fig = px.bar(df, x='department_name', y='count', orientation='v')
            st.plotly_chart(fig, use_container_width=True)