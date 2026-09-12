# Data migration

The legacy Supabase project is read only. The canonical app imports into PostgreSQL through `scripts/migrate_legacy.py`; the browser never connects to Supabase.

## Dry run

Set the legacy connection values as temporary environment variables. Do not put them in `.env`, source control, or a report:

```bash
export LEGACY_SUPABASE_URL='https://your-project.supabase.co'
export LEGACY_SUPABASE_KEY='your-read-only-key'
python scripts/migrate_legacy.py \
  --workspace-id 'TARGET-WORKSPACE-UUID' \
  --report docs/migration-dry-run.md
```

The command reads `tenants`, `transactions`, `expenses`, `archives`, and `settings`, preserves UUIDs, converts Jalali dates, separates transaction kind from the legacy description tag, and prints counts, totals, and blocking issues. It does not write to PostgreSQL.

## Import gate

Only run this after the report has no issues and after taking a PostgreSQL backup:

```bash
export DATABASE_URL='postgresql+psycopg://...'
python scripts/migrate_legacy.py \
  --workspace-id 'TARGET-WORKSPACE-UUID' \
  --import
```

The target workspace must already exist. The importer is idempotent for tenants, transactions, expenses, archives, and settings: existing records with the same IDs are updated, and archive/settings conflicts are resolved within the selected workspace. Embedded legacy metadata inside archive records is preserved as JSON; it is not silently discarded or guessed into new business tables.

A raw export is intentionally opt-in and should be kept outside the repository:

```bash
python scripts/migrate_legacy.py \
  --workspace-id 'TARGET-WORKSPACE-UUID' \
  --export /secure/location/lila-legacy.json
```

After import, compare the dry-run totals with `/api/export`, restore the backup into a separate database, and complete the two-device acceptance test. Do not switch off the legacy app before those checks pass.
