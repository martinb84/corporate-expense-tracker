from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import uuid4


class ExpenseCategory(Enum):
    TRAVEL = "TRAVEL"
    MEALS = "MEALS"
    EQUIPMENT = "EQUIPMENT"
    OTHER = "OTHER"


class ExpenseStatus(Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


@dataclass
class ExpenseReport:
    report_id: str
    timestamp: datetime
    employee_id: str
    category: ExpenseCategory
    amount: Decimal
    status: ExpenseStatus
    reason: str | None = None


@dataclass
class Employee:
    employee_id: str
    name: str
    monthly_allowance: Decimal
    expense_history: list[ExpenseReport] = field(default_factory=list)


class Manager:
    def __init__(self) -> None:
        self.employee: dict[str, Employee] = {}

    def add_employee(
        self, employee_id: str, name: str, monthly_allowance: Decimal
    ) -> Employee:
        employee = Employee(employee_id, name, monthly_allowance)
        self.employee[employee_id] = employee
        return employee

    def _get_employee(self, employee_id: str) -> Employee:
        try:
            return self.employee[employee_id]
        except KeyError as error:
            raise ValueError(f"Employee '{employee_id}' does not exist.") from error

    def submit_expense(
        self,
        employee_id: str,
        category: ExpenseCategory,
        amount: Decimal,
        timestamp: datetime | None = None,
    ) -> ExpenseReport:
        employee = self._get_employee(employee_id)
        expense_timestamp = timestamp if timestamp is not None else datetime.now()
        reason = None

        if category is ExpenseCategory.MEALS and amount > Decimal("75"):
            status = ExpenseStatus.REJECTED
            reason = "Meal expenses cannot exceed $75."
        elif (
            self.get_monthly_spending(
                employee_id, expense_timestamp.year, expense_timestamp.month
            )
            + amount
            > employee.monthly_allowance
        ):
            status = ExpenseStatus.REJECTED
            reason = "Expense exceeds the monthly allowance."
        else:
            status = ExpenseStatus.APPROVED

        report = ExpenseReport(
            report_id=str(uuid4()),
            timestamp=expense_timestamp,
            employee_id=employee_id,
            category=category,
            amount=amount,
            status=status,
            reason=reason,
        )
        employee.expense_history.append(report)
        return report

    def get_monthly_spending(
        self, employee_id: str, year: int, month: int
    ) -> Decimal:
        employee = self._get_employee(employee_id)
        return sum(
            (
                report.amount
                for report in employee.expense_history
                if report.status is ExpenseStatus.APPROVED
                and report.timestamp.year == year
                and report.timestamp.month == month
            ),
            Decimal("0"),
        )

    def get_employee_expenses(self, employee_id: str) -> list[ExpenseReport]:
        return self._get_employee(employee_id).expense_history