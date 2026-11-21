
from decimal import Decimal

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
)

from .services import (
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
            refresh_villa_year(house, work_date.year)

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
                house=None,
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
                    house=house,
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
    rebuild_villa_financial_summaries(instance.house)


@receiver(post_delete, sender=VillaProgram)
def delete_villa_program_finances(sender, instance, **kwargs):
    rebuild_villa_financial_summaries(instance.house)


# --------------------------------------------------
# WORK ENTRIES
# --------------------------------------------------

@receiver(pre_save, sender=WorkEntry)
def remember_old_work_entry(sender, instance, **kwargs):
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
    old = getattr(instance, "_old_financial_values", None)

    if old:
        refresh_period(
            old["house_id"],
            old["service__department_id"],
            old["work_date"],
        )

    refresh_work_entry_related_periods(instance)


@receiver(post_delete, sender=WorkEntry)
def delete_work_entry_finances(sender, instance, **kwargs):
    refresh_work_entry_related_periods(instance)


# --------------------------------------------------
# INVOICES
# --------------------------------------------------

@receiver(pre_save, sender=Invoice)
def remember_old_invoice(sender, instance, **kwargs):
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
    old = getattr(instance, "_old_price_values", None)

    if old:
        refresh_service_price_work(old)

    refresh_service_price_work({
        "house_id": instance.house_id,
        "service_id": instance.service_id,
    })


@receiver(post_delete, sender=VillaServicePrice)
def delete_villa_service_price_finances(sender, instance, **kwargs):
    refresh_service_price_work({
        "house_id": instance.house_id,
        "service_id": instance.service_id,
    })


# --------------------------------------------------
# EMPLOYEE PAY RATE CHANGES
# --------------------------------------------------

@receiver(pre_save, sender=Employee)
def remember_old_employee_rate(sender, instance, **kwargs):
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



