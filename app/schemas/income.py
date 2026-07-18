from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class IncomeCreate(BaseModel):
    source: str
    amount: float
    date: Optional[datetime] = None
    description: Optional[str] = None

class IncomeResponse(BaseModel):
    id: str
    user_id: str
    source: str
    amount: float
    date: str
    description: Optional[str]

class IncomeUpdate(BaseModel):
    source: Optional[str] = None
    amount: Optional[float] = None
    date: Optional[datetime] = None
    description: Optional[str] = None