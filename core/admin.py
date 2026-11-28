from datetime import date
from decimal import Decimal

import nested_admin

from django.contrib import admin, messages
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.forms.models import BaseInlineFormSet
from django.utils import timezone
from django.utils.html import format_html

from .services import (
    rebuild_villa_financial_summaries,
    rebuild_department_financial_summaries,
    get_monthly_program_revenue,
    get_next_month,
    money,
)

from .models import (
    Ownership,
    Customer,
    CustomerPayment,
    House,
    VillaProgram,
    Department,
    ServiceCategory,
    VillaServicePrice,
    Employee,
    IKA,
    Company_Gas,
    WorkEntry,
    Invoice,
    DepartmentCost,
    Supplier,
    SupplierPayment,
    VillaFinancialSummary,
    DepartmentFinancialSummary,
    HouseInfo,
    HouseTechnician,
    HouseWaterReading,
    HouseWaterTank,
    HouseWaterTankReading,
    HouseWaterDelivery,
    HouseWaterSourcePeriod,
    HouseWaterTariff,
    HouseWaterBill,
    HouseElectricityBill,
)


# ==================================================
# CUSTOMER PAYMENTS
# ==================================================

@admin.register(CustomerPayment)
class CustomerPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "payment_date",
        "amount",
        "invoice",
        "reference",
        "has_receipt",
    )

    list_filter = (
        "customer",
        "payment_date",
    )

    search_fields = (
        "invoice__invoice_number",
        "invoice__supplier__name",
        "customer__name",
        "reference",
        "notes",
    )

    autocomplete_fields = ("customer", "invoice")

    ordering = ("-payment_date", "-id")


    @admin.display(boolean=True, description="Receipt")
    def has_receipt(self, obj):
        return bool(obj.receipt)


    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "invoice":
            kwargs["queryset"] = Invoice.objects.filter(ownership=Ownership.CUSTOMER)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# ==================================================
# SUPPLIERS
# ==================================================

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "tax_number",
        "phone",
        "email",
    )

    search_fields = (
        "name",
        "tax_number",
        "email",
    )

    ordering = ("name",)


# ==================================================
# VILLA PROGRAM INLINE
# ==================================================

class VillaProgramInline(nested_admin.NestedTabularInline):
    model = VillaProgram
    extra = 1

    fields = (
        "program_type",
        "price",
        "start_date",
        "end_date",
    )


