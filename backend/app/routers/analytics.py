from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import Optional
from datetime import date, datetime, timedelta
from app.core.database import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.models.category import Category, TransactionType
from app.utils.dependencies import get_current_user
from app.utils.cache import get_cache, set_cache

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
def get_financial_summary(
    start_date: Optional[date] = Query(None, description="Start date for summary"),
    end_date: Optional[date] = Query(None, description="End date for summary"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get financial summary with total income, expenses, and balance"""
    # Default to current month if no dates provided
    if not start_date or not end_date:
        today = datetime.now()
        start_date = date(today.year, today.month, 1)
        # Get last day of month
        if today.month == 12:
            end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)

    # Check cache
    cache_key = f"analytics:{current_user.id}:summary:{start_date}:{end_date}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    # Calculate total income
    total_income = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == TransactionType.INCOME,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).scalar() or 0.0

    # Calculate total expenses
    total_expenses = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == TransactionType.EXPENSE,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).scalar() or 0.0

    balance = total_income - total_expenses

    result = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "balance": round(balance, 2),
        "savings_rate": round((balance / total_income * 100) if total_income > 0 else 0, 2)
    }

    # Cache for 5 minutes
    set_cache(cache_key, result, expiry=300)

    return result


@router.get("/spending-by-category")
def get_spending_by_category(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get spending breakdown by category"""
    # Default to current month if no dates provided
    if not start_date or not end_date:
        today = datetime.now()
        start_date = date(today.year, today.month, 1)
        if today.month == 12:
            end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)

    # Check cache
    cache_key = f"analytics:{current_user.id}:spending_by_category:{start_date}:{end_date}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    # Query spending by category
    results = db.query(
        Category.name,
        Category.id,
        func.sum(Transaction.amount).label("total")
    ).join(
        Transaction, Transaction.category_id == Category.id
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == TransactionType.EXPENSE,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).group_by(
        Category.id, Category.name
    ).all()

    data = [
        {
            "category_id": r.id,
            "category_name": r.name,
            "total": round(r.total, 2)
        }
        for r in results
    ]

    result = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "data": data
    }

    # Cache for 5 minutes
    set_cache(cache_key, result, expiry=300)

    return result


@router.get("/income-by-category")
def get_income_by_category(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get income breakdown by category"""
    # Default to current month
    if not start_date or not end_date:
        today = datetime.now()
        start_date = date(today.year, today.month, 1)
        if today.month == 12:
            end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)

    # Check cache
    cache_key = f"analytics:{current_user.id}:income_by_category:{start_date}:{end_date}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    # Query income by category
    results = db.query(
        Category.name,
        Category.id,
        func.sum(Transaction.amount).label("total")
    ).join(
        Transaction, Transaction.category_id == Category.id
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == TransactionType.INCOME,
        Transaction.date >= start_date,
        Transaction.date <= end_date
    ).group_by(
        Category.id, Category.name
    ).all()

    data = [
        {
            "category_id": r.id,
            "category_name": r.name,
            "total": round(r.total, 2)
        }
        for r in results
    ]

    result = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "data": data
    }

    # Cache for 5 minutes
    set_cache(cache_key, result, expiry=300)

    return result


@router.get("/monthly-trend")
def get_monthly_trend(
    months: int = Query(6, ge=1, le=24, description="Number of months to include"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly income and expense trends"""
    # Check cache
    cache_key = f"analytics:{current_user.id}:monthly_trend:{months}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    # Query transactions grouped by month
    results = db.query(
        extract('year', Transaction.date).label('year'),
        extract('month', Transaction.date).label('month'),
        Transaction.type,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == current_user.id
    ).group_by(
        'year', 'month', Transaction.type
    ).order_by(
        'year', 'month'
    ).all()

    # Organize data by month
    monthly_data = {}
    for r in results:
        month_key = f"{int(r.year)}-{int(r.month):02d}"
        if month_key not in monthly_data:
            monthly_data[month_key] = {"income": 0.0, "expense": 0.0}

        if r.type == TransactionType.INCOME:
            monthly_data[month_key]["income"] = round(r.total, 2)
        else:
            monthly_data[month_key]["expense"] = round(r.total, 2)

    # Convert to list and limit to requested months
    trend_data = [
        {
            "month": month,
            "income": data["income"],
            "expense": data["expense"],
            "balance": round(data["income"] - data["expense"], 2)
        }
        for month, data in sorted(monthly_data.items(), reverse=True)[:months]
    ]

    result = {"data": list(reversed(trend_data))}

    # Cache for 10 minutes
    set_cache(cache_key, result, expiry=600)

    return result
