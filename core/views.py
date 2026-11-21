from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action


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

from .serializers import (
    CustomerSerializer,
    HouseSerializer,
    VillaProgramSerializer,
    DepartmentSerializer,
    ServiceCategorySerializer,
    VillaServicePriceSerializer,
    EmployeeSerializer,
    WorkEntrySerializer,
    InvoiceSerializer,
    DepartmentCostSerializer,
    VillaFinancialSummarySerializer,
    DepartmentFinancialSummarySerializer,
)


class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]


class CustomerViewSet(BaseModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    search_fields = ["name", "company_name", "email", "phone"]
    ordering_fields = ["name", "created_at"]


    @action(
        detail=True,
        methods=["get"],
        url_path="export-statement",
    )
    def export_statement(self, request, pk=None):
        from django.core.exceptions import ValidationError
        from rest_framework.exceptions import ValidationError as APIValidationError
        from .customer_statement_export import export_customer_statement

        customer = self.get_object()
        month = request.query_params.get("month")

        try:
            return export_customer_statement(customer, month=month)
        except ValidationError as exc:
            raise APIValidationError(exc.messages)


class HouseViewSet(BaseModelViewSet):
    queryset = House.objects.select_related("customer").all()
    serializer_class = HouseSerializer
    search_fields = ["name", "area", "customer__name"]
    filterset_fields = ["customer"]
    ordering_fields = ["name", "created_at"]


class VillaProgramViewSet(BaseModelViewSet):
    queryset = VillaProgram.objects.select_related("house").all()
    serializer_class = VillaProgramSerializer
    filterset_fields = ["house", "program_type"]
    ordering_fields = ["program_type", "price", "start_date", "end_date"]


class DepartmentViewSet(BaseModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    search_fields = ["name", "description"]
    ordering_fields = ["name"]


class ServiceCategoryViewSet(BaseModelViewSet):
    queryset = ServiceCategory.objects.select_related("department").all()
    serializer_class = ServiceCategorySerializer
    filterset_fields = ["department"]
    search_fields = ["name", "department__name"]
    ordering_fields = ["name"]


class VillaServicePriceViewSet(BaseModelViewSet):
    queryset = VillaServicePrice.objects.select_related(
        "house",
        "service",
        "service__department",
    ).all()
    serializer_class = VillaServicePriceSerializer
    filterset_fields = ["house", "service"]
    ordering_fields = ["hourly_price"]


class EmployeeViewSet(BaseModelViewSet):
    queryset = Employee.objects.select_related("department").all()
    serializer_class = EmployeeSerializer
    filterset_fields = ["department", "salary_type", "is_active"]
    search_fields = ["first_name", "last_name", "email", "phone"]
    ordering_fields = ["first_name", "last_name", "hire_date"]


from rest_framework.response import Response
from rest_framework import status


class WorkEntryViewSet(BaseModelViewSet):
    queryset = WorkEntry.objects.select_related(
        "employee",
        "house",
        "service",
        "service__department",
    ).all()

    serializer_class = WorkEntrySerializer

    filterset_fields = [
        "house",
        "employee",
        "service",
        "service__department",
        "work_date",
    ]

    search_fields = [
        "employee__first_name",
        "employee__last_name",
        "house__name",
        "service__name",
        "description",
    ]

    ordering_fields = [
        "work_date",
        "hours",
        "employee_cost",
        "customer_charge",
    ]

    def create(self, request, *args, **kwargs):
        many = isinstance(request.data, list)

        serializer = self.get_serializer(
            data=request.data,
            many=many
        )

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )



from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Supplier, SupplierPayment, CustomerPayment

from .serializers import (
    SupplierSerializer,
    SupplierPaymentSerializer,
    CustomerPaymentSerializer,
)


class SupplierViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Supplier.objects.all().order_by("name")
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]


class SupplierPaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        SupplierPayment.objects
        .select_related("supplier")
        .all()
        .order_by("-payment_date", "-id")
    )
    serializer_class = SupplierPaymentSerializer
    permission_classes = [IsAuthenticated]


class CustomerPaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = (
        CustomerPayment.objects
        .select_related("customer")
        .all()
        .order_by("-payment_date", "-id")
    )
    serializer_class = CustomerPaymentSerializer
    permission_classes = [IsAuthenticated]



