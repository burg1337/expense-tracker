from pydantic import BaseModel
from app.models.category import TransactionType


class CategoryBase(BaseModel):
    name: str
    type: TransactionType


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = None
    type: TransactionType | None = None


class CategoryResponse(CategoryBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
