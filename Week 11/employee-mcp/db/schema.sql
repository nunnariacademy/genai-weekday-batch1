DROP TABLE IF EXISTS work_assignments, salaries, employees, departments CASCADE;

CREATE TABLE departments (
    id        SERIAL PRIMARY KEY,
    name      TEXT NOT NULL UNIQUE,
    location  TEXT NOT NULL,
    budget    NUMERIC(14,2) NOT NULL
);

CREATE TABLE employees (
    id                 SERIAL PRIMARY KEY,
    first_name         TEXT NOT NULL,
    last_name          TEXT NOT NULL,
    email              TEXT NOT NULL UNIQUE,
    job_title          TEXT NOT NULL,
    department_id      INT NOT NULL REFERENCES departments(id),
    manager_id         INT REFERENCES employees(id),
    hire_date          DATE NOT NULL,
    is_active          BOOLEAN NOT NULL DEFAULT TRUE,
    performance_rating NUMERIC(2,1) CHECK (performance_rating BETWEEN 1 AND 5)
);

CREATE TABLE salaries (
    id             SERIAL PRIMARY KEY,
    employee_id    INT NOT NULL REFERENCES employees(id),
    annual_amount  NUMERIC(12,2) NOT NULL,
    currency       CHAR(3) NOT NULL DEFAULT 'INR',
    effective_date DATE NOT NULL,
    is_current     BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE work_assignments (
    id              SERIAL PRIMARY KEY,
    employee_id     INT NOT NULL REFERENCES employees(id),
    project_name    TEXT NOT NULL,
    role            TEXT NOT NULL,
    hours_per_week  INT NOT NULL,
    start_date      DATE NOT NULL,
    end_date        DATE,
    status          TEXT NOT NULL CHECK (status IN ('active','completed'))
);
