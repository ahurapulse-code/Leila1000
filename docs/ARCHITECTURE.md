# Lila architecture

## Runtime layers

```text
Browser / PWA
    ↓ same-origin /api
FastAPI application
    ├── authentication and role checks
    ├── rent, penalty, balance, and report calculations
    ├── audit events and export
    └── SQLAlchemy data access
        ↓ Alembic migrations
PostgreSQL
```

## Ownership of responsibilities

| Concern | Owner | Rule |
|---|---|---|
| Persistent data | PostgreSQL | The database is the source of truth. |
| Schema changes | Alembic | Never edit production tables manually. |
| Rent and penalty calculations | Backend | The browser only displays server results. |
| Authorization | FastAPI session + membership | UI hiding is not authorization. |
| Presentation state | Frontend | It may use browser memory/storage only for non-critical preferences. |
| Offline shell | Service worker | Never cache `/api/*`; stale data must not masquerade as current data. |
| Backups | PostgreSQL dump + `/api/export` | JSON export is convenient, not a replacement for a database dump. |

## Canonical domain model

- `Workspace` isolates one property-management space.
- `User` and `Membership` provide identity and roles.
- `Tenant` is the lease/occupancy record.
- `Transaction` is the single canonical ledger for rent and deposit movements; `kind` distinguishes them.
- `Expense` stores property expenses.
- `Obligation` stores payable commitments and their payments.
- `Archive` and `Setting` hold durable history and workspace configuration.
- `AuditEvent` records sensitive changes.

## Rules that prevent future breakage

1. Every new feature starts with a domain decision and a migration, not a browser-only field.
2. A new API endpoint must have an explicit role requirement and a response schema.
3. A financial action must be idempotent or reject duplicate submissions safely.
4. Money is stored as exact numeric values, never floating point.
5. Dates entered in the UI remain explicit Jalali dates; conversion belongs in one backend utility.
6. Any legacy import must be repeatable, logged, and dry-runnable before it can write.
7. The old static app is never patched in parallel with this project; otherwise the two sources diverge again.

## Known gaps before cutover

- Build a tested Supabase-to-PostgreSQL importer that preserves IDs and all legacy metadata.
- Port the legacy transaction-detail and archive workflows into the modular frontend.
- Add automated API tests to CI and include a PostgreSQL test service.
- Replace development seed credentials before deployment.
- Add rate limiting and CSRF protection appropriate to the final hosting setup.
- Configure production HTTPS, secret storage, daily off-site backups, and restore drills.