# ==================================================
# CUSTOMER ADMIN + CUSTOMER BILLING CARD
# ==================================================

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "company_name",
        "email",
        "phone",
        "billing_balance",
    )

    search_fields = (
        "name",
        "company_name",
        "email",
        "phone",
    )

    readonly_fields = (
        "customer_billing_card",
    )

    fieldsets = (
        (
            "Customer information",
            {
                "fields": (
                    "name",
                    "company_name",
                    "email",
                    "phone",
                    "address",
                    "tax_number",
                    "notes",
                )
            },
        ),
        (
            "Customer Billing Card",
            {
                "fields": (
                    "customer_billing_card",
                ),
            },
        ),
    )

    def get_billing_totals(self, customer):
        """
        Calculate the customer's outstanding balance
        from the existing source records.

        Charges:
        - WorkEntry.customer_charge
        - WorkEntry.additional_charges
        - VillaProgram monthly price
        - Villa-assigned supplier invoices

        Credits:
        - CustomerPayment.amount

        All amounts are calculated through today.
        """

        today = timezone.localdate()

        houses = list(customer.villas.filter(is_company_property=False))

        house_ids = [
            house.pk
            for house in houses
        ]

        # ------------------------------------------
        # WORK CHARGES
        # ------------------------------------------

        work_result = WorkEntry.objects.filter(
            ownership=Ownership.CUSTOMER,
            house_id__in=house_ids,
            work_date__lte=today,
        ).aggregate(
            total=Sum("customer_charge"),
            additional=Sum("additional_charges"),
        )

        work_total = money(work_result["total"])
        additional_total = money(work_result["additional"])

        # ------------------------------------------
        # REIMBURSABLE INVOICES
        # ------------------------------------------

        invoice_result = Invoice.objects.filter(
            ownership=Ownership.CUSTOMER,
            house_id__in=house_ids,
            invoice_date__lte=today,
        ).aggregate(
            total=Sum("amount")
        )

        invoice_total = money(invoice_result["total"])

        # ------------------------------------------
        # CUSTOMER PAYMENTS
        # ------------------------------------------

        payment_result = CustomerPayment.objects.filter(
            customer=customer,
            payment_date__lte=today,
        ).aggregate(
            total=Sum("amount")
        )

        payment_total = money(payment_result["total"])

        # ------------------------------------------
        # MONTHLY VILLA PROGRAMS
        # ------------------------------------------

        program_total = Decimal("0.00")
        undated_programs = []

        current_month = today.replace(day=1)

        for house in houses:

            programs = list(
                VillaProgram.objects.filter(house=house)
            )

            if not programs:
                continue

            # The villa creation month is used as the
            # provisional start for programs that do
            # not have an explicit start date.
            #
            # A program with a start_date uses its
            # actual starting month instead.

            villa_first_month = (
                timezone.localdate(house.created_at)
                .replace(day=1)
            )

            first_months = []

            for program in programs:

                if program.start_date:
                    first_months.append(
                        program.start_date.replace(day=1)
                    )
                else:
                    first_months.append(villa_first_month)

                    undated_programs.append(
                        f"{house.name}: "
                        f"{program.get_program_type_display()}"
                    )

            if not first_months:
                continue

            month = min(first_months)

            while month <= current_month:

                # Reuse the existing service function.
                # It charges the full monthly price
                # whenever the program overlaps a month.

                # For undated programs, exclude months
                # before the villa creation month.
                if month < villa_first_month:
                    dated_programs_total = Decimal("0.00")

                    for program in programs:
                        if (
                            program.start_date is not None
                            and program.start_date <=
                            get_month_end(month)
                            and (
                                program.end_date is None
                                or program.end_date >= month
                            )
                        ):
                            dated_programs_total += money(
                                program.price
                            )

                    program_total += dated_programs_total

                else:
                    program_total += (
                        get_monthly_program_revenue(
                            house,
                            month,
                        )
                    )

                month = get_next_month(month)

        program_total = money(program_total)

        # ------------------------------------------
        # TOTAL CUSTOMER CHARGES
        # ------------------------------------------

        total_charges = money(
            work_total
            + additional_total
            + program_total
            + invoice_total
        )

        # ------------------------------------------
        # OUTSTANDING BALANCE
        # ------------------------------------------

        balance = money(
            total_charges - payment_total
        )

        return {
            "work": work_total,
            "additional": additional_total,
            "programs": program_total,
            "invoices": invoice_total,
            "charges": total_charges,
            "payments": payment_total,
            "balance": balance,
            "undated_programs": undated_programs,
            "villa_count": len(houses),
        }

    @admin.display(description="Outstanding balance")
    def billing_balance(self, obj):

        totals = self.get_billing_totals(obj)

        return f"€{totals['balance']:,.2f}"

    @admin.display(description="Customer account")
    def customer_billing_card(self, obj):

        if not obj or not obj.pk:
            return "Save the customer to see billing details."

        totals = self.get_billing_totals(obj)

        warning = ""

        if totals["undated_programs"]:
            warning = format_html(
                "<p style='color:#b45309;'>"
                "<strong>Billing date warning:</strong> "
                "{} program(s) have no start date. "
                "Their charges are estimated from the "
                "villa creation month. Confirm their "
                "actual billing start dates before "
                "relying on this balance."
                "</p>",
                len(totals["undated_programs"]),
            )

        return format_html(
            "<div style='max-width:750px;"
            "line-height:2;padding:12px 0;'>"

            "<h2>Customer Billing Card</h2>"

            "<p><strong>Customer:</strong> {}</p>"

            "<p><strong>Managed villas:</strong> {}</p>"

            "<hr>"

            "<h3>Charges</h3>"

            "<p>Work charges: <strong>€{}</strong></p>"
            "<p>Additional charges: <strong>€{}</strong></p>"

            "<p>BP / Gardening / Pool: "
            "<strong>€{}</strong></p>"

            "<p>Reimbursable villa invoices: "
            "<strong>€{}</strong></p>"

            "<hr>"

            "<p><strong>Total charges: €{}</strong></p>"

            "<h3>Payments</h3>"

            "<p>Total customer payments: "
            "<strong>€{}</strong></p>"

            "<hr>"

            "<h2>Outstanding balance: €{}</h2>"

            "<p style='color:#777;'>"
            "Balance includes charges and payments "
            "through today."
            "</p>"

            "{}"

            "</div>",

            obj.name,
            totals["villa_count"],
            f"{totals['work']:,.2f}",
            f"{totals['additional']:,.2f}",
            f"{totals['programs']:,.2f}",
            f"{totals['invoices']:,.2f}",
            f"{totals['charges']:,.2f}",
            f"{totals['payments']:,.2f}",
            f"{totals['balance']:,.2f}",
            warning,
        )


def get_month_end(month_start):
    """
    Return the final day of a calendar month.
    """
    from calendar import monthrange

    last_day = monthrange(
        month_start.year,
        month_start.month,
    )[1]

    return date(
        month_start.year,
        month_start.month,
        last_day,
    )


# ==================================================
# VILLA FINANCIAL SUMMARY INLINE
# ==================================================

class VillaFinancialSummaryInline(nested_admin.NestedTabularInline):
    model = VillaFinancialSummary

    extra = 0
    can_delete = False

    fields = (
        "period_type",
        "period_start",
        "work_revenue",
        "program_revenue",
        "total_revenue",
        "employee_cost",
        "invoice_expenses",
        "company_invoice_cost",
        "ika_cost",
        "gas_cost",
        "total_cost",
        "gross_margin",
    )

    readonly_fields = fields


