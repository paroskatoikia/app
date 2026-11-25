from calendar import monthrange
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Sum, Min, Q
from django.utils import timezone

from .models import (
    House,
    IKA,
    Company_Gas,
    DepartmentCost,
    Department,
    WorkEntry,
    Invoice,
    VillaProgram,
    VillaFinancialSummary,
    DepartmentFinancialSummary,
)


ZERO = Decimal("0.00")
CENT = Decimal("0.01")


def money(value):
    return Decimal(value or ZERO).quantize(
        CENT,
        rounding=ROUND_HALF_UP,
    )


# --------------------------------------------------
# VILLA PROGRAM REVENUE
# --------------------------------------------------

def get_monthly_program_revenue(house, period_start):
    """
    Calculate monthly revenue for all active villa programs.

    BP, Gardening and Pool all use monthly prices.
    A full monthly price is charged if the program overlaps
    any part of the calendar month. No prorating.

    Blank start date = no lower date boundary.
    Blank end date = no upper date boundary.
    """

    period_start, period_end = get_month_dates(
        period_start.year,
        period_start.month,
    )

    programs = VillaProgram.objects.filter(house=house)

    total_revenue = ZERO

    for program in programs:
        if (
            (program.start_date is None or program.start_date <= period_end)
            and
            (program.end_date is None or program.end_date >= period_start)
        ):
            total_revenue += money(program.price)

    return money(total_revenue)


def get_yearly_program_revenue(house, year):
    """Add program revenue for all 12 calendar months."""

    total_revenue = ZERO

    for month in range(1, 13):
        month_start = date(year, month, 1)

        total_revenue += get_monthly_program_revenue(
            house,
            month_start,
        )

    return money(total_revenue)


# --------------------------------------------------
# DATE HELPERS
# --------------------------------------------------

def get_month_dates(year, month):
    period_start = date(year, month, 1)
    last_day = monthrange(year, month)[1]
    period_end = date(year, month, last_day)

    return period_start, period_end


def get_next_month(period_start):
    if period_start.month == 12:
        return date(period_start.year + 1, 1, 1)

    return date(
        period_start.year,
        period_start.month + 1,
        1,
    )


def aggregate_amounts(queryset, fields):
    result = queryset.aggregate(
        **{field: Sum(field) for field in fields}
    )

    return {
        field: money(result[field])
        for field in fields
    }


# --------------------------------------------------
# VILLA MONTHLY SUMMARY
# --------------------------------------------------

def monthly_employee_expenses(year, month):
    """Return allocations by (house_id, department_id); None house = overhead.

    Allocate each employee's monthly IKA and fuel by recorded hours. Round
    cumulative shares so the allocated cents always equal the original cost.
    """
    start, end = get_month_dates(year, month)
    if start > timezone.localdate():
        return {}
    costs = {}
    for row in IKA.objects.filter(start_date__lte=end).filter(Q(end_date__isnull=True) | Q(end_date__gte=start)).select_related("employee"):
        key = (row.employee_id, row.employee.department_id)
        costs.setdefault(key, [ZERO, ZERO])[0] += row.monthly_cost
    for row in Company_Gas.objects.filter(date__range=(start, end)).select_related("employee"):
        key = (row.employee_id, row.employee.department_id)
        costs.setdefault(key, [ZERO, ZERO])[1] += row.price_total
    allocations = {}
    for (employee_id, department_id), amounts in costs.items():
        groups = list(WorkEntry.objects.filter(employee_id=employee_id, work_date__range=(start, end), hours__gt=0).values("house_id", "service__department_id").annotate(weight=Sum("hours")).order_by("house_id", "service__department_id"))
        if not groups:
            groups = [{"house_id": None, "service__department_id": department_id, "weight": Decimal(1)}]
        total = sum(g["weight"] for g in groups)
        cumulative = ZERO
        previous = [ZERO, ZERO]
        for g in groups:
            cumulative += g["weight"]
            key = (g["house_id"], g["service__department_id"] or department_id)
            bucket = allocations.setdefault(key, [ZERO, ZERO])
            for i, amount in enumerate(amounts):
                current = money(amount * cumulative / total)
                bucket[i] += current - previous[i]
                previous[i] = current
    return allocations


def allocated_employee_expenses(year, month, house=None, department=None):
    values = [v for (h, d), v in monthly_employee_expenses(year, month).items()
              if (house is None or h == house.pk) and (department is None or d == department.pk)]
    return tuple(money(sum((v[i] for v in values), ZERO)) for i in range(2))


def company_invoice_queryset(queryset):
    # Unassigned invoices are general company costs per existing Invoice help text.
    return queryset.filter(Q(house__is_company_property=True) | Q(house__isnull=True))


