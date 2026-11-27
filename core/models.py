from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.db import models

import os
import re
import unicodedata

from decimal import Decimal
from django.core.files.storage import default_storage


class Ownership(models.TextChoices):
    COMPANY = "company", "Company"
    CUSTOMER = "customer", "Customer"


def validate_ownership(record):
    if record.ownership == Ownership.COMPANY:
        if record.house_id:
            raise ValidationError({"house": "Company records must not have a villa."})
    elif record.ownership == Ownership.CUSTOMER:
        if not record.house_id or not record.house.customer_id or record.house.is_company_property:
            raise ValidationError({"house": "Select a customer villa."})


MONEY_VALIDATORS = [MinValueValidator(Decimal("0.00"))]


class Customer(models.Model):
    name = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    tax_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class House(models.Model):
    """A managed villa. The Python model name stays House to simplify migrations."""



    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT, related_name="villas", null=True, blank=True
    )
    name = models.CharField(max_length=200)

    is_company_property = models.BooleanField(default=False, help_text="Invoices for this property are company expenses.")

    def clean(self):
        super().clean()
        if not self.is_company_property and not self.customer_id:
            raise ValidationError({"customer": "A customer is required for customer villas."})
        if self.is_company_property and self.customer_id:
            raise ValidationError({"customer": "Company properties must not have a customer."})

    area = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)






    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Villa"
        verbose_name_plural = "Villas"

    def __str__(self):
        return self.name


class HouseInfo(models.Model):
    house = models.OneToOneField(
        House,
        on_delete=models.CASCADE,
        related_name="info"
    )

    # Wi-Fi
    wifi_name = models.CharField(max_length=200, blank=True)
    wifi_password = models.CharField(max_length=255, blank=True)

    # Alarm
    alarm_code = models.CharField(max_length=100, blank=True)
    alarm_company = models.CharField(max_length=200, blank=True)
    alarm_phone = models.CharField(max_length=50, blank=True)

    # Access and emergency information
    access_instructions = models.TextField(blank=True)
    emergency_notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "House Information"
        verbose_name_plural = "House Information"

    def __str__(self):
        return f"Information - {self.house.name}"



class HouseTechnician(models.Model):
    TECHNICIAN_TYPES = [
        ("plumber", "Plumber"),
        ("electrician", "Electrician"),
        ("general", "General Technician"),
        ("pool", "Pool Technician"),
        ("air_conditioning", "Air Conditioning"),
        ("gardener", "Gardener"),
        ("other", "Other"),
    ]

    house_info = models.ForeignKey(
        HouseInfo,
        on_delete=models.CASCADE,
        related_name="technicians"
    )

    technician_type = models.CharField(
        max_length=30,
        choices=TECHNICIAN_TYPES,
        default="general"
    )

    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)
    company = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["technician_type", "name"]

    def __str__(self):
        return f"{self.name} - {self.get_technician_type_display()}"



from django.core.exceptions import ValidationError
from django.db import models


# -----------------------------------------------------------------------------
# VILLA UTILITIES: water operations, water bills and electricity bills
# -----------------------------------------------------------------------------
# Municipal readings are cumulative meter readings, not interval consumption.
# Tank readings are visual estimates, not exact measured litres.

