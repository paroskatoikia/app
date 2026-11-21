
from rest_framework import serializers

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


class HouseSerializer(serializers.ModelSerializer):
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


class WorkEntrySerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    house_name = serializers.CharField(
        source="house",
        read_only=True,
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


class InvoiceSerializer(serializers.ModelSerializer):
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


class SupplierPaymentSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(
        source="supplier.name",
        read_only=True,
    )

    class Meta:
        model = SupplierPayment
        fields = "__all__"


class CustomerPaymentSerializer(serializers.ModelSerializer):
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