# ==================================================
# DEPARTMENT FINANCIAL SUMMARY INLINE
# ==================================================

class DepartmentFinancialSummaryInline(admin.TabularInline):
    model = DepartmentFinancialSummary
    fk_name = "department"

    extra = 0
    can_delete = False

    fields = (
        "house",
        "period_type",
        "period_start",
        "work_revenue",
        "employee_cost",
        "invoice_expenses",
        "company_invoice_cost",
        "ika_cost",
        "gas_cost",
        "total_cost",
        "gross_margin",
    )

    readonly_fields = fields


# ==================================================
# VILLA SERVICE PRICE INLINE
# ==================================================

class VillaServicePriceInline(nested_admin.NestedTabularInline):
    model = VillaServicePrice
    extra = 1


# ==================================================
# VILLA INFORMATION AND TANK INLINES
# ==================================================

class VillaHouseTechnicianInline(nested_admin.NestedTabularInline):
    model = HouseTechnician
    extra = 1
    fields = ("technician_type", "name", "phone", "company", "email", "is_primary", "notes")


class HouseInfoInline(nested_admin.NestedStackedInline):
    model = HouseInfo
    inlines = [VillaHouseTechnicianInline]
    extra = 1
    max_num = 1
    can_delete = False
    fieldsets = (
        ("Wi-Fi", {"fields": ("wifi_name", "wifi_password")}),
        ("Alarm", {"fields": ("alarm_code", "alarm_company", "alarm_phone")}),
    )


class HouseWaterTankInline(nested_admin.NestedTabularInline):
    model = HouseWaterTank
    extra = 0
    fields = ("name", "capacity_litres", "minimum_level_litres", "notes")


# ==================================================
# VILLA ADMIN
# ==================================================

@admin.register(House)
class VillaAdmin(nested_admin.NestedModelAdmin):

    list_display = (
        "name",
        "customer",
        "area",
        "is_company_property",
        "monthly_program_revenue",
    )

    list_filter = ("area", "is_company_property")

    search_fields = (
        "name",
        "customer__name",
        "customer__company_name",
    )

    inlines = [
        VillaProgramInline,
        VillaServicePriceInline,
        HouseWaterTankInline,
        HouseInfoInline,
        VillaFinancialSummaryInline,
    ]

    actions = ["recalculate_finances"]

    fieldsets = (
        (
            "Villa information",
            {
                "fields": (
                    "name",
                    "customer",
                    "is_company_property",
                    "area",
                    "description",
                )
            },
        ),
    )

    @admin.display(description="Monthly Program Revenue (€)")
    def monthly_program_revenue(self, obj):
        period = timezone.localdate().replace(day=1)
        return f"€{get_monthly_program_revenue(obj, period):,.2f}"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        context = getattr(response, "context_data", None)
        if context and "cl" in context:
            period = timezone.localdate().replace(day=1)
            total = sum(
                (get_monthly_program_revenue(villa, period)
                 for villa in context["cl"].queryset.iterator()),
                Decimal("0.00"),
            )
            context["title"] = (
                f'{context["title"]} — Monthly Program Revenue '
                f'({period:%B %Y}): €{total:,.2f}'
            )
        return response

    @admin.action(
        description="Recalculate villa financial summaries"
    )
    def recalculate_finances(self, request, queryset):

        for villa in queryset:
            rebuild_villa_financial_summaries(villa)

        self.message_user(
            request,
            "Villa financial summaries recalculated successfully.",
        )


# ==================================================
# DEPARTMENT ADMIN
# ==================================================

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = ("name",)

    search_fields = ("name",)

    inlines = [
        DepartmentFinancialSummaryInline,
    ]

    actions = ["recalculate_finances"]

    @admin.action(
        description="Recalculate department financial summaries"
    )
    def recalculate_finances(self, request, queryset):

        for department in queryset:
            rebuild_department_financial_summaries(
                department
            )

        self.message_user(
            request,
            "Department financial summaries recalculated successfully.",
        )


# ==================================================
# SERVICE CATEGORY ADMIN
# ==================================================

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "department",
    )

    list_filter = ("department",)

    search_fields = (
        "name",
        "department__name",
    )


# ==================================================
# VILLA SERVICE PRICE ADMIN
# ==================================================

@admin.register(VillaServicePrice)
class VillaServicePriceAdmin(admin.ModelAdmin):

    list_display = (
        "house",
        "service",
        "hourly_price",
    )

    list_filter = (
        "house",
        "service__department",
        "service",
    )

    search_fields = (
        "house__name",
        "service__name",
    )


# ==================================================
# EMPLOYEE ADMIN
# ==================================================

class CompanyGasInline(admin.TabularInline):
    model = Company_Gas
    extra = 0


from .models import IKAPackage
from django.db import transaction
from datetime import timedelta

