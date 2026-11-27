from decimal import Decimal
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import date
from django.db import transaction

from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from .models import (
    House,
    Department,
    Employee,
    ServiceCategory,
    VillaServicePrice,
    WorkEntry,
    Invoice,
    VillaProgram,
    VillaFinancialSummary, DepartmentFinancialSummary,
)

from .services import (
    monthly_employee_expenses, get_month_dates,
    refresh_villa_month,
    refresh_villa_year,
    rebuild_villa_financial_summaries,
    refresh_department_month,
    refresh_department_year,
)


# --------------------------------------------------
# GENERAL FINANCIAL REFRESH
# --------------------------------------------------

def refresh_period(house_id, department_id, work_date):
    """
    Refresh the monthly and yearly summaries affected by one dated record.

    WorkEntry snapshots are deliberately not recalculated here.
    Summaries use the saved historical employee/customer amounts.
    """

    if not work_date:
        return

    house = None

    if house_id:
        house = House.objects.filter(pk=house_id).first()

        if house:
            refresh_villa_month(house, work_date.year, work_date.month)
            refresh_villa_year(house, work_date.year, rebuild=False)

    if department_id:
        department = Department.objects.filter(pk=department_id).first()

        if department:
            # Department-wide summary (all villas combined).
            refresh_department_month(
                department,
                work_date.year,
                work_date.month,
                house=None,
            )

            refresh_department_year(
                department,
                work_date.year,
                house=None, rebuild=False,
            )

            # Department summary for this specific villa.
            if house_id and house:
                refresh_department_month(
                    department,
                    work_date.year,
                    work_date.month,
                    house=house,
                )

                refresh_department_year(
                    department,
                    work_date.year,
                    house=house, rebuild=False,
                )


def refresh_work_entry_related_periods(work_entry):
    refresh_period(
        work_entry.house_id,
        work_entry.service.department_id,
        work_entry.work_date,
    )


# --------------------------------------------------
# VILLA PROGRAMS
# --------------------------------------------------

@receiver(post_save, sender=VillaProgram)
def update_villa_program_finances(sender, instance, **kwargs):
    if kwargs.get("raw", False):
        return
    rebuild_villa_financial_summaries(instance.house)


@receiver(post_delete, sender=VillaProgram)
def delete_villa_program_finances(sender, instance, **kwargs):
    if kwargs.get("raw", False):
        return
    rebuild_villa_financial_summaries(instance.house)


# --------------------------------------------------
# WORK ENTRIES
# --------------------------------------------------

@receiver(pre_save, sender=WorkEntry)
def remember_old_work_entry(sender, instance, **kwargs):
    if kwargs.get("raw", False):
        return
    if instance.pk:
        instance._old_financial_values = (
            sender.objects.filter(pk=instance.pk)
            .values(
                "house_id",
                "work_date",
                "service__department_id",
            )
            .first()
        )
    else:
        instance._old_financial_values = None


@receiver(post_save, sender=WorkEntry)
def update_work_entry_finances(sender, instance, created, **kwargs):
    if kwargs.get("raw", False):
        return
    # Work hours affect the allocation of IKA and fuel across all villas.
    old = getattr(instance, "_old_financial_values", None)
    dates = {instance.work_date.replace(day=1)}
    if old:
        dates.add(old["work_date"].replace(day=1))
    for affected_date in dates:
        refresh_company_gas_period(affected_date)


@receiver(post_delete, sender=WorkEntry)
def delete_work_entry_finances(sender, instance, **kwargs):
    if kwargs.get("raw", False):
        return
    refresh_company_gas_period(instance.work_date)


# --------------------------------------------------
# INVOICES
# --------------------------------------------------

@receiver(pre_save, sender=Invoice)
def remember_old_invoice(sender, instance, **kwargs):
    if kwargs.get("raw", False):
        return
    if instance.pk:
        instance._old_financial_values = (
            sender.objects.filter(pk=instance.pk)
            .values("house_id", "invoice_date", "department_id")
            .first()
        )
    else:
        instance._old_financial_values = None


