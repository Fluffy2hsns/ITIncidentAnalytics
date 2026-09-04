USE ITIncidentAnalytics;
GO

-- 1. Общее количество инцидентов
SELECT COUNT(*) AS total_incidents FROM Incidents;

-- 2. Количество открытых инцидентов (не Closed)
SELECT COUNT(*) AS open_incidents FROM Incidents WHERE status <> 'Closed';

-- 3. Количество Critical-инцидентов
SELECT COUNT(*) AS critical_incidents FROM Incidents WHERE priority = 'Critical';

-- 4. Инциденты по приоритету
SELECT priority, COUNT(*) AS count FROM Incidents GROUP BY priority ORDER BY count DESC;

-- 5. Инциденты по статусу
SELECT status, COUNT(*) AS count FROM Incidents GROUP BY status ORDER BY count DESC;

-- 6. Инциденты по категориям
SELECT c.category_name, COUNT(*) AS count
FROM Incidents i
JOIN IncidentCategories c ON i.category_id = c.category_id
GROUP BY c.category_name ORDER BY count DESC;

-- 7. Инциденты по системам
SELECT s.system_name, COUNT(*) AS count
FROM Incidents i
JOIN Systems s ON i.system_id = s.system_id
GROUP BY s.system_name ORDER BY count DESC;

-- 8. Инциденты по отделам
SELECT d.department_name, COUNT(*) AS count
FROM Incidents i
JOIN Employees e ON i.assigned_employee_id = e.employee_id
JOIN Departments d ON e.department_id = d.department_id
GROUP BY d.department_name ORDER BY count DESC;

-- 9. Инциденты по сотрудникам
SELECT e.full_name, COUNT(*) AS count
FROM Incidents i
JOIN Employees e ON i.assigned_employee_id = e.employee_id
GROUP BY e.full_name ORDER BY count DESC;

-- 10. Среднее время решения (в часах)
SELECT AVG(DATEDIFF(HOUR, created_at, resolved_at)) AS avg_resolution_hours
FROM Incidents WHERE resolved_at IS NOT NULL;

-- 11. Максимальное время решения
SELECT MAX(DATEDIFF(HOUR, created_at, resolved_at)) AS max_resolution_hours
FROM Incidents WHERE resolved_at IS NOT NULL;

-- 12. Минимальное время решения
SELECT MIN(DATEDIFF(HOUR, created_at, resolved_at)) AS min_resolution_hours
FROM Incidents WHERE resolved_at IS NOT NULL;

-- 13. Инциденты по месяцам
SELECT YEAR(created_at) AS year, MONTH(created_at) AS month, COUNT(*) AS count
FROM Incidents
GROUP BY YEAR(created_at), MONTH(created_at)
ORDER BY year, month;

-- 14. Количество SLA breaches
SELECT COUNT(*) AS sla_breaches
FROM View_SLAStatus WHERE sla_status = 'Breached';

-- 15. SLA compliance percentage
SELECT 
    ROUND(100.0 * SUM(CASE WHEN sla_status = 'Met' THEN 1 ELSE 0 END) / 
    NULLIF(SUM(CASE WHEN sla_status IN ('Met','Breached') THEN 1 ELSE 0 END), 0), 2) AS sla_compliance_percent
FROM View_SLAStatus;

-- 16. Top-5 проблемных систем
SELECT TOP 5 s.system_name, COUNT(*) AS incident_count
FROM Incidents i
JOIN Systems s ON i.system_id = s.system_id
GROUP BY s.system_name
ORDER BY incident_count DESC;

-- 17. Top-5 сотрудников по количеству обработанных инцидентов
SELECT TOP 5 e.full_name, COUNT(*) AS handled_count
FROM Incidents i
JOIN Employees e ON i.assigned_employee_id = e.employee_id
GROUP BY e.full_name
ORDER BY handled_count DESC;

-- 18. Среднее время решения по категориям
SELECT c.category_name, AVG(DATEDIFF(HOUR, i.created_at, i.resolved_at)) AS avg_resolution_hours
FROM Incidents i
JOIN IncidentCategories c ON i.category_id = c.category_id
WHERE i.resolved_at IS NOT NULL
GROUP BY c.category_name;

-- 19. Среднее время решения по сотрудникам
SELECT e.full_name, AVG(DATEDIFF(HOUR, i.created_at, i.resolved_at)) AS avg_resolution_hours
FROM Incidents i
JOIN Employees e ON i.assigned_employee_id = e.employee_id
WHERE i.resolved_at IS NOT NULL
GROUP BY e.full_name;

-- 20. Количество Critical-инцидентов по системам
SELECT s.system_name, COUNT(*) AS critical_count
FROM Incidents i
JOIN Systems s ON i.system_id = s.system_id
WHERE i.priority = 'Critical'
GROUP BY s.system_name;