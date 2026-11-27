from collections import defaultdict
from datetime import date
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape

from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    LongTable, TableStyle, Flowable, PageBreak,
)

from .models import (
    Customer, House, Employee, Department, Supplier,
    WorkEntry, VillaProgram, Invoice,
    CustomerPayment, SupplierPayment, Ownership,
)

from .customer_statement_export import _build_pdf


ZERO = Decimal("0")
NAVY = colors.HexColor("#253B36")
GREEN = colors.HexColor("#557967")
GOLD = colors.HexColor("#B79A62")
LIGHT = colors.HexColor("#F2F5F1")
MUTED = colors.HexColor("#718078")


def amount(value):
    return Decimal(str(value or "0"))


def money(value):
    return f"{amount(value):,.2f} EUR"


def safe(value):
    import re
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", str(value))
    return value.strip(" ._")[:85] or "Unknown"


def month_of(value):
    return value.strftime("%Y-%m")


def register_fonts():
    regular = getattr(settings, "CUSTOMER_STATEMENT_FONT_PATH", None)
    bold = getattr(settings, "CUSTOMER_STATEMENT_BOLD_FONT_PATH", None)

    choices = [
        (
            regular,
            bold,
        ),
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ),
        (
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ),
    ]

    for normal_path, bold_path in choices:
        if (
            normal_path and bold_path
            and Path(normal_path).is_file()
            and Path(bold_path).is_file()
        ):
            if "BusinessRegular" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(
                    TTFont("BusinessRegular", str(normal_path))
                )
                pdfmetrics.registerFont(
                    TTFont("BusinessBold", str(bold_path))
                )
            return "BusinessRegular", "BusinessBold"

    raise RuntimeError(
        "No Unicode PDF font found. Set "
        "CUSTOMER_STATEMENT_FONT_PATH and "
        "CUSTOMER_STATEMENT_BOLD_FONT_PATH in settings.py."
    )


class RevenueBarChart(Flowable):
    def __init__(self, values, width=500, height=235):
        super().__init__()
        self.values = list(values)[-12:]
        self.width = width
        self.height = height

    def draw(self):
        canvas = self.canv
        normal, bold = register_fonts()

        left = 62
        bottom = 42
        top = self.height - 28
        plot_width = self.width - left - 12
        plot_height = top - bottom

        maximum = max(
            [float(v) for _, v in self.values] + [0.0]
        )
        maximum = maximum * 1.15 if maximum else 1

        canvas.setFont(bold, 10)
        canvas.setFillColor(NAVY)
        canvas.drawString(
            left, self.height - 14, "REVENUE BY MONTH (EUR)"
        )

        for tick in range(5):
            y = bottom + plot_height * tick / 4
            canvas.setStrokeColor(colors.HexColor("#DFE6E0"))
            canvas.line(left, y, self.width - 5, y)
            canvas.setFont(normal, 7)
            canvas.setFillColor(MUTED)
            canvas.drawRightString(
                left - 7, y - 3,
                f"{maximum * tick / 4:,.0f}"
            )

        if not self.values:
            canvas.setFont(normal, 10)
            canvas.drawCentredString(
                self.width / 2,
                self.height / 2,
                "No recorded revenue"
            )
            return

        step = plot_width / len(self.values)
        bar_width = min(30, step * 0.65)

        for index, (period, value) in enumerate(self.values):
            x = left + step * (index + 0.5)
            value = float(value)
            height = max(0, value / maximum * plot_height)

            canvas.setFillColor(
                GREEN if index % 2 == 0 else GOLD
            )
            canvas.roundRect(
                x - bar_width / 2,
                bottom,
                bar_width,
                height,
                3,
                stroke=0,
                fill=1,
            )

            canvas.setFillColor(NAVY)
            canvas.setFont(normal, 7)
            canvas.drawCentredString(
                x, bottom - 14, str(period)[2:]
            )

            if value:
                canvas.setFont(normal, 6)
                canvas.drawCentredString(
                    x,
                    min(top + 4, bottom + height + 5),
                    f"{value:,.0f}",
                )


