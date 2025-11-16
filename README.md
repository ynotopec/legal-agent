# Legal Case Management API

This project provides an open-source FastAPI service to manage legal disputes. It offers endpoints to capture cases, parties, documents, hearings, and tasks using a SQLite backend powered by SQLModel.

## Features
- Create, update, list, and delete legal cases.
- Attach parties with their roles and contact details.
- Track documents with metadata and optional multipart uploads.
- Maintain hearing schedules and notes.
- Manage action items with due dates and completion flags.

## Requirements
- Python 3.11+
- All dependencies are open-source (see `requirements.txt`).

## Getting Started
1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the API**
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Explore the documentation**
   Open http://localhost:8000/docs to interact with the OpenAPI interface.

## Configuration
Environment variables can override defaults defined in `app/settings.py`:
- `DATABASE_URL`: Database connection string (default `sqlite+aiosqlite:///./legal_agent.db`).
- `DB_ECHO`: Set to `true` to enable SQL logging.

## Example workflow
1. Create a case via `POST /cases` with title, description, jurisdiction, and status.
2. Add parties to the case with `POST /cases/{case_id}/parties`.
3. Upload evidence metadata with `POST /cases/{case_id}/documents` or multipart file uploads via `POST /cases/{case_id}/documents/upload`.
4. Schedule hearings using `POST /cases/{case_id}/hearings`.
5. Track next actions using `POST /cases/{case_id}/tasks` and list them with `GET /cases/{case_id}/tasks`.

## Tests
No automated tests are provided yet. You can validate the API manually through the Swagger UI or with tools like `curl` and `httpie`.
