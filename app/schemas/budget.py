from pydantic import BaseModel
from typing import Optional

class BudgetCreate(BaseModel):
    category: str
    amount: float
    month: str  # Format: YYYY-MM

class BudgetResponse(BaseModel):
    id: str
    user_id: str
    category: str
    amount: float
    month: str

class BudgetUpdate(BaseModel):
    amount: Optional[float] = None