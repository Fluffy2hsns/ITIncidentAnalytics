import pandas as pd
from database.connection import get_connection

def execute_query(query, params=None):
    """Выполняет SQL-запрос и возвращает pandas DataFrame."""
    conn = get_connection()
    try:
        if params:
            df = pd.read_sql(query, conn, params=params)
        else:
            df = pd.read_sql(query, conn)
        return df
    finally:
        conn.close()

# --- Общие KPI ---
def get_kpi_total_incidents(filters=None):
    # filters: dict with optional keys: date_from, date_to, priority, status, category_id, system_id, department_id
    conditions = []
    params = []
    if filters:
        if filters.get('date_from'):
            conditions.append("i.created_at >= ?")
            params.append(filters['date_from'])
        if filters.get('date_to'):
            conditions.append("i.created_at <= ?")
            params.append(filters['date_to'])
        if filters.get('priority'):
            conditions.append("i.priority = ?")
            params.append(filters['priority'])
        if filters.get('status'):
            conditions.append("i.status = ?")
            params.append(filters['status'])
        if filters.get('category_id'):
            conditions.append("i.category_id = ?")
            params.append(filters['category_id'])
        if filters.get('system_id'):
            conditions.append("i.system_id = ?")
            params.append(filters['system_id'])
        if filters.get('department_id'):
            conditions.append("e.department_id = ?")
            params.append(filters['department_id'])
    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"""
        SELECT COUNT(*) AS total_incidents
        FROM Incidents i
        LEFT JOIN Employees e ON i.assigned_employee_id = e.employee_id
        {where}
    """
    df = execute_query(query, params)
    return df.iloc[0,0]

def get_kpi_open_incidents(filters=None):
    conditions = []
    params = []
    if filters:
        if filters.get('date_from'):
            conditions.append("i.created_at >= ?")
            params.append(filters['date_from'])
        if filters.get('date_to'):
            conditions.append("i.created_at <= ?")
            params.append(filters['date_to'])
        if filters.get('priority'):
            conditions.append("i.priority = ?")
            params.append(filters['priority'])
        if filters.get('category_id'):
            conditions.append("i.category_id = ?")
            params.append(filters['category_id'])
        if filters.get('system_id'):
            conditions.append("i.system_id = ?")
            params.append(filters['system_id'])
        if filters.get('department_id'):
            conditions.append("e.department_id = ?")
            params.append(filters['department_id'])
    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    # Open = status <> 'Closed'
    if where:
        where += " AND i.status <> 'Closed'"
    else:
        where = "WHERE i.status <> 'Closed'"
    query = f"""
        SELECT COUNT(*) AS open_incidents
        FROM Incidents i
        LEFT JOIN Employees e ON i.assigned_employee_id = e.employee_id
        {where}
    """
    df = execute_query(query, params)
    return df.iloc[0,0]

def get_kpi_critical_incidents(filters=None):
    conditions = []
    params = []
    if filters:
        if filters.get('date_from'):
            conditions.append("i.created_at >= ?")
            params.append(filters['date_from'])
        if filters.get('date_to'):
            conditions.append("i.created_at <= ?")
            params.append(filters['date_to'])
        if filters.get('status'):
            conditions.append("i.status = ?")
            params.append(filters['status'])
        if filters.get('category_id'):
            conditions.append("i.category_id = ?")
            params.append(filters['category_id'])
        if filters.get('system_id'):
            conditions.append("i.system_id = ?")
            params.append(filters['system_id'])
        if filters.get('department_id'):
            conditions.append("e.department_id = ?")
            params.append(filters['department_id'])
    conditions.append("i.priority = 'Critical'")
    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"""
        SELECT COUNT(*) AS critical_incidents
        FROM Incidents i
        LEFT JOIN Employees e ON i.assigned_employee_id = e.employee_id
        {where}
    """
    df = execute_query(query, params)
    return df.iloc[0,0]

