USE ITIncidentAnalytics;
GO

-- Отключение проверки внешних ключей на время заполнения
ALTER TABLE Employees NOCHECK CONSTRAINT ALL;
ALTER TABLE Systems NOCHECK CONSTRAINT ALL;
ALTER TABLE Incidents NOCHECK CONSTRAINT ALL;
ALTER TABLE IncidentHistory NOCHECK CONSTRAINT ALL;

-- Очистка таблиц (если нужно)
TRUNCATE TABLE IncidentHistory;
DELETE FROM Incidents;
DBCC CHECKIDENT ('Incidents', RESEED, 0);
DELETE FROM IncidentCategories;
DBCC CHECKIDENT ('IncidentCategories', RESEED, 0);
DELETE FROM Systems;
DBCC CHECKIDENT ('Systems', RESEED, 0);
DELETE FROM Employees;
DBCC CHECKIDENT ('Employees', RESEED, 0);
DELETE FROM Departments;
DBCC CHECKIDENT ('Departments', RESEED, 0);

-- Departments
INSERT INTO Departments (department_name) VALUES
('IT Support'), ('Development'), ('Data Analytics'), ('Cybersecurity'), ('Infrastructure'), ('Management');

-- Employees
DECLARE @i INT = 1;
WHILE @i <= 30
BEGIN
    INSERT INTO Employees (full_name, position, department_id, email, is_active)
    VALUES (
        CONCAT('Employee ', @i),
        CASE WHEN @i % 5 = 0 THEN 'Senior Specialist' ELSE 'Specialist' END,
        (SELECT TOP 1 department_id FROM Departments ORDER BY NEWID()),
        CONCAT('employee', @i, '@company.com'),
        1
    );
    SET @i = @i + 1;
END;

-- Systems
INSERT INTO Systems (system_name, system_type, criticality, department_id, is_active)
VALUES
('CRM', 'Application', 'High', 1, 1),
('ERP', 'Application', 'Critical', 1, 1),
('Database Server', 'Infrastructure', 'Critical', 5, 1),
('Web Application', 'Application', 'High', 2, 1),
('API Gateway', 'Infrastructure', 'High', 2, 1),
('Corporate Network', 'Network', 'High', 5, 1),
('Email Server', 'Infrastructure', 'Medium', 5, 1),
('VPN', 'Network', 'Medium', 5, 1),
('File Server', 'Infrastructure', 'Medium', 5, 1),
('Monitoring System', 'Tool', 'Low', 5, 1),
('Backup System', 'Infrastructure', 'High', 5, 1),
('HR Portal', 'Application', 'Medium', 6, 1);

-- IncidentCategories
INSERT INTO IncidentCategories (category_name, description) VALUES
('Network', 'Network connectivity issues'),
('Database', 'Database errors and performance'),
('Software', 'Software bugs and crashes'),
('Hardware', 'Physical hardware failures'),
('Security', 'Security incidents and vulnerabilities'),
('Access', 'Access rights and authentication'),
('Server', 'Server outages and performance'),
('Performance', 'General performance degradation');

-- Генерация инцидентов
DECLARE @counter INT = 1;
DECLARE @totalIncidents INT = 400; -- 400 инцидентов
DECLARE @startDate DATETIME = '2025-01-01 08:00:00';
DECLARE @endDate DATETIME = GETDATE();
DECLARE @randomDays INT, @randomHours INT, @randomMinutes INT, @randomSeconds INT;
DECLARE @created DATETIME, @first_resp DATETIME, @resolved DATETIME;
DECLARE @cat_id INT, @sys_id INT, @emp_id INT, @priority NVARCHAR(20), @status NVARCHAR(30), @sla INT;

