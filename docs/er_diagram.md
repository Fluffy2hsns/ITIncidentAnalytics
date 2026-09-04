erDiagram
    Departments ||--o{ Employees : "has"
    Departments ||--o{ Systems : "owns"
    Employees ||--o{ Incidents : "assigned to"
    Systems ||--o{ Incidents : "affects"
    IncidentCategories ||--o{ Incidents : "categorizes"
    Incidents ||--o{ IncidentHistory : "has history"
    Employees ||--o{ IncidentHistory : "changes"

    Departments {
        int department_id PK
        string department_name
    }
    Employees {
        int employee_id PK
        string full_name
        string position
        int department_id FK
        string email
        bit is_active
    }
    Systems {
        int system_id PK
        string system_name
        string system_type
        string criticality
        int department_id FK
        bit is_active
    }
    IncidentCategories {
        int category_id PK
        string category_name
        string description
    }
    Incidents {
        int incident_id PK
        string title
        string description
        int category_id FK
        int system_id FK
        int assigned_employee_id FK
        string priority
        string status
        datetime created_at
        datetime first_response_at
        datetime resolved_at
        int sla_hours
    }
    IncidentHistory {
        int history_id PK
        int incident_id FK
        string old_status
        string new_status
        int changed_by FK
        datetime changed_at
        string comment
    }