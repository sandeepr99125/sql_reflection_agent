import sqlite3

# Schema definition passed to the LLM context
DB_SCHEMA = """
TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT,
    country TEXT
);

TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT,
    total_amount REAL,
    status TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
"""

def init_db() -> sqlite3.Connection:
    """Creates an in-memory SQLite database populated with test data."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT,
            country TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date TEXT,
            total_amount REAL,
            status TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
    """)

    cursor.executemany("INSERT INTO customers VALUES (?, ?, ?);", [
        (1, 'Alice Corp', 'USA'),
        (2, 'Bob Logistics', 'UK'),
        (3, 'Charlie Retail', 'USA'),
        (4, 'Delta Traders', 'Germany')
    ])

    cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?);", [
        (101, 1, '2026-01-15', 450.00, 'COMPLETED'),
        (102, 1, '2026-02-10', 850.00, 'COMPLETED'),
        (103, 2, '2026-02-12', 120.00, 'PENDING'),
        (104, 3, '2026-03-01', 950.00, 'COMPLETED'),
        (105, 3, '2026-03-05', 200.00, 'REFUNDED')
    ])

    conn.commit()
    return conn

def execute_query(conn: sqlite3.Connection, query: str):
    """Executes SQL query and returns results or error message."""
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [description[0] for description in cursor.description] if cursor.description else []
        return {"success": True, "data": results, "columns": columns, "error": None}
    except Exception as e:
        return {"success": False, "data": None, "columns": [], "error": str(e)}