def create_pdf(title, subtitle, sections):
    normal, bold = register_fonts()
    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=48,
        bottomMargin=48,
        title=title,
    )

    title_style = ParagraphStyle(
        "BusinessTitle",
        fontName=bold,
        fontSize=21,
        leading=28,
        textColor=NAVY,
        spaceAfter=12,
    )

    heading_style = ParagraphStyle(
        "BusinessHeading",
        fontName=bold,
        fontSize=13,
        leading=18,
        textColor=NAVY,
        spaceBefore=16,
        spaceAfter=9,
    )

    body_style = ParagraphStyle(
        "BusinessBody",
        fontName=normal,
        fontSize=8.5,
        leading=13,
        textColor=NAVY,
        spaceAfter=8,
        wordWrap="CJK",
    )

    header_style = ParagraphStyle(
        "BusinessTableHeader",
        parent=body_style,
        fontName=bold,
        fontSize=7,
        leading=10,
        textColor=colors.white,
    )

    cell_style = ParagraphStyle(
        "BusinessTableCell",
        parent=body_style,
        fontSize=7,
        leading=10,
    )

    story = [
        Paragraph(escape(title), title_style),
        Paragraph(escape(subtitle), body_style),
        Spacer(1, 12),
    ]

    for kind, label, content in sections:
        if kind == "heading":
            story.append(
                Paragraph(escape(label), heading_style)
            )

        elif kind == "text":
            story.append(
                Paragraph(escape(str(content)), body_style)
            )

        elif kind == "chart":
            story.append(
                RevenueBarChart(content, document.width)
            )
            story.append(Spacer(1, 12))

        elif kind == "table":
            headers, rows = content
            rows = list(rows)

            if not headers:
                continue

            widths = [
                document.width / len(headers)
                for _ in headers
            ]

            matrix = [[
                Paragraph(escape(str(h)), header_style)
                for h in headers
            ]]

            for row in rows:
                matrix.append([
                    Paragraph(
                        escape(str(value if value is not None else "")),
                        cell_style,
                    )
                    for value in row
                ])

            if len(matrix) == 1:
                matrix.append([
                    Paragraph("No records", cell_style)
                ] + [
                    Paragraph("", cell_style)
                    for _ in headers[1:]
                ])

            table = LongTable(
                matrix,
                colWidths=widths,
                repeatRows=1,
            )

            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, LIGHT]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]))

            story.append(table)

        elif kind == "page":
            story.append(PageBreak())

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(normal, 7)
        canvas.setFillColor(MUTED)
        canvas.drawString(
            40, 25,
            "PAROS KATOIKIA | CONFIDENTIAL MANAGEMENT REPORT"
        )
        canvas.drawRightString(
            A4[0] - 40, 25, f"Page {doc.page}"
        )
        canvas.restoreState()

    document.build(
        story,
        onFirstPage=footer,
        onLaterPages=footer,
    )

    return output.getvalue()


def pdf_table(archive, filename, headers, rows):
    rows = list(rows)

    archive.writestr(
        filename,
        create_pdf(
            filename.split("/")[-1].replace("_", " ").replace(".pdf", ""),
            f"{len(rows)} records | Generated {timezone.localdate()}",
            [
                ("table", "", (headers, rows)),
            ],
        ),
    )


def add_attachment(archive, folder, invoice):
    if not invoice.attachment:
        return

    try:
        filename = Path(
            invoice.attachment.name.replace("\\", "/")
        ).name

        destination = (
            f"{folder}/{invoice.pk}_{safe(filename)}"
        )

        with invoice.attachment.open("rb") as source:
            with archive.open(destination, "w") as target:
                while True:
                    chunk = source.read(1024 * 1024)
                    if not chunk:
                        break
                    target.write(chunk)

    except (OSError, ValueError, FileNotFoundError):
        archive.writestr(
            f"{folder}/MISSING_{invoice.pk}.txt",
            f"Attachment unavailable for invoice {invoice.invoice_number}",
        )


