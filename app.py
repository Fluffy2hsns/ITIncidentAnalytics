import streamlit as st
from streamlit_option_menu import option_menu
# import pages.dashboard as dashboard
# import pages.incidents as incidents
# import pages.add_incident as add_incident
# import pages.employees as employees
# import pages.analytics as analytics
import app_pages.dashboard as dashboard
import app_pages.incidents as incidents
import app_pages.add_incident as add_incident
import app_pages.employees as employees
import app_pages.analytics as analytics



st.set_page_config(
    page_title="IT Incident Management & Analytics",
    page_icon="🖥️",
    layout="wide"
)

# Инициализация session_state для навигации, если нужно
if 'page' not in st.session_state:
    st.session_state.page = 'dashboard'

def main():
    with st.sidebar:
        selected = option_menu(
            menu_title="Navigation",
            options=["Dashboard", "Incidents", "Add Incident", "Employees", "Analytics"],
            icons=["bar-chart-line", "ticket", "plus-circle", "people", "graph-up"],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "5px"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px"},
                "nav-link-selected": {"background-color": "#1f4e79"},
            }
        )
    if selected == "Dashboard":
        dashboard.app()
    elif selected == "Incidents":
        incidents.app()
    elif selected == "Add Incident":
        add_incident.app()
    elif selected == "Employees":
        employees.app()
    elif selected == "Analytics":
        analytics.app()

if __name__ == "__main__":
    main()