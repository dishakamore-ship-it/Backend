from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ExpenseCreate(BaseModel):
    category: str
    amount: float
    date: Optional[datetime] = None
    description: Optional[str] = None

class ExpenseResponse(BaseModel):
    id: str
    user_id: str
    category: str
    amount: float
    date: str
    description: Optional[str]

class ExpenseUpdate(BaseModel):
    category: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[datetime] = None
    description: Optional[str] = None