class InvoiceViewSet(BaseModelViewSet):
    queryset = Invoice.objects.select_related(
        "department",
        "house",
    ).all()
    serializer_class = InvoiceSerializer
    filterset_fields = ["department", "house", "invoice_date"]
    search_fields = ["supplier", "invoice_number", "description"]
    ordering_fields = ["invoice_date", "amount", "supplier"]


class DepartmentCostViewSet(BaseModelViewSet):
    queryset = DepartmentCost.objects.select_related(
        "department",
        "house",
    ).all()
    serializer_class = DepartmentCostSerializer
    filterset_fields = ["department", "house", "cost_date"]
    search_fields = ["description", "notes"]
    ordering_fields = ["cost_date", "amount"]


class VillaFinancialSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = VillaFinancialSummary.objects.select_related("house").all()
    serializer_class = VillaFinancialSummarySerializer
    filterset_fields = ["house", "period_type", "period_start"]
    ordering_fields = ["period_start", "period_type", "gross_margin"]


class DepartmentFinancialSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = DepartmentFinancialSummary.objects.select_related(
        "department",
        "house",
    ).all()
    serializer_class = DepartmentFinancialSummarySerializer
    filterset_fields = [
        "department",
        "house",
        "period_type",
        "period_start",
    ]
    ordering_fields = ["period_start", "period_type", "gross_margin"]



from datetime import timedelta

from django.db.models import Max
from django.utils import timezone
from rest_framework.views import APIView

from .models import (
    HouseInspection,
    HouseWaterReading,
    HouseWaterTankReading,
)

from .serializers import HouseInspectionSerializer


class HouseInspectionViewSet(BaseModelViewSet):
    queryset = HouseInspection.objects.select_related("house").all()
    serializer_class = HouseInspectionSerializer

    filterset_fields = ["house", "condition"]
    search_fields = ["house__name", "checked_by", "notes"]
    ordering_fields = ["inspection_date", "created_at"]


class WeeklyChecksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        deadline = now - timedelta(days=7)
        due_soon_cutoff = now - timedelta(days=5)

        houses = House.objects.select_related("customer").all()

        municipal_dates = dict(
            HouseWaterReading.objects.values("house_id")
            .annotate(last_date=Max("reading_date"))
            .values_list("house_id", "last_date")
        )

        tank_dates = dict(
            HouseWaterTankReading.objects.values("tank__house_id")
            .annotate(last_date=Max("reading_date"))
            .values_list("tank__house_id", "last_date")
        )

        inspection_dates = dict(
            HouseInspection.objects
            .filter(inspection_date__lte=now)
            .values("house_id")
            .annotate(last_date=Max("inspection_date"))
            .values_list("house_id", "last_date")
        )

        results = []

        for house in houses:
            municipal = municipal_dates.get(house.id)
            tank = tank_dates.get(house.id)

            water_dates = [
                value
                for value in [municipal, tank]
                if value is not None and value <= now
            ]

            last_water = max(water_dates) if water_dates else None
            last_house = inspection_dates.get(house.id)

            if last_house and last_house > now:
                last_house = None

            water_missing = (
                last_water is None or last_water <= deadline
            )

            house_missing = (
                last_house is None or last_house <= deadline
            )

            if water_missing or house_missing:
                status_value = "overdue"
            elif (
                last_water <= due_soon_cutoff
                or last_house <= due_soon_cutoff
            ):
                status_value = "due_soon"
            else:
                status_value = "complete"

            results.append({
                "house_id": house.id,
                "house_name": house.name,
                "customer_name": house.customer.name,
                "area": house.area,
                "last_water_check": (
                    last_water.isoformat() if last_water else None
                ),
                "last_house_check": (
                    last_house.isoformat() if last_house else None
                ),
                "next_water_due": (
                    (last_water + timedelta(days=7)).isoformat()
                    if last_water else None
                ),
                "next_house_due": (
                    (last_house + timedelta(days=7)).isoformat()
                    if last_house else None
                ),
                "water_missing": water_missing,
                "house_missing": house_missing,
                "status": status_value,
            })

        status_order = {
            "overdue": 0,
            "due_soon": 1,
            "complete": 2,
        }

        results.sort(
            key=lambda item: (
                status_order[item["status"]],
                item["house_name"].lower(),
            )
        )

        return Response({
            "summary": {
                "total": len(results),
                "complete": sum(
                    item["status"] == "complete"
                    for item in results
                ),
                "due_soon": sum(
                    item["status"] == "due_soon"
                    for item in results
                ),
                "overdue": sum(
                    item["status"] == "overdue"
                    for item in results
                ),
            },
            "results": results,
        })
