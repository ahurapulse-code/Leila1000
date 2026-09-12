from uuid import UUID

from app.legacy_migration import build_plan


WORKSPACE_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
TENANT_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
TRANSACTION_ID = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
EXPENSE_ID = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")


def test_legacy_rows_map_to_canonical_records_without_losing_visibility():
    plan, issues = build_plan(
        {
            "tenants": [{"id": str(TENANT_ID), "name": "واحد ۳ · سارا احمدی", "contract_date": "۱۴۰۵/۰۱/۰۱", "rent": 30000000, "deposit": 500000000}],
            "transactions": [{"id": str(TRANSACTION_ID), "tenant_id": str(TENANT_ID), "date": "۱۴۰۵/۰۲/۰۱", "amount": 30000000, "description": "اجاره اردیبهشت [نوع:اجاره]", "show_in_report": False}],
            "expenses": [{"id": str(EXPENSE_ID), "date": "۱۴۰۵/۰۲/۰۳", "amount": 4500000, "description": "سرویس کولر", "show_in_report": False}],
            "archives": [],
            "settings": [],
        },
        WORKSPACE_ID,
    )

    assert issues == []
    assert plan["tenants"][0]["name"] == "سارا احمدی"
    assert plan["tenants"][0]["unit"] == "واحد ۳"
    assert plan["transactions"][0]["kind"] == "rent"
    assert plan["transactions"][0]["description"] == "اجاره اردیبهشت"
    assert plan["transactions"][0]["show_in_report"] is False
    assert plan["expenses"][0]["show_in_report"] is False


def test_archived_expense_without_date_is_preserved_for_manual_review():
    plan, issues = build_plan(
        {
            "tenants": [],
            "transactions": [],
            "expenses": [{"id": str(EXPENSE_ID), "date": "—", "amount": 500000, "show_in_report": False, "archived": True}],
            "archives": [],
            "settings": [],
        },
        WORKSPACE_ID,
    )

    assert issues == []
    assert plan["expenses"][0]["spent_on"] is None
    assert plan["expenses"][0]["legacy_date_text"] == "—"
    assert plan["expenses"][0]["archived"] is True


def test_legacy_rows_with_invalid_dates_are_blocked():
    plan, issues = build_plan(
        {
            "tenants": [{"id": str(TENANT_ID), "name": "واحد ۱ · تست", "contract_date": "—", "rent": 1}],
            "transactions": [],
            "expenses": [],
            "archives": [],
            "settings": [],
        },
        WORKSPACE_ID,
    )

    assert plan["tenants"] == []
    assert len(issues) == 1
    assert issues[0].table == "tenants"
    assert "date" in issues[0].message
