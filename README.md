# ai-requirements-automation-suite-6255-6266

Multi-container app:
- automation_backend (Flask, port 3001)
- automation_frontend (React, port 3000)
- automation_database (MySQL)

Environment
- Frontend: copy automation_frontend/.env.example to .env
  - REACT_APP_API_BASE=http://localhost:3001
- Backend: copy automation_backend/.env.example to .env (optional)
  - DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:PORT/DBNAME
  - Or omit to use fallback parsing from automation_database/db_connection.txt
  - If still unset, backend defaults to SQLite file: sqlite:///automation_dev.db

Wiring verification
- Frontend client uses process.env.REACT_APP_API_BASE (see automation_frontend/src/api/client.js)
- Backend reads DATABASE_URL from env, else parses automation_database/db_connection.txt, else SQLite
- CORS allows http://localhost:3000 by default (see automation_backend/app/__init__.py)
- Allure reports: GET /api/jobs/{id}/allure/index.html serves static HTML for latest run

Minimal end-to-end smoke checklist
1) Backend
   - cd automation_backend
   - python -m venv .venv && source .venv/bin/activate
   - pip install -r requirements.txt
   - Optional: cp .env.example .env and set DATABASE_URL or rely on fallback/SQLite
   - Run: python run.py  (listens on 3001)
   - Health: curl http://localhost:3001/

2) Frontend
   - cd automation_frontend
   - cp .env.example .env  (REACT_APP_API_BASE=http://localhost:3001)
   - npm install
   - npm start  (dev server on 3000)

3) Pipeline (via curl or UI)
   - Upload:   curl -F "file=@/path/to/reqs.csv" http://localhost:3001/api/upload
     -> capture returned job.id
   - Parse:    curl -X POST http://localhost:3001/api/parse/<job_id>
   - Generate: curl -X POST http://localhost:3001/api/generate/<job_id>
   - Execute:  curl -X POST http://localhost:3001/api/execute/<job_id>

4) Allure report
   - Open in browser: http://localhost:3001/api/jobs/<job_id>/allure/index.html
   - Notes: If Allure CLI not installed, results exist but static report may be empty.

Troubleshooting
- CORS: Backend allows http://localhost:3000; ensure frontend dev runs on port 3000.
- DB: Provide DATABASE_URL or ensure automation_database/db_connection.txt exists for fallback; otherwise SQLite is used.