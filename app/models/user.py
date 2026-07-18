from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: EmailStr
    password: str
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

class UserInDB(User):
    hashed_password: str