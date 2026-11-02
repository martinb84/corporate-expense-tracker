from datetime import datetime
from decimal import Decimal

import pytest

from expense_system import ExpenseCategory, ExpenseStatus, Manager


@pytest.fixture
def manager() -> Manager:
    manager = Manager()
    manager.add_employee("employee-1", "Taylor", Decimal("200"))
    return manager


def test_add_employee_stores_employee_and_initializes_history(manager: Manager) -> None:
    employee = manager.employee["employee-1"]

    assert employee.name == "Taylor"
    assert employee.monthly_allowance == Decimal("200")
    assert employee.expense_history == []


def test_submit_expense_approves_valid_expense_and_records_it(
    manager: Manager,
) -> None:
    timestamp = datetime(2026, 5, 10, 12, 0)

    report = manager.submit_expense(
        "employee-1",
        ExpenseCategory.TRAVEL,
        Decimal("50"),
        timestamp,
    )

    assert report.report_id
    assert report.timestamp == timestamp
    assert report.employee_id == "employee-1"
    assert report.category is ExpenseCategory.TRAVEL
    assert report.amount == Decimal("50")
    assert report.status is ExpenseStatus.APPROVED
    assert report.reason is None
    assert manager.get_employee_expenses("employee-1") == [report]


def test_meal_at_single_meal_limit_is_approved(manager: Manager) -> None:
    report = manager.submit_expense(
        "employee-1",
        ExpenseCategory.MEALS,
        Decimal("75"),
        datetime(2026, 5, 10),
    )

    assert report.status is ExpenseStatus.APPROVED
    assert report.reason is None


def test_meal_over_single_meal_limit_is_rejected(manager: Manager) -> None:
    report = manager.submit_expense(
        "employee-1",
        ExpenseCategory.MEALS,
        Decimal("75.01"),
        datetime(2026, 5, 10),
    )

    assert report.status is ExpenseStatus.REJECTED
    assert report.reason == "Meal expenses cannot exceed $75."
    assert manager.get_monthly_spending("employee-1", 2026, 5) == Decimal("0")


def test_expense_at_monthly_allowance_is_approved(manager: Manager) -> None:
    report = manager.submit_expense(
        "employee-1",
        ExpenseCategory.EQUIPMENT,
        Decimal("200"),
        datetime(2026, 5, 10),
    )

    assert report.status is ExpenseStatus.APPROVED
    assert report.reason is None
    assert manager.get_monthly_spending("employee-1", 2026, 5) == Decimal("200")


def test_expense_exceeding_monthly_allowance_is_rejected(
    manager: Manager,
) -> None:
    manager.submit_expense(
        "employee-1",
        ExpenseCategory.TRAVEL,
        Decimal("150"),
        datetime(2026, 5, 10),
    )

    report = manager.submit_expense(
        "employee-1",
        ExpenseCategory.EQUIPMENT,
        Decimal("50.01"),
        datetime(2026, 5, 11),
    )

    assert report.status is ExpenseStatus.REJECTED
    assert report.reason == "Expense exceeds the monthly allowance."
    assert manager.get_monthly_spending("employee-1", 2026, 5) == Decimal("150")


def test_monthly_spending_counts_only_approved_expenses_in_requested_month(
    manager: Manager,
) -> None:
    manager.submit_expense(
        "employee-1",
        ExpenseCategory.TRAVEL,
        Decimal("40"),
        datetime(2026, 5, 10),
    )
    manager.submit_expense(
        "employee-1",
        ExpenseCategory.MEALS,
        Decimal("80"),
        datetime(2026, 5, 11),
    )
    manager.submit_expense(
        "employee-1",
        ExpenseCategory.TRAVEL,
        Decimal("30"),
        datetime(2026, 6, 10),
    )
    manager.submit_expense(
        "employee-1",
        ExpenseCategory.TRAVEL,
        Decimal("20"),
        datetime(2027, 5, 10),
    )

    assert manager.get_monthly_spending("employee-1", 2026, 5) == Decimal("40")
    assert manager.get_monthly_spending("employee-1", 2026, 6) == Decimal("30")
    assert manager.get_monthly_spending("employee-1", 2027, 5) == Decimal("20")


def test_submit_expense_raises_value_error_for_unknown_employee(
    manager: Manager,
) -> None:
    with pytest.raises(
        ValueError, match="Employee 'unknown' does not exist\\."
    ):
        manager.submit_expense(
            "unknown",
            ExpenseCategory.TRAVEL,
            Decimal("10"),
            datetime(2026, 5, 10),
        )


def test_get_monthly_spending_raises_value_error_for_unknown_employee(
    manager: Manager,
) -> None:
    with pytest.raises(
        ValueError, match="Employee 'unknown' does not exist\\."
    ):
        manager.get_monthly_spending("unknown", 2026, 5)


def test_get_employee_expenses_raises_value_error_for_unknown_employee(
    manager: Manager,
) -> None:
    with pytest.raises(
        ValueError, match="Employee 'unknown' does not exist\\."
    ):
        manager.get_employee_expenses("unknown")