class HouseWaterReading(models.Model):
    house = models.ForeignKey(
        House, on_delete=models.CASCADE, related_name="water_readings"
    )
    reading_date = models.DateTimeField()
    meter_litres = models.DecimalField(
        max_digits=14, decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Cumulative municipal meter reading in litres (not usage since last visit).",
    )
    checked_by = models.CharField(max_length=150, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-reading_date", "-pk"]
        constraints = [
            models.UniqueConstraint(
                fields=["house", "reading_date"],
                name="unique_house_municipal_reading_datetime",
            ),
        ]

    @property
    def previous_reading(self):
        return type(self).objects.filter(
            house_id=self.house_id,
            reading_date__lt=self.reading_date,
        ).order_by("-reading_date", "-pk").first()

    @property
    def consumption_litres(self):
        previous = self.previous_reading
        if previous is None:
            return None
        difference = self.meter_litres - previous.meter_litres
        # A negative difference requires investigation (meter reset/replacement).
        return difference if difference >= 0 else None

    @property
    def daily_average_litres(self):
        previous = self.previous_reading
        if previous is None or self.consumption_litres is None:
            return None
        elapsed_days = Decimal(str(
            (self.reading_date - previous.reading_date).total_seconds()
        )) / Decimal("86400")
        if elapsed_days <= 0:
            return None
        return self.consumption_litres / elapsed_days

    def __str__(self):
        return f"{self.house.name} - {self.reading_date} - {self.meter_litres} L"


class HouseWaterTank(models.Model):
    house = models.ForeignKey(
        House, on_delete=models.CASCADE, related_name="water_tanks"
    )
    name = models.CharField(max_length=100, default="Main Water Tank")
    capacity_litres = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    minimum_level_litres = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    notes = models.TextField(blank=True)

    def clean(self):
        super().clean()
        if (self.capacity_litres is not None
                and self.minimum_level_litres is not None
                and self.minimum_level_litres > self.capacity_litres):
            raise ValidationError({
                "minimum_level_litres": "Minimum level cannot exceed tank capacity."
            })

    def __str__(self):
        return f"{self.house.name} - {self.name}"


class HouseWaterTankReading(models.Model):
    LEVEL_CHOICES = [
        ("full", "Full"),
        ("three_quarters", "About 3/4 full"),
        ("half", "About half full"),
        ("quarter", "About 1/4 full"),
        ("nearly_empty", "Nearly empty"),
        ("empty", "Empty"),
        ("unknown", "Unable to determine"),
    ]
    # These fractions are illustrative estimates, not meter measurements.
    LEVEL_FRACTIONS = {
        "full": Decimal("1"),
        "three_quarters": Decimal("0.75"),
        "half": Decimal("0.50"),
        "quarter": Decimal("0.25"),
        "nearly_empty": Decimal("0.10"),
        "empty": Decimal("0"),
    }

    tank = models.ForeignKey(
        HouseWaterTank, on_delete=models.CASCADE, related_name="level_readings"
    )
    reading_date = models.DateTimeField()
    visual_level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    checked_by = models.CharField(max_length=150, blank=True)
    notes = models.TextField(blank=True)

    @property
    def estimated_litres(self):
        fraction = self.LEVEL_FRACTIONS.get(self.visual_level)
        if fraction is None:
            return None
        return self.tank.capacity_litres * fraction

    class Meta:
        ordering = ["-reading_date", "-pk"]

    def __str__(self):
        return f"{self.tank} - {self.get_visual_level_display()}"


class HouseWaterDelivery(models.Model):
    tank = models.ForeignKey(
        HouseWaterTank, on_delete=models.PROTECT, related_name="deliveries"
    )
    delivery_date = models.DateField()
    supplier_name = models.CharField(max_length=200)
    supplier_phone = models.CharField(max_length=50, blank=True)
    litres_delivered = models.DecimalField(
        max_digits=14, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    water_cost = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=MONEY_VALIDATORS,
        help_text="Water charge excluding separately entered delivery fee.",
    )
    delivery_fee = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"),
        validators=MONEY_VALIDATORS,
    )
    # Actual amount on the supplier invoice, including any taxes/other fees.
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=MONEY_VALIDATORS,
    )
    invoice_pdf = models.FileField(
        upload_to="villa_water_invoices/%Y/%m/", blank=True, null=True
    )
    notes = models.TextField(blank=True)

    @property
    def price_per_litre(self):
        if not self.litres_delivered:
            return None
        return self.total_amount / self.litres_delivered

    class Meta:
        ordering = ["-delivery_date", "-pk"]

    def __str__(self):
        return f"{self.tank.house.name} - {self.supplier_name} - {self.litres_delivered} L"


class HouseWaterSourcePeriod(models.Model):
    SOURCE_CHOICES = [
        ("municipal", "Municipal supply"),
        ("tank", "Storage tank supply"),
    ]
    house = models.ForeignKey(
        House, on_delete=models.CASCADE, related_name="water_source_periods"
    )
    source = models.CharField(max_length=12, choices=SOURCE_CHOICES)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def clean(self):
        super().clean()
        if self.ended_at and self.started_at and self.ended_at <= self.started_at:
            raise ValidationError({"ended_at": "End must be after start."})
        # Reject overlapping source periods for the same villa.
        if self.house_id and self.started_at:
            overlap = type(self).objects.filter(house_id=self.house_id)
            if self.pk:
                overlap = overlap.exclude(pk=self.pk)
            overlap = overlap.filter(
                models.Q(ended_at__isnull=True) | models.Q(ended_at__gt=self.started_at)
            )
            if self.ended_at:
                overlap = overlap.filter(started_at__lt=self.ended_at)
            if overlap.exists():
                raise ValidationError("Water source periods for a villa cannot overlap.")

    class Meta:
        ordering = ["-started_at", "-pk"]

    def __str__(self):
        return f"{self.house.name} - {self.get_source_display()} - {self.started_at}"