def get_kpi_sla_compliance(filters=None):
    conditions = []
    params = []
    if filters:
        if filters.get('date_from'):
            conditions.append("i.created_at >= ?")
            params.append(filters['date_from'])
        if filters.get('date_to'):
            conditions.append("i.created_at <= ?")
            params.append(filters['date_to'])
        if filters.get('priority'):
            conditions.append("i.priority = ?")
            params.append(filters['priority'])
        if filters.get('category_id'):
            conditions.append("i.category_id = ?")
            params.append(filters['category_id'])
        if filters.get('system_id'):
            conditions.append("i.system_id = ?")
            params.append(filters['system_id'])
        if filters.get('department_id'):
            conditions.append("e.department_id = ?")
            params.append(filters['department_id'])
    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"""
        SELECT 
            CASE 
                WHEN COUNT(*) = 0 THEN 0
                ELSE ROUND(100.0 * SUM(CASE WHEN sla_status = 'Met' THEN 1 ELSE 0 END) / 
                     NULLIF(SUM(CASE WHEN sla_status IN ('Met','Breached') THEN 1 ELSE 0 END), 0), 2)
            END AS sla_compliance
        FROM View_SLAStatus v
        JOIN Incidents i ON v.incident_id = i.incident_id
        LEFT JOIN Employees e ON i.assigned_employee_id = e.employee_id
        {where}
    """
    df = execute_query(query, params)
    return df.iloc[0,0]

def get_kpi_avg_resolution_time(filters=None):
    conditions = []
    params = []
    if filters:
        if filters.get('date_from'):
            conditions.append("i.created_at >= ?")
            params.append(filters['date_from'])
        if filters.get('date_to'):
            conditions.append("i.created_at <= ?")
            params.append(filters['date_to'])
        if filters.get('priority'):
            conditions.append("i.priority = ?")
            params.append(filters['priority'])
        if filters.get('category_id'):
            conditions.append("i.category_id = ?")
            params.append(filters['category_id'])
        if filters.get('system_id'):
            conditions.append("i.system_id = ?")
            params.append(filters['system_id'])
        if filters.get('department_id'):
            conditions.append("e.department_id = ?")
            params.append(filters['department_id'])
    conditions.append("i.resolved_at IS NOT NULL")
    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"""
        SELECT AVG(DATEDIFF(MINUTE, i.created_at, i.resolved_at)) / 60.0 AS avg_hours
        FROM Incidents i
        LEFT JOIN Employees e ON i.assigned_employee_id = e.employee_id
        {where}
    """
    df = execute_query(query, params)
    return df.iloc[0,0]

# --- Данные для графиков ---
def get_incidents_by_month(filters=None):
    conditions = []
    params = []
    if filters:
        if filters.get('date_from'):
            conditions.append("i.created_at >= ?")
            params.append(filters['date_from'])
        if filters.get('date_to'):
            conditions.append("i.created_at <= ?")
            params.append(filters['date_to'])
        if filters.get('priority'):
            conditions.append("i.priority = ?")
            params.append(filters['priority'])
        if filters.get('status'):
            conditions.append("i.status = ?")
            params.append(filters['status'])
        if filters.get('category_id'):
            conditions.append("i.category_id = ?")
            params.append(filters['category_id'])
        if filters.get('system_id'):
            conditions.append("i.system_id = ?")
            params.append(filters['system_id'])
        if filters.get('department_id'):
            conditions.append("e.department_id = ?")
            params.append(filters['department_id'])
    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"""
        SELECT YEAR(i.created_at) AS year, MONTH(i.created_at) AS month, COUNT(*) AS count
        FROM Incidents i
        LEFT JOIN Employees e ON i.assigned_employee_id = e.employee_id
        {where}
        GROUP BY YEAR(i.created_at), MONTH(i.created_at)
        ORDER BY year, month
    """
    return execute_query(query, params)

def get_incidents_by_priority(filters=None):
    conditions = []
    params = []
    if filters:
        if filters.get('date_from'):
            conditions.append("i.created_at >= ?")
            params.append(filters['date_from'])
        if filters.get('date_to'):
            conditions.append("i.created_at <= ?")
            params.append(filters['date_to'])
        if filters.get('status'):
            conditions.append("i.status = ?")
            params.append(filters['status'])
        if filters.get('category_id'):
            conditions.append("i.category_id = ?")
            params.append(filters['category_id'])
        if filters.get('system_id'):
            conditions.append("i.system_id = ?")
            params.append(filters['system_id'])
        if filters.get('department_id'):
            conditions.append("e.department_id = ?")
            params.append(filters['department_id'])
    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"""
        SELECT i.priority, COUNT(*) AS count
        FROM Incidents i
        LEFT JOIN Employees e ON i.assigned_employee_id = e.employee_id
        {where}
        GROUP BY i.priority
        ORDER BY count DESC
    """
    return execute_query(query, params)

