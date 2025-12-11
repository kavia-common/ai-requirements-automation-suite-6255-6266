# Automation Backend

Flask API for uploading requirement files, parsing, generating simple pytest tests, executing them, and serving Allure reports.

Run
- Python entry: run.py (binds 0.0.0.0:3001)
- Env: copy .env.example to .env and adjust as needed
  - DATABASE_URL: mysql+pymysql://USER:PASSWORD@HOST:PORT/DBNAME
  - If unset, backend attempts fallback parse from automation_database/db_connection.txt
  - If both missing, defaults to SQLite file: sqlite:///automation_dev.db

CORS
- Configured to allow http://localhost:3000 for the React frontend.

Allure static route
- Latest run per job mounted at: /api/jobs/<job_id>/allure/index.html
- Specific run files: /api/allure/<job_id>/<run_id>/report/<path>

Minimal smoke test
1) Start backend: python run.py  (listens on 3001)
2) Upload a CSV:
   curl -F "file=@/path/to/reqs.csv" http://localhost:3001/api/upload
   Note the returned job.id (e.g., 1)
3) Parse:
   curl -X POST http://localhost:3001/api/parse/1
4) Generate:
   curl -X POST http://localhost:3001/api/generate/1
5) Execute:
   curl -X POST http://localhost:3001/api/execute/1
6) Open Allure (if generated):
   http://localhost:3001/api/jobs/1/allure/index.html

Notes
- If Allure CLI is not installed, the results will still be collected in allure-results, but the static report may be empty.
- Storage folders are created under STORAGE_BASE (default: ./storage).
