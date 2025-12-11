# ai-requirements-automation-suite-6255-6266

Multi-container app:
- automation_backend (Flask, port 3001)
- automation_frontend (React, port 3000)
- automation_database (MySQL)

Environment
- Frontend: copy automation_frontend/.env.example to .env
  - REACT_APP_API_BASE=http://localhost:3001
- Backend: copy automation_backend/.env.example to .env
  - DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:PORT/DBNAME
  - Or omit to use fallback parsing from automation_database/db_connection.txt

Minimal end-to-end smoke
1) Start backend: python automation_backend/run.py (listens on 3001)
2) Start frontend dev server (in its workspace) with REACT_APP_API_BASE pointing to http://localhost:3001
3) Use UI to upload a CSV; or via curl:
   - Upload:  curl -F "file=@/path/to/reqs.csv" http://localhost:3001/api/upload
   - Parse:   curl -X POST http://localhost:3001/api/parse/<job_id>
   - Generate:curl -X POST http://localhost:3001/api/generate/<job_id>
   - Execute: curl -X POST http://localhost:3001/api/execute/<job_id>
4) View Allure (if generated): http://localhost:3001/api/jobs/<job_id>/allure/index.html