def get_incidents_by_category(filters=None):
    conditions = []
    params = []
    if filters:
        if filters.get('date_from'):
            conditions.append("i.created_at >= ?")
            params.append(filters['date_from'])
        if filters.get('date_to'):
            conditions.append("i.created_at <= ?")
            params.append(filters['date_to'])
        if filters.get('priority'):
            conditions.append("i.priority = ?")
            params.append(filters['priority'])
        if filters.get('status'):
            conditions.append("i.status = ?")
            params.append(filters['status'])
        if filters.get('system_id'):
            conditions.append("i.system_id = ?")
            params.append(filters['system_id'])
        if filters.get('department_id'):
            conditions.append("e.department_id = ?")
            params.append(filters['department_id'])
    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"""
        SELECT c.category_name, COUNT(*) AS count
        FROM Incidents i
        JOIN IncidentCategories c ON i.category_id = c.category_id
        LEFT JOIN Employees e ON i.assigned_employee_id = e.employee_id
        {where}
        GROUP BY c.category_name
        ORDER BY count DESC
    """
    return execute_query(query, params)

def get_incidents_by_status(filters=None):
    conditions = []
    params = []
    if filters:
        if filters.get('date_from'):
            conditions.append("i.created_at >= ?")
            params.append(filters['date_from'])
        if filters.get('date_to'):
            conditions.append("i.created_at <= ?")
            params.append(filters['date_to'])
        if filters.get('priority'):
            conditions.append("i.priority = ?")
            params.append(filters['priority'])
        if filters.get('category_id'):
            conditions.append("i.category_id = ?")
            params.append(filters['category_id'])
        if filters.get('system_id'):
            conditions.append("i.system_id = ?")
            params.append(filters['system_id'])
        if filters.get('department_id'):
            conditions.append("e.department_id = ?")
            params.append(filters['department_id'])
    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"""
        SELECT i.status, COUNT(*) AS count
        FROM Incidents i
        LEFT JOIN Employees e ON i.assigned_employee_id = e.employee_id
        {where}
        GROUP BY i.status
        ORDER BY count DESC
    """
    return execute_query(query, params)

def get_top_problematic_systems(filters=None, top_n=5):
    conditions = []
    params = []
    if filters:
        if filters.get('date_from'):
            conditions.append("i.created_at >= ?")
            params.append(filters['date_from'])
        if filters.get('date_to'):
            conditions.append("i.created_at <= ?")
            params.append(filters['date_to'])
        if filters.get('priority'):
            conditions.append("i.priority = ?")
            params.append(filters['priority'])
        if filters.get('status'):
            conditions.append("i.status = ?")
            params.append(filters['status'])
        if filters.get('category_id'):
            conditions.append("i.category_id = ?")
            params.append(filters['category_id'])
        if filters.get('department_id'):
            conditions.append("e.department_id = ?")
            params.append(filters['department_id'])
    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"""
        SELECT TOP {top_n} s.system_name, COUNT(*) AS incident_count
        FROM Incidents i
        JOIN Systems s ON i.system_id = s.system_id
        LEFT JOIN Employees e ON i.assigned_employee_id = e.employee_id
        {where}
        GROUP BY s.system_name
        ORDER BY incident_count DESC
    """
    return execute_query(query, params)

def get_incidents_by_department(filters=None):
    conditions = []
    params = []
    if filters:
        if filters.get('date_from'):
            conditions.append("i.created_at >= ?")
            params.append(filters['date_from'])
        if filters.get('date_to'):
            conditions.append("i.created_at <= ?")
            params.append(filters['date_to'])
        if filters.get('priority'):
            conditions.append("i.priority = ?")
            params.append(filters['priority'])
        if filters.get('status'):
            conditions.append("i.status = ?")
            params.append(filters['status'])
        if filters.get('category_id'):
            conditions.append("i.category_id = ?")
            params.append(filters['category_id'])
        if filters.get('system_id'):
            conditions.append("i.system_id = ?")
            params.append(filters['system_id'])
    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"""
        SELECT d.department_name, COUNT(*) AS count
        FROM Incidents i
        LEFT JOIN Employees e ON i.assigned_employee_id = e.employee_id
        LEFT JOIN Departments d ON e.department_id = d.department_id
        {where}
        GROUP BY d.department_name
        ORDER BY count DESC
    """
    return execute_query(query, params)

