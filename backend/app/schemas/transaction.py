from pydantic import BaseModel
from datetime import date, datetime
from app.models.category import TransactionType


class TransactionBase(BaseModel):
    category_id: int
    amount: float
    description: str | None = None
    type: TransactionType
    date: date


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    category_id: int | None = None
    amount: float | None = None
    description: str | None = None
    type: TransactionType | None = None
    date: date | None = None


class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