@admin.register(IKAPackage)
class IKAPackageAdmin(admin.ModelAdmin):
    list_display = ("name", "monthly_cost", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


class IKAAssignmentForm(forms.ModelForm):
    is_active = forms.BooleanField(required=False, initial=True, help_text="Uncheck to stop charges after this month.")
    class Meta:
        model = IKA
        fields = ("employee", "package", "start_date", "notes")
        labels = {"start_date": "Starting month (first day)"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["package"].required = True
        self.fields["package"].queryset = IKAPackage.objects.filter(is_active=True) | IKAPackage.objects.filter(pk=self.instance.package_id)
        if self.instance.pk:
            self.fields["employee"].disabled = True
            self.fields["start_date"].disabled = True
            self.fields["is_active"].initial = self.instance.end_date is None
        else:
            self.fields["start_date"].initial = timezone.localdate().replace(day=1)

    def clean(self):
        data = super().clean()
        if not self.instance.pk and not data.get("is_active"):
            self.add_error("is_active", "New assignments must be active.")
        if not self.instance.pk and data.get("employee") and data.get("start_date"):
            if IKA.objects.filter(employee=data["employee"]).filter(models.Q(end_date__isnull=True) | models.Q(end_date__gte=data["start_date"])).exists():
                self.add_error("start_date", "An existing assignment overlaps this month.")
        return data


from django.db import models

@admin.register(IKA)
class IKAAdmin(admin.ModelAdmin):
    form = IKAAssignmentForm
    list_display = ("employee", "package_name", "monthly_cost", "start_date", "end_date", "active_status")
    list_filter = ("employee", "package", "start_date")
    search_fields = ("employee__first_name", "employee__last_name", "package_name", "notes")
    readonly_fields = ("monthly_cost", "end_date")
    fields = ("employee", "package", "start_date", "is_active", "monthly_cost", "end_date", "notes")

    @admin.display(boolean=True, description="Is active")
    def active_status(self, obj):
        return obj.end_date is None

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request, obj) and (obj is None or obj.end_date is None)

    def has_delete_permission(self, request, obj=None):
        return False

    @transaction.atomic
    def save_model(self, request, obj, form, change):
        today = timezone.localdate()
        next_month = get_next_month(today.replace(day=1))
        package = obj.package
        if not change:
            obj.monthly_cost = package.monthly_cost
            obj.package_name = package.name
            obj.save()
            return
        old = IKA.objects.select_for_update().get(pk=obj.pk)
        active = form.cleaned_data["is_active"]
        changed = old.package_id != package.pk or old.monthly_cost != package.monthly_cost or old.package_name != package.name
        if not active:
            if old.start_date >= next_month:
                old.delete()
                return
            old.end_date = next_month - timedelta(days=1)
            old.notes = obj.notes
            old.save()
        elif changed and old.start_date < next_month:
            old.end_date = next_month - timedelta(days=1)
            old.save()
            IKA.objects.create(employee=old.employee, package=package, package_name=package.name, monthly_cost=package.monthly_cost, start_date=next_month, notes=obj.notes)
        else:
            obj.monthly_cost = package.monthly_cost
            obj.package_name = package.name
            obj.save()


@admin.register(Company_Gas)
class CompanyGasAdmin(admin.ModelAdmin):
    list_display = ("employee", "gas_type", "price_total", "date", "invoice_pdf")
    list_filter = ("gas_type", "date", "employee")
    date_hierarchy = "date"
    search_fields = ("employee__first_name", "employee__last_name", "notes")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    inlines = [CompanyGasInline]

    list_display = (
        "first_name",
        "last_name",
        "department",
        "salary_type",
        "salary_rate",
        "is_active",
    )

    list_filter = (
        "department",
        "salary_type",
        "is_active",
    )

    search_fields = (
        "first_name",
        "last_name",
        "email",
        "phone",
    )

    fieldsets = (
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "department",
                    "hire_date",
                    "is_active",
                )
            },
        ),
        (
            "Salary Information",
            {
                "fields": (
                    "salary_type",
                    "hourly_rate",
                    "daily_rate",
                    "monthly_salary",
                )
            },
        ),
        (
            "Additional Information",
            {
                "fields": ("notes",)
            },
        ),
    )


# ==================================================
# WORK ENTRY ADMIN
# ==================================================

