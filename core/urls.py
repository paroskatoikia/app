from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .views import CompanyGasViewSet

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import ImportantJobReminderViewSet
from .views import (
    CustomerViewSet,
    HouseViewSet,
    VillaProgramViewSet,
    DepartmentViewSet,
    ServiceCategoryViewSet,
    VillaServicePriceViewSet,
    EmployeeViewSet,
    WorkEntryViewSet,
    InvoiceViewSet,
    DepartmentCostViewSet,
    VillaFinancialSummaryViewSet,
    DepartmentFinancialSummaryViewSet,
    SupplierViewSet,
    SupplierPaymentViewSet,
    CustomerPaymentViewSet,
    HouseInspectionViewSet,
    WeeklyChecksView,
)

from .weekly_checks_api import (
    HouseWaterReadingViewSet,
    HouseWaterTankViewSet,
    HouseWaterTankReadingViewSet,
)

from .business_overview_export import export_business_overview


# ============================================================
# BUSINESS OVERVIEW ZIP EXPORT
# ============================================================

class BusinessOverviewExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return export_business_overview()


# ============================================================
# API ROUTER
# ============================================================

router = DefaultRouter()

# Existing endpoints
router.register("customers", CustomerViewSet, basename="customer")
router.register("villas", HouseViewSet, basename="villa")
router.register("programs", VillaProgramViewSet, basename="program")
router.register("departments", DepartmentViewSet, basename="department")
router.register("services", ServiceCategoryViewSet, basename="service")
router.register("service-prices", VillaServicePriceViewSet, basename="service-price")
router.register("employees", EmployeeViewSet, basename="employee")
router.register("work-entries", WorkEntryViewSet, basename="work-entry")
router.register("invoices", InvoiceViewSet, basename="invoice")
router.register("department-costs", DepartmentCostViewSet, basename="department-cost")

router.register(
    "villa-financial-summaries",
    VillaFinancialSummaryViewSet,
    basename="villa-financial-summary",
)

router.register(
    "department-financial-summaries",
    DepartmentFinancialSummaryViewSet,
    basename="department-financial-summary",
)

# Suppliers and payments
router.register(
    "suppliers",
    SupplierViewSet,
    basename="supplier",
)

router.register(
    "supplier-payments",
    SupplierPaymentViewSet,
    basename="supplier-payment",
)

router.register(
    "customer-payments",
    CustomerPaymentViewSet,
    basename="customer-payment",
)

# Weekly house checks and existing water measurement models
router.register(
    "house-inspections",
    HouseInspectionViewSet,
    basename="house-inspections",
)

router.register(
    "water-readings",
    HouseWaterReadingViewSet,
    basename="water-readings",
)

router.register(
    "water-tanks",
    HouseWaterTankViewSet,
    basename="water-tanks",
)

router.register(
    "water-tank-readings",
    HouseWaterTankReadingViewSet,
    basename="water-tank-readings",
)

router.register(
    r"important-job-reminders",
    ImportantJobReminderViewSet,
    basename="important-job-reminders",
)

router.register(
    r"company-gas",
    CompanyGasViewSet,
    basename="company-gas",
)


# ============================================================
# URL PATTERNS
# ============================================================

urlpatterns = [

    # Business Overview ZIP export
    path(
        "business-export/",
        BusinessOverviewExportView.as_view(),
        name="business-overview-export",
    ),

    # Independent weekly house and water check statuses
    path(
        "weekly-checks/",
        WeeklyChecksView.as_view(),
        name="weekly-checks",
    ),

    # All existing and new router endpoints
    path("", include(router.urls)),

    # JWT authentication
    path(
        "auth/login/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),

    path(
        "auth/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
]