def program_months(program, today):
    if not program.start_date or program.start_date > today:
        return []

    end = min(program.end_date or today, today)

    if end < program.start_date:
        return []

    year = program.start_date.year
    month = program.start_date.month
    result = []

    while (year, month) <= (end.year, end.month):
        result.append(f"{year:04d}-{month:02d}")
        month += 1

        if month > 12:
            year += 1
            month = 1

    return result


def export_business_overview():
    today = timezone.localdate()

    customers = list(Customer.objects.all().order_by("name"))
    villas = list(
        House.objects.filter(is_company_property=False, customer__isnull=False).select_related("customer").order_by("name")
    )
    employees = list(
        Employee.objects.select_related("department").all()
    )
    suppliers = list(Supplier.objects.all().order_by("name"))
    departments = list(Department.objects.all().order_by("name"))

    works = list(
        WorkEntry.objects.filter(
            work_date__lte=today
        ).select_related(
            "house__customer",
            "employee",
            "service__department",
        ).order_by("work_date", "pk")
    )

    invoices = list(
        Invoice.objects.filter(
            invoice_date__lte=today
        ).select_related(
            "house__customer",
            "supplier",
            "department",
        ).order_by("invoice_date", "pk")
    )

    programs = list(
        VillaProgram.objects.select_related(
            "house__customer"
        ).filter(house__is_company_property=False, house__customer__isnull=False)
    )

    customer_payments = list(
        CustomerPayment.objects.filter(
            payment_date__lte=today
        ).select_related("customer", "invoice")
    )

    supplier_payments = list(
        SupplierPayment.objects.filter(
            payment_date__lte=today
        ).select_related("supplier", "invoice")
    )

    monthly = defaultdict(
        lambda: defaultdict(lambda: ZERO)
    )

    customer_data = defaultdict(
        lambda: defaultdict(lambda: ZERO)
    )
    supplier_data = defaultdict(
        lambda: defaultdict(lambda: ZERO)
    )
    employee_data = defaultdict(
        lambda: defaultdict(lambda: ZERO)
    )
    villa_data = defaultdict(
        lambda: defaultdict(lambda: ZERO)
    )
    department_data = defaultdict(
        lambda: defaultdict(lambda: ZERO)
    )
    service_data = defaultdict(
        lambda: defaultdict(lambda: ZERO)
    )

    customer_works = defaultdict(list)
    customer_invoices = defaultdict(list)
    customer_programs = defaultdict(list)
    customer_payment_records = defaultdict(list)
    supplier_invoices = defaultdict(list)
    supplier_payment_records = defaultdict(list)
    employee_works = defaultdict(list)

    for work in works:
        period = month_of(work.work_date)
        revenue = amount(work.customer_charge) if work.ownership == Ownership.CUSTOMER else ZERO
        cost = amount(work.employee_cost)

        customer_id = work.house.customer_id if work.ownership == Ownership.CUSTOMER and work.house_id else None
        villa_id = work.house_id
        employee_id = work.employee_id

        department = (
            work.service.department.name
            if work.service.department_id
            else "Unassigned"
        )
        service = work.service.name

        monthly[period]["work_revenue"] += revenue
        monthly[period]["employee_cost"] += cost

        customer_data[customer_id]["work_revenue"] += revenue
        customer_data[customer_id]["employee_cost"] += cost

        employee_data[employee_id]["revenue"] += revenue
        employee_data[employee_id]["cost"] += cost
        employee_data[employee_id]["hours"] += amount(work.hours)
        employee_data[employee_id]["entries"] += 1

        villa_data[villa_id]["work_revenue"] += revenue
        villa_data[villa_id]["employee_cost"] += cost

        department_data[department]["revenue"] += revenue
        department_data[department]["cost"] += cost

        service_data[service]["revenue"] += revenue
        service_data[service]["cost"] += cost

        customer_works[customer_id].append(work)
        employee_works[employee_id].append(work)

    for invoice in invoices:
        value = amount(invoice.amount)
        period = month_of(invoice.invoice_date)

        if invoice.ownership == Ownership.COMPANY:
            monthly[period]["supplier_invoices"] += value
            if invoice.department_id:
                department_data[invoice.department.name]["invoices"] += value
            supplier_data[invoice.supplier_id]["invoices"] += value
            supplier_invoices[invoice.supplier_id].append(invoice)
        elif invoice.ownership == Ownership.CUSTOMER and invoice.house_id:
            customer_id = invoice.house.customer_id
            customer_data[customer_id]["invoices"] += value
            villa_data[invoice.house_id]["invoices"] += value
            customer_invoices[customer_id].append(invoice)

    for program in programs:
        if not program.house_id:
            continue

        customer_id = program.house.customer_id
        months = program_months(program, today)

        if months:
            customer_programs[customer_id].append(program)

        for period in months:
            value = amount(program.price)

            monthly[period]["program_revenue"] += value
            customer_data[customer_id]["program_revenue"] += value
            villa_data[program.house_id]["program_revenue"] += value

    for payment in customer_payments:
        value = amount(payment.amount)

        monthly[month_of(payment.payment_date)][
            "customer_payments"
        ] += value

        info = customer_data[payment.customer_id]
        if payment.invoice_id and payment.invoice.invoice_date <= today:
            info["invoice_paid"] += value
            info["paid"] += value
        elif not payment.invoice_id and not (payment.reference or "").strip():
            info["service_paid"] += value
            info["paid"] += value
        else:
            info["unmatched"] += value
        customer_payment_records[payment.customer_id].append(payment)

    for payment in supplier_payments:
        value = amount(payment.amount)

        monthly[month_of(payment.payment_date)][
            "supplier_payments"
        ] += value

        supplier_data[payment.supplier_id]["paid"] += value
        supplier_payment_records[payment.supplier_id].append(payment)

    def financials(values):
        work_revenue = values["work_revenue"]
        program_revenue = values["program_revenue"]
        employee_cost = values["employee_cost"]
        invoice_cost = values["supplier_invoices"]

        revenue = work_revenue + program_revenue
        gross_margin = revenue - employee_cost
        result = gross_margin - invoice_cost

        margin_percent = (
            gross_margin / revenue * 100
            if revenue else ZERO
        )

        return {
            "revenue": revenue,
            "gross_margin": gross_margin,
            "gross_margin_percent": margin_percent,
            "result": result,
            "employee_cost": employee_cost,
            "invoice_cost": invoice_cost,
            "customer_payments": values["customer_payments"],
            "supplier_payments": values["supplier_payments"],
        }

    annual = defaultdict(
        lambda: defaultdict(lambda: ZERO)
    )

    total_values = defaultdict(lambda: ZERO)

    for period, values in monthly.items():
        year = period[:4]

        for key, value in values.items():
            annual[year][key] += value
            total_values[key] += value

    overall = financials(total_values)
    this_year = financials(annual[str(today.year)])
    this_month = financials(monthly[today.strftime("%Y-%m")])

    monthly_revenue = [
        (
            period,
            financials(monthly[period])["revenue"],
        )
        for period in sorted(monthly)
    ]

    def summary_text(fin):
        return (
            f"Total revenue: {money(fin['revenue'])}. "
            f"Recorded gross margin: {money(fin['gross_margin'])}. "
            f"Gross margin percentage: "
            f"{fin['gross_margin_percent']:.1f}%. "
            f"Employee work costs: {money(fin['employee_cost'])}. "
            f"Company invoice costs: {money(fin['invoice_cost'])}. "
            f"Result after company invoices: {money(fin['result'])}. "
            f"Customer payments: {money(fin['customer_payments'])}. "
            f"Supplier payments: {money(fin['supplier_payments'])}."
        )

    def period_rows(source):
        rows = []

        for period in sorted(source):
            fin = financials(source[period])

            rows.append((
                period,
                money(fin["revenue"]),
                money(fin["gross_margin"]),
                f"{fin['gross_margin_percent']:.1f}%",
                money(fin["result"]),
                money(fin["customer_payments"]),
            ))

        return rows

    executive_sections = [
        ("heading", "Business at a glance", None),
        (
            "text", "",
            f"{len(customers)} customers | "
            f"{len(villas)} villas | "
            f"{len(employees)} staff | "
            f"{len(suppliers)} suppliers | "
            f"{len(works)} work entries | "
            f"{len(invoices)} invoices."
        ),

        ("heading", "Current month", None),
        ("text", "", summary_text(this_month)),

        ("heading", "Current year", None),
        ("text", "", summary_text(this_year)),

        ("heading", "All recorded history", None),
        ("text", "", summary_text(overall)),

        ("heading", "Monthly revenue trend", None),
        ("chart", "", monthly_revenue[-12:]),

        ("heading", "Monthly financial performance", None),
        (
            "table", "",
            (
                [
                    "Month", "Revenue", "Gross margin",
                    "Margin %", "Result", "Collected"
                ],
                period_rows(monthly)[-12:],
            )
        ),

        ("heading", "Annual financial performance", None),
        (
            "table", "",
            (
                [
                    "Year", "Revenue", "Gross margin",
                    "Margin %", "Result", "Collected"
                ],
                period_rows(annual),
            )
        ),

        ("heading", "Financial interpretation", None),
        (
            "text", "",
            "Revenue includes recorded work-entry customer charges "
            "and monthly villa-program revenue. Recorded gross margin "
            "subtracts employee work-entry costs. The result after "
            "invoices also subtracts supplier invoice expenses. "
            "IKA, fuel and other department overhead are not included in this report result. "
            "These are management calculations, not audited profit."
        ),
        (
            "text", "",
            "Customer account balances additionally include "
            "villa-linked supplier invoices, matching the dashboard. "
            "These invoice amounts are not counted again as company "
            "revenue or operating expenses. Invoice payments use direct invoice links; "
            "unmatched customer references are excluded from allocated balances."
        ),
    ]

    output = BytesIO()
    root = f"Business_Overview_{today:%Y-%m-%d}"

    with ZipFile(output, "w", ZIP_DEFLATED, allowZip64=True) as archive:

        archive.writestr(
            f"{root}/00_Executive_Overview.pdf",
            create_pdf(
                "PAROS KATOIKIA | Executive Overview",
                f"Management report | {today:%d %B %Y}",
                executive_sections,
            ),
        )

        pdf_table(
            archive,
            f"{root}/01_Financials/Monthly_Performance.pdf",
            [
                "Month", "Revenue", "Gross margin",
                "Margin %", "Result", "Collected"
            ],
            period_rows(monthly),
        )

        pdf_table(
            archive,
            f"{root}/01_Financials/Annual_Performance.pdf",
            [
                "Year", "Revenue", "Gross margin",
                "Margin %", "Result", "Collected"
            ],
            period_rows(annual),
        )

        pdf_table(
            archive,
            f"{root}/01_Financials/All_Work_Entries.pdf",
            [
                "Date", "Customer", "Villa",
                "Employee", "Service", "Hours",
                "Description", "Charge", "Cost"
            ],
            [
                (
                    w.work_date,
                    w.house.customer.name if w.house_id and w.house.customer_id else "Company",
                    w.house.name if w.house_id else "—",
                    str(w.employee),
                    w.service.name,
                    w.hours,
                    w.description,
                    money(w.customer_charge),
                    money(w.employee_cost),
                )
                for w in works
            ],
        )

        pdf_table(
            archive,
            f"{root}/02_Customers/Customer_Balances.pdf",
            [
                "Customer", "Work", "Programs",
                "Invoices", "Paid", "Balance"
            ],
            [
                (
                    c.name,
                    money(customer_data[c.pk]["work_revenue"]),
                    money(customer_data[c.pk]["program_revenue"]),
                    money(customer_data[c.pk]["invoices"]),
                    money(customer_data[c.pk]["paid"]),
                    money(
                        customer_data[c.pk]["work_revenue"]
                        + customer_data[c.pk]["program_revenue"]
                        + customer_data[c.pk]["invoices"]
                        - customer_data[c.pk]["paid"]
                    ),
                )
                for c in customers
            ],
        )

        for customer in customers:
            cid = customer.pk
            info = customer_data[cid]

            folder = (
                f"{root}/02_Customers/"
                f"{cid}_{safe(customer.name)}"
            )

            owned_villas = [
                villa for villa in villas
                if villa.customer_id == cid
            ]

            statement = _build_pdf(
                customer,
                owned_villas,
                customer_works[cid],
                customer_invoices[cid],
                customer_programs[cid],
                customer_payment_records[cid],
                today,
            )

            archive.writestr(
                f"{folder}/Customer_Statement.pdf",
                statement,
            )

            revenue = (
                info["work_revenue"]
                + info["program_revenue"]
            )
            margin = revenue - info["employee_cost"]

            customer_months = defaultdict(lambda: ZERO)

            for work in customer_works[cid]:
                customer_months[month_of(work.work_date)] += (
                    amount(work.customer_charge)
                )

            for program in customer_programs[cid]:
                for period in program_months(program, today):
                    customer_months[period] += amount(program.price)

            archive.writestr(
                f"{folder}/Financial_Analysis.pdf",
                create_pdf(
                    f"Customer | {customer.name}",
                    f"Financial analysis | {today}",
                    [
                        ("heading", "Revenue and gross margin", None),
                        (
                            "text", "",
                            f"Total revenue: {money(revenue)}. "
                            f"Recorded employee work costs: "
                            f"{money(info['employee_cost'])}. "
                            f"Recorded gross margin: {money(margin)}."
                        ),
                        ("heading", "Account balance", None),
                        (
                            "text", "",
                            f"Villa-linked invoices: "
                            f"{money(info['invoices'])}. "
                            f"Service payments: {money(info['service_paid'])}. "
                            f"Invoice payments: {money(info['invoice_paid'])}. "
                            f"Unmatched payments: {money(info['unmatched'])}. "
                            f"Balance: "
                            f"{money(revenue + info['invoices'] - info['paid'])}."
                        ),
                        ("heading", "Monthly revenue", None),
                        (
                            "chart", "",
                            sorted(customer_months.items())[-12:]
                        ),
                    ],
                ),
            )

            pdf_table(
                archive,
                f"{folder}/Work_Entries.pdf",
                [
                    "Date", "Villa", "Employee",
                    "Service", "Hours", "Description", "Charge"
                ],
                [
                    (
                        w.work_date,
                        w.house.name if w.house_id else "—",
                        str(w.employee),
                        w.service.name,
                        w.hours,
                        w.description,
                        money(w.customer_charge),
                    )
                    for w in customer_works[cid]
                ],
            )

            for invoice in customer_invoices[cid]:
                add_attachment(
                    archive,
                    f"{folder}/Invoices",
                    invoice,
                )

        pdf_table(
            archive,
            f"{root}/03_Suppliers/Supplier_Balances.pdf",
            ["Supplier", "Invoices", "Paid", "Balance"],
            [
                (
                    s.name,
                    money(supplier_data[s.pk]["invoices"]),
                    money(supplier_data[s.pk]["paid"]),
                    money(
                        supplier_data[s.pk]["invoices"]
                        - supplier_data[s.pk]["paid"]
                    ),
                )
                for s in suppliers
            ],
        )

        for supplier in suppliers:
            sid = supplier.pk
            info = supplier_data[sid]
            folder = (
                f"{root}/03_Suppliers/"
                f"{sid}_{safe(supplier.name)}"
            )

            supplier_months = defaultdict(lambda: ZERO)

            for invoice in supplier_invoices[sid]:
                supplier_months[
                    month_of(invoice.invoice_date)
                ] += amount(invoice.amount)

            archive.writestr(
                f"{folder}/Supplier_Summary.pdf",
                create_pdf(
                    f"Supplier | {supplier.name}",
                    f"Supplier report | {today}",
                    [
                        ("heading", "Financial position", None),
                        (
                            "text", "",
                            f"Total invoiced: {money(info['invoices'])}. "
                            f"Total paid: {money(info['paid'])}. "
                            f"Outstanding: "
                            f"{money(info['invoices'] - info['paid'])}."
                        ),
                        ("heading", "Monthly invoice amounts", None),
                        (
                            "chart", "",
                            sorted(supplier_months.items())[-12:]
                        ),
                        ("heading", "Company context", None),
                        (
                            "text", "",
                            f"Company revenue: "
                            f"{money(overall['revenue'])}. "
                            f"Company recorded gross margin: "
                            f"{money(overall['gross_margin'])}. "
                            "These company totals are context, not "
                            "revenue generated by the supplier."
                        ),
                    ],
                ),
            )

            pdf_table(
                archive,
                f"{folder}/Invoices.pdf",
                [
                    "Date", "Invoice", "Villa",
                    "Department", "Amount", "Description"
                ],
                [
                    (
                        i.invoice_date,
                        i.invoice_number,
                        i.house.name if i.house_id else "General",
                        i.department.name,
                        money(i.amount),
                        i.description,
                    )
                    for i in supplier_invoices[sid]
                ],
            )

            pdf_table(
                archive,
                f"{folder}/Payments.pdf",
                ["Date", "Reference", "Amount"],
                [
                    (
                        p.payment_date,
                        p.invoice.invoice_number if p.invoice_id else (p.reference or "Unallocated"),
                        money(p.amount),
                    )
                    for p in supplier_payment_records[sid]
                ],
            )

            for invoice in supplier_invoices[sid]:
                add_attachment(
                    archive,
                    f"{folder}/Invoice_Attachments",
                    invoice,
                )

        pdf_table(
            archive,
            f"{root}/04_Staff/Staff_Performance.pdf",
            [
                "Employee", "Entries", "Hours",
                "Revenue", "Work cost", "Gross margin"
            ],
            [
                (
                    str(e),
                    employee_data[e.pk]["entries"],
                    employee_data[e.pk]["hours"],
                    money(employee_data[e.pk]["revenue"]),
                    money(employee_data[e.pk]["cost"]),
                    money(
                        employee_data[e.pk]["revenue"]
                        - employee_data[e.pk]["cost"]
                    ),
                )
                for e in employees
            ],
        )

        for employee in employees:
            eid = employee.pk
            info = employee_data[eid]
            folder = (
                f"{root}/04_Staff/"
                f"{eid}_{safe(str(employee))}"
            )

            employee_months = defaultdict(lambda: ZERO)

            for work in employee_works[eid]:
                employee_months[
                    month_of(work.work_date)
                ] += amount(work.customer_charge)

            archive.writestr(
                f"{folder}/Staff_Summary.pdf",
                create_pdf(
                    f"Staff | {employee}",
                    f"Work performance | {today}",
                    [
                        ("heading", "Recorded work", None),
                        (
                            "text", "",
                            f"Entries: {info['entries']}. "
                            f"Hours: {info['hours']}. "
                            f"Work revenue: {money(info['revenue'])}. "
                            f"Recorded work cost: {money(info['cost'])}. "
                            f"Recorded gross margin: "
                            f"{money(info['revenue'] - info['cost'])}."
                        ),
                        ("heading", "Monthly work revenue", None),
                        (
                            "chart", "",
                            sorted(employee_months.items())[-12:]
                        ),
                        ("heading", "Important note", None),
                        (
                            "text", "",
                            "Work cost is based on saved work entries. "
                            "It may not include full payroll, taxes, "
                            "benefits, or fixed monthly salaries."
                        ),
                    ],
                ),
            )

            pdf_table(
                archive,
                f"{folder}/Work_Entries.pdf",
                [
                    "Date", "Customer", "Villa",
                    "Service", "Hours", "Description",
                    "Revenue", "Work cost"
                ],
                [
                    (
                        w.work_date,
                        w.house.customer.name if w.house_id and w.house.customer_id else "Company",
                        w.house.name if w.house_id else "—",
                        w.service.name,
                        w.hours,
                        w.description,
                        money(w.customer_charge),
                        money(w.employee_cost),
                    )
                    for w in employee_works[eid]
                ],
            )

        for villa in villas:
            info = villa_data[villa.pk]
            revenue = (
                info["work_revenue"]
                + info["program_revenue"]
            )
            margin = revenue - info["employee_cost"]

            archive.writestr(
                f"{root}/05_Villas/"
                f"{villa.pk}_{safe(villa.name)}.pdf",
                create_pdf(
                    f"Villa | {villa.name}",
                    f"Customer: {villa.customer.name}",
                    [
                        ("heading", "Financial performance", None),
                        (
                            "text", "",
                            f"Total revenue: {money(revenue)}. "
                            f"Recorded gross margin: {money(margin)}. "
                            f"Customer invoice reimbursements: "
                            f"{money(info['invoices'])}. "
                            "Reimbursements are excluded from operating margin."
                        ),
                    ],
                ),
            )

        for department in departments:
            info = department_data[department.name]

            archive.writestr(
                f"{root}/06_Departments/"
                f"{department.pk}_{safe(department.name)}.pdf",
                create_pdf(
                    f"Department | {department.name}",
                    f"Performance report | {today}",
                    [
                        ("heading", "Financial performance", None),
                        (
                            "text", "",
                            f"Work revenue: {money(info['revenue'])}. "
                            f"Employee work costs: {money(info['cost'])}. "
                            f"Recorded gross margin: "
                            f"{money(info['revenue'] - info['cost'])}. "
                            f"Company invoice costs: "
                            f"{money(info['invoices'])}. "
                            f"Result after company invoices: "
                            f"{money(info['revenue'] - info['cost'] - info['invoices'])}."
                        ),
                    ],
                ),
            )

        for service_name, info in sorted(service_data.items()):
            archive.writestr(
                f"{root}/07_Services/{safe(service_name)}.pdf",
                create_pdf(
                    f"Service | {service_name}",
                    f"Performance report | {today}",
                    [
                        ("heading", "Financial performance", None),
                        (
                            "text", "",
                            f"Total work revenue: "
                            f"{money(info['revenue'])}. "
                            f"Recorded work costs: "
                            f"{money(info['cost'])}. "
                            f"Recorded gross margin: "
                            f"{money(info['revenue'] - info['cost'])}."
                        ),
                    ],
                ),
            )

        archive.writestr(
            f"{root}/00_Report_Guide.pdf",
            create_pdf(
                "Financial Reporting Guide",
                f"PAROS KATOIKIA | {today}",
                [
                    ("heading", "Revenue", None),
                    (
                        "text", "",
                        "Revenue is recorded work-entry customer charges "
                        "plus full-month villa-program charges."
                    ),
                    ("heading", "Gross margin", None),
                    (
                        "text", "",
                        "Recorded gross margin is revenue minus "
                        "employee costs stored in work entries."
                    ),
                    ("heading", "Result after invoices", None),
                    (
                        "text", "",
                        "The calculated result also subtracts "
                        "company-owned supplier invoice expenses. This is not "
                        "a complete accounting net profit."
                    ),
                    ("heading", "Customer balances", None),
                    (
                        "text", "",
                        "Customer balances include villa-linked "
                        "supplier invoices, matching the dashboard. "
                        "These are not counted again as business revenue."
                    ),
                    ("heading", "Reporting limitations", None),
                    (
                        "text", "",
                        "Future-dated records are excluded. "
                        "Villa programs are charged for whole "
                        "overlapping months without proration. "
                        "Programs missing a start date are excluded. "
                        "Linked payments are assigned to individual invoices. "
                        "Unlinked supplier payments remain supplier-account payments. "
                        "Unmatched customer references are excluded from allocated balances."
                    ),
                    ("heading", "Confidentiality", None),
                    (
                        "text", "",
                        "This export contains confidential customer, "
                        "supplier and employee information. "
                        "Store it securely and restrict access."
                    ),
                ],
            ),
        )

    response = HttpResponse(
        output.getvalue(),
        content_type="application/zip",
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{root}.zip"'
    )
    response["Cache-Control"] = "private, no-store"

    return response