def get_company_monthly_costs(year, month):
    """Direct company totals, including overhead with no recorded work hours.

    Do not add these totals again to allocated villa/department costs.
    """
    start, end = get_month_dates(year, month)
    ika, gas = allocated_employee_expenses(year, month)
    wages = money(WorkEntry.objects.filter(work_date__range=(start, end)).aggregate(v=Sum("employee_cost"))["v"])
    invoices = money(company_invoice_queryset(Invoice.objects.filter(invoice_date__range=(start, end))).aggregate(v=Sum("amount"))["v"])
    other = money(DepartmentCost.objects.filter(cost_date__range=(start, end)).aggregate(v=Sum("amount"))["v"])
    return {"employee_cost": wages, "ika_cost": ika, "gas_cost": gas, "company_invoice_cost": invoices, "other_department_cost": other, "total_cost": money(wages + ika + gas + invoices + other)}


def refresh_villa_month(house, year, month):
    period_start, period_end = get_month_dates(
        year,
        month,
    )

    work = WorkEntry.objects.filter(
        house=house,
        work_date__range=(period_start, period_end),
    ).aggregate(
        revenue=Sum("customer_charge"),
        employee_cost=Sum("employee_cost"),
    )

    invoices = Invoice.objects.filter(
        house=house,
        invoice_date__range=(period_start, period_end),
    ).aggregate(
        expenses=Sum("amount"),
    )

    work_revenue = money(work["revenue"])
    employee_cost = money(work["employee_cost"])
    invoice_expenses = money(invoices["expenses"])

    ika_cost, gas_cost = allocated_employee_expenses(year, month, house=house)
    company_invoice_cost = invoice_expenses if house.is_company_property else ZERO

    program_revenue = get_monthly_program_revenue(
        house,
        period_start,
    )

    # Total revenue includes work AND all programs.
    total_revenue = money(
        work_revenue + program_revenue
    )

    # Total cost includes employee costs AND invoices.
    total_cost = money(
        employee_cost + ika_cost + gas_cost + company_invoice_cost
    )

    # Gross margin is revenue minus all costs.
    gross_margin = money(
        total_revenue - total_cost
    )

    summary, created = VillaFinancialSummary.objects.update_or_create(
        house=house,
        period_type="monthly",
        period_start=period_start,
        defaults={
            "work_revenue": work_revenue,
            "program_revenue": program_revenue,
            "total_revenue": total_revenue,
            "employee_cost": employee_cost,
            "invoice_expenses": invoice_expenses,
            "ika_cost": ika_cost,
            "gas_cost": gas_cost,
            "company_invoice_cost": company_invoice_cost,
            "total_cost": total_cost,
            "gross_margin": gross_margin,
        },
    )

    return summary


# --------------------------------------------------
# VILLA YEARLY SUMMARY
# --------------------------------------------------

def refresh_villa_year(house, year):
    # Refresh every month first, so the yearly figures
    # are calculated from the latest monthly data.
    for month in range(1, 13):
        refresh_villa_month(
            house,
            year,
            month,
        )

    monthly_records = VillaFinancialSummary.objects.filter(
        house=house,
        period_type="monthly",
        period_start__year=year,
    )

    totals = aggregate_amounts(
        monthly_records,
        [
            "work_revenue",
            "program_revenue",
            "employee_cost",
            "invoice_expenses",
            "ika_cost",
            "gas_cost",
            "company_invoice_cost",
        ],
    )

    # Yearly revenue includes work AND program revenue.
    total_revenue = money(
        totals["work_revenue"] + totals["program_revenue"]
    )

    # Yearly cost includes employee costs AND invoices.
    total_cost = money(
        totals["employee_cost"] + totals["ika_cost"] + totals["gas_cost"] + totals["company_invoice_cost"]
    )

    # Gross margin is revenue minus all costs.
    gross_margin = money(
        total_revenue - total_cost
    )

    summary, created = VillaFinancialSummary.objects.update_or_create(
        house=house,
        period_type="yearly",
        period_start=date(year, 1, 1),
        defaults={
            **totals,
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "gross_margin": gross_margin,
        },
    )

    return summary


# --------------------------------------------------
# REBUILD ALL VILLA SUMMARIES
# --------------------------------------------------

