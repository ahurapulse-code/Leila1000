# Legacy migration dry run

- Generated: 2026-09-09T18:55:42+00:00
- Target workspace: `aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa`
- Mode: read-only mapping; no PostgreSQL writes

## Source rows

| Table | Read | Mapped |
| --- | ---: | ---: |
| `tenants` | 9 | 9 |
| `transactions` | 111 | 111 |
| `expenses` | 3 | 3 |
| `archives` | 3 | 3 |
| `settings` | 2 | 2 |

## Mapped totals

- `transactions.amount`: `257,669,371.00`
- `expenses.amount`: `1,101,000.00`
- `archives.balance`: `272,700.00`

## Issues

- None

## Gate

- Import is blocked while issues are present.
- Review these totals against the legacy app before import.
- Take and test a PostgreSQL backup before running with `--import`.
- This report contains counts and totals only; it does not contain tenant names or raw records.
