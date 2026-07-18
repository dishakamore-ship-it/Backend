from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Budget(BaseModel):
    id: Optional[str] = None
    user_id: str
    category: str
    amount: float
    month: str  # Format: YYYY-MM
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()