WHILE @counter <= @totalIncidents
BEGIN
    -- Случайная дата создания в диапазоне от @startDate до @endDate
    SET @randomDays = DATEDIFF(DAY, @startDate, @endDate);
    SET @created = DATEADD(DAY, RAND() * @randomDays, @startDate);
    SET @created = DATEADD(SECOND, RAND() * 86400, @created);

    -- Приоритет
    SET @priority = CASE 
        WHEN RAND() < 0.1 THEN 'Critical'
        WHEN RAND() < 0.3 THEN 'High'
        WHEN RAND() < 0.6 THEN 'Medium'
        ELSE 'Low'
    END;

    -- Категория, система, сотрудник
    SELECT TOP 1 @cat_id = category_id FROM IncidentCategories ORDER BY NEWID();
    SELECT TOP 1 @sys_id = system_id FROM Systems ORDER BY NEWID();
    SELECT TOP 1 @emp_id = employee_id FROM Employees ORDER BY NEWID();

    -- SLA в часах
    SET @sla = CASE @priority
        WHEN 'Critical' THEN 4
        WHEN 'High' THEN 8
        WHEN 'Medium' THEN 24
        ELSE 48
    END;

    -- Статус: большинство resolved/closed, часть открытых
    SET @status = CASE 
        WHEN RAND() < 0.15 THEN 'New'
        WHEN RAND() < 0.25 THEN 'Assigned'
        WHEN RAND() < 0.35 THEN 'In Progress'
        WHEN RAND() < 0.80 THEN 'Resolved'
        ELSE 'Closed'
    END;

    -- Если статус New/Assigned/In Progress, то first_response_at и resolved_at могут быть NULL
    IF @status IN ('New', 'Assigned', 'In Progress')
    BEGIN
        SET @first_resp = NULL;
        SET @resolved = NULL;
    END
    ELSE
    BEGIN
        -- first_response_at = created + случайное время до 2 часов
        SET @first_resp = DATEADD(MINUTE, RAND() * 120, @created);
        -- resolved_at = first_response + случайное время до 10 часов (может превысить SLA)
        SET @resolved = DATEADD(MINUTE, RAND() * 600, @first_resp);
        -- Иногда resolved_at раньше first_response? Не допустимо, поэтому гарантируем порядок
        IF @resolved < @first_resp
            SET @resolved = @first_resp;
    END

    INSERT INTO Incidents (title, description, category_id, system_id, assigned_employee_id, priority, status, created_at, first_response_at, resolved_at, sla_hours)
    VALUES (
        CONCAT('Incident #', @counter, ' - ', (SELECT TOP 1 category_name FROM IncidentCategories WHERE category_id = @cat_id)),
        CONCAT('Description for incident #', @counter, ' related to ', (SELECT TOP 1 system_name FROM Systems WHERE system_id = @sys_id)),
        @cat_id,
        @sys_id,
        @emp_id,
        @priority,
        @status,
        @created,
        @first_resp,
        @resolved,
        @sla
    );

    SET @counter = @counter + 1;
END;

-- Генерация истории статусов для каждого инцидента
DECLARE @incident_id INT;
DECLARE history_cursor CURSOR FOR
SELECT incident_id, created_at, first_response_at, resolved_at, status FROM Incidents;

OPEN history_cursor;
FETCH NEXT FROM history_cursor INTO @incident_id, @created, @first_resp, @resolved, @status;

WHILE @@FETCH_STATUS = 0
BEGIN
    DECLARE @prev_status NVARCHAR(30) = 'New';
    DECLARE @next_status NVARCHAR(30);
    DECLARE @change_time DATETIME;
    DECLARE @changed_by INT;

    -- Всегда добавляем запись "New" при создании
    SELECT TOP 1 @changed_by = employee_id FROM Employees ORDER BY NEWID();
    INSERT INTO IncidentHistory (incident_id, old_status, new_status, changed_by, changed_at, comment)
    VALUES (@incident_id, NULL, 'New', @changed_by, @created, 'Incident created');

    -- Если есть first_response_at, добавляем Assigned
    IF @first_resp IS NOT NULL
    BEGIN
        SELECT TOP 1 @changed_by = employee_id FROM Employees ORDER BY NEWID();
        INSERT INTO IncidentHistory (incident_id, old_status, new_status, changed_by, changed_at, comment)
        VALUES (@incident_id, 'New', 'Assigned', @changed_by, @first_resp, 'Assigned to specialist');
    END

    -- Если есть resolved_at, добавляем In Progress и Resolved
    IF @resolved IS NOT NULL
    BEGIN
        -- In Progress примерно через 30% времени между first_resp и resolved
        SET @change_time = DATEADD(MINUTE, DATEDIFF(MINUTE, @first_resp, @resolved) * 0.3, @first_resp);
        SELECT TOP 1 @changed_by = employee_id FROM Employees ORDER BY NEWID();
        INSERT INTO IncidentHistory (incident_id, old_status, new_status, changed_by, changed_at, comment)
        VALUES (@incident_id, 'Assigned', 'In Progress', @changed_by, @change_time, 'Work started');

        -- Resolved
        SELECT TOP 1 @changed_by = employee_id FROM Employees ORDER BY NEWID();
        INSERT INTO IncidentHistory (incident_id, old_status, new_status, changed_by, changed_at, comment)
        VALUES (@incident_id, 'In Progress', 'Resolved', @changed_by, @resolved, 'Resolved');
    END

    -- Если статус Closed, добавляем запись Closed
    IF @status = 'Closed'
    BEGIN
        -- Closed через некоторое время после resolved
        SET @change_time = DATEADD(HOUR, RAND() * 48, @resolved);
        SELECT TOP 1 @changed_by = employee_id FROM Employees ORDER BY NEWID();
        INSERT INTO IncidentHistory (incident_id, old_status, new_status, changed_by, changed_at, comment)
        VALUES (@incident_id, 'Resolved', 'Closed', @changed_by, @change_time, 'Closed');
    END

    FETCH NEXT FROM history_cursor INTO @incident_id, @created, @first_resp, @resolved, @status;
END;

CLOSE history_cursor;
DEALLOCATE history_cursor;

-- Включение проверки внешних ключей
ALTER TABLE Employees CHECK CONSTRAINT ALL;
ALTER TABLE Systems CHECK CONSTRAINT ALL;
ALTER TABLE Incidents CHECK CONSTRAINT ALL;
ALTER TABLE IncidentHistory CHECK CONSTRAINT ALL;
GO