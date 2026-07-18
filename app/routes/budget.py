from fastapi import APIRouter, HTTPException, Depends, status
from app.config.database import Database
from app.schemas.budget import BudgetCreate, BudgetResponse, BudgetUpdate
from app.utils.auth import get_current_user
from app.schemas.user import TokenData
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/budgets", tags=["budgets"])

@router.post("/", response_model=BudgetResponse)
async def create_budget(
    budget_data: BudgetCreate,
    current_user: TokenData = Depends(get_current_user)
):
    db = Database.get_db()
    
    # Check if budget exists for this category and month
    existing = await db.budgets.find_one({
        "user_id": current_user.user_id,
        "category": budget_data.category,
        "month": budget_data.month
    })
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Budget already exists for this category and month"
        )
    
    budget_id = str(uuid.uuid4())
    budget = {
        "_id": budget_id,
        "user_id": current_user.user_id,
        "category": budget_data.category,
        "amount": budget_data.amount,
        "month": budget_data.month,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.budgets.insert_one(budget)
    
    return BudgetResponse(
        id=budget_id,
        user_id=current_user.user_id,
        category=budget_data.category,
        amount=budget_data.amount,
        month=budget_data.month
    )

@router.get("/", response_model=list[BudgetResponse])
async def get_budgets(current_user: TokenData = Depends(get_current_user)):
    db = Database.get_db()
    
    budgets = await db.budgets.find({"user_id": current_user.user_id}).to_list(length=100)
    
    return [
        BudgetResponse(
            id=budget["_id"],
            user_id=budget["user_id"],
            category=budget["category"],
            amount=budget["amount"],
            month=budget["month"]
        )
        for budget in budgets
    ]

@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: str,
    budget_data: BudgetUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    db = Database.get_db()
    
    budget = await db.budgets.find_one({"_id": budget_id, "user_id": current_user.user_id})
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    update_data = {}
    if budget_data.amount is not None:
        update_data["amount"] = budget_data.amount
    
    update_data["updated_at"] = datetime.utcnow()
    
    if update_data:
        await db.budgets.update_one(
            {"_id": budget_id},
            {"$set": update_data}
        )
    
    updated_budget = await db.budgets.find_one({"_id": budget_id})
    
    return BudgetResponse(
        id=updated_budget["_id"],
        user_id=updated_budget["user_id"],
        category=updated_budget["category"],
        amount=updated_budget["amount"],
        month=updated_budget["month"]
    )

@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    db = Database.get_db()
    
    result = await db.budgets.delete_one({"_id": budget_id, "user_id": current_user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return {"message": "Budget deleted successfully"}