class HouseWaterTariff(models.Model):
    """Shared progressive municipal water price bracket for ALL villas.

    Ranges are [from_litres, to_litres); blank to_litres means unlimited.
    Prices are EUR per 1,000 litres (equivalent to EUR per m³).
    """
    from_litres = models.DecimalField(
        "From (litres)", max_digits=14, decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    to_litres = models.DecimalField(
        "To (litres) — leave blank for unlimited",
        max_digits=14, decimal_places=2, null=True, blank=True,
    )
    price_per_1000_litres = models.DecimalField(
        "Price (€ per 1,000 litres)", max_digits=12, decimal_places=4,
        validators=[MinValueValidator(Decimal("0"))],
    )

    def clean(self):
        super().clean()
        if self.to_litres is not None and self.to_litres <= self.from_litres:
            raise ValidationError({"to_litres": "Must exceed the From value."})
        if self.from_litres is None:
            return
        others = type(self).objects.exclude(pk=self.pk)
        # Half-open intervals: 0–1000 and 1000–2000 touch, but do not overlap.
        for other in others:
            if (self.to_litres is None or other.from_litres < self.to_litres) and (
                other.to_litres is None or self.from_litres < other.to_litres
            ):
                raise ValidationError("This bracket overlaps another water tariff bracket.")

    class Meta:
        ordering = ["from_litres"]
        verbose_name = "Shared water tariff bracket"
        verbose_name_plural = "Shared water tariff brackets"

    def __str__(self):
        end = f"{self.to_litres:g}" if self.to_litres is not None else "unlimited"
        return f"{self.from_litres:g}–{end} L: €{self.price_per_1000_litres}/1,000 L"


class HouseWaterBill(models.Model):
    house = models.ForeignKey(
        House, on_delete=models.CASCADE, related_name="water_bills"
    )
    billing_from = models.DateField()
    billing_to = models.DateField()
    invoice_date = models.DateField(null=True, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True)
    meter_start_litres = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    meter_end_litres = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )
    # Actual billed consumption; may differ from staff reading intervals.
    billed_litres = models.DecimalField(
        max_digits=14, decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=MONEY_VALIDATORS,
    )
    invoice_pdf = models.FileField(
        upload_to="villa_municipal_water_bills/%Y/%m/", blank=True, null=True
    )
    meter_number = models.CharField(
        "Αριθμός Ρολογιού",
        max_length=100,
        blank=True,
        db_index=True,
    )

    supply_number = models.CharField(
        "Αριθμός Παροχής",
        max_length=100,
        blank=True,
    )
    notes = models.TextField(blank=True)

    def clean(self):
        super().clean()
        if self.billing_from and self.billing_to and self.billing_to < self.billing_from:
            raise ValidationError({"billing_to": "Must not precede billing_from."})
        if (self.meter_start_litres is not None and self.meter_end_litres is not None
                and self.meter_end_litres < self.meter_start_litres):
            raise ValidationError({"meter_end_litres": "Check meter replacement or reset."})

    @property
    def effective_price_per_1000_litres(self):
        if not self.billed_litres:
            return None
        return self.total_amount * Decimal("1000") / self.billed_litres

    class Meta:
        ordering = ["-billing_to", "-pk"]

    def __str__(self):
        return f"{self.house.name} - Water - {self.billing_from} to {self.billing_to}"


class HouseElectricityBill(models.Model):
    house = models.ForeignKey(
        House, on_delete=models.CASCADE, related_name="electricity_bills"
    )
    provider_name = models.CharField(max_length=200, blank=True)
    billing_from = models.DateField()
    billing_to = models.DateField()
    invoice_date = models.DateField(null=True, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True)
    consumption_kwh = models.DecimalField(
        max_digits=14, decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    total_amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=MONEY_VALIDATORS,
    )
    invoice_pdf = models.FileField(
        upload_to="villa_electricity_bills/%Y/%m/", blank=True, null=True
    )
    meter_number = models.CharField(
        "Αριθμός Ρολογιού",
        max_length=100,
        blank=True,
        db_index=True,
    )

    supply_number = models.CharField(
        "Αριθμός Παροχής",
        max_length=100,
        blank=True,
    )
    notes = models.TextField(blank=True)

    def clean(self):
        super().clean()
        if self.billing_from and self.billing_to and self.billing_to < self.billing_from:
            raise ValidationError({"billing_to": "Must not precede billing_from."})

    @property
    def effective_price_per_kwh(self):
        if not self.consumption_kwh:
            return None
        return self.total_amount / self.consumption_kwh

    class Meta:
        ordering = ["-billing_to", "-pk"]

    def __str__(self):
        return f"{self.house.name} - Electricity - {self.billing_from} to {self.billing_to}"


