from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.models.category import Category, TransactionType
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from app.utils.dependencies import get_current_user
from app.utils.cache import delete_cache

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new transaction (expense or income)"""
    # Verify category belongs to user
    category = db.query(Category).filter(
        Category.id == transaction_data.category_id,
        Category.user_id == current_user.id
    ).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    new_transaction = Transaction(
        user_id=current_user.id,
        category_id=transaction_data.category_id,
        amount=transaction_data.amount,
        description=transaction_data.description,
        type=transaction_data.type,
        date=transaction_data.date
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    # Invalidate cache
    delete_cache(f"transactions:{current_user.id}:*")
    delete_cache(f"analytics:{current_user.id}:*")

    return new_transaction


@router.get("/", response_model=List[TransactionResponse])
def get_transactions(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    type: Optional[TransactionType] = Query(None, description="Filter by transaction type"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    start_date: Optional[date] = Query(None, description="Filter from this date"),
    end_date: Optional[date] = Query(None, description="Filter until this date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transactions with pagination and filters"""
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    # Apply filters
    if type:
        query = query.filter(Transaction.type == type)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    # Apply pagination and ordering
    transactions = query.order_by(Transaction.date.desc()).offset(skip).limit(limit).all()

    return transactions


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific transaction"""
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a transaction"""
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    # Verify category if provided
    if transaction_data.category_id is not None:
        category = db.query(Category).filter(
            Category.id == transaction_data.category_id,
            Category.user_id == current_user.id
        ).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

    # Update fields
    if transaction_data.category_id is not None:
        transaction.category_id = transaction_data.category_id
    if transaction_data.amount is not None:
        transaction.amount = transaction_data.amount
    if transaction_data.description is not None:
        transaction.description = transaction_data.description
    if transaction_data.type is not None:
        transaction.type = transaction_data.type
    if transaction_data.date is not None:
        transaction.date = transaction_data.date

    db.commit()
    db.refresh(transaction)

    # Invalidate cache
    delete_cache(f"transactions:{current_user.id}:*")
    delete_cache(f"analytics:{current_user.id}:*")

    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a transaction"""
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    db.delete(transaction)
    db.commit()

    # Invalidate cache
    delete_cache(f"transactions:{current_user.id}:*")
    delete_cache(f"analytics:{current_user.id}:*")

    return None
