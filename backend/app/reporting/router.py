from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from io import BytesIO
from reportlab.pdfgen import canvas
from openpyxl import Workbook
from ..deps import get_db, get_current_user
from .. import models

router = APIRouter(prefix="/report", tags=["reporting"])

@router.get("/download/pdf")
def download_pdf(db: Session = Depends(get_db), user=Depends(get_current_user)):
    total_revenue = db.query(func.coalesce(func.sum(models.Transaction.revenue), 0)).scalar()
    num_orders = db.query(func.count(models.Transaction.id)).scalar()
    avg_order_value = (total_revenue / num_orders) if num_orders else 0

    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setTitle("Sales Report")
    p.setFont("Helvetica-Bold", 16)
    p.drawString(72, 800, "Sales Summary Report")
    p.setFont("Helvetica", 12)
    p.drawString(72, 770, f"Total Revenue: ${total_revenue:,.2f}")
    p.drawString(72, 750, f"Orders: {num_orders}")
    p.drawString(72, 730, f"Avg Order Value: ${avg_order_value:,.2f}")
    p.showPage()
    p.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=report.pdf"})

@router.get("/download/excel")
def download_excel(db: Session = Depends(get_db), user=Depends(get_current_user)):
    wb = Workbook()
    ws = wb.active
    ws.title = "Monthly Sales"
    ws.append(["Month", "Revenue"])
    month = func.strftime('%Y-%m', models.Transaction.order_date)
    rows = (
        db.query(month.label('month'), func.sum(models.Transaction.revenue).label('revenue'))
        .group_by(month)
        .order_by(month)
        .all()
    )
    for m, rev in rows:
        ws.append([m, float(rev or 0)])
    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)
    return StreamingResponse(stream, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=report.xlsx"})