@admin.register(WorkEntry)
class WorkEntryAdmin(admin.ModelAdmin):

    list_display = (
        "work_date",
        "ownership",
        "employee",
        "house",
        "service",
        "hours",
        "customer_hourly_rate_snapshot",
        "customer_charge",
        "additional_charges",
        "total_customer_charge_display",
        "employee_cost",
        "total_company_cost_display",
        "gross_margin",
    )

    list_filter = (
        "ownership",
        "work_date",
        "employee",
        "house",
        "service",
        "service__department",
    )

    search_fields = (
        "employee__first_name",
        "employee__last_name",
        "house__name",
        "description",
        "additional_charges_notes",
    )

    date_hierarchy = "work_date"

    readonly_fields = (
        "employee_salary_type_snapshot",
        "employee_rate_snapshot",
        "employee_cost",
        "customer_hourly_rate_snapshot",
        "customer_charge",
        "total_customer_charge_display",
        "created_at",
    )

    fieldsets = (
        ("Work information", {"fields": (
            "ownership", "employee", "house", "service", "work_date", "hours", "description",
        )}),
        ("Additional charges", {"fields": (
            "additional_charges", "additional_charges_notes",
        )}),
        ("Financial information", {"fields": (
            "customer_hourly_rate_snapshot", "customer_charge",
            "total_customer_charge_display", "employee_salary_type_snapshot",
            "employee_rate_snapshot", "employee_cost", "created_at",
        )}),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj is not None:
            return fieldsets
        return tuple(
            (title, {**options, "fields": tuple(
                field for field in options["fields"] if field != "ownership"
            )})
            for title, options in fieldsets
        )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.ownership = Ownership.CUSTOMER
        super().save_model(request, obj, form, change)

    @admin.display(description="Total customer charge")
    def total_customer_charge_display(self, obj):
        if not obj or not obj.pk:
            return "Calculated after saving"
        return f"€{obj.total_customer_charge:,.2f}"

    @admin.display(description="Total company cost")
    def total_company_cost_display(self, obj):
        return obj.total_company_cost


# ==================================================
# INVOICE ADMIN
# ==================================================

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    list_display = (
        "ownership",
        "invoice_date",
        "supplier",
        "invoice_number",
        "department",
        "house",
        "amount",
    )

    list_filter = (
        "ownership",
        "invoice_date",
        "department",
        "house",
    )

    search_fields = (
        "supplier__name",
        "invoice_number",
        "description",
        "department__name",
        "house__name",
    )

    autocomplete_fields = ("house", "supplier", "department")

    def get_search_results(self, request, queryset, search_term):
        queryset, distinct = super().get_search_results(request, queryset, search_term)
        if request.GET.get("field_name") == "invoice":
            scope = {"customerpayment": Ownership.CUSTOMER, "supplierpayment": Ownership.COMPANY}.get(request.GET.get("model_name"))
            if scope and request.GET.get("app_label") == "core":
                queryset = queryset.filter(ownership=scope)
        return queryset, distinct

    date_hierarchy = "invoice_date"


# ==================================================
# DEPARTMENT COST ADMIN
# ==================================================

@admin.register(DepartmentCost)
class DepartmentCostAdmin(admin.ModelAdmin):

    list_display = (
        "cost_date",
        "department",
        "house",
        "description",
        "amount",
    )

    list_filter = (
        "cost_date",
        "department",
        "house",
    )

    search_fields = (
        "description",
        "department__name",
        "house__name",
        "notes",
    )

    date_hierarchy = "cost_date"


# ==================================================
# SUPPLIER PAYMENTS
# ==================================================

@admin.register(SupplierPayment)
class SupplierPaymentAdmin(admin.ModelAdmin):

    list_display = (
        "supplier",
        "payment_date",
        "amount",
        "invoice",
        "reference",
        "has_receipt",
    )

    list_filter = (
        "supplier",
        "payment_date",
    )

    search_fields = (
        "invoice__invoice_number",
        "invoice__supplier__name",
        "supplier__name",
        "reference",
        "notes",
    )

    autocomplete_fields = ("supplier", "invoice")

    ordering = ("-payment_date", "-id")



    @admin.display(boolean=True, description="Receipt")
    def has_receipt(self, obj):
        return bool(obj.receipt)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "invoice":
            kwargs["queryset"] = Invoice.objects.filter(ownership=Ownership.COMPANY)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# ==================================================
# VILLA PROPERTY INFORMATION AND CONTACTS
# ==================================================

class HouseTechnicianInline(admin.TabularInline):
    model = HouseTechnician
    extra = 1
    fields = ("technician_type", "name", "phone", "company", "email", "is_primary", "notes")


@admin.register(HouseInfo)
class HouseInfoAdmin(admin.ModelAdmin):
    list_display = ("house", "wifi_name", "alarm_company", "alarm_phone")
    search_fields = ("house__name", "house__customer__name", "wifi_name", "alarm_company")
    autocomplete_fields = ("house",)
    inlines = [HouseTechnicianInline]
    fieldsets = (
        ("Villa", {"fields": ("house",)}),
        ("Wi-Fi (authorized staff only)", {"fields": ("wifi_name", "wifi_password")}),
        ("Alarm (authorized staff only)", {"fields": ("alarm_code", "alarm_company", "alarm_phone")}),
    )


@admin.register(HouseTechnician)
class HouseTechnicianAdmin(admin.ModelAdmin):
    list_display = ("name", "technician_type", "house_info", "phone", "company", "is_primary")
    list_filter = ("technician_type", "is_primary")
    search_fields = ("name", "phone", "company", "house_info__house__name")
    autocomplete_fields = ("house_info",)


# ==================================================
# WATER: MUNICIPAL METER AND SOURCE SWITCHES
# ==================================================

@admin.register(HouseWaterReading)
class HouseWaterReadingAdmin(admin.ModelAdmin):
    list_display = ("house", "reading_date", "meter_litres", "consumed_since_previous", "daily_average", "checked_by")
    list_filter = ("house", "reading_date")
    search_fields = ("house__name", "checked_by", "notes")
    autocomplete_fields = ("house",)
    date_hierarchy = "reading_date"
    readonly_fields = ("consumed_since_previous", "daily_average", "created_at")

    @admin.display(description="Consumed since previous (L)")
    def consumed_since_previous(self, obj):
        if not obj.pk:
            return "—"
        value = obj.consumption_litres
        return f"{value:,.2f} L" if value is not None else "—"

    @admin.display(description="Average per day (L)")
    def daily_average(self, obj):
        if not obj.pk:
            return "—"
        value = obj.daily_average_litres
        return f"{value:,.2f} L/day" if value is not None else "—"


@admin.register(HouseWaterSourcePeriod)
class HouseWaterSourcePeriodAdmin(admin.ModelAdmin):
    list_display = ("house", "source", "started_at", "ended_at", "currently_active")
    list_filter = ("source", "house", "started_at")
    search_fields = ("house__name", "notes")
    autocomplete_fields = ("house",)
    date_hierarchy = "started_at"

    @admin.display(boolean=True, description="Active")
    def currently_active(self, obj):
        return obj.ended_at is None


# ==================================================
# WATER: TANKS, VISUAL CHECKS, AND DELIVERIES
# ==================================================

class HouseWaterTankReadingInline(admin.TabularInline):
    model = HouseWaterTankReading
    extra = 0
    fields = ("reading_date", "visual_level", "checked_by", "notes")
    show_change_link = True


@admin.register(HouseWaterTank)
class HouseWaterTankAdmin(admin.ModelAdmin):
    list_display = ("house", "name", "capacity_litres", "minimum_level_litres", "latest_visual_level")
    list_filter = ("house",)
    search_fields = ("house__name", "name")
    autocomplete_fields = ("house",)
    inlines = [HouseWaterTankReadingInline]

    @admin.display(description="Last visual check")
    def latest_visual_level(self, obj):
        reading = obj.level_readings.order_by("-reading_date", "-pk").first()
        return reading.get_visual_level_display() if reading else "Not checked"


@admin.register(HouseWaterTankReading)
class HouseWaterTankReadingAdmin(admin.ModelAdmin):
    list_display = ("tank", "reading_date", "visual_level", "estimated_remaining", "checked_by")
    list_filter = ("visual_level", "reading_date")
    search_fields = ("tank__house__name", "tank__name", "checked_by")
    autocomplete_fields = ("tank",)
    date_hierarchy = "reading_date"
    readonly_fields = ("estimated_remaining",)

    @admin.display(description="Estimated remaining (not measured)")
    def estimated_remaining(self, obj):
        if not obj.pk:
            return "—"
        value = obj.estimated_litres
        return f"~{value:,.0f} L (visual estimate)" if value is not None else "Unknown"


@admin.register(HouseWaterDelivery)
class HouseWaterDeliveryAdmin(admin.ModelAdmin):
    list_display = ("delivery_date", "tank", "supplier_name", "litres_delivered", "water_cost", "delivery_fee", "total_amount", "effective_unit_price", "invoice_pdf")
    list_filter = ("delivery_date", "tank__house")
    search_fields = ("tank__house__name", "supplier_name", "supplier_phone", "notes")
    autocomplete_fields = ("tank",)
    date_hierarchy = "delivery_date"
    readonly_fields = ("effective_unit_price",)

    @admin.display(description="Effective €/L")
    def effective_unit_price(self, obj):
        if not obj.pk:
            return "—"
        value = obj.price_per_litre
        return f"€{value:,.4f}" if value is not None else "—"


class HouseWaterTariffCubicMeterForm(forms.ModelForm):
    """Admin uses m³ while existing storage and calculations remain in litres."""

    from_cubic_meters = forms.DecimalField(
        label="From (m³ / 1,000 litres)", min_value=Decimal("0"),
        max_digits=11, decimal_places=3,
    )
    to_cubic_meters = forms.DecimalField(
        label="To (m³ / 1,000 litres) — blank for unlimited",
        required=False, min_value=Decimal("0"), max_digits=11, decimal_places=3,
    )

    class Meta:
        model = HouseWaterTariff
        fields = ("price_per_1000_litres",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["from_cubic_meters"].initial = self.instance.from_litres / Decimal("1000")
            if self.instance.to_litres is not None:
                self.fields["to_cubic_meters"].initial = self.instance.to_litres / Decimal("1000")

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("from_cubic_meters")
        end = cleaned.get("to_cubic_meters")
        if start is None:
            return cleaned
        if end is not None and end <= start:
            self.add_error("to_cubic_meters", "To must be greater than From.")
            return cleaned
        from_litres = start * Decimal("1000")
        to_litres = end * Decimal("1000") if end is not None else None
        for other in HouseWaterTariff.objects.exclude(pk=self.instance.pk):
            if (to_litres is None or other.from_litres < to_litres) and (
                other.to_litres is None or from_litres < other.to_litres
            ):
                self.add_error("from_cubic_meters", "This bracket overlaps an existing bracket.")
                break
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.from_litres = self.cleaned_data["from_cubic_meters"] * Decimal("1000")
        end = self.cleaned_data["to_cubic_meters"]
        instance.to_litres = end * Decimal("1000") if end is not None else None
        if commit:
            instance.save()
            self.save_m2m()
        return instance


@admin.register(HouseWaterTariff)
class HouseWaterTariffAdmin(admin.ModelAdmin):
    form = HouseWaterTariffCubicMeterForm
    list_display = ("from_m3", "to_m3", "price_per_1000_litres")
    ordering = ("from_litres",)
    fields = ("from_cubic_meters", "to_cubic_meters", "price_per_1000_litres")

    @admin.display(description="From (m³)", ordering="from_litres")
    def from_m3(self, obj):
        return obj.from_litres / Decimal("1000")

    @admin.display(description="To (m³)", ordering="to_litres")
    def to_m3(self, obj):
        return obj.to_litres / Decimal("1000") if obj.to_litres is not None else "Unlimited"


# ==================================================
# UTILITIES: WATER AND ELECTRICITY INVOICES
# ==================================================
@admin.register(HouseWaterBill)

class HouseWaterBillAdmin(admin.ModelAdmin):
    list_display = (
        "house", "meter_number", "supply_number", "billing_from", "billing_to",
        "billed_litres", "total_amount", "invoice_pdf",
    )
    list_filter = ("house", "billing_to")
    search_fields = (
        "house__name", "house__customer__name", "meter_number",
        "supply_number", "invoice_number", "notes",
    )
    autocomplete_fields = ("house",)
    date_hierarchy = "billing_to"
    fields = (
        "house", "meter_number", "supply_number", "billing_from", "billing_to",
        "invoice_date", "invoice_number", "meter_start_litres",
        "meter_end_litres", "billed_litres", "total_amount", "invoice_pdf", "notes",
    )


@admin.register(HouseElectricityBill)
class HouseElectricityBillAdmin(admin.ModelAdmin):
    list_display = (
        "house", "meter_number", "supply_number", "provider_name",
        "billing_from", "billing_to", "consumption_kwh", "total_amount", "invoice_pdf",
    )
    list_filter = ("house", "billing_to")
    search_fields = (
        "house__name", "house__customer__name", "meter_number",
        "supply_number", "invoice_number", "provider_name", "notes",
    )
    autocomplete_fields = ("house",)
    date_hierarchy = "billing_to"
    fields = (
        "house", "meter_number", "supply_number", "provider_name",
        "billing_from", "billing_to", "invoice_date", "invoice_number",
        "consumption_kwh", "total_amount", "invoice_pdf", "notes",
    )


# ==================================================
# MUNICIPAL WATER BILLING CYCLES (TARIFF RESET DATES)
# ==================================================





from .models import HouseInspection


@admin.register(HouseInspection)
class HouseInspectionAdmin(admin.ModelAdmin):
    list_display = (
        "house",
        "inspection_date",
        "checked_by",
        "condition",
    )

    list_filter = (
        "condition",
        "inspection_date",
        "house",
    )

    search_fields = (
        "house__name",
        "checked_by",
        "notes",
    )

    date_hierarchy = "inspection_date"
    ordering = ("-inspection_date",)




from django.utils.html import format_html
from .models import ImportantJobReminder


@admin.register(ImportantJobReminder)
class ImportantJobReminderAdmin(admin.ModelAdmin):

    list_display = (
        "deadline",
        "customer",
        "description",
        "procedure_days",
        "days_remaining",
        "recommended_start_date",
        "importance_display",
        "completed",
    )

    list_editable = (
        "completed",
    )

    list_filter = (
        "completed",
        "deadline",
        "customer",
    )

    search_fields = (
        "description",
        "customer__name",
    )

    ordering = (
        "completed",
        "deadline",
    )

    date_hierarchy = "deadline"

    list_per_page = 50

    readonly_fields = (
        "days_remaining",
        "recommended_start_date",
        "latest_start_date",
        "spare_days",
        "importance_display",
        "completed_at",
        "last_notification_level",
        "last_notification_at",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Job information",
            {
                "fields": (
                    "customer",
                    "description",
                    "deadline",
                    "procedure_days",
                )
            },
        ),
        (
            "Importance and schedule",
            {
                "fields": (
                    "importance_display",
                    "days_remaining",
                    "recommended_start_date",
                    "latest_start_date",
                    "spare_days",
                )
            },
        ),
        (
            "Completion",
            {
                "fields": (
                    "completed",
                    "completed_at",
                )
            },
        ),
        (
            "Email notifications",
            {
                "fields": (
                    "last_notification_level",
                    "last_notification_at",
                )
            },
        ),
        (
            "History",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    actions = [
        "mark_completed",
        "mark_pending",
    ]

    @admin.display(description="Importance")
    def importance_display(self, obj):

        if not obj or not obj.deadline or not obj.procedure_days:
            return "Calculated after saving"

        colors = {
            "normal": "#16a34a",
            "important": "#ca8a04",
            "urgent": "#ea580c",
            "critical": "#dc2626",
            "overdue": "#991b1b",
            "completed": "#64748b",
        }

        level = obj.importance

        return format_html(
            '<span style="background:{};'
            'color:white;padding:5px 10px;'
            'border-radius:5px;font-weight:bold;">'
            '{}</span>',
            colors.get(level, "#64748b"),
            level.upper(),
        )

    @admin.action(
        description="Mark selected jobs as completed"
    )
    def mark_completed(self, request, queryset):

        count = 0

        for job in queryset.filter(completed=False):
            job.completed = True
            job.save()
            count += 1

        self.message_user(
            request,
            f"{count} jobs completed.",
        )

    @admin.action(
        description="Reopen selected jobs"
    )
    def mark_pending(self, request, queryset):

        count = 0

        for job in queryset.filter(completed=True):
            job.completed = False
            job.save()
            count += 1

        self.message_user(
            request,
            f"{count} jobs reopened.",
        )


from .models import GroupedWorkEntry

from datetime import date
from django import forms
from django.db import models
from django.utils.html import format_html

from .models import GroupedWorkEntry


class WorkEntryMonthFilter(admin.SimpleListFilter):
    title = "Billing month"
    parameter_name = "billing_month"

    def lookups(self, request, model_admin):
        months = model_admin.get_queryset(request).dates(
            "work_date", "month", order="DESC"
        )

        return [
            (month.strftime("%Y-%m"), month.strftime("%B %Y"))
            for month in months
        ]

    def queryset(self, request, queryset):
        if self.value():
            try:
                month = date.fromisoformat(self.value() + "-01")
            except ValueError:
                return queryset.none()

            return queryset.filter(
                work_date__year=month.year,
                work_date__month=month.month,
            )

        return queryset

@admin.register(GroupedWorkEntry)
class GroupedWorkEntryAdmin(WorkEntryAdmin):

    def changelist_view(self, request, extra_context=None):
        if request.method == "POST":
            from .signals import batch_financial_refresh
            with batch_financial_refresh():
                return super().changelist_view(request, extra_context)
        return super().changelist_view(request, extra_context)


    change_list_template = "admin/change_list.html"

    formfield_overrides = {
        models.TextField: {
            "widget": forms.Textarea(
                attrs={
                    "rows": 2,
                    "cols": 30,
                }
            )
        },
    }

    list_display = (
        "work_date",
        "ownership",
        "employee",
        "compact_service",
        "hours",
        "description",
        "additional_charges",
        "additional_charges_notes",
        "total_customer_charge_display",
    )

    list_editable = (
        "hours",
        "description",
        "additional_charges",
        "additional_charges_notes",
    )

    list_filter = (
        "ownership",
        ("house", admin.RelatedOnlyFieldListFilter),
        WorkEntryMonthFilter,
        "house__customer",
        "service",
    )

    def get_list_filter(self, request):
        return self.list_filter

    ordering = (
        "work_date",
        "house__name",
        "pk",
    )

    date_hierarchy = "work_date"

    list_per_page = 200
    list_max_show_all = 1000

    list_select_related = (
        "house",
        "employee",
        "service__department",
    )

    @admin.display(
        description="Service",
        ordering="service__name",
    )
    def compact_service(self, obj):
        return format_html(
            '<div style="width:160px; '
            'white-space:normal; '
            'overflow-wrap:anywhere; '
            'line-height:1.4;">{}</div>',
            obj.service,
        )

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)

        if obj:
            return tuple(fields) + (
                "ownership",
                "employee",
                "house",
                "service",
            )

        return fields

    def save_model(self, request, obj, form, change):
        entry = (
            WorkEntry.objects.get(pk=obj.pk)
            if change else WorkEntry()
        )

        fields = (
            "ownership",
            "employee",
            "house",
            "service",
            "work_date",
            "hours",
            "description",
            "additional_charges",
            "additional_charges_notes",
        )

        for field in fields:
            if not change or field in form.changed_data:
                setattr(entry, field, getattr(obj, field))

        if not change:
            entry.ownership = Ownership.CUSTOMER
            obj.ownership = Ownership.CUSTOMER

        entry.save()

        obj.pk = entry.pk
        obj._state.adding = False
        obj._state.db = entry._state.db

        for field in (
            "employee_salary_type_snapshot",
            "employee_rate_snapshot",
            "customer_hourly_rate_snapshot",
            "employee_cost",
            "customer_charge",
            "created_at",
        ):
            setattr(obj, field, getattr(entry, field))

    def delete_model(self, request, obj):
        WorkEntry.objects.get(pk=obj.pk).delete()

    def delete_queryset(self, request, queryset):
        WorkEntry.objects.filter(
            pk__in=queryset.values_list("pk", flat=True)
        ).delete()
