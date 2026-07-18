from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Income(BaseModel):
    id: Optional[str] = None
    user_id: str
    source: str
    amount: float
    date: datetime = datetime.utcnow()
    description: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()