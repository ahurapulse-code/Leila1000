# Lila project guidance

- PostgreSQL is the only canonical data store for the new app.
- Do not add business data to `localStorage`; browser storage may hold only presentation preferences.
- All schema changes require a new Alembic migration in `backend/alembic/versions/`.
- Keep tenant payment records in the canonical `transactions` table; do not create a parallel payments table.
- Keep date and money calculations in backend services, with tests before changing behavior.
- Keep authorization server-side. Frontend visibility controls are not security.
- Preserve RTL/PWA behavior: HTTPS, manifest, service worker, and mobile layout.
- Treat `legacy-reference/` as read-only reference material. Do not patch it as the production source.
- Never commit real passwords, session secrets, API keys, or a real data export.
- Before a production cutover, complete data migration, backup/restore testing, audit logging review, and two-device acceptance testing.
