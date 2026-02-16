# SQL Performance Dashboard

Compare optimized vs slow query execution times and view the top N customers using a PostgreSQL database and Streamlit dashboard.

**Features**
- View top N customers by total spend.
- Compare execution times of optimized vs slow SQL queries.
- Dockerized setup for PostgreSQL and the Streamlit app.
- [Watch video demos of the project in action](https://www.youtube.com/playlist?list=PLgjQN-RUJyF_4grHQQzuGWU6YRaYqAr2G).

**Tech Stack**
- Python 3.10+
- Streamlit
- PostgreSQL
- Docker & Docker Compose
- Pandas, Psycopg2

**Setup**
1. Clone the repository:
```bash
git clone git@github.com:OsmanyGithub/sql-performance-api.git
cd sql-performance-api
```
2. Build and start Docker containers:
```bash
docker-compose up --build
```
Open the dashboard in your browser: http://localhost:8501

 **Usage**
- Select the top N customers to view and compare query performance.
- Stop the app with Ctrl + C.

**Project Structure**
- dashboard.py – Streamlit app code
- performance_lab.sql – PostgreSQL schema and sample data
- Dockerfile & docker-compose.yml – Docker setup
- requirements.txt – Python dependencies
