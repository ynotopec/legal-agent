# Legal Case Management API

This project provides an open-source FastAPI service to manage legal disputes. It offers endpoints to capture cases, parties, documents, hearings, and tasks using a SQLite backend powered by SQLModel.

## Features
- Create, update, list, and delete legal cases.
- Attach parties with their roles and contact details.
- Track documents with metadata and optional multipart uploads.
- Build a defense dossier automatically from case metadata, parties, and uploaded documents.
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
- `API_KEYS`: Comma-separated allowed API keys. When set, all `/cases` routes require the `X-API-Key` header. When empty (default), auth is disabled — a warning is printed at startup; do not expose the API publicly in that mode.
- `UPLOAD_DIR`: Directory where multipart uploads are stored (default `./uploads`).
- `MAX_UPLOAD_MB`: Maximum accepted upload size in MB (default `10`; larger files are rejected with HTTP 413).

## API notes
- List endpoints accept `skip` and `limit` query parameters (`limit` defaults to 100, max 100).
- Multipart uploads (`POST /cases/{case_id}/documents/upload`) are persisted to `UPLOAD_DIR/{case_id}/` with sanitized filenames (path components stripped, unsafe characters replaced).
- `/health` is always public (for probes); all other routes enforce the API key when `API_KEYS` is set.

## Example workflow
1. Create a case via `POST /cases` with title, description, jurisdiction, and status.
2. Add parties to the case with `POST /cases/{case_id}/parties`.
3. Upload evidence metadata with `POST /cases/{case_id}/documents` or multipart file uploads via `POST /cases/{case_id}/documents/upload`.
4. Generate a consolidated defense dossier with `GET /cases/{case_id}/defense-dossier` to combine parties and documents without manual assembly.
5. Schedule hearings using `POST /cases/{case_id}/hearings`.
6. Track next actions using `POST /cases/{case_id}/tasks` and list them with `GET /cases/{case_id}/tasks`.

## Tests
No automated tests are provided yet. You can validate the API manually through the Swagger UI or with tools like `curl` and `httpie`.
