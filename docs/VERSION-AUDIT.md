# Lila version audit

Reviewed on 2026-09-09 from all Lila ZIPs in the workspace.

## Decision

Use `Projects/Lila` as the only development and future production source.

Use `Projects/Lila/legacy-reference/Lila-app-fixed` only as a read-only reference for the current UI and legacy workflows. Do not deploy it as the long-term application.

## What was found

| Version | Assessment | Decision |
|---|---|---|
| `Lila-app-fixed.zip` | Most complete legacy static build. Live Supabase wiring exists, but the app is one very large `index.html` with inline handlers, browser `localStorage`, frontend-only role/PIN behavior, direct Supabase access, and cache-sensitive scripts. | Keep as read-only legacy reference. |
| `Lila-app-fixed (1).zip` | Byte-different copy of the same legacy line. | Archive only. |
| `Lila-app-fixed (2).zip` | Byte-identical to `(1)`. | Archive only. |
| `Lila-page5-transaction-polished.zip` | Older feature/presentation branch. | Archive only. |
| `Lila-cloudflare-S10-v238.zip` | Older Cloudflare/PWA packaging branch. | Archive only. |
| `Lila-v2-experimental (1).zip` | Best structural direction: FastAPI, PostgreSQL, Alembic migrations, server-side calculations, sessions, roles, audit events, and modular frontend. It is not a drop-in replacement because it has no imported legacy data and does not yet include every legacy workflow. | Use as the architectural base; it has been normalized into this project. |

## Data connection finding

The legacy static build is connected to the Supabase project and currently exposes readable records through its configured API: 9 tenants, 111 transactions, 3 expenses, and 3 archives at the time of review. The structured v2 app intentionally does not connect directly to that Supabase project; PostgreSQL is its future source of truth. This is why v2 must not be mistaken for a ready-to-use copy of the old app.

## Why the structured source wins

The canonical project separates the browser, API, database, migrations, and deployment. Financial calculations and authorization live on the server. Transactions have one canonical table, instead of allowing multiple browser-side representations to drift. Database changes are reviewable migrations, and exports/audit records provide a path to recovery.

## Cutover gate

Do not stop using the legacy app until all of these are complete:

- a dry-run importer maps Supabase fields to PostgreSQL while preserving IDs and Jalali dates;
- imported counts and financial totals match the legacy source;
- merge metadata, archives, deleted records, notes, and any other legacy-only fields are accounted for;
- backup and restore have been tested on a separate database;
- manager and owner flows pass on two devices;
- the structured app has HTTPS, non-default credentials, secrets outside the repository, CSRF/rate-limit protection appropriate to its host, and daily off-site backups.
