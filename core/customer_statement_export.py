"""Customer statement ZIP: PDF report plus original invoice attachments.
Install alongside core/views.py and expose via CustomerViewSet action.
Requires reportlab (pip install reportlab).
"""
from collections import defaultdict
from xml.sax.saxutils import escape
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from io import BytesIO
from pathlib import PurePosixPath
import re
import unicodedata
from zipfile import ZipFile, ZIP_DEFLATED

from django.conf import settings
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    KeepTogether, PageBreak, Flowable,
)
from reportlab.lib.pagesizes import A4
from .models import (
    House, WorkEntry, Invoice, VillaProgram, CustomerPayment,
    HouseInspection, HouseWaterReading, HouseWaterTankReading,
)

D = lambda value: Decimal(str(value or '0'))
EURO = lambda value: f"{D(value):,.2f} EUR"
NAVY = colors.HexColor('#203D36')
GREEN = colors.HexColor('#3D7561')
GOLD = colors.HexColor('#B99B65')
LIGHT = colors.HexColor('#F3F6F3')
MUTED = colors.HexColor('#61756C')

# Default Greek standard VAT. Override in Django settings for special cases.
VAT_RATE = D(getattr(settings, 'CUSTOMER_STATEMENT_VAT_RATE', '0.24'))
PRICES_INCLUDE_VAT = getattr(settings, 'CUSTOMER_STATEMENT_PRICES_INCLUDE_VAT', False)

