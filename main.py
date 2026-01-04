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


@app.tool
def get_employee(employee_id: int) -> Dict[str, Any]:
    """Get a single employee by id"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        from psycopg2.extras import RealDictCursor
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            SELECT id, name, position, department, salary, hire_date
            FROM employees
            WHERE id = %s
            """,
            (employee_id,),
        )
        row = cursor.fetchone()
        if row is None:
            raise RuntimeError(f"Employee with id {employee_id} not found.")
        return {
            "id": row["id"],
            "name": row["name"],
            "position": row["position"],
            "department": row["department"],
            "salary": float(row["salary"]),
            "hire_date": row["hire_date"].isoformat() if row["hire_date"] else None,
        }
    except Exception as e:
        raise RuntimeError(f"Error getting employee: {e}") from e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.tool
def update_employee(employee_id: int, name: Optional[str] = None, position: Optional[str] = None, department: Optional[str] = None, salary: Optional[float] = None, hire_date: Optional[str] = None) -> Dict[str, Any]:
    """Update an existing employee's fields (partial updates allowed)"""
    conn = None
    cursor = None
    try:
        if name is not None and not name.strip():
            raise ValueError("Name cannot be empty.")
        if salary is not None and salary <= 0:
            raise ValueError("Salary must be a non-negative number.")

        fields: List[str] = []
        values: List[Any] = []

        if name is not None:
            fields.append("name = %s")
            values.append(name.strip())
        if position is not None:
            fields.append("position = %s")
            values.append(position.strip())
        if department is not None:
            fields.append("department = %s")
            values.append(department.strip())
        if salary is not None:
            fields.append("salary = %s")
            values.append(salary)
        if hire_date is not None:
            hire_date_obj = datetime.fromisoformat(hire_date) if hire_date else None
            fields.append("hire_date = %s")
            values.append(hire_date_obj)

        if not fields:
            raise ValueError("At least one field must be provided to update.")

        conn = get_db_connection()
        from psycopg2.extras import RealDictCursor
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # build parameterized query
        set_clause = ", ".join(fields)
        values.append(employee_id)
        sql = f"UPDATE employees SET {set_clause} WHERE id = %s RETURNING id, name, position, department, salary, hire_date"
        cursor.execute(sql, tuple(values))
        updated = cursor.fetchone()
        if updated is None:
            raise RuntimeError(f"Employee with id {employee_id} not found or not updated.")
        conn.commit()
        return {
            "success": True,
            "employee": {
                "id": updated["id"],
                "name": updated["name"],
                "position": updated["position"],
                "department": updated["department"],
                "salary": float(updated["salary"]),
                "hire_date": updated["hire_date"].isoformat() if updated["hire_date"] else None,
            },
        }
    except Exception as e:
        raise RuntimeError(f"Error updating employee: {e}") from e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@app.tool
def delete_employee(employee_id: int) -> Dict[str, Any]:
    """Delete an employee by id"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        from psycopg2.extras import RealDictCursor
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(
            """
            DELETE FROM employees WHERE id = %s RETURNING id
            """,
            (employee_id,),
        )
        deleted = cursor.fetchone()
        if deleted is None:
            raise RuntimeError(f"Employee with id {employee_id} not found.")
        conn.commit()
        return {"success": True, "deleted_id": deleted["id"]}
    except Exception as e:
        raise RuntimeError(f"Error deleting employee: {e}") from e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(transport="sse", host="0.0.0.0", port=3000)