class VillaProgram(models.Model):
    """
    A program assigned to an individual villa.

    BP, Gardening and Pool all use monthly prices.
    All programs can have optional start and end dates.
    """

    PROGRAM_CHOICES = [
        ("bp", "Basic Property Management "),
        ("gardening", "Gardening Maintenance "),
        ("pool", "Pool Maintenance"),
    ]

    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name="programs",
    )

    program_type = models.CharField(
        max_length=20,
        choices=PROGRAM_CHOICES,
    )

    # Monthly price for all programs.
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=MONEY_VALIDATORS,
    )

    # Optional dates for all programs.
    start_date = models.DateField(
        null=True,
        blank=True,
    )

    end_date = models.DateField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["program_type"]
        constraints = [
            models.UniqueConstraint(
                fields=["house", "program_type"],
                name="unique_villa_program",
            )
        ]

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError({
                    "end_date": "The end date cannot be earlier than the start date."
                })

    def __str__(self):
        return f"{self.house.name} - {self.get_program_type_display()}"


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ServiceCategory(models.Model):
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="services"
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        unique_together = ("department", "name")

    def __str__(self):
        return f"{self.department.name} - {self.name}"


class VillaServicePrice(models.Model):
    """Customer charge rate for one service at one particular villa."""

    house = models.ForeignKey(
        House, on_delete=models.CASCADE, related_name="service_prices"
    )
    service = models.ForeignKey(
        ServiceCategory, on_delete=models.PROTECT, related_name="villa_prices"
    )
    hourly_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=MONEY_VALIDATORS
    )


    class Meta:
        ordering = ["house__name", "service__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["house", "service"],
                name="unique_villa_service_price",
            )
        ]

    def __str__(self):
        return f"{self.house} - {self.service}: {self.hourly_price}/hour"


class Employee(models.Model):
    SALARY_TYPES = [
        ("hourly", "Hourly"),
        ("daily", "Daily"),
        ("monthly", "Monthly Salary"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)

    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="employees"
    )

    salary_type = models.CharField(
        max_length=20, choices=SALARY_TYPES, default="hourly"
    )

    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=MONEY_VALIDATORS,
    )

    daily_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=MONEY_VALIDATORS,
    )

    monthly_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=MONEY_VALIDATORS,
    )

    hire_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def salary_rate(self):
        return {
            "hourly": self.hourly_rate,
            "daily": self.daily_rate,
            "monthly": self.monthly_salary,
        }.get(self.salary_type, Decimal("0.00"))

    def calculate_work_cost(self, hours=0):
        """Calculate employee cost using recorded hours."""

        hours = Decimal(str(hours or 0))

        if self.salary_type == "hourly":
            hourly_cost = self.hourly_rate

        elif self.salary_type == "daily":
            hourly_cost = self.daily_rate / Decimal("8")

        elif self.salary_type == "monthly":
            hourly_cost = self.monthly_salary / Decimal("208")

        else:
            hourly_cost = Decimal("0.00")

        return hours * hourly_cost


class IKAPackage(models.Model):
    name = models.CharField(max_length=150, unique=True)
    monthly_cost = models.DecimalField(max_digits=12, decimal_places=2, validators=MONEY_VALIDATORS)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} — €{self.monthly_cost}/month"


class IKA(models.Model):
    package = models.ForeignKey(IKAPackage, on_delete=models.PROTECT, null=True, blank=True)
    package_name = models.CharField(max_length=150, blank=True, default="")
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="ika_records")
    insurance_hours = models.PositiveSmallIntegerField(choices=[(4, "4 hours"), (8, "8 hours")], default=4)
    monthly_cost = models.DecimalField(max_digits=12, decimal_places=2, validators=MONEY_VALIDATORS, help_text="Employer contribution only; exclude amounts already counted in wages.")
    start_date = models.DateField(help_text="First day of the first insured month.")
    end_date = models.DateField(null=True, blank=True, help_text="Last day of the final insured month; blank means ongoing.")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-start_date", "employee"]
        verbose_name = "IKA"
        verbose_name_plural = "IKA"

    def clean(self):
        from calendar import monthrange
        super().clean()
        if not self.start_date:
            return
        if self.start_date.day != 1:
            raise ValidationError({"start_date": "Use the first day of the month."})
        if self.end_date and (self.end_date < self.start_date or self.end_date.day != monthrange(self.end_date.year, self.end_date.month)[1]):
            raise ValidationError({"end_date": "Use the last day of a month on or after the start date."})
        if self.employee_id:
            qs = IKA.objects.filter(employee_id=self.employee_id).exclude(pk=self.pk).filter(models.Q(end_date__isnull=True) | models.Q(end_date__gte=self.start_date))
            if self.end_date:
                qs = qs.filter(start_date__lte=self.end_date)
            if qs.exists():
                raise ValidationError("IKA periods cannot overlap for the same employee.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} - IKA - {self.start_date}"


class Company_Gas(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name="gas_records")
    gas_type = models.CharField(max_length=20, choices=[("petrol", "Petrol (Unleaded)"), ("diesel", "Diesel"), ("lpg", "LPG"), ("other", "Other")])
    price_total = models.DecimalField(max_digits=12, decimal_places=2, validators=MONEY_VALIDATORS)
    date = models.DateField()
    invoice_pdf = models.FileField(upload_to="company_gas/%Y/%m/", blank=True, validators=[FileExtensionValidator(["pdf"])])
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]
        verbose_name = "Company Gas"
        verbose_name_plural = "Company Gas"

    def __str__(self):
        return f"{self.employee} - {self.date} - {self.price_total} EUR"


