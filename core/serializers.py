from rest_framework import serializers

from copy import copy
from django.core.exceptions import ValidationError as DjangoValidationError


class ModelCleanSerializer(serializers.ModelSerializer):
    """Apply the same business rules in the API and Django admin."""

    def validate(self, attrs):
        attrs = super().validate(attrs)
        candidate = copy(self.instance) if self.instance is not None else self.Meta.model()
        for name, value in attrs.items():
            setattr(candidate, name, value)
        try:
            candidate.clean()
        except DjangoValidationError as exc:
            if hasattr(exc, "message_dict"):
                raise serializers.ValidationError({
                    ("non_field_errors" if key == "__all__" else key): value
                    for key, value in exc.message_dict.items()
                }) from exc
            raise serializers.ValidationError(exc.messages) from exc
        return attrs


from .models import (
    Customer,
    House,
    VillaProgram,
    Department,
    ServiceCategory,
    VillaServicePrice,
    Employee,
    WorkEntry,
    Invoice,
    DepartmentCost,
    VillaFinancialSummary,
    DepartmentFinancialSummary,
)


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class HouseSerializer(ModelCleanSerializer):
    customer_name = serializers.CharField(
        source="customer",
        read_only=True,
    )

    class Meta:
        model = House
        fields = "__all__"


class VillaProgramSerializer(serializers.ModelSerializer):
    house_name = serializers.CharField(
        source="house",
        read_only=True,
    )

    class Meta:
        model = VillaProgram
        fields = "__all__"

    def validate(self, attrs):
        start_date = attrs.get(
            "start_date",
            getattr(self.instance, "start_date", None),
        )
        end_date = attrs.get(
            "end_date",
            getattr(self.instance, "end_date", None),
        )

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({
                "end_date": "The end date cannot be earlier than the start date."
            })

        return attrs


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class ServiceCategorySerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="department",
        read_only=True,
    )

    class Meta:
        model = ServiceCategory
        fields = "__all__"


class VillaServicePriceSerializer(serializers.ModelSerializer):
    house_name = serializers.CharField(
        source="house",
        read_only=True,
    )
    service_name = serializers.CharField(
        source="service",
        read_only=True,
    )

    class Meta:
        model = VillaServicePrice
        fields = "__all__"


class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    department_name = serializers.CharField(
        source="department",
        read_only=True,
    )
    salary_rate = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Employee
        fields = "__all__"

    def get_full_name(self, obj):
        return str(obj)


class WorkEntrySerializer(ModelCleanSerializer):
    ownership = serializers.ChoiceField(choices=(("company", "Company"), ("customer", "Customer")))
    ownership_display = serializers.CharField(source="get_ownership_display", read_only=True)
    employee_name = serializers.SerializerMethodField()
    house_name = serializers.CharField(
        source="house",
        read_only=True,
        allow_null=True,
    )
    service_name = serializers.CharField(
        source="service",
        read_only=True,
    )
    department_name = serializers.CharField(
        source="service.department",
        read_only=True,
    )

    total_company_cost = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )
    gross_margin = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = WorkEntry
        fields = "__all__"
        read_only_fields = [
            "employee_salary_type_snapshot",
            "employee_rate_snapshot",
            "employee_cost",
            "customer_hourly_rate_snapshot",
            "customer_charge",
            "created_at",
        ]

    def get_employee_name(self, obj):
        return str(obj.employee)