def rebuild_villa_financial_summaries(house):
    today = timezone.localdate()

    first_month = timezone.localdate(
        house.created_at
    ).replace(day=1)

    # Include earlier program start dates if applicable.
    earliest_program_start = VillaProgram.objects.filter(
        house=house,
        start_date__isnull=False,
    ).aggregate(
        first_date=Min("start_date"),
    )["first_date"]

    if earliest_program_start:
        program_first_month = earliest_program_start.replace(day=1)

        if program_first_month < first_month:
            first_month = program_first_month

    current_month = first_month
    years = set()

    while current_month <= today.replace(day=1):
        refresh_villa_month(
            house,
            current_month.year,
            current_month.month,
        )

        years.add(current_month.year)

        current_month = get_next_month(current_month)

    # Recalculate yearly summaries after monthly summaries.
    for year in sorted(years):
        refresh_villa_year(
            house,
            year,
        )


# --------------------------------------------------
# DEPARTMENT MONTHLY SUMMARY
# --------------------------------------------------

def refresh_department_month(
    department,
    year,
    month,
    house=None,
):
    period_start, period_end = get_month_dates(
        year,
        month,
    )

    work_queryset = WorkEntry.objects.filter(
        service__department=department,
        work_date__range=(period_start, period_end),
    )

    invoice_queryset = Invoice.objects.filter(
        department=department,
        invoice_date__range=(period_start, period_end),
    )

    if house is not None:
        work_queryset = work_queryset.filter(
            house=house,
        )

        invoice_queryset = invoice_queryset.filter(
            house=house,
        )

    work = work_queryset.aggregate(
        revenue=Sum("customer_charge"),
        employee_cost=Sum("employee_cost"),
    )

    invoices = invoice_queryset.aggregate(
        expenses=Sum("amount"),
    )

    work_revenue = money(work["revenue"])
    employee_cost = money(work["employee_cost"])
    invoice_expenses = money(invoices["expenses"])

    # Department invoices are reimbursed by the customer separately.
    # Keep them visible, but do not include them in department costs
    # or subtract them from gross margin.
    total_revenue = work_revenue
    ika_cost, gas_cost = allocated_employee_expenses(year, month, house=house, department=department)
    company_invoice_cost = money(company_invoice_queryset(invoice_queryset).aggregate(v=Sum("amount"))["v"])
    total_cost = employee_cost + ika_cost + gas_cost + company_invoice_cost
    gross_margin = money(total_revenue - total_cost)

    summary, created = DepartmentFinancialSummary.objects.update_or_create(
        department=department,
        house=house,
        period_type="monthly",
        period_start=period_start,
        defaults={
            "work_revenue": work_revenue,
            "employee_cost": employee_cost,
            "invoice_expenses": invoice_expenses,
            "ika_cost": ika_cost,
            "gas_cost": gas_cost,
            "company_invoice_cost": company_invoice_cost,
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "gross_margin": gross_margin,
        },
    )

    return summary


# --------------------------------------------------
# DEPARTMENT YEARLY SUMMARY
# --------------------------------------------------

def refresh_department_year(
    department,
    year,
    house=None,
):
    for month in range(1, 13):
        refresh_department_month(department, year, month, house=house)
    monthly_records = DepartmentFinancialSummary.objects.filter(
        department=department,
        house=house,
        period_type="monthly",
        period_start__year=year,
    )

    totals = aggregate_amounts(
        monthly_records,
        [
            "work_revenue",
            "employee_cost",
            "invoice_expenses",
            "ika_cost",
            "gas_cost",
            "company_invoice_cost",
        ],
    )

    # Invoice expenses are reimbursed separately by the customer.
    # They remain visible in the summary but are excluded from costs
    # and gross margin.
    total_revenue = totals["work_revenue"]
    total_cost = totals["employee_cost"] + totals["ika_cost"] + totals["gas_cost"] + totals["company_invoice_cost"]
    gross_margin = money(total_revenue - total_cost)

    summary, created = DepartmentFinancialSummary.objects.update_or_create(
        department=department,
        house=house,
        period_type="yearly",
        period_start=date(year, 1, 1),
        defaults={
            **totals,
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "gross_margin": gross_margin,
        },
    )

    return summary


# --------------------------------------------------
# REBUILD ALL DEPARTMENT SUMMARIES
# --------------------------------------------------