@receiver(post_save, sender=Invoice)
def update_invoice_finances(sender, instance, created, **kwargs):
    if kwargs.get("raw", False):
        return
    old = getattr(instance, "_old_financial_values", None)

    if old:
        refresh_period(
            old["house_id"],
            old["department_id"],
            old["invoice_date"],
        )

    refresh_period(
        instance.house_id,
        instance.department_id,
        instance.invoice_date,
    )


@receiver(post_delete, sender=Invoice)
def delete_invoice_finances(sender, instance, **kwargs):
    if kwargs.get("raw", False):
        return
    refresh_period(
        instance.house_id,
        instance.department_id,
        instance.invoice_date,
    )


# --------------------------------------------------
# VILLA SERVICE CHARGING PRICES
# --------------------------------------------------

@receiver(pre_save, sender=VillaServicePrice)
def remember_old_villa_service_price(sender, instance, **kwargs):
    if kwargs.get("raw", False):
        return
    if instance.pk:
        instance._old_price_values = (
            sender.objects.filter(pk=instance.pk)
            .values("house_id", "service_id")
            .first()
        )
    else:
        instance._old_price_values = None


def refresh_service_price_work(price_values):
    if not price_values:
        return

    entries = WorkEntry.objects.filter(
        house_id=price_values["house_id"],
        service_id=price_values["service_id"],
    ).select_related("service")

    for entry in entries:
        refresh_work_entry_related_periods(entry)


@receiver(post_save, sender=VillaServicePrice)
def update_villa_service_price_finances(sender, instance, **kwargs):
    if kwargs.get("raw", False):
        return
    old = getattr(instance, "_old_price_values", None)

    if old:
        refresh_service_price_work(old)

    refresh_service_price_work({
        "house_id": instance.house_id,
        "service_id": instance.service_id,
    })


@receiver(post_delete, sender=VillaServicePrice)
def delete_villa_service_price_finances(sender, instance, **kwargs):
    if kwargs.get("raw", False):
        return
    refresh_service_price_work({
        "house_id": instance.house_id,
        "service_id": instance.service_id,
    })


# --------------------------------------------------
# EMPLOYEE PAY RATE CHANGES
# --------------------------------------------------

@receiver(pre_save, sender=Employee)
def remember_old_employee_rate(sender, instance, **kwargs):
    if kwargs.get("raw", False):
        return
    """
    Remember the previous employee salary settings.

    salary_rate is a Python property, not a database field.
    Therefore, retrieve the actual salary fields instead.
    """

    if instance.pk:
        instance._old_salary_values = (
            sender.objects.filter(pk=instance.pk)
            .values(
                "salary_type",
                "hourly_rate",
                "daily_rate",
                "monthly_salary",
            )
            .first()
        )
    else:
        instance._old_salary_values = None


def refresh_employee_work_summaries(employee_id):
    """
    Refresh summaries for periods where this employee has work entries.

    Do not update WorkEntry.employee_cost or its salary snapshots.
    Historical costs remain exactly as originally recorded.
    """

    entries = WorkEntry.objects.filter(
        employee_id=employee_id,
    ).select_related(
        "house",
        "service__department",
    )

    seen = set()

    for entry in entries:
        key = (
            entry.house_id,
            entry.service.department_id,
            entry.work_date,
        )

        if key in seen:
            continue

        seen.add(key)

        refresh_work_entry_related_periods(entry)


@receiver(post_save, sender=Employee)
def update_employee_rate_finances(sender, instance, created, **kwargs):
    if kwargs.get("raw", False):
        return
    """
    Refresh affected financial summaries when an employee's
    salary type or applicable salary rate changes.

    Existing WorkEntry salary snapshots are not modified.
    """

    old = getattr(instance, "_old_salary_values", None)

    # New employees have no previous salary settings to compare.
    if not old:
        return

    old_rate = {
        "hourly": old["hourly_rate"],
        "daily": old["daily_rate"],
        "monthly": old["monthly_salary"],
    }.get(old["salary_type"], Decimal("0.00"))

    if (
        old["salary_type"] != instance.salary_type
        or old_rate != instance.salary_rate
    ):
        refresh_employee_work_summaries(instance.pk)





# --------------------------------------------------
# COMPANY GAS FINANCIAL REFRESH
# --------------------------------------------------

from .models import Company_Gas


_pending_months = ContextVar("financial_pending_months", default=None)

