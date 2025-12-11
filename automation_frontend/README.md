# Automation Frontend

Environment
- Copy .env.example to .env
  - REACT_APP_API_BASE should point to the backend: http://localhost:3001

API client
- src/api/client.js exports API_BASE and functions: uploadFile, parseJob, generateJob, executeJob, getAllureIndexUrl
- The client reads REACT_APP_API_BASE from process.env.

During development
- The backend enables CORS for http://localhost:3000 by default.
- Ensure the frontend dev server runs on port 3000.
