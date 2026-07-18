from fastapi import APIRouter, HTTPException, Depends, status
from app.config.database import Database
from app.schemas.income import IncomeCreate, IncomeResponse, IncomeUpdate
from app.models.income import Income
from app.utils.auth import get_current_user
from app.schemas.user import TokenData
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/incomes", tags=["incomes"])

@router.post("/", response_model=IncomeResponse)
async def create_income(
    income_data: IncomeCreate,
    current_user: TokenData = Depends(get_current_user)
):
    db = Database.get_db()
    
    income_id = str(uuid.uuid4())
    income = {
        "_id": income_id,
        "user_id": current_user.user_id,
        "source": income_data.source,
        "amount": income_data.amount,
        "date": income_data.date or datetime.utcnow(),
        "description": income_data.description,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.incomes.insert_one(income)
    
    return IncomeResponse(
        id=income_id,
        user_id=current_user.user_id,
        source=income_data.source,
        amount=income_data.amount,
        date=income["date"].isoformat(),
        description=income_data.description
    )

@router.get("/", response_model=list[IncomeResponse])
async def get_incomes(current_user: TokenData = Depends(get_current_user)):
    db = Database.get_db()
    
    incomes = await db.incomes.find({"user_id": current_user.user_id}).sort("date", -1).to_list(length=100)
    
    return [
        IncomeResponse(
            id=income["_id"],
            user_id=income["user_id"],
            source=income["source"],
            amount=income["amount"],
            date=income["date"].isoformat(),
            description=income.get("description")
        )
        for income in incomes
    ]

@router.put("/{income_id}", response_model=IncomeResponse)
async def update_income(
    income_id: str,
    income_data: IncomeUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    db = Database.get_db()
    
    # Find income
    income = await db.incomes.find_one({"_id": income_id, "user_id": current_user.user_id})
    if not income:
        raise HTTPException(status_code=404, detail="Income not found")
    
    # Update fields
    update_data = {}
    if income_data.source is not None:
        update_data["source"] = income_data.source
    if income_data.amount is not None:
        update_data["amount"] = income_data.amount
    if income_data.date is not None:
        update_data["date"] = income_data.date
    if income_data.description is not None:
        update_data["description"] = income_data.description
    
    update_data["updated_at"] = datetime.utcnow()
    
    if update_data:
        await db.incomes.update_one(
            {"_id": income_id},
            {"$set": update_data}
        )
    
    updated_income = await db.incomes.find_one({"_id": income_id})
    
    return IncomeResponse(
        id=updated_income["_id"],
        user_id=updated_income["user_id"],
        source=updated_income["source"],
        amount=updated_income["amount"],
        date=updated_income["date"].isoformat(),
        description=updated_income.get("description")
    )

@router.delete("/{income_id}")
async def delete_income(
    income_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    db = Database.get_db()
    
    result = await db.incomes.delete_one({"_id": income_id, "user_id": current_user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Income not found")
    
    return {"message": "Income deleted successfully"}