# --- Для страницы Incidents ---
def get_all_incidents(filters=None):
    conditions = []
    params = []
    if filters:
        if filters.get('search'):
            conditions.append("(i.title LIKE ? OR i.description LIKE ?)")
            params.extend([f"%{filters['search']}%", f"%{filters['search']}%"])
        if filters.get('priority'):
            conditions.append("i.priority = ?")
            params.append(filters['priority'])
        if filters.get('status'):
            conditions.append("i.status = ?")
            params.append(filters['status'])
        if filters.get('category_id'):
            conditions.append("i.category_id = ?")
            params.append(filters['category_id'])
        if filters.get('system_id'):
            conditions.append("i.system_id = ?")
            params.append(filters['system_id'])
        if filters.get('department_id'):
            conditions.append("e.department_id = ?")
            params.append(filters['department_id'])
    where = "WHERE " + " AND ".join(conditions) if conditions else ""
    query = f"""
        SELECT 
            i.incident_id,
            i.title,
            c.category_name,
            s.system_name,
            i.priority,
            i.status,
            e.full_name AS assigned_employee,
            i.created_at,
            i.resolved_at,
            i.sla_hours
        FROM Incidents i
        LEFT JOIN IncidentCategories c ON i.category_id = c.category_id
        LEFT JOIN Systems s ON i.system_id = s.system_id
        LEFT JOIN Employees e ON i.assigned_employee_id = e.employee_id
        {where}
        ORDER BY i.created_at DESC
    """
    return execute_query(query, params)

def get_incident_details(incident_id):
    query = """
        SELECT * FROM View_IncidentDetails WHERE incident_id = ?
    """
    df = execute_query(query, [incident_id])
    if not df.empty:
        return df.iloc[0]
    return None

def get_incident_history(incident_id):
    query = """
        SELECT h.history_id, h.old_status, h.new_status, h.changed_at, e.full_name AS changed_by, h.comment
        FROM IncidentHistory h
        JOIN Employees e ON h.changed_by = e.employee_id
        WHERE h.incident_id = ?
        ORDER BY h.changed_at
    """
    return execute_query(query, [incident_id])

def update_incident_status(incident_id, new_status, changed_by, comment=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Получаем текущий статус
        cursor.execute("SELECT status FROM Incidents WHERE incident_id = ?", incident_id)
        row = cursor.fetchone()
        if not row:
            raise ValueError("Incident not found")
        old_status = row[0]
        # Обновляем статус
        cursor.execute("UPDATE Incidents SET status = ? WHERE incident_id = ?", new_status, incident_id)
        # Если статус Resolved или Closed и resolved_at пусто, заполняем
        if new_status in ('Resolved', 'Closed'):
            cursor.execute("""
                UPDATE Incidents SET resolved_at = GETDATE()
                WHERE incident_id = ? AND resolved_at IS NULL
            """, incident_id)
        # Добавляем в историю
        cursor.execute("""
            INSERT INTO IncidentHistory (incident_id, old_status, new_status, changed_by, changed_at, comment)
            VALUES (?, ?, ?, ?, GETDATE(), ?)
        """, incident_id, old_status, new_status, changed_by, comment)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def create_incident(title, description, category_id, system_id, assigned_employee_id, priority, sla_hours):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Incidents (title, description, category_id, system_id, assigned_employee_id, priority, status, created_at, sla_hours)
            VALUES (?, ?, ?, ?, ?, ?, 'New', GETDATE(), ?)
        """, title, description, category_id, system_id, assigned_employee_id, priority, sla_hours)
        # Получаем ID созданного инцидента
        cursor.execute("SELECT SCOPE_IDENTITY()")
        incident_id = cursor.fetchone()[0]
        # Добавляем запись в историю
        # changed_by выбираем того же сотрудника или администратора (например, 1)
        cursor.execute("""
            INSERT INTO IncidentHistory (incident_id, old_status, new_status, changed_by, changed_at, comment)
            VALUES (?, NULL, 'New', ?, GETDATE(), 'Incident created')
        """, incident_id, assigned_employee_id)
        conn.commit()
        return incident_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()