-- All data below is fictional / simulated.
INSERT INTO departments (name, location, budget) VALUES
 ('Engineering', 'Coimbatore', 12000000),
 ('Data & AI',   'Coimbatore', 15000000),
 ('Sales',       'Chennai',     8000000),
 ('HR',          'Coimbatore',  4000000);

INSERT INTO employees (first_name,last_name,email,job_title,department_id,manager_id,hire_date,performance_rating) VALUES
 ('Aarav','Menon',        'aarav.menon@example.com',     'Engineering Manager',     1, NULL, '2019-03-11', 4.5),
 ('Priya','Nair',         'priya.nair@example.com',      'Senior Backend Engineer', 1, 1,    '2020-06-01', 4.7),
 ('Rohan','Iyer',         'rohan.iyer@example.com',      'Frontend Engineer',       1, 1,    '2022-09-15', 3.6),
 ('Meera','Krishnan',     'meera.krishnan@example.com',  'Head of Data & AI',       2, NULL, '2018-01-22', 4.8),
 ('Karthik','Subramanian','karthik.s@example.com',       'ML Engineer',             2, 4,    '2021-08-02', 4.2),
 ('Divya','Raman',        'divya.raman@example.com',     'Data Analyst',            2, 4,    '2023-02-13', 3.9),
 ('Arjun','Patel',        'arjun.patel@example.com',     'Sales Manager',           3, NULL, '2019-11-04', 4.1),
 ('Sneha','Reddy',        'sneha.reddy@example.com',     'Account Executive',       3, 7,    '2022-01-17', 4.4),
 ('Vikram','Rao',         'vikram.rao@example.com',      'Sales Associate',         3, 7,    '2024-05-20', 2.9),
 ('Ananya','Das',         'ananya.das@example.com',      'HR Manager',              4, NULL, '2018-07-09', 4.3),
 ('Ishaan','Gupta',       'ishaan.gupta@example.com',    'Junior Engineer',         1, 1,    '2025-01-06', 3.4),
 ('Lakshmi','Venkat',     'lakshmi.venkat@example.com',  'Recruiter',               4, 10,   '2023-10-03', 4.0);

-- Salary history (annual, INR). Three people got a raise in 2025.
INSERT INTO salaries (employee_id, annual_amount, effective_date, is_current) VALUES
 (2, 2200000, '2022-04-01', FALSE),
 (5, 1900000, '2022-04-01', FALSE),
 (8, 1200000, '2022-04-01', FALSE);

INSERT INTO salaries (employee_id, annual_amount, effective_date, is_current) VALUES
 (1, 3200000, '2025-04-01', TRUE),
 (2, 2600000, '2025-04-01', TRUE),
 (3, 1400000, '2025-04-01', TRUE),
 (4, 3800000, '2025-04-01', TRUE),
 (5, 2400000, '2025-04-01', TRUE),
 (6, 1200000, '2025-04-01', TRUE),
 (7, 2800000, '2025-04-01', TRUE),
 (8, 1500000, '2025-04-01', TRUE),
 (9,  700000, '2025-04-01', TRUE),
 (10,2500000, '2025-04-01', TRUE),
 (11, 800000, '2025-01-06', TRUE),
 (12,1000000, '2025-04-01', TRUE);

INSERT INTO work_assignments (employee_id, project_name, role, hours_per_week, start_date, end_date, status) VALUES
 (1, 'Payments API Revamp',        'Project Sponsor',    8, '2025-01-15', NULL,         'active'),
 (2, 'Payments API Revamp',        'Tech Lead',         30, '2025-01-15', NULL,         'active'),
 (11,'Payments API Revamp',        'Support Developer',  8, '2025-03-01', NULL,         'active'),
 (3, 'Mobile App v2',              'Frontend Developer',35, '2025-03-01', NULL,         'active'),
 (11,'Mobile App v2',              'Developer',         30, '2025-02-01', NULL,         'active'),
 (4, 'Customer Churn Model',       'Project Lead',      15, '2025-02-10', NULL,         'active'),
 (5, 'Customer Churn Model',       'ML Engineer',       32, '2025-02-10', NULL,         'active'),
 (5, 'Doc Extraction Pipeline',    'ML Engineer',        8, '2024-09-01', '2025-01-31', 'completed'),
 (3, 'Doc Extraction Pipeline',    'UI Developer',      10, '2024-09-01', '2025-01-31', 'completed'),
 (6, 'Sales Dashboard',            'Analyst',           25, '2025-04-01', NULL,         'active'),
 (7, 'Sales Dashboard',            'Business Owner',     5, '2025-04-01', NULL,         'active'),
 (8, 'Enterprise Onboarding Drive','Account Lead',      30, '2025-05-01', NULL,         'active'),
 (9, 'Enterprise Onboarding Drive','Associate',         35, '2025-05-01', NULL,         'active'),
 (10,'Recruitment Portal',         'Project Sponsor',    6, '2025-03-15', NULL,         'active'),
 (12,'Recruitment Portal',         'Coordinator',       30, '2025-03-15', NULL,         'active');