def _money(value):
    return D(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def _vat_parts(value):
    """Return (net, VAT, gross) based on the configured source-price convention."""
    value = _money(value)
    if PRICES_INCLUDE_VAT:
        net = _money(value / (Decimal('1') + VAT_RATE))
        return net, value - net, value
    vat = _money(value * VAT_RATE)
    return value, vat, value + vat



def _work_rows(w):
    """Keep each purchase row attached to its parent work entry."""
    rows = [(w.work_date.isoformat(), w.house.name, w.service.name,
             f'{D(w.hours):,.0f} hours', w.description or '—', EURO(w.customer_charge))]
    if D(w.additional_charges) != 0:
        rows.append(('', '', 'Additional charges', '',
                     w.additional_charges_notes or 'Materials / purchases',
                     EURO(w.additional_charges)))
    return rows


def _safe(value):
    s = unicodedata.normalize('NFKC', str(value or 'UNKNOWN'))
    s = re.sub(r'[^\w.\-]+', '_', s, flags=re.UNICODE).strip('._')
    return s[:100] or 'UNKNOWN'


def _font_names():
    # Set CUSTOMER_STATEMENT_FONT_PATH in settings for guaranteed Greek support.
    from pathlib import Path
    candidates = [getattr(settings, 'CUSTOMER_STATEMENT_FONT_PATH', None),
                  '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                  'C:/Windows/Fonts/arial.ttf']
    bold_candidates = [getattr(settings, 'CUSTOMER_STATEMENT_BOLD_FONT_PATH', None),
                       '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                       'C:/Windows/Fonts/arialbd.ttf']
    regular = next((str(p) for p in candidates if p and Path(p).is_file()), None)
    bold = next((str(p) for p in bold_candidates if p and Path(p).is_file()), None)
    if not regular:
        raise RuntimeError('Set CUSTOMER_STATEMENT_FONT_PATH to a Unicode TTF font (e.g. DejaVuSans.ttf).')
    if 'StatementRegular' not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont('StatementRegular', regular))
    if 'StatementBold' not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont('StatementBold', bold or regular))
    pdfmetrics.registerFontFamily('StatementRegular', normal='StatementRegular', bold='StatementBold')
    return 'StatementRegular', 'StatementBold'


class HorizontalBars(Flowable):
    def __init__(self, items, width=475):
        super().__init__()
        self.items = [(str(n), float(v)) for n, v in items if D(v) > 0]
        self.width = width
        self.height = max(34, len(self.items) * 39 + 8)

    def draw(self):
        c = self.canv
        if not self.items:
            c.setFont('StatementRegular', 9)
            c.drawString(5, 12, 'No charges recorded for this period.')
            return
        largest = max(v for _, v in self.items)
        for i, (name, value) in enumerate(self.items):
            y = self.height - (i + 1) * 39 + 12
            c.setFillColor(NAVY)
            c.setFont('StatementRegular', 9)
            c.drawString(4, y + 14, name[:56])
            c.setFillColor(LIGHT)
            c.roundRect(4, y, self.width - 115, 10, 4, fill=1, stroke=0)
            c.setFillColor(GREEN if i % 2 == 0 else GOLD)
            c.roundRect(4, y, max(2, (self.width - 115) * value / largest), 10, 4, fill=1, stroke=0)
            c.setFillColor(NAVY)
            c.setFont('StatementRegular', 8)
            c.drawRightString(self.width - 3, y + 1, EURO(value))


def _month_count(program, today):
    if not program.start_date or program.start_date > today:
        return 0
    end = min(program.end_date or today, today)
    if end < program.start_date:
        return 0
    return (end.year - program.start_date.year) * 12 + end.month - program.start_date.month + 1


def _customer_check_activity(villa_ids, start, cutoff):
    """Report-only activity rows; never create WorkEntry or add billable charges.

    Returns (date, villa name, service label, units, details, charge).
    All source records are scoped to the customer's villas and reporting dates.
    """
    if not villa_ids or cutoff < start:
        return []

    # Compare local dates, matching WorkEntry.work_date's monthly reporting window.
    activities = []
    inspections = (HouseInspection.objects.filter(
        house_id__in=villa_ids,
        inspection_date__date__gte=start,
        inspection_date__date__lte=cutoff,
    ).select_related('house').order_by('inspection_date', 'pk'))
    for item in inspections:
        details = (
            f"Checked by: {item.checked_by or '—'}; "
            f"Condition: {item.get_condition_display()}"
        )
        if item.notes:
            details += f"; Notes: {item.notes}"
        activities.append((
            timezone.localtime(item.inspection_date).date().isoformat(),
            item.house.name, 'House check', 'Included', details, EURO(0),
        ))

    meters = (HouseWaterReading.objects.filter(
        house_id__in=villa_ids,
        reading_date__date__gte=start,
        reading_date__date__lte=cutoff,
    ).select_related('house').order_by('reading_date', 'pk'))
    for item in meters:
        details = (
            f"Checked by: {item.checked_by or '—'}; "
            f"Municipal meter: {item.meter_litres:,.2f} L"
        )
        if item.notes:
            details += f"; Notes: {item.notes}"
        activities.append((
            timezone.localtime(item.reading_date).date().isoformat(),
            item.house.name, 'Municipal water measurement', 'Included', details, EURO(0),
        ))

    tank_checks = (HouseWaterTankReading.objects.filter(
        tank__house_id__in=villa_ids,
        reading_date__date__gte=start,
        reading_date__date__lte=cutoff,
    ).select_related('tank', 'tank__house').order_by('reading_date', 'pk'))
    for item in tank_checks:
        details = (
            f"Checked by: {item.checked_by or '—'}; "
            f"Tank: {item.tank.name}; Level: {item.get_visual_level_display()}"
        )
        if item.notes:
            details += f"; Notes: {item.notes}"
        activities.append((
            timezone.localtime(item.reading_date).date().isoformat(),
            item.tank.house.name, 'Water tank measurement', 'Included', details, EURO(0),
        ))

    return sorted(activities, key=lambda row: (row[0], row[1], row[2]))


def _build_pdf(customer, villas, works, invoices, programs, payments, today):
    regular, bold = _font_names()
    buffer = BytesIO()
    doc = BaseDocTemplate(buffer, pagesize=A4, leftMargin=48, rightMargin=48,
                          topMargin=60, bottomMargin=54, title=f'Customer statement - {customer.name}')
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, leftPadding=0,
                  rightPadding=0, topPadding=0, bottomPadding=0)

    def page(canvas, document):
        canvas.saveState()
        canvas.setFillColor(NAVY)
        canvas.rect(0, A4[1] - 12, A4[0], 12, fill=1, stroke=0)
        canvas.setFont(bold, 8)
        canvas.drawString(48, 31, 'CUSTOMER WORK & FINANCIAL STATEMENT')
        canvas.setFont(regular, 8)
        canvas.drawRightString(A4[0] - 48, 31, f'Page {document.page}')
        canvas.restoreState()

    doc.addPageTemplates(PageTemplate(id='statement', frames=frame, onPage=page))
    title = ParagraphStyle('title', fontName=bold, fontSize=23, leading=30, textColor=NAVY, spaceAfter=12)
    h2 = ParagraphStyle('h2', fontName=bold, fontSize=13, leading=19, textColor=NAVY, spaceBefore=18, spaceAfter=10)
    body = ParagraphStyle('body', fontName=regular, fontSize=9, leading=15, textColor=NAVY, spaceAfter=9)
    small = ParagraphStyle('small', fontName=regular, fontSize=7.4, leading=11, textColor=NAVY)
    muted = ParagraphStyle('muted', fontName=regular, fontSize=8, leading=12, textColor=MUTED, spaceAfter=9)
    story = [Paragraph('YOUR PROPERTY, IN PERSPECTIVE', muted),
             Paragraph('Customer statement', title),
             Paragraph(escape(customer.name), ParagraphStyle('customer', parent=h2, fontSize=16, spaceBefore=0)),
             Paragraph(f'Prepared {today:%d %B %Y}  |  All amounts in EUR  |  Through {today:%d %B %Y}', muted)]

    work_total = sum((D(w.customer_charge) for w in works), Decimal('0'))
    additional_total = sum((D(w.additional_charges) for w in works), Decimal('0'))
    invoice_total = sum((D(i.amount) for i in invoices), Decimal('0'))
    program_total = sum((D(p.price) * _month_count(p, today) for p in programs), Decimal('0'))
    paid = sum((D(p.amount) for p in payments), Decimal('0'))
    charges = work_total + additional_total + invoice_total + program_total
    balance = charges - paid
    counts = len(works)
    story.append(Paragraph('AT A GLANCE', h2))
    cards = [[Paragraph('TOTAL CHARGES', muted), Paragraph('PAYMENTS RECEIVED', muted), Paragraph('OUTSTANDING / CREDIT', muted)],
             [Paragraph(EURO(charges), body), Paragraph(EURO(paid), body), Paragraph(EURO(abs(balance)), body)]]
    t = Table(cards, colWidths=[doc.width / 3] * 3)
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), LIGHT), ('BOX', (0, 0), (-1, -1), 0.4, colors.HexColor('#DDE8E0')),
                           ('TOPPADDING', (0, 0), (-1, -1), 12), ('BOTTOMPADDING', (0, 0), (-1, -1), 8)]))
    story.extend([t, Spacer(1, 10)])
    story.append(Paragraph(
        f'This statement covers <b>{len(villas)} villa(s)</b> and <b>{counts} recorded work entries</b>. '
        f'Work services contributed <b>{EURO(work_total)}</b>; additional charges <b>{EURO(additional_total)}</b>; villa-linked supplier invoices '
        f'contributed <b>{EURO(invoice_total)}</b>; and dated monthly villa programs '
        f'contributed <b>{EURO(program_total)}</b>. Payments received total <b>{EURO(paid)}</b>. '
        + (f'The remaining balance is <b>{EURO(balance)}</b>.' if balance >= 0 else f'The account has a credit of <b>{EURO(-balance)}</b>.'), body))

    dept_totals = defaultdict(Decimal)
    villa_totals = defaultdict(Decimal)
    for w in works:
        dept_totals[w.service.department.name if w.service.department_id else 'Unassigned'] += D(w.customer_charge) + D(w.additional_charges)
        villa_totals[w.house.name] += D(w.customer_charge) + D(w.additional_charges)
    for inv in invoices:
        dept_totals[inv.department.name if inv.department_id else 'Unassigned'] += D(inv.amount)
        villa_totals[inv.house.name] += D(inv.amount)
    for p in programs:
        val = D(p.price) * _month_count(p, today)
        if val:
            dept_totals['Villa programs (not departmental)'] += val
            villa_totals[p.house.name] += val

    story.extend([Paragraph('WHERE THE INVESTMENT WENT', h2),
                  Paragraph('Charges by department and program, combining work entries, villa-linked invoices, and monthly programs.', muted),
                  HorizontalBars(sorted(dept_totals.items(), key=lambda x: -x[1]), width=doc.width),
                  Paragraph('VILLA BREAKDOWN', h2),
                  HorizontalBars(sorted(villa_totals.items(), key=lambda x: -x[1]), width=doc.width)])

    def tabular(headers, rows, widths):
        table_data = [[Paragraph(str(h), ParagraphStyle('head', parent=small, fontName=bold, textColor=colors.white)) for h in headers]]
        for row in rows:
            table_data.append([Paragraph(escape(str(cell)).replace('\n', '<br/>'), small) for cell in row])
        if len(table_data) == 1:
            table_data.append([Paragraph('No records', small)] + [''] * (len(headers) - 1))
        tab = Table(table_data, colWidths=widths, repeatRows=1, hAlign='LEFT')
        tab.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), NAVY),
                                 ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
                                 ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                 ('LINEBELOW', (0, 0), (-1, 0), 0.5, GOLD),
                                 ('LEFTPADDING', (0, 0), (-1, -1), 7),
                                 ('RIGHTPADDING', (0, 0), (-1, -1), 7),
                                 ('TOPPADDING', (0, 0), (-1, -1), 7),
                                 ('BOTTOMPADDING', (0, 0), (-1, -1), 7)]))
        return tab

    story.append(Paragraph('DETAILED WORK STATEMENT', h2))
    story.append(Paragraph('Work rows use historical customer-charge snapshots; additional purchases appear immediately below their work entry.', muted))
    work_rows = [row for w in works for row in _work_rows(w)]
    story.append(tabular(['Date', 'Villa', 'Service', 'Hours', 'Work performed', 'Charge'],
                         work_rows, [64, 75, 88, 43, 120, 91]))

    story.append(Paragraph('VILLA PROGRAMS', h2))
    story.append(Paragraph('Monthly programs are charged in full for each overlapping calendar month; no proration. Programs without a start date are excluded.', muted))
    program_rows = [(p.house.name, p.get_program_type_display(),
                     str(p.start_date or 'Not set'), str(p.end_date or 'Ongoing'),
                     str(_month_count(p, today)), EURO(D(p.price) * _month_count(p, today))) for p in programs]
    story.append(tabular(['Villa', 'Program', 'From', 'To', 'Months', 'Charge'],
                         program_rows, [88, 99, 83, 83, 47, 81]))

    story.append(Paragraph('VILLA-LINKED SUPPLIER INVOICES', h2))
    story.append(Paragraph('These expenses are included in customer charges to match the current dashboard calculation. Confirm that all such invoices are reimbursable before sharing externally.', muted))
    invoice_rows = [(i.invoice_date.isoformat(), i.invoice_number, i.supplier.name,
                     i.house.name, i.department.name, EURO(i.amount)) for i in invoices]
    story.append(tabular(['Date', 'Invoice #', 'Supplier', 'Villa', 'Department', 'Amount'],
                         invoice_rows, [70, 83, 100, 78, 85, 65]))

    story.append(Paragraph('PAYMENT HISTORY', h2))
    pay_rows = [(p.payment_date.isoformat(), p.reference or '—', p.notes or '—', EURO(p.amount)) for p in payments]
    story.append(tabular(['Date', 'Reference', 'Notes', 'Amount'], pay_rows, [84, 112, 190, 95]))
    story.extend([Spacer(1, 18), Paragraph('NOTES ON THIS STATEMENT', h2),
                  Paragraph('Balances are calculated as recorded work charges + additional charges + villa-linked supplier invoices + dated monthly villa programs - customer payments. '
                            'Payments are account-level and are not assigned to individual work entries or invoices. '
                            'Future-dated entries are excluded. The attached invoices are supporting source documents, not proof of payment. '
                            'This is a management statement, not a tax invoice.', muted)])
    doc.build(story)
    return buffer.getvalue()



