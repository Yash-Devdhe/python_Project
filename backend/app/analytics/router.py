from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..deps import get_db, get_current_user
from .. import models

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/kpis")
def kpis(db: Session = Depends(get_db), user=Depends(get_current_user)):
    total_revenue = db.query(func.coalesce(func.sum(models.Transaction.revenue), 0)).scalar()
    num_orders = db.query(func.count(models.Transaction.id)).scalar()
    avg_order_value = (total_revenue / num_orders) if num_orders else 0
    return {"total_revenue": total_revenue, "num_orders": num_orders, "avg_order_value": avg_order_value}

@router.get("/sales/monthly")
def sales_monthly(db: Session = Depends(get_db), user=Depends(get_current_user)):
    month = func.strftime('%Y-%m', models.Transaction.order_date)
    rows = (
        db.query(month.label('month'), func.sum(models.Transaction.revenue).label('revenue'))
        .group_by(month)
        .order_by(month)
        .all()
    )
    return [{"month": r[0], "revenue": float(r[1] or 0)} for r in rows]

@router.get("/products/top")
def top_products(limit: int = 10, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = (
        db.query(models.Product.name, func.sum(models.Transaction.revenue).label('revenue'))
        .join(models.Transaction, models.Transaction.product_id == models.Product.id)
        .group_by(models.Product.id)
        .order_by(func.sum(models.Transaction.revenue).desc())
        .limit(limit)
        .all()
    )
    return [{"product": r[0], "revenue": float(r[1] or 0)} for r in rows]

@router.get("/regions")
def regions(limit: int = 10, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = (
        db.query(models.Customer.region, func.sum(models.Transaction.revenue).label('revenue'))
        .join(models.Transaction, models.Transaction.customer_id == models.Customer.id)
        .group_by(models.Customer.region)
        .order_by(func.sum(models.Transaction.revenue).desc())
        .limit(limit)
        .all()
    )
    return [{"region": r[0] or "Unknown", "revenue": float(r[1] or 0)} for r in rows]
