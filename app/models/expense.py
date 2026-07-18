from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Expense(BaseModel):
    id: Optional[str] = None
    user_id: str
    category: str
    amount: float
    date: datetime = datetime.utcnow()
    description: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()