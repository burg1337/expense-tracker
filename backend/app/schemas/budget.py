from pydantic import BaseModel
from datetime import date
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
    category_id: int | None = None
    amount: float | None = None
    period: BudgetPeriod | None = None
    start_date: date | None = None
    end_date: date | None = None


class BudgetResponse(BudgetBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