class WorkEntry(models.Model):
    """Daily work record with separate historical cost and revenue snapshots."""

    employee = models.ForeignKey(
        Employee, on_delete=models.PROTECT, related_name="work_entries"
    )

    ownership = models.CharField(max_length=10, choices=Ownership.choices, db_index=True, default=Ownership.CUSTOMER)

    house = models.ForeignKey(
        House, on_delete=models.PROTECT, related_name="work_entries", null=True, blank=True
    )

    service = models.ForeignKey(
        ServiceCategory, on_delete=models.PROTECT, related_name="work_entries"
    )

    work_date = models.DateField()

    hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=MONEY_VALIDATORS,
    )

    description = models.TextField(blank=True)

    additional_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=MONEY_VALIDATORS,
        verbose_name="Additional charges (€)",
    )

    additional_charges_notes = models.TextField(
        blank=True,
        verbose_name="Additional charges notes",
        help_text="Enter purchased items, supplier names and other details.",
    )

    # Employee-cost snapshot: what the company pays for this employee's work.
    employee_salary_type_snapshot = models.CharField(
        max_length=20,
        choices=Employee.SALARY_TYPES,
        blank=True,
    )

    employee_rate_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    employee_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # Villa-revenue snapshot: what you charge the customer.
    customer_hourly_rate_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    customer_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
    )




    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-work_date"]
        constraints = [models.CheckConstraint(condition=(models.Q(ownership="company", house__isnull=True) | models.Q(ownership="customer", house__isnull=False)), name="work_entry_ownership_house")]

    def clean(self):
        super().clean()
        validate_ownership(self)
        if self.ownership == Ownership.COMPANY and self.additional_charges:
            raise ValidationError({"additional_charges": "Record internal purchases as company expenses."})

    def save(self, *args, **kwargs):
        self.clean()
        is_new = self._state.adding

        if is_new:
            # Freeze employee pay terms when this work is first recorded.
            self.employee_salary_type_snapshot = self.employee.salary_type
            self.employee_rate_snapshot = self.employee.salary_rate

            # Freeze the villa's service rate at the time of this report.
            villa_price = VillaServicePrice.objects.filter(
                house=self.house,
                service=self.service,
            ).first()

            self.customer_hourly_rate_snapshot = (
                villa_price.hourly_price
                if villa_price
                else Decimal("0.00")
            )

        # Recalculate using the frozen rates, not today's prices.
        rate = self.employee_rate_snapshot or Decimal("0.00")
        salary_type = self.employee_salary_type_snapshot
        hours = Decimal(self.hours or 0)

        if salary_type == "hourly":
            hourly_cost = rate

        elif salary_type == "daily":
            hourly_cost = rate / Decimal("8")

        elif salary_type == "monthly":
            # 8 hours/day × 6 days/week × 52 weeks/year ÷ 12 = 208 hours/month.
            hourly_cost = rate / Decimal("208")

        else:
            hourly_cost = Decimal("0.00")

        self.employee_cost = hours * hourly_cost

        self.customer_charge = (
            Decimal(self.hours or 0)
            * (self.customer_hourly_rate_snapshot or Decimal("0.00"))
        )

        if self.ownership == Ownership.COMPANY:
            self.customer_hourly_rate_snapshot = Decimal("0.00")
            self.customer_charge = Decimal("0.00")
        super().save(*args, **kwargs)

    @property
    def total_customer_charge(self):
        return self.customer_charge + self.additional_charges

    @property
    def total_company_cost(self):
        return self.employee_cost

    @property
    def gross_margin(self):
        return self.customer_charge - self.total_company_cost

    def __str__(self):
        return f"{self.employee} - {self.house} - {self.work_date}"


class Supplier(models.Model):
    name = models.CharField(max_length=200, unique=True)
    tax_number = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"

    def __str__(self):
        return self.name


def safe_invoice_filename_part(value):
    """
    Convert a name into a safe filename component.
    Handles Greek characters, spaces and unsafe symbols.
    """
    value = str(value or "").strip()

    value = unicodedata.normalize("NFKC", value)

    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", value)
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"_+", "_", value)

    return value.strip("._") or "UNKNOWN"




