import io
import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def export_records_to_csv(records_qs):
    """
    Exports filtered SaleRecord queryset to an in-memory CSV string.
    """
    import csv
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Order ID', 'Order Date', 'Product Name', 'Category', 'Region',
        'Quantity', 'Revenue ($)', 'Cost ($)', 'Profit ($)', 'Margin (%)', 'Customer'
    ])
    for r in records_qs:
        writer.writerow([
            r.order_id or '',
            r.order_date.isoformat() if r.order_date else '',
            r.product_name or '',
            r.category or '',
            r.region or '',
            r.quantity,
            float(r.revenue),
            float(r.cost),
            float(r.profit),
            float(r.profit_margin),
            r.customer_name or ''
        ])
    return output.getvalue().encode('utf-8')

def export_executive_excel(dataset, metrics, records_qs):
    """
    Generates a professionally styled multi-sheet Excel workbook.
    """
    wb = Workbook()
    
    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    title_font = Font(name="Segoe UI", size=16, bold=True, color="0F172A")
    subtitle_font = Font(name="Segoe UI", size=10, italic=True, color="64748B")
    metric_title_font = Font(name="Segoe UI", size=10, bold=True, color="475569")
    metric_val_font = Font(name="Segoe UI", size=14, bold=True, color="0284C7")
    thin_border = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )

    # Sheet 1: Executive KPI Summary
    ws_kpi = wb.active
    ws_kpi.title = "Executive Summary"
    ws_kpi.views.sheetView[0].showGridLines = True

    ws_kpi.merge_cells("A1:E1")
    ws_kpi["A1"] = f"Executive Performance Summary - {dataset.name}"
    ws_kpi["A1"].font = title_font
    
    ws_kpi.merge_cells("A2:E2")
    ws_kpi["A2"] = f"Generated on {datetime.datetime.now().strftime('%b %d, %Y %I:%M %p')} | Total Records: {metrics['summary_count']}"
    ws_kpi["A2"].font = subtitle_font

    kpis = metrics.get('kpis', {})
    kpi_items = [
        ("Total Revenue", f"${kpis.get('total_revenue', 0):,.2f}"),
        ("Total Net Profit", f"${kpis.get('total_profit', 0):,.2f}"),
        ("Overall Profit Margin", f"{kpis.get('profit_margin', 0):.2f}%"),
        ("Total Completed Orders", f"{kpis.get('total_orders', 0):,}"),
        ("Total Units Sold", f"{kpis.get('total_units', 0):,}"),
        ("Average Order Value (AOV)", f"${kpis.get('avg_order_value', 0):,.2f}"),
        ("Month-over-Month Growth", f"{kpis.get('mom_growth', 0):+.2f}%")
    ]

    ws_kpi.cell(row=4, column=1, value="Core Business Metric").font = header_font
    ws_kpi.cell(row=4, column=1).fill = header_fill
    ws_kpi.cell(row=4, column=2, value="Current Value").font = header_font
    ws_kpi.cell(row=4, column=2).fill = header_fill

    for r_idx, (k, v) in enumerate(kpi_items, start=5):
        cell_k = ws_kpi.cell(row=r_idx, column=1, value=k)
        cell_k.font = metric_title_font
        cell_k.border = thin_border
        cell_v = ws_kpi.cell(row=r_idx, column=2, value=v)
        cell_v.font = metric_val_font
        cell_v.border = thin_border

    # Sheet 2: Category Breakdown
    ws_cat = wb.create_sheet(title="Category Performance")
    ws_cat.views.sheetView[0].showGridLines = True
    cat_headers = ["Category", "Total Revenue ($)", "Total Profit ($)", "Profit Margin (%)", "Revenue Share (%)"]
    for c_idx, h in enumerate(cat_headers, 1):
        c = ws_cat.cell(row=1, column=c_idx, value=h)
        c.font = header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center")

    cats = metrics.get('category_performance', {})
    labels = cats.get('labels', [])
    revs = cats.get('revenue', [])
    profs = cats.get('profit', [])
    margins = cats.get('margin', [])
    shares = cats.get('shares', [])

    for r_idx, label in enumerate(labels, start=2):
        ws_cat.cell(row=r_idx, column=1, value=label).border = thin_border
        ws_cat.cell(row=r_idx, column=2, value=revs[r_idx-2]).border = thin_border
        ws_cat.cell(row=r_idx, column=3, value=profs[r_idx-2]).border = thin_border
        ws_cat.cell(row=r_idx, column=4, value=f"{margins[r_idx-2]}%").border = thin_border
        ws_cat.cell(row=r_idx, column=5, value=f"{shares[r_idx-2]}%").border = thin_border

    # Sheet 3: Regional Breakdown
    ws_reg = wb.create_sheet(title="Regional Performance")
    ws_reg.views.sheetView[0].showGridLines = True
    reg_headers = ["Region", "Total Revenue ($)", "Total Profit ($)", "Total Orders"]
    for c_idx, h in enumerate(reg_headers, 1):
        c = ws_reg.cell(row=1, column=c_idx, value=h)
        c.font = header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center")

    regs = metrics.get('region_performance', {})
    reg_labels = regs.get('labels', [])
    reg_revs = regs.get('revenue', [])
    reg_profs = regs.get('profit', [])
    reg_orders = regs.get('orders', [])

    for r_idx, label in enumerate(reg_labels, start=2):
        ws_reg.cell(row=r_idx, column=1, value=label).border = thin_border
        ws_reg.cell(row=r_idx, column=2, value=reg_revs[r_idx-2]).border = thin_border
        ws_reg.cell(row=r_idx, column=3, value=reg_profs[r_idx-2]).border = thin_border
        ws_reg.cell(row=r_idx, column=4, value=reg_orders[r_idx-2]).border = thin_border

    # Sheet 4: Top 20 Products
    ws_prod = wb.create_sheet(title="Top Products")
    ws_prod.views.sheetView[0].showGridLines = True
    prod_headers = ["Product Name", "Category", "Revenue ($)", "Profit ($)", "Units Sold", "Margin (%)"]
    for c_idx, h in enumerate(prod_headers, 1):
        c = ws_prod.cell(row=1, column=c_idx, value=h)
        c.font = header_font
        c.fill = header_fill
        c.alignment = Alignment(horizontal="center")

    for r_idx, p in enumerate(metrics.get('top_products', []), start=2):
        ws_prod.cell(row=r_idx, column=1, value=p['name']).border = thin_border
        ws_prod.cell(row=r_idx, column=2, value=p['category']).border = thin_border
        ws_prod.cell(row=r_idx, column=3, value=p['revenue']).border = thin_border
        ws_prod.cell(row=r_idx, column=4, value=p['profit']).border = thin_border
        ws_prod.cell(row=r_idx, column=5, value=p['units']).border = thin_border
        ws_prod.cell(row=r_idx, column=6, value=f"{p['margin']}%").border = thin_border

    # Auto-adjust column widths for all sheets
    for ws in wb.worksheets:
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 14)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()