def _build_monthly_pdf(customer, villas, works, invoices, programs, payments, today,
               period_start=None, opening_balance=Decimal('0'), check_activities=None):
    """Monthly customer statement. Backward compatible with older overview exports."""
    regular, bold = _font_names()
    period_start = period_start or today.replace(day=1)
    period_label = period_start.strftime('%B %Y')
    buffer = BytesIO()
    doc = BaseDocTemplate(buffer, pagesize=A4, leftMargin=48, rightMargin=48,
                          topMargin=60, bottomMargin=54,
                          title=f'{period_label} statement - {customer.name}')
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

    def page(canvas, document):
        canvas.saveState()
        canvas.setFillColor(NAVY)
        canvas.rect(0, A4[1] - 12, A4[0], 12, fill=1, stroke=0)
        canvas.setFont(bold, 8)
        canvas.drawString(48, 31, f'MONTHLY CUSTOMER STATEMENT | {period_label}')
        canvas.setFont(regular, 8)
        canvas.drawRightString(A4[0] - 48, 31, f'Page {document.page}')
        canvas.restoreState()

    doc.addPageTemplates(PageTemplate(id='statement', frames=frame, onPage=page))
    title = ParagraphStyle('title', fontName=bold, fontSize=23, leading=30,
                           textColor=NAVY, spaceAfter=12)
    h2 = ParagraphStyle('h2', fontName=bold, fontSize=13, leading=19,
                        textColor=NAVY, spaceBefore=18, spaceAfter=10)
    body = ParagraphStyle('body', fontName=regular, fontSize=9, leading=15,
                          textColor=NAVY, spaceAfter=9)
    small = ParagraphStyle('small', fontName=regular, fontSize=7.4, leading=11,
                           textColor=NAVY)
    muted = ParagraphStyle('muted', fontName=regular, fontSize=8, leading=12,
                           textColor=MUTED, spaceAfter=9)
    story = [
        Paragraph('PAROS KATOIKIA | MONTHLY BILLING', muted),
        Paragraph('Customer statement', title),
        Paragraph(escape(customer.name), ParagraphStyle('customer', parent=h2,
                                                         fontSize=16, spaceBefore=0)),
        Paragraph(f'Billing period: {period_label} | Prepared {timezone.localdate():%d %B %Y}', muted),
    ]

    work_total = sum((D(w.customer_charge) for w in works), Decimal('0'))
    additional_total = sum((D(w.additional_charges) for w in works), Decimal('0'))
    invoice_total = sum((D(i.amount) for i in invoices), Decimal('0'))
    program_items = [(p, D(p.price)) for p in programs
                     if p.start_date and p.start_date <= today
                     and (p.end_date is None or p.end_date >= period_start)]
    program_total = sum((value for _, value in program_items), Decimal('0'))
    paid = sum((D(p.amount) for p in payments), Decimal('0'))
    # Supplier invoices are pass-through amounts: do not apply VAT again.
    taxable_charges = work_total + program_total
    net_charges, vat_charges, gross_taxable_charges = _vat_parts(taxable_charges)
    gross_charges = gross_taxable_charges + additional_total + invoice_total
    # Opening balance already includes historical VAT using the same convention.
    closing = opening_balance + gross_charges - paid

    def tabular(headers, rows, widths, total_row=False, highlighted_rows=None, footer_count=0):
        head_style = ParagraphStyle('head', parent=small, fontName=bold,
                                    textColor=colors.white)
        table_data = [[Paragraph(escape(str(h)), head_style) for h in headers]]
        for row in rows:
            table_data.append([Paragraph(escape(str(cell)).replace('\n', '<br/>'), small) for cell in row])
        if len(table_data) == 1:
            table_data.append([Paragraph('No records', small)] + [''] * (len(headers) - 1))
        tab = Table(table_data, colWidths=widths, repeatRows=1, hAlign='LEFT')
        tab.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LINEBELOW', (0, 0), (-1, 0), 0.5, GOLD),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ]))
        for index in (highlighted_rows or []):
            tab.setStyle(TableStyle([
                ('BACKGROUND', (0, index), (-1, index), colors.HexColor('#E8E8E8')),
            ]))
        if footer_count:
            first_footer = len(table_data) - footer_count
            last_footer = len(table_data) - 1
            tab.setStyle(TableStyle([
                ('BACKGROUND', (0, first_footer), (-1, last_footer), colors.HexColor('#EDEFEF')),
                ('LINEABOVE', (0, first_footer), (-1, first_footer), 1.6, NAVY),
                ('TOPPADDING', (0, first_footer), (-1, first_footer), 12),
                ('LINEABOVE', (0, last_footer), (-1, last_footer), 0.8, GREEN),
                ('BACKGROUND', (0, last_footer), (-1, last_footer), colors.HexColor('#DDE6E1')),
                ('TOPPADDING', (0, last_footer), (-1, last_footer), 10),
                ('BOTTOMPADDING', (0, last_footer), (-1, last_footer), 10),
            ]))
        return tab

    # Only show the villa chart for customers who actually own multiple villas.
    if len(villas) > 1:
        villa_totals = defaultdict(lambda: Decimal('0'))
        for w in works:
            villa_totals[w.house.name] += D(w.customer_charge) + D(w.additional_charges)
        for i in invoices:
            villa_totals[i.house.name] += D(i.amount)
        for p, value in program_items:
            villa_totals[p.house.name] += value
        story.extend([
            Paragraph('VILLA BREAKDOWN', h2),
            HorizontalBars(sorted(villa_totals.items(), key=lambda x: -x[1]),
                           width=doc.width),
        ])

    story.append(Paragraph('MONTHLY WORK & PROGRAM STATEMENT', h2))
    story.append(Paragraph(
        'Monthly villa programs appear first, followed by recorded work and villa checks. '
        'House inspections and water measurements are included in the subscription at no extra charge.', muted))
    rows = []
    show_villa = len(villas) > 1
    for p, value in sorted(program_items, key=lambda x: (x[0].house.name, str(x[0].program_type))):
        row = (period_label, p.house.name,
               f'MONTHLY FEE: {p.get_program_type_display()}', 'Monthly',
               'Recurring monthly fee', EURO(value))
        rows.append(row if show_villa else (row[0], *row[2:]))
    program_row_count = len(rows)
    activity_groups = [_work_rows(w) for w in works]
    activity_groups.extend([row] for row in (check_activities or []))
    # Sort parent entries, then append their purchase rows without re-sorting.
    for group in sorted(activity_groups, key=lambda g: (g[0][0], g[0][1], g[0][2])):
        for row in group:
            rows.append(row if show_villa else (row[0], *row[2:]))
    # Program rows use light grey; a ruled footer separates totals from entries.
    entry_total = program_total + work_total
    entry_net, entry_vat, entry_gross = _vat_parts(entry_total)
    if show_villa:
        rows.extend([
            ('SUBTOTAL', '', '', '', '', EURO(entry_net + additional_total)),
            (f'VAT {VAT_RATE:.0%}', '', '', '', '', EURO(entry_vat)),
            ('PREVIOUS AMOUNT', '', '', '', '', EURO(opening_balance)),
            ('PAYMENTS THIS MONTH (-)', '', '', '', '', EURO(-paid)),
            ('TOTAL', '', '', '', '', EURO(opening_balance + entry_gross + additional_total - paid)),
        ])
        story.append(tabular(['Period / Date', 'Villa', 'Service / Monthly Fee', 'Units',
                              'Work performed', 'Charge'],
                             rows, [76, 70, 100, 47, 113, 75], footer_count=5,
                             highlighted_rows=range(1, program_row_count + 1)))
    else:
        rows.extend([
            ('SUBTOTAL', '', '', '', EURO(entry_net + additional_total)),
            (f'VAT {VAT_RATE:.0%}', '', '', '', EURO(entry_vat)),
            ('PREVIOUS AMOUNT', '', '', '', EURO(opening_balance)),
            ('PAYMENTS THIS MONTH (-)', '', '', '', EURO(-paid)),
            ('TOTAL', '', '', '', EURO(opening_balance + entry_gross + additional_total - paid)),
        ])
        story.append(tabular(['Period / Date', 'Service / Monthly Fee', 'Units',
                              'Work performed', 'Charge'],
                             rows, [88, 126, 54, 130, 83], footer_count=5,
                             highlighted_rows=range(1, program_row_count + 1)))

    story.append(Paragraph('MONTHLY ACCOUNT SUMMARY', h2))
    cards = [
        [Paragraph('OPENING BALANCE', muted),
         Paragraph('MONTHLY CHARGES', muted)],
        [Paragraph(EURO(opening_balance), body),
         Paragraph(EURO(gross_charges), body)],
        [Paragraph('ADDITIONAL CHARGES (included above)', muted), Paragraph('', muted)],
        [Paragraph(EURO(additional_total), body), Paragraph('', body)],
        [Paragraph('SUPPLIER INVOICES TOTAL', muted),
         Paragraph('INVOICES THIS MONTH', muted)],
        [Paragraph(EURO(invoice_total), body),
         Paragraph(str(len(invoices)), body)],
        [Paragraph('PAYMENTS THIS MONTH', muted),
         Paragraph('CLOSING BALANCE / AMOUNT DUE' if closing >= 0
                   else 'CLOSING CREDIT BALANCE', muted)],
        [Paragraph(EURO(paid), body),
         Paragraph(EURO(abs(closing)), body)],
    ]
    t = Table(cards, colWidths=[doc.width / 2] * 2)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.4, colors.HexColor('#DDE8E0')),
        ('TOPPADDING', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.extend([t, Spacer(1, 12)])
    story.append(Paragraph(
        f'In {period_label}, villa programs contributed <b>{EURO(program_total)}</b>, '
        f'work services <b>{EURO(work_total)}</b>, additional charges <b>{EURO(additional_total)}</b>, and villa-linked supplier invoices '
        f'<b>{EURO(invoice_total)}</b> with no additional VAT. VAT on monthly fees and services is '
        f'<b>{EURO(vat_charges)}</b>. Payments recorded in the month were '
        f'<b>{EURO(paid)}</b>; the closing account balance is <b>{EURO(closing)}</b>' + (' (credit).' if closing < 0 else '.'), body))

    story.append(Spacer(1, 16))
    story.append(Paragraph('STATEMENT NOTES', h2))
    story.append(Paragraph(
        'Opening balance is the net balance of all recorded charges and payments '
        'before this billing month; it is not a separately posted opening-balance '
        'transaction. Payments are account-level and cannot be allocated to '
        'specific invoices or work entries. Programs are charged in full for '
        'each overlapping month, without proration. Programs without a start '
        'date are excluded. VAT applies to monthly fees and services only; '
        'supplier invoices and additional charges are included at their recorded amounts without additional VAT. '
        'This is a management statement, not a tax invoice.', muted))
    doc.build(story)
    return buffer.getvalue()


def _period_bounds(month):
    """Validate YYYY-MM and return inclusive start and exclusive next-month boundary."""
    if not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', str(month or '')):
        raise ValidationError('Month must use YYYY-MM, for example 2026-11.')
    start = date(int(month[:4]), int(month[5:]), 1)
    if start.month == 12:
        next_month = date(start.year + 1, 1, 1)
    else:
        next_month = date(start.year, start.month + 1, 1)
    return start, next_month


def _program_active(program, start, next_month):
    return (program.start_date is not None
            and program.start_date < next_month
            and (program.end_date is None or program.end_date >= start))


def export_customer_statement(customer, month=None):
    """Generate one monthly statement ZIP with the month's supporting invoices."""
    today = timezone.localdate()
    month = month or today.strftime('%Y-%m')
    start, next_month = _period_bounds(month)
    # Never include future-dated transactions in an already selected month.
    cutoff = min(today, next_month - timedelta(days=1))
    villas = list(House.objects.filter(customer=customer).order_by('name'))
    villa_ids = [v.pk for v in villas]

    works = list(WorkEntry.objects.filter(
        house_id__in=villa_ids, work_date__gte=start, work_date__lte=cutoff
    ).select_related('house', 'service__department').order_by('work_date', 'pk'))
    invoices = list(Invoice.objects.filter(
        house_id__in=villa_ids, invoice_date__gte=start, invoice_date__lte=cutoff
    ).select_related('house', 'department', 'supplier').order_by('invoice_date', 'pk'))
    programs = list(VillaProgram.objects.filter(
        house_id__in=villa_ids
    ).select_related('house').order_by('house__name', 'start_date', 'pk'))
    active_programs = [p for p in programs if _program_active(p, start, next_month)
                       and p.start_date <= cutoff]
    payments = list(CustomerPayment.objects.filter(
        customer=customer, payment_date__gte=start, payment_date__lte=cutoff
    ).order_by('payment_date', 'pk'))

    # Opening balance uses every historical charge/payment before this month.
    old_work = WorkEntry.objects.filter(
        house_id__in=villa_ids, work_date__lt=start
    ).values_list('customer_charge', flat=True)
    old_additional = WorkEntry.objects.filter(
        house_id__in=villa_ids, work_date__lt=start
    ).values_list('additional_charges', flat=True)
    old_invoices = Invoice.objects.filter(
        house_id__in=villa_ids, invoice_date__lt=start
    ).values_list('amount', flat=True)
    old_payments = CustomerPayment.objects.filter(
        customer=customer, payment_date__lt=start
    ).values_list('amount', flat=True)
    old_programs = Decimal('0')
    for program in programs:
        if program.start_date and program.start_date < start:
            old_programs += D(program.price) * _month_count(
                program, start - timedelta(days=1))
    historical_taxable_charges = (
        sum((D(v) for v in old_work), Decimal('0')) + old_programs
    )
    historical_invoice_total = sum((D(v) for v in old_invoices), Decimal('0'))
    opening_balance = (
        _vat_parts(historical_taxable_charges)[2]
        + historical_invoice_total
        + sum((D(v) for v in old_additional), Decimal('0'))
        - sum((D(v) for v in old_payments), Decimal('0'))
    )

    check_activities = _customer_check_activity(villa_ids, start, cutoff)
    pdf = _build_monthly_pdf(customer, villas, works, invoices, active_programs,
                     payments, cutoff, period_start=start,
                      opening_balance=opening_balance,
                      check_activities=check_activities)
    output = BytesIO()
    prefix = f'Customer_{customer.pk}_{_safe(customer.name)}_{month}'
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        archive.writestr(f'{prefix}/Customer_Statement_{month}.pdf', pdf)
        if not invoices:
            archive.writestr(f'{prefix}/Invoices/NO_INVOICES.txt',
                             'No villa-linked invoices for this billing month.\n')
        for invoice in invoices:
            if not invoice.attachment or not invoice.attachment.name:
                continue
            try:
                with invoice.attachment.open('rb') as source:
                    name = PurePosixPath(invoice.attachment.name.replace('\\', '/')).name
                    archive.writestr(
                        f'{prefix}/Invoices/{invoice.pk}_{_safe(name)}', source.read())
            except (OSError, ValueError, FileNotFoundError):
                archive.writestr(f'{prefix}/Invoices/MISSING_{invoice.pk}.txt',
                                 f'Attachment unavailable for invoice {invoice.invoice_number}.\n')
    response = HttpResponse(output.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = (
        f'attachment; filename="Customer_{customer.pk}_Statement_{month}.zip"')
    response['Cache-Control'] = 'private, no-store'
    return response
