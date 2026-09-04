# IT Incident Management & Analytics System

## Project Overview
Система для регистрации, управления, мониторинга и анализа IT-инцидентов. Внутренний инструмент IT-отдела, позволяющий отслеживать инциденты, назначать ответственных, контролировать SLA и строить аналитические отчёты.

## Features
- 📊 **Dashboard** с ключевыми метриками и графиками
- 🎫 **Просмотр и фильтрация инцидентов** с детальной информацией и историей
- ➕ **Создание новых инцидентов**
- 👥 **Справочник сотрудников** с персональной статистикой
- 📈 **Расширенная аналитика** (динамика, SLA, производительность)
- 🔄 Автоматический расчёт SLA и времени решения
- 💾 Хранение всех данных в SQL Server, полная история изменений

## Technology Stack
- **Backend**: Python 3.x
- **Web Framework**: Streamlit
- **Database**: Microsoft SQL Server
- **T-SQL** для создания схемы и запросов
- **Data manipulation**: pandas
- **Visualization**: Plotly
- **DB Connection**: pyodbc
- **Environment**: python-dotenv

## Database Structure
База данных `ITIncidentAnalytics` содержит 6 таблиц:
- `Departments` – отделы
- `Employees` – сотрудники
- `Systems` – IT-системы
- `IncidentCategories` – категории инцидентов
- `Incidents` – основные записи об инцидентах
- `IncidentHistory` – история изменения статусов

## ER Diagram
![ER Diagram](docs/er_diagram.md)

## Installation

### 1. Клонирование репозитория
```bash
git clone https://github.com/yourusername/ITIncidentAnalytics.git
cd ITIncidentAnalytics