def rebuild_department_financial_summaries(department):
    today = timezone.localdate()
    current_month = today.replace(day=1)

    work_start = WorkEntry.objects.filter(
        service__department=department,
    ).aggregate(
        first_date=Min("work_date"),
    )["first_date"]

    invoice_start = Invoice.objects.filter(
        department=department,
    ).aggregate(
        first_date=Min("invoice_date"),
    )["first_date"]

    existing_start = DepartmentFinancialSummary.objects.filter(
        department=department,
        period_type="monthly",
    ).aggregate(
        first_date=Min("period_start"),
    )["first_date"]

    possible_starts = [
        value
        for value in (
            work_start,
            invoice_start,
            existing_start,
        )
        if value is not None
    ]

    for model, field in [(IKA, "start_date"), (Company_Gas, "date")]:
        first = model.objects.filter(employee__department=department).aggregate(v=Min(field))["v"]
        if first:
            possible_starts.append(first)

    if not possible_starts:
        return

    first_month = min(possible_starts).replace(day=1)

    work_house_ids = WorkEntry.objects.filter(
        service__department=department,
    ).values_list(
        "house_id",
        flat=True,
    ).distinct()

    invoice_house_ids = Invoice.objects.filter(
        department=department,
        house__isnull=False,
    ).values_list(
        "house_id",
        flat=True,
    ).distinct()

    old_summary_house_ids = DepartmentFinancialSummary.objects.filter(
        department=department,
        house__isnull=False,
    ).values_list(
        "house_id",
        flat=True,
    ).distinct()

    house_ids = set(work_house_ids)
    house_ids.update(invoice_house_ids)
    house_ids.update(old_summary_house_ids)

    houses = House.objects.filter(
        id__in=house_ids,
    )

    current = first_month
    years = set()

    while current <= current_month:

        # Department total across all villas.
        refresh_department_month(
            department,
            current.year,
            current.month,
            house=None,
        )

        # Department summary for each individual villa.
        for house in houses:
            refresh_department_month(
                department,
                current.year,
                current.month,
                house=house,
            )

        years.add(current.year)
        current = get_next_month(current)

    for year in sorted(years):

        # Department total across all villas.
        refresh_department_year(
            department,
            year,
            house=None,
        )

        # Department summary for each villa.
        for house in houses:
            refresh_department_year(
                department,
                year,
                house=house,
            )


# -----------------------------------------------------------------------------
# SHARED MUNICIPAL WATER TARIFF CALCULATIONS
# -----------------------------------------------------------------------------

def calculate_municipal_water_cost(litres):
    """Price a volume using the shared progressive tiers; returns Decimal or None.

    None means the tariff table is empty, has gaps, or cannot price the volume.
    Prices are EUR per 1,000 litres. Does not include fixed municipal charges.
    """
    from .models import HouseWaterTariff

    volume = Decimal(str(litres))
    if volume < 0:
        return None
    brackets = list(HouseWaterTariff.objects.order_by("from_litres"))
    if not brackets or brackets[0].from_litres != 0:
        return None
    cursor = Decimal("0")
    total = Decimal("0")
    for bracket in brackets:
        if bracket.from_litres != cursor:
            return None
        if bracket.to_litres is not None and bracket.to_litres <= cursor:
            return None
        if volume > cursor:
            end = volume if bracket.to_litres is None else min(volume, bracket.to_litres)
            total += (end - cursor) * bracket.price_per_1000_litres / Decimal("1000")
        if bracket.to_litres is None:
            return money(total)
        cursor = bracket.to_litres
        if volume <= cursor:
            return money(total)
    return None


def compare_house_water_costs(house):
    """Historical comparison based on latest bill and latest tanker delivery.

    A bill reflects a COMPLETED period, not current live tariff usage.
    Does not infer physical source changes or claim verified savings.
    """
    from .models import HouseWaterBill, HouseWaterDelivery

    bill = HouseWaterBill.objects.filter(house=house).order_by("-billing_to", "-pk").first()
    delivery = HouseWaterDelivery.objects.filter(tank__house=house).order_by("-delivery_date", "-pk").first()
    if bill is None or delivery is None or not delivery.litres_delivered:
        return {"status": "insufficient_data", "reason": "A water bill and tanker delivery are needed."}
    municipal = calculate_municipal_water_cost(bill.billed_litres)
    if municipal is None:
        return {"status": "insufficient_data", "reason": "Complete the shared tariff brackets without gaps."}
    tanker_equivalent = money(bill.billed_litres * delivery.total_amount / delivery.litres_delivered)
    return {
        "status": "comparison_available",
        "billing_from": bill.billing_from.isoformat(),
        "billing_to": bill.billing_to.isoformat(),
        "litres": str(bill.billed_litres),
        "estimated_municipal_variable_cost_eur": str(municipal),
        "tanker_equivalent_cost_eur": str(tanker_equivalent),
        "lower_cost_source_for_this_volume": (
            "municipal" if municipal < tanker_equivalent else
            "tank" if tanker_equivalent < municipal else "equal"
        ),
        "note": "Historical whole-volume comparison only. Progressive switching decisions must compare marginal costs; actual bill fees and tanker minimum delivery costs may differ.",
    }

