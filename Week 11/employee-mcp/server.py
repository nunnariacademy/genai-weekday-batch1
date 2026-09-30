"""MCP server exposing the employee database.

Three MCP primitives are demonstrated:
  * TOOLS      - functions the model can call (model-controlled) -> live DB queries
  * RESOURCES  - read-only context identified by a URI (app-controlled) -> policy/text
  * PROMPTS    - reusable prompt templates (user-controlled) -> review workflows

Runs over stdio, so NEVER print() to stdout in this file (it would corrupt the
protocol stream). Use logging / stderr if you need debug output.
"""
import json
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from mcp.server.fastmcp import FastMCP

from config import DB_CONFIG

RESOURCE_DIR = Path(__file__).parent / "resources"

mcp = FastMCP("employee-directory")


# --------------------------------------------------------------------------- helpers
def query(sql: str, params: tuple = ()) -> list[dict]:
    with psycopg.connect(**DB_CONFIG, row_factory=dict_row) as conn:
        return conn.execute(sql, params).fetchall()


def to_json(data) -> str:
    # default=str handles Decimal and date values coming out of Postgres
    return json.dumps(data, default=str, indent=2)


# --------------------------------------------------------------------------- TOOLS
@mcp.tool()
def list_departments() -> str:
    """List all departments with their location, budget and active headcount."""
    rows = query("""
        SELECT d.id, d.name, d.location, d.budget, COUNT(e.id) AS headcount
        FROM departments d
        LEFT JOIN employees e ON e.department_id = d.id AND e.is_active
        GROUP BY d.id ORDER BY d.id
    """)
    return to_json(rows)


@mcp.tool()
def search_employees(name: str = "", department: str = "", limit: int = 20) -> str:
    """Search employees by partial name and/or department name.
    Returns id, name, title, department and performance rating.
    Leave both filters empty to list everyone."""
    rows = query("""
        SELECT e.id, e.first_name || ' ' || e.last_name AS name, e.job_title,
               d.name AS department, e.performance_rating
        FROM employees e JOIN departments d ON d.id = e.department_id
        WHERE (e.first_name || ' ' || e.last_name) ILIKE %s
          AND d.name ILIKE %s
        ORDER BY e.id LIMIT %s
    """, (f"%{name}%", f"%{department}%", limit))
    return to_json(rows)


@mcp.tool()
def get_employee_details(employee_id: int) -> str:
    """Full profile of one employee: title, department, manager, hire date,
    rating, current salary and current/past project assignments."""
    emp = query("""
        SELECT e.id, e.first_name || ' ' || e.last_name AS name, e.email, e.job_title,
               d.name AS department, m.first_name || ' ' || m.last_name AS manager,
               e.hire_date, e.is_active, e.performance_rating,
               s.annual_amount AS current_salary, s.currency
        FROM employees e
        JOIN departments d ON d.id = e.department_id
        LEFT JOIN employees m ON m.id = e.manager_id
        LEFT JOIN salaries s ON s.employee_id = e.id AND s.is_current
        WHERE e.id = %s
    """, (employee_id,))
    if not emp:
        return to_json({"error": f"No employee with id {employee_id}"})
    work = query("""
        SELECT project_name, role, hours_per_week, start_date, end_date, status
        FROM work_assignments WHERE employee_id = %s ORDER BY start_date DESC
    """, (employee_id,))
    return to_json({**emp[0], "assignments": work})


@mcp.tool()
def get_salary_history(employee_id: int) -> str:
    """Salary history of one employee, newest first (annual amounts)."""
    rows = query("""
        SELECT annual_amount, currency, effective_date, is_current
        FROM salaries WHERE employee_id = %s ORDER BY effective_date DESC
    """, (employee_id,))
    return to_json(rows)


@mcp.tool()
def get_department_salary_stats(department: str = "") -> str:
    """Average/min/max/total CURRENT annual salary per department.
    Optionally filter by department name."""
    rows = query("""
        SELECT d.name AS department, COUNT(*) AS employees,
               ROUND(AVG(s.annual_amount)) AS avg_salary,
               MIN(s.annual_amount) AS min_salary,
               MAX(s.annual_amount) AS max_salary,
               SUM(s.annual_amount) AS total_payroll
        FROM salaries s
        JOIN employees e ON e.id = s.employee_id
        JOIN departments d ON d.id = e.department_id
        WHERE s.is_current AND d.name ILIKE %s
        GROUP BY d.name ORDER BY d.name
    """, (f"%{department}%",))
    return to_json(rows)


