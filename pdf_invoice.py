from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle


def generate_invoice_pdf(path, invoice_id, customer, items):
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    c.setFont('Helvetica-Bold', 16)
    c.drawString(30, height - 40, f'Invoice #{invoice_id}')
    c.setFont('Helvetica', 10)
    c.drawString(30, height - 60, f'Customer: {customer}')

    data = [['#', 'Name', 'Price', 'Qty', 'Total']]
    total = 0
    for i, it in enumerate(items, start=1):
        data.append([str(i), it['name'], f"{it['price']:.2f}", str(it['qty']), f"{it['total']:.2f}"])
        total += it['total']

    data.append(['', '', '', 'Grand Total', f"{total:.2f}"])

    table = Table(data, colWidths=[20*mm, 80*mm, 30*mm, 20*mm, 30*mm])
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ALIGN', (2,1), (-1,-2), 'RIGHT'),
        ('ALIGN', (-2, -1), (-1, -1), 'RIGHT'),
    ])
    table.setStyle(style)

    w, h = table.wrapOn(c, width - 60, height)
    table.drawOn(c, 30, height - 120 - h)

    c.showPage()
    c.save()