class InvoiceSerializer(ModelCleanSerializer):
    ownership = serializers.ChoiceField(choices=(("company", "Company"), ("customer", "Customer")))
    ownership_display = serializers.CharField(source="get_ownership_display", read_only=True)
    department_name = serializers.CharField(
        source="department",
        read_only=True,
    )
    house_name = serializers.CharField(
        source="house",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = Invoice
        fields = "__all__"


class DepartmentCostSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="department",
        read_only=True,
    )
    house_name = serializers.CharField(
        source="house",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = DepartmentCost
        fields = "__all__"


class VillaFinancialSummarySerializer(serializers.ModelSerializer):
    house_name = serializers.CharField(
        source="house",
        read_only=True,
    )

    class Meta:
        model = VillaFinancialSummary
        fields = "__all__"
        read_only_fields = [
            field.name
            for field in VillaFinancialSummary._meta.fields
        ]


class DepartmentFinancialSummarySerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="department",
        read_only=True,
    )
    house_name = serializers.CharField(
        source="house",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = DepartmentFinancialSummary
        fields = "__all__"
        read_only_fields = [
            field.name
            for field in DepartmentFinancialSummary._meta.fields
        ]




from .models import Supplier, SupplierPayment, CustomerPayment


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"


class SupplierPaymentSerializer(ModelCleanSerializer):
    invoice_number = serializers.CharField(source="invoice.invoice_number", read_only=True, allow_null=True, default=None)
    supplier_name = serializers.CharField(
        source="supplier.name",
        read_only=True,
    )

    class Meta:
        model = SupplierPayment
        fields = "__all__"


class CustomerPaymentSerializer(ModelCleanSerializer):
    invoice_number = serializers.CharField(source="invoice.invoice_number", read_only=True, allow_null=True, default=None)
    customer_name = serializers.CharField(
        source="customer.name",
        read_only=True,
    )

    class Meta:
        model = CustomerPayment
        fields = "__all__"


from .models import HouseInspection


class HouseInspectionSerializer(serializers.ModelSerializer):
    house_name = serializers.CharField(
        source="house.name",
        read_only=True,
    )

    condition_display = serializers.CharField(
        source="get_condition_display",
        read_only=True,
    )

    class Meta:
        model = HouseInspection
        fields = "__all__"
        read_only_fields = [
            "created_at",
        ]

    def validate_inspection_date(self, value):
        from django.utils import timezone

        if value > timezone.now():
            raise serializers.ValidationError(
                "The inspection date cannot be in the future."
            )

        return value




from rest_framework import serializers

from .models import ImportantJobReminder


class ImportantJobReminderSerializer(
    serializers.ModelSerializer
):

    customer_name = serializers.StringRelatedField(
        source="customer",
        read_only=True,
    )

    days_remaining = serializers.IntegerField(
        read_only=True,
    )

    spare_days = serializers.IntegerField(
        read_only=True,
    )

    notification_days = serializers.FloatField(
        read_only=True,
    )

    recommended_start_date = serializers.DateField(
        read_only=True,
    )

    latest_start_date = serializers.DateField(
        read_only=True,
    )

    importance = serializers.CharField(
        read_only=True,
    )

    importance_score = serializers.IntegerField(
        read_only=True,
    )

    email_required = serializers.BooleanField(
        read_only=True,
    )

    is_overdue = serializers.BooleanField(
        read_only=True,
    )

    class Meta:

        model = ImportantJobReminder

        fields = [
            "id",
            "customer",
            "customer_name",
            "description",
            "deadline",
            "procedure_days",
            "days_remaining",
            "spare_days",
            "notification_days",
            "recommended_start_date",
            "latest_start_date",
            "importance",
            "importance_score",
            "email_required",
            "is_overdue",
            "completed",
            "completed_at",
            "last_notification_level",
            "last_notification_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "completed_at",
            "last_notification_level",
            "last_notification_at",
            "created_at",
            "updated_at",
        ]

from rest_framework import serializers
from .models import Company_Gas


class CompanyGasSerializer(serializers.ModelSerializer):

    employee_name = serializers.CharField(
        source="employee.__str__",
        read_only=True,
    )

    department_name = serializers.CharField(
        source="employee.department.name",
        read_only=True,
    )

    department_id = serializers.IntegerField(
        source="employee.department_id",
        read_only=True,
    )

    gas_type_display = serializers.CharField(
        source="get_gas_type_display",
        read_only=True,
    )

    class Meta:
        model = Company_Gas

        fields = [
            "id",
            "employee",
            "employee_name",
            "department_id",
            "department_name",
            "gas_type",
            "gas_type_display",
            "price_total",
            "date",
            "invoice_pdf",
            "notes",
        ]


from .models import IKA

class IKASerializer(serializers.ModelSerializer):
    accrued_cost = serializers.SerializerMethodField()
    class Meta:
        model = IKA
        fields = ("id", "employee", "package_name", "monthly_cost", "start_date", "end_date", "accrued_cost")

    def get_accrued_cost(self, obj):
        from .services import ika_accrued_cost
        return str(ika_accrued_cost(obj))