class Invoice(models.Model):
    """Supplier invoice recorded as a business expense."""

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="invoices",
    )

    ownership = models.CharField(max_length=10, choices=Ownership.choices, db_index=True, default=Ownership.CUSTOMER)

    house = models.ForeignKey(
        House,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="invoices",
        help_text=(
            "Required for customer invoices; leave blank for company invoices."
        ),
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="invoices",
    )

    invoice_number = models.CharField(max_length=100)
    invoice_date = models.DateField()
    description = models.TextField(blank=True)

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=MONEY_VALIDATORS,
    )

    attachment = models.FileField(
        upload_to="invoices/%Y/%m/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-invoice_date"]

        constraints = [
            models.CheckConstraint(condition=(models.Q(ownership="company", house__isnull=True) | models.Q(ownership="customer", house__isnull=False)), name="invoice_ownership_house"),
            models.UniqueConstraint(
                fields=["supplier", "invoice_number"],
                name="unique_supplier_invoice_number",
            )
        ]

    def __str__(self):
        number = self.invoice_number or "No invoice number"
        return f"{self.supplier} - {number} - {self.amount}"

    def clean(self):
        super().clean()
        validate_ownership(self)
        if self.pk:
            if self.company_payments.exclude(supplier_id=self.supplier_id).exists() or (self.ownership != Ownership.COMPANY and self.company_payments.exists()):
                raise ValidationError("Invoice ownership or supplier conflicts with existing payments.")
            if self.customer_payments.exists() and (self.ownership != Ownership.CUSTOMER or not self.house_id or self.customer_payments.exclude(customer_id=self.house.customer_id).exists()):
                raise ValidationError("Invoice ownership or customer conflicts with existing payments.")

    def get_customer_name(self):
        if self.ownership == Ownership.COMPANY:
            return "COMPANY"
        if self.house_id and self.house.customer_id:
            return self.house.customer.name

        return "UNASSIGNED"

    def get_attachment_path(self, original_filename):
        supplier_name = safe_invoice_filename_part(
            self.supplier.name
        )

        customer_name = safe_invoice_filename_part(
            self.get_customer_name()
        )

        invoice_date = self.invoice_date.strftime("%Y-%m-%d")

        price = f"{self.amount:.2f}"

        extension = os.path.splitext(original_filename)[1].lower()

        filename = (
            f"TIMOLOGIO_{self.pk}_"
            f"{supplier_name}_"
            f"{customer_name}_"
            f"{invoice_date}_"
            f"{price}{extension}"
        )

        return f"invoices/{customer_name}/{filename}"

    def save(self, *args, **kwargs):
        self.clean()
        new_attachment = (
            self.attachment
            and not self.attachment._committed
        )

        old_attachment_name = None

        if self.pk:
            old_attachment_name = (
                type(self).objects
                .filter(pk=self.pk)
                .values_list("attachment", flat=True)
                .first()
            )

        if not new_attachment:
            return super().save(*args, **kwargs)

        uploaded_file = self.attachment.file
        original_filename = self.attachment.name

        # Save the database record first to obtain its ID.
        self.attachment = None
        super().save(*args, **kwargs)

        target_path = self.get_attachment_path(original_filename)

        # Avoid overwriting an existing file.
        target_path = self.attachment.storage.get_available_name(
            target_path
        )

        saved_path = self.attachment.storage.save(
            target_path,
            uploaded_file,
        )

        self.attachment.name = saved_path
        self.attachment._committed = True

        # Update only the attachment field.
        super().save(update_fields=["attachment"])

        # Delete the previous attachment after successful replacement.
        if old_attachment_name and old_attachment_name != saved_path:
            self.attachment.storage.delete(old_attachment_name)


class DepartmentCost(models.Model):
    """Department expense not necessarily backed by a supplier invoice."""

    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="cost_entries"
    )

    house = models.ForeignKey(
        House,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="department_costs",
    )

    cost_date = models.DateField()
    description = models.CharField(max_length=250)

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=MONEY_VALIDATORS,
    )

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-cost_date"]

    def __str__(self):
        return f"{self.department} - {self.description} - {self.amount}"




from decimal import Decimal
from django.db import models


class VillaFinancialSummary(models.Model):
    """Stored monthly and yearly financial summaries for each villa."""

    PERIOD_CHOICES = [
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    ]

    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name="financial_summaries",
    )

    period_type = models.CharField(
        max_length=10,
        choices=PERIOD_CHOICES,
    )

    period_start = models.DateField()

    # Revenue
    work_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    program_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # Costs
    employee_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    invoice_expenses = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    ika_cost = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    gas_cost = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    company_invoice_cost = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    # Final totals
    total_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    gross_margin = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-period_start", "period_type"]

        constraints = [
            models.UniqueConstraint(
                fields=["house", "period_type", "period_start"],
                name="unique_villa_financial_period",
            )
        ]

        verbose_name = "Villa Financial Summary"
        verbose_name_plural = "Villa Financial Summaries"

    def calculate_totals(self):
        # Revenue includes work and program revenue only.
        self.total_revenue = (
            self.work_revenue + self.program_revenue
        )

        # Costs exclude customer-reimbursed invoices.
        self.total_cost = (
            self.employee_cost + self.ika_cost + self.gas_cost + self.company_invoice_cost
        )

        # Gross margin is revenue minus all costs.
        self.gross_margin = (
            self.total_revenue - self.total_cost
        )

    def save(self, *args, **kwargs):
        self.calculate_totals()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.house.name} - "
            f"{self.get_period_type_display()} - "
            f"{self.period_start}"
        )




