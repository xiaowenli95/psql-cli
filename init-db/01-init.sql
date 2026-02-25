-- Initialize database with sample data and read-only user

-- Create some sample tables
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department VARCHAR(50),
    salary NUMERIC(10, 2),
    hire_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    budget NUMERIC(12, 2),
    manager_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    budget NUMERIC(12, 2),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS employee_projects (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES employees(id),
    project_id INTEGER REFERENCES projects(id),
    role VARCHAR(50),
    hours_allocated INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO departments (name, budget, manager_id) VALUES
    ('Engineering', 500000.00, NULL),
    ('Marketing', 200000.00, NULL),
    ('Sales', 300000.00, NULL),
    ('HR', 150000.00, NULL),
    ('Finance', 250000.00, NULL);

INSERT INTO employees (name, email, department, salary, hire_date) VALUES
    ('John Doe', 'john.doe@company.com', 'Engineering', 95000.00, '2020-01-15'),
    ('Jane Smith', 'jane.smith@company.com', 'Engineering', 105000.00, '2019-03-20'),
    ('Bob Johnson', 'bob.johnson@company.com', 'Marketing', 75000.00, '2021-06-01'),
    ('Alice Williams', 'alice.williams@company.com', 'Sales', 80000.00, '2020-09-10'),
    ('Charlie Brown', 'charlie.brown@company.com', 'Engineering', 88000.00, '2021-02-28'),
    ('Diana Prince', 'diana.prince@company.com', 'HR', 72000.00, '2019-11-15'),
    ('Eve Anderson', 'eve.anderson@company.com', 'Finance', 92000.00, '2020-04-01'),
    ('Frank Miller', 'frank.miller@company.com', 'Sales', 85000.00, '2021-08-20'),
    ('Grace Lee', 'grace.lee@company.com', 'Marketing', 78000.00, '2020-07-12'),
    ('Henry Wilson', 'henry.wilson@company.com', 'Engineering', 98000.00, '2019-05-30');

INSERT INTO projects (name, description, start_date, end_date, budget, status) VALUES
    ('Website Redesign', 'Complete overhaul of company website', '2024-01-01', '2024-06-30', 150000.00, 'active'),
    ('Mobile App', 'Develop iOS and Android mobile applications', '2024-02-15', '2024-12-31', 300000.00, 'active'),
    ('CRM Integration', 'Integrate new CRM system', '2023-09-01', '2024-03-31', 100000.00, 'completed'),
    ('Marketing Campaign Q1', 'Q1 2024 marketing initiatives', '2024-01-01', '2024-03-31', 50000.00, 'completed'),
    ('Data Migration', 'Migrate legacy data to new system', '2024-03-01', '2024-09-30', 80000.00, 'active');

INSERT INTO employee_projects (employee_id, project_id, role, hours_allocated) VALUES
    (1, 1, 'Lead Developer', 160),
    (2, 2, 'Lead Developer', 200),
    (5, 1, 'Developer', 120),
    (5, 2, 'Developer', 80),
    (10, 2, 'Senior Developer', 180),
    (3, 4, 'Marketing Lead', 160),
    (9, 4, 'Marketing Specialist', 120),
    (4, 4, 'Sales Coordinator', 80),
    (8, 4, 'Sales Representative', 60),
    (7, 5, 'Project Manager', 100);

-- Update department manager_ids
UPDATE departments SET manager_id = 2 WHERE name = 'Engineering';
UPDATE departments SET manager_id = 3 WHERE name = 'Marketing';
UPDATE departments SET manager_id = 4 WHERE name = 'Sales';
UPDATE departments SET manager_id = 6 WHERE name = 'HR';
UPDATE departments SET manager_id = 7 WHERE name = 'Finance';

-- Create read-only user
CREATE USER readonly_user WITH PASSWORD 'readonly_pass';

-- Grant connect privilege
GRANT CONNECT ON DATABASE testdb TO readonly_user;

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO readonly_user;

-- Grant select on all existing tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

-- Grant select on all future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly_user;

-- Grant usage on sequences (needed for serial columns in queries)
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO readonly_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO readonly_user;

-- Display summary
SELECT 'Database initialized successfully!' AS status;
SELECT 'Tables created: ' || COUNT(*) || ' tables' AS info 
FROM information_schema.tables 
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

SELECT 'Sample data inserted:' AS info;
SELECT 'Employees: ' || COUNT(*) AS count FROM employees
UNION ALL
SELECT 'Departments: ' || COUNT(*) FROM departments
UNION ALL
SELECT 'Projects: ' || COUNT(*) FROM projects
UNION ALL
SELECT 'Employee-Project assignments: ' || COUNT(*) FROM employee_projects;
