from pydantic import BaseModel
from typing import Optional
from app.models.category import TransactionType


class CategoryBase(BaseModel):
    name: str
    type: TransactionType


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[TransactionType] = None


class CategoryResponse(CategoryBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
