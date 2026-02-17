from fastapi import FastAPI
import psycopg2
import time
import os

app = FastAPI()

# Database connection settings
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}



def get_connection():
    return psycopg2.connect(**DB_CONFIG)


@app.get("/")
def read_root():
    return {"message": "SQL Performance API is running"}


@app.get("/top-customers")
def get_top_customers():
    conn = get_connection()
    cur = conn.cursor()

    query = """
    SELECT c.id, c.name, SUM(o.total_amount) AS total_spent
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    GROUP BY c.id, c.name
    ORDER BY total_spent DESC
    LIMIT 10;
    """

    start_time = time.time()
    cur.execute(query)
    results = cur.fetchall()
    execution_time = time.time() - start_time

    cur.close()
    conn.close()

    return {
        "execution_time_seconds": round(execution_time, 4),
        "data": results
    }

@app.get("/slow")
def get_slow_customers():
    conn = get_connection()
    cur = conn.cursor()

    start_time = time.time()

    # Slow query: aggreaget without using indexes
    cur.execute("""
        SELECT c.id, c.name, SUM(o.total_amount) AS total_spent
        FROM customers c
        JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id, c.name
        ORDER BY total_spent DESC
        LIMIT 10;
    """)

    result = cur.fetchall()
    elapsed_time = time.time() - start_time # end timer

    conn.close()

    return {
        "elapsed_time_seconds": elapsed_time,
        "top_customers": [
            {"id": row[0], "name": row[1], "total_spent": row[2]}
            for row in result
        ]
    }
