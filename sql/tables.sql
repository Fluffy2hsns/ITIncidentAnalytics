USE ITIncidentAnalytics;
GO

-- Таблица Departments
CREATE TABLE Departments (
    department_id INT IDENTITY(1,1) PRIMARY KEY,
    department_name NVARCHAR(100) NOT NULL UNIQUE
);

-- Таблица Employees
CREATE TABLE Employees (
    employee_id INT IDENTITY(1,1) PRIMARY KEY,
    full_name NVARCHAR(150) NOT NULL,
    position NVARCHAR(100),
    department_id INT,
    email NVARCHAR(150) UNIQUE,
    is_active BIT DEFAULT 1,
    CONSTRAINT FK_Employees_Departments FOREIGN KEY (department_id) REFERENCES Departments(department_id)
);

-- Таблица Systems
CREATE TABLE Systems (
    system_id INT IDENTITY(1,1) PRIMARY KEY,
    system_name NVARCHAR(150) NOT NULL UNIQUE,
    system_type NVARCHAR(100),
    criticality NVARCHAR(20) CHECK (criticality IN ('Low', 'Medium', 'High', 'Critical')),
    department_id INT,
    is_active BIT DEFAULT 1,
    CONSTRAINT FK_Systems_Departments FOREIGN KEY (department_id) REFERENCES Departments(department_id)
);

-- Таблица IncidentCategories
CREATE TABLE IncidentCategories (
    category_id INT IDENTITY(1,1) PRIMARY KEY,
    category_name NVARCHAR(100) NOT NULL UNIQUE,
    description NVARCHAR(300)
);

-- Таблица Incidents
CREATE TABLE Incidents (
    incident_id INT IDENTITY(1,1) PRIMARY KEY,
    title NVARCHAR(200) NOT NULL,
    description NVARCHAR(MAX),
    category_id INT,
    system_id INT,
    assigned_employee_id INT,
    priority NVARCHAR(20) CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),
    status NVARCHAR(30) CHECK (status IN ('New', 'Assigned', 'In Progress', 'Resolved', 'Closed')),
    created_at DATETIME DEFAULT GETDATE(),
    first_response_at DATETIME NULL,
    resolved_at DATETIME NULL,
    sla_hours INT,
    CONSTRAINT FK_Incidents_Categories FOREIGN KEY (category_id) REFERENCES IncidentCategories(category_id),
    CONSTRAINT FK_Incidents_Systems FOREIGN KEY (system_id) REFERENCES Systems(system_id),
    CONSTRAINT FK_Incidents_Employees FOREIGN KEY (assigned_employee_id) REFERENCES Employees(employee_id)
);

-- Таблица IncidentHistory
CREATE TABLE IncidentHistory (
    history_id INT IDENTITY(1,1) PRIMARY KEY,
    incident_id INT NOT NULL,
    old_status NVARCHAR(30),
    new_status NVARCHAR(30) NOT NULL,
    changed_by INT NOT NULL,
    changed_at DATETIME DEFAULT GETDATE(),
    comment NVARCHAR(500),
    CONSTRAINT FK_History_Incidents FOREIGN KEY (incident_id) REFERENCES Incidents(incident_id),
    CONSTRAINT FK_History_Employees FOREIGN KEY (changed_by) REFERENCES Employees(employee_id)
);
GO