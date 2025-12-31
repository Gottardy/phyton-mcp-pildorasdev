import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from fastmcp import FastMCP

app = FastMCP("pildorasDev_db_server")

def get_db_connection():
    conn = psycopg2.connect(
        # Prefer `DB_DATABASE` (matches docker-compose); fall back to legacy `DB_NAME`
        dbname=os.getenv("DB_DATABASE", os.getenv("DB_NAME")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
    )
    return conn

@app.tool
def list_employees(limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """List employees with pagination"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        # Use RealDictCursor so rows are mapping-like (indexable by column name)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT id, name, position, department, salary, hire_date 
            FROM employees 
            ORDER BY id LIMIT %s OFFSET %s
            """,
            (limit, offset),
        )
        rows = cursor.fetchall()
        employees: List[Dict[str, Any]] = []
        from typing import cast  # inline import para no asumir el top-level
        for r in rows:
            # r already acts like Dict[str, Any] because of RealDictCursor
            row: Dict[str, Any] = r
            employee = {
                "id": row["id"],
                "name": row["name"],
                "position": row["position"],
                "department": row["department"],
                "salary": float(row["salary"]),
                "hire_date": row["hire_date"].isoformat() if row["hire_date"] else None,
            }
            employees.append(employee)
        return employees
    except Exception as e:
        # Mantener firma consistente: propagar excepción en lugar de devolver dict
        raise RuntimeError(f"Error listing employees: {e}") from e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.tool
def add_employee(name: str, position: str, department: str, salary: float, hire_date: Optional[str] = None) -> Dict[str, Any]:
    """Add a new employee"""
    conn = None
    cursor = None
    try:
        if not name or not position or not department or salary is None:
            raise ValueError("Name, position, department, and salary are required fields.")
        if not name.strip():
            raise ValueError("Name cannot be empty.")
        if salary <= 0:
            raise ValueError("Salary must be a non-negative number.")
        if not hire_date:
            hire_date = datetime.now().strftime('%Y-%m-%d')

        conn = get_db_connection()
        from psycopg2.extras import RealDictCursor
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        hire_date_obj = datetime.fromisoformat(hire_date) if hire_date else None
        cursor.execute(
            """
            INSERT INTO employees (name, position, department, salary, hire_date) 
            VALUES (%s, %s, %s, %s, %s) RETURNING id, name, position, department, salary, hire_date
            """,
            (name.strip(), position.strip(), department.strip(), salary, hire_date_obj),
        )
        new_employee = cursor.fetchone()
        if new_employee is None:
            raise RuntimeError("No se devolvió la fila insertada.")
        conn.commit()
        return {
            "success": True,
            "employee": {
                "id": new_employee["id"],
                "name": new_employee["name"],
                "position": new_employee["position"],
                "department": new_employee["department"],
                "salary": float(new_employee["salary"]),
                "hire_date": str(new_employee["hire_date"]),
            },
        }
    except Exception as e:
        # Mantener consistencia de tipos: propagar excepción
        raise RuntimeError(f"Error adding employee: {e}") from e
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    app.run(transport="sse", host="0.0.0.0", port=3000)
