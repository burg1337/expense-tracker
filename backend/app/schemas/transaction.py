from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from app.models.category import TransactionType


class TransactionBase(BaseModel):
    category_id: int
    amount: float
    description: Optional[str] = None
    type: TransactionType
    date: date


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    category_id: Optional[int] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    type: Optional[TransactionType] = None
    date: Optional[date] = None


class TransactionResponse(TransactionBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