@mcp.tool()
def get_top_performers(limit: int = 5, min_rating: float = 0.0) -> str:
    """Employees ranked by performance rating (highest first), with current salary."""
    rows = query("""
        SELECT e.id, e.first_name || ' ' || e.last_name AS name, e.job_title,
               d.name AS department, e.performance_rating, s.annual_amount AS current_salary
        FROM employees e
        JOIN departments d ON d.id = e.department_id
        LEFT JOIN salaries s ON s.employee_id = e.id AND s.is_current
        WHERE e.performance_rating >= %s
        ORDER BY e.performance_rating DESC LIMIT %s
    """, (min_rating, limit))
    return to_json(rows)


@mcp.tool()
def get_project_team(project_name: str) -> str:
    """Who works on a project (partial name match): person, role, weekly hours, status."""
    rows = query("""
        SELECT w.project_name, e.first_name || ' ' || e.last_name AS name,
               w.role, w.hours_per_week, w.status
        FROM work_assignments w JOIN employees e ON e.id = w.employee_id
        WHERE w.project_name ILIKE %s ORDER BY w.project_name, w.hours_per_week DESC
    """, (f"%{project_name}%",))
    return to_json(rows)


# --------------------------------------------------------------------------- RESOURCES
@mcp.resource("performance://guidelines")
def performance_guidelines() -> str:
    """Company performance review policy: rating scale, criteria, raise and promotion rules."""
    return (RESOURCE_DIR / "performance_review_guidelines.md").read_text()


@mcp.resource("performance://highlights-2025")
def performance_highlights() -> str:
    """Written mid-2025 performance notes for every employee, plus company-wide themes."""
    return (RESOURCE_DIR / "performance_highlights_2025.md").read_text()


# A resource TEMPLATE: the {employee_id} part is filled in by the client.
@mcp.resource("employee://{employee_id}/profile")
def employee_profile(employee_id: int) -> str:
    """Short text profile card for one employee (built live from the database)."""
    rows = query("""
        SELECT e.first_name || ' ' || e.last_name AS name, e.job_title, d.name AS department,
               e.hire_date, e.performance_rating
        FROM employees e JOIN departments d ON d.id = e.department_id WHERE e.id = %s
    """, (employee_id,))
    if not rows:
        return f"No employee with id {employee_id}."
    r = rows[0]
    return (f"{r['name']} - {r['job_title']}, {r['department']}. "
            f"Hired {r['hire_date']}. Performance rating: {r['performance_rating']}/5.")


# --------------------------------------------------------------------------- PROMPTS
@mcp.prompt()
def performance_review(employee_name: str) -> str:
    """Write a structured performance review for one employee."""
    return f"""You are an HR business partner. Write a performance review for {employee_name}.

Steps:
1. Use the search_employees tool to find their id, then get_employee_details for their profile and projects.
2. Read the performance://guidelines resource and the performance://highlights-2025 resource.
3. Write the review with these sections: Summary, Strengths, Growth areas, Rating justification
   (use the rating scale from the guidelines), and Recommended next steps (raise / promotion / coaching).
Cite at least two concrete facts (projects, numbers, ratings) from the data you retrieved."""


@mcp.prompt()
def salary_review(department: str) -> str:
    """Analyse pay fairness and raise recommendations for a department."""
    return f"""You are a compensation analyst reviewing the {department} department.

Steps:
1. Call get_department_salary_stats for the department, then search_employees to list its people.
2. For each person call get_salary_history and compare their pay to their performance rating.
3. Read the performance://guidelines resource for the raise policy.
Produce a table (name, rating, current salary, suggested raise band) and flag anyone who looks
underpaid or overpaid relative to their rating."""


@mcp.prompt()
def team_health_check() -> str:
    """Company-wide snapshot of performance, workload and risks."""
    return """You are an operations analyst preparing a leadership briefing.

Use list_departments, get_top_performers and get_department_salary_stats, then read the
performance://highlights-2025 resource. Summarise: (1) top talent, (2) people at risk
(low ratings), (3) workload or staffing concerns, (4) three recommended actions."""


if __name__ == "__main__":
    mcp.run()  # stdio transport