class DepartmentFinancialSummary(models.Model):
    """Monthly and yearly financial summaries for departments."""

    PERIOD_CHOICES = [
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    ]

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="financial_summaries",
    )

    # NULL means the total for the entire department.
    # A villa ID means the summary is for that department at that villa.
    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name="department_financial_summaries",
        null=True,
        blank=True,
    )

    period_type = models.CharField(
        max_length=10,
        choices=PERIOD_CHOICES,
    )

    period_start = models.DateField()

    # Revenue
    work_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    # Costs
    employee_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    invoice_expenses = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    ika_cost = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    gas_cost = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    company_invoice_cost = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))

    # Final totals
    total_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    gross_margin = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-period_start", "department"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "department",
                    "house",
                    "period_type",
                    "period_start",
                ],
                condition=models.Q(house__isnull=False),
                name="unique_department_villa_period",
            ),
            models.UniqueConstraint(
                fields=[
                    "department",
                    "period_type",
                    "period_start",
                ],
                condition=models.Q(house__isnull=True),
                name="unique_department_total_period",
            ),
        ]

        verbose_name = "Department Financial Summary"
        verbose_name_plural = "Department Financial Summaries"

    def calculate_totals(self):
        # Department revenue comes only from completed work.
        self.total_revenue = self.work_revenue

        # Only company invoices reduce margin.
        self.total_cost = self.employee_cost + self.ika_cost + self.gas_cost + self.company_invoice_cost

        # Department gross margin includes company expenses.
        self.gross_margin = self.total_revenue - self.total_cost

    def save(self, *args, **kwargs):
        self.calculate_totals()
        super().save(*args, **kwargs)

    def __str__(self):
        scope = self.house.name if self.house else "All Villas"

        return (
            f"{self.department.name} - {scope} - "
            f"{self.get_period_type_display()} - "
            f"{self.period_start}"
        )




class SupplierPayment(models.Model):
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="payments"
    )

    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, null=True, blank=True, related_name="company_payments")

    payment_date = models.DateField()

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))]
    )

    reference = models.CharField(
        max_length=160,
        blank=True
    )

    notes = models.TextField(blank=True)

    def clean(self):
        super().clean()
        if self.invoice_id and (self.invoice.ownership != Ownership.COMPANY or self.invoice.supplier_id != self.supplier_id):
            raise ValidationError({"invoice": "Select a company invoice belonging to this supplier."})
        if self.invoice_id:
            self.reference = self.invoice.invoice_number

    def save(self, *args, **kwargs):
        self.full_clean()
        if kwargs.get("update_fields") is not None:
            kwargs["update_fields"] = set(kwargs["update_fields"]) | {"reference"}
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ["-payment_date", "-id"]

    def __str__(self):
        return f"{self.supplier} - {self.amount} €"




class CustomerPayment(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="payments",
    )

    invoice = models.ForeignKey(Invoice, on_delete=models.PROTECT, null=True, blank=True, related_name="customer_payments")

    payment_date = models.DateField()

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01"))
        ],
    )

    reference = models.CharField(
        max_length=160,
        blank=True,
        help_text="Invoice number, or blank for a general payment.",
    )

    receipt = models.FileField(
        upload_to="customer_receipts/%Y/%m/",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["pdf", "jpg", "jpeg", "png", "webp", "gif", "bmp", "tif", "tiff", "heic", "heif"])],
        help_text="Upload a PDF or image of the payment receipt.",
    )
    notes = models.TextField(blank=True)

    def clean(self):
        super().clean()
        if self.invoice_id and (self.invoice.ownership != Ownership.CUSTOMER or not self.invoice.house_id or self.invoice.house.customer_id != self.customer_id):
            raise ValidationError({"invoice": "Select an invoice belonging to this customer."})
        if self.invoice_id:
            self.reference = self.invoice.invoice_number

    def save(self, *args, **kwargs):
        self.full_clean()
        if kwargs.get("update_fields") is not None:
            kwargs["update_fields"] = set(kwargs["update_fields"]) | {"reference"}
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ["-payment_date", "-id"]

    def __str__(self):
        return f"{self.customer} - {self.amount} €"




