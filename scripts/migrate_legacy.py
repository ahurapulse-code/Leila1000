from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.legacy_migration import MigrationIssue, build_plan

TABLES = ("tenants", "transactions", "expenses", "archives", "settings")
PAGE_SIZE = 1000


def fetch_table(base_url: str, api_key: str, table: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    offset = 0
    while True:
        query = urlencode({"select": "*", "limit": PAGE_SIZE, "offset": offset})
        request = Request(
            f"{base_url.rstrip('/')}/rest/v1/{table}?{query}",
            headers={"apikey": api_key, "Authorization": f"Bearer {api_key}", "Accept": "application/json"},
        )
        try:
            with urlopen(request, timeout=30) as response:
                chunk = json.load(response)
        except (HTTPError, URLError) as exc:
            detail = getattr(exc, "read", lambda: b"")()
            raise RuntimeError(f"could not read {table}: {exc} {detail[:200].decode(errors='replace')}") from exc
        if not isinstance(chunk, list):
            raise RuntimeError(f"unexpected response for {table}")
        rows.extend(chunk)
        if len(chunk) < PAGE_SIZE:
            return rows
        offset += len(chunk)


def fetch_dataset(base_url: str, api_key: str) -> dict[str, list[dict[str, Any]]]:
    return {table: fetch_table(base_url, api_key, table) for table in TABLES}


def json_default(value: Any) -> Any:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, (Decimal, UUID)):
        return str(value)
    raise TypeError(type(value).__name__)


def report_text(dataset: dict[str, list[dict[str, Any]]], plan: dict[str, list[dict[str, Any]]], issues: list[MigrationIssue], workspace_id: UUID) -> str:
    lines = [
        "# Legacy migration dry run",
        "",
        f"- Generated: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"- Target workspace: `{workspace_id}`",
        "- Mode: read-only mapping; no PostgreSQL writes",
        "",
        "## Source rows",
        "",
        "| Table | Read | Mapped |",
        "| --- | ---: | ---: |",
    ]
    lines.extend(f"| `{table}` | {len(dataset.get(table, []))} | {len(plan.get(table, []))} |" for table in TABLES)
    lines.extend(["", "## Mapped totals", ""])
    for table, field in (("transactions", "amount"), ("expenses", "amount"), ("archives", "balance")):
        total = sum((row.get(field, Decimal("0")) for row in plan.get(table, [])), Decimal("0"))
        lines.append(f"- `{table}.{field}`: `{total:,.2f}`")
    lines.extend(["", "## Issues", ""])
    if issues:
        lines.extend(f"- `{issue.table}/{issue.row_id}`: {issue.message}" for issue in issues)
    else:
        lines.append("- None")
    lines.extend([
        "",
        "## Gate",
        "",
        "- Import is blocked while issues are present.",
        "- Review these totals against the legacy app before import.",
        "- Take and test a PostgreSQL backup before running with `--import`.",
        "- This report contains counts and totals only; it does not contain tenant names or raw records.",
    ])
    return "\n".join(lines) + "\n"


def upsert_rows(plan: dict[str, list[dict[str, Any]]]) -> None:
    from sqlalchemy import select
    from app.db import SessionLocal
    from app.models import Archive, Expense, Setting, Tenant, Transaction

    models = {"tenants": Tenant, "transactions": Transaction, "expenses": Expense, "archives": Archive, "settings": Setting}
    with SessionLocal.begin() as db:
        for table in TABLES:
            model = models[table]
            for data in plan[table]:
                existing = db.get(model, data["id"])
                if existing is not None and getattr(existing, "workspace_id", data["workspace_id"]) != data["workspace_id"]:
                    raise RuntimeError(f"{table}/{data['id']} belongs to another workspace")
                if existing is None and table in {"archives", "settings"}:
                    unique_field = "title" if table == "archives" else "key"
                    existing = db.scalar(select(model).where(model.workspace_id == data["workspace_id"], getattr(model, unique_field) == data[unique_field]))
                if existing is None:
                    db.add(model(**data))
                else:
                    for key, value in data.items():
                        if key != "id":
                            setattr(existing, key, value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or import the legacy Lila Supabase data")
    parser.add_argument("--source-url", default=os.getenv("LEGACY_SUPABASE_URL"))
    parser.add_argument("--source-key", default=os.getenv("LEGACY_SUPABASE_KEY"))
    parser.add_argument("--workspace-id", required=True, type=UUID)
    parser.add_argument("--report", type=Path, default=ROOT / "docs" / "migration-dry-run.md")
    parser.add_argument("--export", type=Path, help="optional raw JSON export; keep it outside git")
    parser.add_argument("--import", dest="do_import", action="store_true", help="write mapped rows to PostgreSQL after validation")
    args = parser.parse_args()
    if not args.source_url or not args.source_key:
        parser.error("set LEGACY_SUPABASE_URL and LEGACY_SUPABASE_KEY or pass both source options")
    if args.do_import and not os.getenv("DATABASE_URL"):
        parser.error("set DATABASE_URL before using --import")
    dataset = fetch_dataset(args.source_url, args.source_key)
    plan, issues = build_plan(dataset, args.workspace_id)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report_text(dataset, plan, issues, args.workspace_id), encoding="utf-8")
    print(f"Wrote validation report: {args.report}")
    if args.export:
        args.export.parent.mkdir(parents=True, exist_ok=True)
        args.export.write_text(json.dumps(dataset, ensure_ascii=False, indent=2, default=json_default), encoding="utf-8")
        print(f"Wrote raw export: {args.export}")
    if issues:
        print(f"Migration blocked: {len(issues)} issue(s) require review.")
        return 2
    if args.do_import:
        upsert_rows(plan)
        print("Import completed.")
    else:
        print("Dry run only. No database rows were changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
