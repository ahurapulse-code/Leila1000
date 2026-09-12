from decimal import Decimal
from app.calculator import calculate_status


def test_lease_is_settled_when_all_due_months_are_paid():
    result = calculate_status(contract_start=(1405, 1, 1), monthly_rent=Decimal('1000000'), penalty_rate=Decimal('0'), payments=[((1405, 1, 1), Decimal('2000000'))], today=(1405, 2, 1))
    assert result['months_due'] == 2
    assert result['amount_paid'] == Decimal('2000000.00')
    assert result['balance'] == Decimal('0.00')
    assert result['status'] == 'settled'


def test_lease_reports_late_days_and_penalty():
    result = calculate_status(contract_start=(1405, 1, 1), monthly_rent=Decimal('1000000'), penalty_rate=Decimal('1'), payments=[], today=(1405, 2, 6))
    assert result['months_due'] == 2
    assert result['days_late'] == 36
    assert result['penalty'] == Decimal('720000.00')
    assert result['balance'] == Decimal('2000000.00')
