import streamlit as st
import pandas as pd
import psycopg2
import time
import os

# -----------------------------
# Database connection config
# -----------------------------
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "performance_lab"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password")
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)

# -----------------------------
# Query Functions
# -----------------------------
def get_top_customers_fast(limit=10):
    conn = get_connection()
    cur = conn.cursor()
    start = time.time()

    cur.execute(f"""
        SELECT c.id, c.name, SUM(o.total_amount) AS total_spent
        FROM customers c
        JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id, c.name
        ORDER BY total_spent DESC
        LIMIT {limit};
    """)

    data = cur.fetchall()
    elapsed = time.time() - start
    cur.close()
    conn.close()

    df = pd.DataFrame(data, columns=["id", "name", "total_spent"])
    return df, elapsed


def get_top_customers_slow(limit=10):
    conn = get_connection()
    cur = conn.cursor()
    start = time.time()

    # Disable index usage separately
    cur.execute("SET enable_indexscan = OFF;")
    cur.execute("SET enable_bitmapscan = OFF;")

    cur.execute(f"""
        SELECT c.id, c.name, SUM(o.total_amount) AS total_spent
        FROM customers c
        JOIN orders o ON c.id = o.customer_id
        GROUP BY c.id, c.name
        ORDER BY total_spent DESC
        LIMIT {limit};
    """)

    data = cur.fetchall()
    elapsed = time.time() - start

    # Re-enable indexes
    cur.execute("SET enable_indexscan = ON;")
    cur.execute("SET enable_bitmapscan = ON;")

    cur.close()
    conn.close()

    df = pd.DataFrame(data, columns=["id", "name", "total_spent"])
    return df, elapsed

# -----------------------------
# Execution Plan Function
# -----------------------------
def get_query_plan(query, disable_index=False):
    """
    Returns the execution plan of a SQL query as JSON.
    If disable_index=True, disables index scans temporarily.
    """
    conn = get_connection()
    cur = conn.cursor()

    if disable_index:
        cur.execute("SET enable_indexscan = OFF;")
        cur.execute("SET enable_bitmapscan = OFF;")

    cur.execute(f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}")
    plan_json = cur.fetchone()[0][0]  # extract first element

    if disable_index:
        cur.execute("SET enable_indexscan = ON;")
        cur.execute("SET enable_bitmapscan = ON;")

    cur.close()
    conn.close()

    return plan_json

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("SQL Performance Dashboard")
st.write("Compare optimized vs slow query execution times and view the top N customers.")

# Slider for top-N
N = st.slider("Select Top N customers", min_value=5, max_value=100, value=10)

# Run queries
fast_df, fast_time = get_top_customers_fast(limit=N)
slow_df, slow_time = get_top_customers_slow(limit=N)

# Execution plans
optimized_query = f"""
    SELECT c.id, c.name, SUM(o.total_amount) AS total_spent
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    GROUP BY c.id, c.name
    ORDER BY total_spent DESC
    LIMIT {N};
"""
st.subheader("Optimized Query Execution Plan")
fast_plan = get_query_plan(optimized_query)
st.json(fast_plan)

st.subheader("Slow Query Execution Plan")
slow_plan = get_query_plan(optimized_query, disable_index=True)
st.json(slow_plan)

# Execution time display
st.subheader("Query Execution Time (seconds)")
st.write(f"Optimized query: {fast_time:.3f} s")
st.write(f"Slow query: {slow_time:.3f} s")

# Side-by-side tables
st.subheader("Top Customers Comparison")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Optimized Query**")
    st.dataframe(fast_df)
with col2:
    st.markdown("**Slow Query**")
    st.dataframe(slow_df)

# Execution time bar chart
st.subheader("Execution Time Comparison")
st.bar_chart({
    "Optimized": [fast_time],
    "Slow": [slow_time]
})
