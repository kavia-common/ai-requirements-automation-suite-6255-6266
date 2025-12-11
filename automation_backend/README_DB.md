Database setup notes:
- This service uses SQLAlchemy with Flask-Migrate. Run-time will auto-create SQLite if DATABASE_URL is not provided.
- For MySQL, set DATABASE_URL to: mysql+pymysql://USER:PASSWORD@HOST:PORT/DBNAME
- Ensure DB exists. The service does not create the database itself.
- To create tables with migrations locally:
  1) flask db init
  2) flask db migrate -m "init"
  3) flask db upgrade

Environment variables (see .env.example):
- DATABASE_URL
- STORAGE_BASE