class HouseInspection(models.Model):
    CONDITION_CHOICES = [
        ("good", "Good"),
        ("attention", "Needs Attention"),
        ("urgent", "Urgent Issue"),
    ]

    house = models.ForeignKey(
        House,
        on_delete=models.CASCADE,
        related_name="house_inspections",
    )

    inspection_date = models.DateTimeField()

    checked_by = models.CharField(
        max_length=150
    )

    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-inspection_date", "-id"]
        verbose_name = "House Inspection"
        verbose_name_plural = "House Inspections"

    def __str__(self):
        return (
            f"{self.house.name} - "
            f"{self.inspection_date:%d/%m/%Y}"
        )


from datetime import timedelta
from django.core.validators import MinValueValidator
from django.utils import timezone


class ImportantJobReminder(models.Model):

    class Importance(models.TextChoices):
        NORMAL = "normal", "Normal"
        IMPORTANT = "important", "Important"
        URGENT = "urgent", "Urgent"
        CRITICAL = "critical", "Critical"
        OVERDUE = "overdue", "Overdue"
        COMPLETED = "completed", "Completed"

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="important_job_reminders",
    )

    description = models.TextField()

    deadline = models.DateField(
        db_index=True,
    )

    procedure_days = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Procedure duration (days)",
    )

    completed = models.BooleanField(
        default=False,
        db_index=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
    )

    last_notification_level = models.CharField(
        max_length=20,
        blank=True,
        default="",
        editable=False,
    )

    last_notification_at = models.DateTimeField(
        null=True,
        blank=True,
        editable=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["deadline", "id"]
        verbose_name = "Important Job Reminder"
        verbose_name_plural = "Important Job Reminders"

    def __str__(self):
        return f"{self.customer} - {self.deadline}"

    @property
    def days_remaining(self):
        if self.deadline is None:
            return None
        return (
            self.deadline - timezone.localdate()
        ).days

    @property
    def notification_days(self):
        return (self.procedure_days or 0) * 1.5

    @property
    def recommended_start_date(self):
        if self.deadline is None or not self.procedure_days:
            return None
        return self.deadline - timedelta(
            days=int(self.notification_days)
        )

    @property
    def latest_start_date(self):
        if self.deadline is None or not self.procedure_days:
            return None
        return self.deadline - timedelta(
            days=self.procedure_days
        )

    @property
    def spare_days(self):
        if self.days_remaining is None or not self.procedure_days:
            return None
        return self.days_remaining - self.procedure_days

    @property
    def is_overdue(self):
        return (
            not self.completed
            and self.days_remaining is not None
            and self.days_remaining < 0
        )

    @property
    def importance(self):

        if self.completed:
            return self.Importance.COMPLETED

        if self.deadline is None or not self.procedure_days:
            return self.Importance.NORMAL

        remaining = self.days_remaining
        duration = self.procedure_days

        if remaining < 0:
            return self.Importance.OVERDUE

        if remaining < duration:
            return self.Importance.CRITICAL

        if remaining == duration:
            return self.Importance.URGENT

        if remaining <= self.notification_days:
            return self.Importance.IMPORTANT

        return self.Importance.NORMAL

    @property
    def email_required(self):
        return (
            not self.completed
            and self.days_remaining is not None
            and bool(self.procedure_days)
            and self.days_remaining <= self.notification_days
        )

    @property
    def importance_score(self):

        scores = {
            self.Importance.COMPLETED: 0,
            self.Importance.NORMAL: 1,
            self.Importance.IMPORTANT: 2,
            self.Importance.URGENT: 3,
            self.Importance.CRITICAL: 4,
            self.Importance.OVERDUE: 5,
        }

        return scores[self.importance]

    def save(self, *args, **kwargs):

        previous = None

        if self.pk:
            previous = (
                type(self).objects
                .filter(pk=self.pk)
                .first()
            )

        if self.completed:

            if not self.completed_at:
                self.completed_at = timezone.now()

        else:

            self.completed_at = None

            # Reset notifications if the job is reopened
            # or its schedule changes.
            if previous and (
                previous.completed
                or previous.deadline != self.deadline
                or previous.procedure_days != self.procedure_days
            ):
                self.last_notification_level = ""
                self.last_notification_at = None

        update_fields = kwargs.get("update_fields")

        if update_fields is not None:
            kwargs["update_fields"] = set(
                update_fields
            ) | {
                "completed_at",
                "last_notification_level",
                "last_notification_at",
                "updated_at",
            }

        super().save(*args, **kwargs)



class GroupedWorkEntry(WorkEntry):
    class Meta:
        proxy = True
        ordering = ["work_date", "house__name", "pk"]
        verbose_name = "Grouped work entry"
        verbose_name_plural = "Grouped work entries"
