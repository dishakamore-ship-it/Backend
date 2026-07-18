from fastapi import APIRouter, HTTPException, status
from datetime import timedelta
from app.config.database import Database
from app.config.security import get_password_hash, verify_password, create_access_token
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.models.user import User
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    db = Database.get_db()
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_data.password)
    
    user = {
        "_id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.users.insert_one(user)
    
    return UserResponse(
        id=user_id,
        username=user_data.username,
        email=user_data.email,
        created_at=datetime.utcnow().isoformat()
    )

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    db = Database.get_db()
    
    # Find user
    user = await db.users.find_one({"email": user_data.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user["_id"]},
        expires_delta=timedelta(minutes=30)
    )
    
    return Token(access_token=access_token, token_type="bearer")