@contextmanager
def batch_financial_refresh():
    if _pending_months.get() is not None:
        yield
        return
    pending = set()
    token = _pending_months.set(pending)
    try:
        with transaction.atomic():
            yield
            for period in sorted(pending):
                _refresh_month(period)
    finally:
        _pending_months.reset(token)


def refresh_company_gas_period(expense_date):
    if not expense_date:
        return
    period = expense_date.replace(day=1)
    pending = _pending_months.get()
    if pending is not None:
        pending.add(period)
    else:
        with transaction.atomic():
            _refresh_month(period)


def _refresh_month(period):
    year, month = period.year, period.month
    start, end = get_month_dates(year, month)
    allocations = monthly_employee_expenses(year, month)
    # Include previous summary keys so moved/deleted records clear old totals.
    work = WorkEntry.objects.filter(work_date__range=(start, end))
    invoices = Invoice.objects.filter(invoice_date__range=(start, end))
    pairs = set(work.values_list("house_id", "service__department_id"))
    pairs.update(invoices.values_list("house_id", "department_id"))
    pairs.update(allocations)
    pairs.update(DepartmentFinancialSummary.objects.filter(period_type="monthly", period_start=start).values_list("house_id", "department_id"))
    house_ids = {h for h, d in pairs if h is not None}
    house_ids.update(VillaFinancialSummary.objects.filter(period_type="monthly", period_start=start).values_list("house_id", flat=True))
    pairs.update((None, d) for h, d in list(pairs) if d is not None)
    houses = House.objects.in_bulk(house_ids)
    departments = Department.objects.in_bulk({d for h, d in pairs if d is not None})
    for house in houses.values():
        refresh_villa_month(house, year, month, allocations=allocations)
        refresh_villa_year(house, year, rebuild=False)
    for h, d in sorted(pairs, key=lambda pair: (pair[1] or 0, pair[0] or 0)):
        if d not in departments or (h is not None and h not in houses):
            continue
        house = houses.get(h)
        refresh_department_month(departments[d], year, month, house=house, allocations=allocations)
        refresh_department_year(departments[d], year, house=house, rebuild=False)


@receiver(pre_save, sender=Company_Gas)
def remember_old_company_gas(sender, instance, **kwargs):
    if kwargs.get("raw", False):
        return

    if instance.pk:
        instance._old_gas_values = (
            sender.objects.filter(pk=instance.pk)
            .values("date", "employee_id", "price_total")
            .first()
        )
    else:
        instance._old_gas_values = None


@receiver(post_save, sender=Company_Gas)
def update_company_gas_finances(sender, instance, **kwargs):
    if kwargs.get("raw", False):
        return

    old = getattr(instance, "_old_gas_values", None)

    if old:
        old_date = old["date"]

        if (
            old_date.year,
            old_date.month,
        ) != (
            instance.date.year,
            instance.date.month,
        ):
            refresh_company_gas_period(old_date)

    refresh_company_gas_period(instance.date)


@receiver(post_delete, sender=Company_Gas)
def delete_company_gas_finances(sender, instance, **kwargs):
    if kwargs.get("raw", False):
        return

    refresh_company_gas_period(instance.date)


from .models import IKA
from django.utils import timezone

@receiver(pre_save, sender=IKA)
def remember_old_ika_period(sender, instance, **kwargs):
    if kwargs.get("raw", False):
        return
    instance._old_ika_period = (
        sender.objects.filter(pk=instance.pk).values("start_date", "end_date").first()
        if instance.pk else None
    )


@receiver(post_save, sender=IKA)
@receiver(post_delete, sender=IKA)
def refresh_ika_finances(sender, instance, **kwargs):
    if kwargs.get("raw", False):
        return
    today = timezone.localdate()
    periods = [(instance.start_date, instance.end_date)]
    old = getattr(instance, "_old_ika_period", None)
    if old:
        periods.append((old["start_date"], old["end_date"]))
    months = set()
    for start, end in periods:
        end = min(end or today, today)
        current = start.replace(day=1)
        while current <= end:
            months.add(current)
            current = date(current.year + (current.month == 12), current.month % 12 + 1, 1)
    with batch_financial_refresh():
        for period in sorted(months):
            refresh_company_gas_period(period)