def export_executive_pdf(dataset, metrics, insights):
    """
    Generates a beautifully structured Executive Brief PDF Report using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B')
    )
    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # Title & Subtitle
    story.append(Paragraph("SaaS Business Analytics Executive Brief", title_style))
    story.append(Paragraph(
        f"Dataset: <b>{dataset.name}</b> &nbsp;|&nbsp; Generated on: {datetime.datetime.now().strftime('%B %d, %Y')} &nbsp;|&nbsp; Business Health: <b>{insights.get('overall_health', 'Healthy')}</b>",
        subtitle_style
    ))
    story.append(Spacer(1, 14))

    # Executive Summary Paragraph
    story.append(Paragraph("Executive Narrative & Performance Overview", h2_style))
    exec_text = insights.get('executive_summary', 'Performance data analyzed.')
    story.append(Paragraph(exec_text, body_style))
    story.append(Spacer(1, 14))

    # Key Performance Indicators Table
    story.append(Paragraph("Key Performance Metrics", h2_style))
    kpis = metrics.get('kpis', {})
    kpi_data = [
        [
            Paragraph("<b>Total Revenue</b>", body_style), f"${kpis.get('total_revenue', 0):,.2f}",
            Paragraph("<b>Total Net Profit</b>", body_style), f"${kpis.get('total_profit', 0):,.2f}"
        ],
        [
            Paragraph("<b>Profit Margin</b>", body_style), f"{kpis.get('profit_margin', 0):.2f}%",
            Paragraph("<b>Total Orders</b>", body_style), f"{kpis.get('total_orders', 0):,}"
        ],
        [
            Paragraph("<b>Total Units Sold</b>", body_style), f"{kpis.get('total_units', 0):,}",
            Paragraph("<b>Avg Order Value (AOV)</b>", body_style), f"${kpis.get('avg_order_value', 0):,.2f}"
        ]
    ]
    t_kpi = Table(kpi_data, colWidths=[130, 130, 140, 130])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1E293B')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 7),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 14))

    # Category Breakdown Table
    story.append(Paragraph("Category Performance Breakdown", h2_style))
    cat_rows = [["Category", "Revenue", "Net Profit", "Margin", "Revenue Share"]]
    cats = metrics.get('category_performance', {})
    for i, c_name in enumerate(cats.get('labels', [])[:6]):
        cat_rows.append([
            c_name,
            f"${cats['revenue'][i]:,.2f}",
            f"${cats['profit'][i]:,.2f}",
            f"{cats['margin'][i]:.1f}%",
            f"{cats['shares'][i]:.1f}%"
        ])
    t_cat = Table(cat_rows, colWidths=[150, 100, 100, 90, 90])
    t_cat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F1F5F9')]),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
    ]))
    story.append(t_cat)
    story.append(Spacer(1, 14))

    # Recommendations & Strategic Actions
    recs = insights.get('recommendations', [])
    if recs:
        story.append(Paragraph("Strategic Business Recommendations", h2_style))
        for r in recs:
            rec_line = f"• <b>[{r.get('priority', 'Normal')}] {r.get('category', 'Strategy')}:</b> {r.get('text', '')}"
            story.append(Paragraph(rec_line, body_style))
            story.append(Spacer(1, 4))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

