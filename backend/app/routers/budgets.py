from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import date
from app.core.database import get_db
from app.models.user import User
from app.models.budget import Budget
from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse
from app.utils.dependencies import get_current_user
from app.utils.cache import delete_cache

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new budget"""
    # Verify category belongs to user
    category = db.query(Category).filter(
        Category.id == budget_data.category_id,
        Category.user_id == current_user.id
    ).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # Validate dates
    if budget_data.start_date >= budget_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )

    new_budget = Budget(
        user_id=current_user.id,
        category_id=budget_data.category_id,
        amount=budget_data.amount,
        period=budget_data.period,
        start_date=budget_data.start_date,
        end_date=budget_data.end_date
    )

    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)

    # Invalidate cache
    delete_cache(f"budgets:{current_user.id}:*")
    delete_cache(f"analytics:{current_user.id}:*")

    return new_budget


@router.get("/", response_model=List[BudgetResponse])
def get_budgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all budgets for current user"""
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id).all()
    return budgets


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific budget"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

    return budget


@router.get("/{budget_id}/status")
def get_budget_status(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get budget status with spending information"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

    # Calculate total spent in this budget period
    total_spent = db.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == current_user.id,
        Transaction.category_id == budget.category_id,
        Transaction.date >= budget.start_date,
        Transaction.date <= budget.end_date,
        Transaction.type == "expense"
    ).scalar() or 0.0

    remaining = budget.amount - total_spent
    percentage_used = (total_spent / budget.amount * 100) if budget.amount > 0 else 0

    return {
        "budget_id": budget.id,
        "budget_amount": budget.amount,
        "spent": total_spent,
        "remaining": remaining,
        "percentage_used": round(percentage_used, 2),
        "period": budget.period,
        "start_date": budget.start_date,
        "end_date": budget.end_date,
        "is_exceeded": total_spent > budget.amount
    }


@router.put("/{budget_id}", response_model=BudgetResponse)
def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a budget"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

    # Verify category if provided
    if budget_data.category_id is not None:
        category = db.query(Category).filter(
            Category.id == budget_data.category_id,
            Category.user_id == current_user.id
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

    # Update fields
    if budget_data.category_id is not None:
        budget.category_id = budget_data.category_id
    if budget_data.amount is not None:
        budget.amount = budget_data.amount
    if budget_data.period is not None:
        budget.period = budget_data.period
    if budget_data.start_date is not None:
        budget.start_date = budget_data.start_date
    if budget_data.end_date is not None:
        budget.end_date = budget_data.end_date

    # Validate dates
    if budget.start_date >= budget.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )

    db.commit()
    db.refresh(budget)

    # Invalidate cache
    delete_cache(f"budgets:{current_user.id}:*")
    delete_cache(f"analytics:{current_user.id}:*")

    return budget


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a budget"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

    db.delete(budget)
    db.commit()

    # Invalidate cache
    delete_cache(f"budgets:{current_user.id}:*")
    delete_cache(f"analytics:{current_user.id}:*")

    return None
