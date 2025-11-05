from pydantic import BaseModel
from datetime import date
from typing import Optional
from app.models.budget import BudgetPeriod


class BudgetBase(BaseModel):
    category_id: int
    amount: float
    period: BudgetPeriod
    start_date: date
    end_date: date


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    category_id: Optional[int] = None
    amount: Optional[float] = None
    period: Optional[BudgetPeriod] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class BudgetResponse(BudgetBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
