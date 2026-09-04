USE ITIncidentAnalytics;
GO

-- View_IncidentDetails
CREATE OR ALTER VIEW View_IncidentDetails AS
SELECT
    i.incident_id,
    i.title,
    c.category_name AS category,
    s.system_name AS system,
    e.full_name AS employee,
    d.department_name AS department,
    i.priority,
    i.status,
    i.created_at,
    i.first_response_at,
    i.resolved_at,
    i.sla_hours
FROM Incidents i
LEFT JOIN IncidentCategories c ON i.category_id = c.category_id
LEFT JOIN Systems s ON i.system_id = s.system_id
LEFT JOIN Employees e ON i.assigned_employee_id = e.employee_id
LEFT JOIN Departments d ON e.department_id = d.department_id;
GO

-- View_IncidentResolutionTime
CREATE OR ALTER VIEW View_IncidentResolutionTime AS
SELECT
    i.incident_id,
    i.title,
    i.priority,
    i.status,
    i.created_at,
    i.resolved_at,
    DATEDIFF(HOUR, i.created_at, i.resolved_at) AS resolution_hours
FROM Incidents i;
GO

-- View_SLAStatus
CREATE OR ALTER VIEW View_SLAStatus AS
SELECT
    i.incident_id,
    i.title,
    i.priority,
    DATEDIFF(HOUR, i.created_at, i.resolved_at) AS resolution_hours,
    i.sla_hours,
    CASE
        WHEN i.resolved_at IS NULL THEN 'In Progress'
        WHEN DATEDIFF(HOUR, i.created_at, i.resolved_at) <= i.sla_hours THEN 'Met'
        ELSE 'Breached'
    END AS sla_status
FROM Incidents i;
GO