# Deploy Lila on Render

The GitHub repository root must contain `backend/`, `frontend/`, `alembic.ini`, `render.yaml`, and `docker-compose.yml`. Upload the contents of the canonical project to the repository root; do not upload the ZIP as a nested folder.

`docker-compose.yml` is for local development. Render uses `render.yaml` and `backend/Dockerfile` to create one Docker web service and one managed PostgreSQL database.

## First deployment

1. Push the repository to GitHub.
2. In Render, create a Blueprint from that repository and review the resources before applying them.
3. Keep the database and web service in the same Render region.
4. Set the manager and owner email/password values when Render prompts for the `sync: false` variables. Do not commit them to GitHub.
5. Wait for the database to become available and then the web service to deploy.
6. Open `https://<your-service>.onrender.com/api/health`. It must return `{"status":"ok"}`.
7. Open the service URL and sign in with the manager account.

The Docker image runs Alembic migrations, seeds the initial accounts, and binds Uvicorn to Render's injected `PORT`. Render requires the server to bind to `0.0.0.0`; the Dockerfile already does this.

## Important production choice

The Blueprint uses Render's paid `0.1c-256mb` Postgres plan so the database is persistent. Do not change it to `free` for production: Render documents that free Postgres databases expire after 30 days and do not support backups. A free web service may also sleep; use a paid web plan if the tablet must open it without wake-up delay.

## Data cutover

Do not import the legacy data during the first deploy. First verify health, login, migrations, and a database backup. Then run the read-only migration dry run, compare counts and totals, and only after review run the import command from Render Shell. The browser never connects directly to Supabase.
