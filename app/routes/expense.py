from fastapi import APIRouter, HTTPException, Depends, status
from app.config.database import Database
from app.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.utils.auth import get_current_user
from app.schemas.user import TokenData
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/expenses", tags=["expenses"])

@router.post("/", response_model=ExpenseResponse)
async def create_expense(
    expense_data: ExpenseCreate,
    current_user: TokenData = Depends(get_current_user)
):
    db = Database.get_db()
    
    expense_id = str(uuid.uuid4())
    expense = {
        "_id": expense_id,
        "user_id": current_user.user_id,
        "category": expense_data.category,
        "amount": expense_data.amount,
        "date": expense_data.date or datetime.utcnow(),
        "description": expense_data.description,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.expenses.insert_one(expense)
    
    return ExpenseResponse(
        id=expense_id,
        user_id=current_user.user_id,
        category=expense_data.category,
        amount=expense_data.amount,
        date=expense["date"].isoformat(),
        description=expense_data.description
    )

@router.get("/", response_model=list[ExpenseResponse])
async def get_expenses(current_user: TokenData = Depends(get_current_user)):
    db = Database.get_db()
    
    expenses = await db.expenses.find({"user_id": current_user.user_id}).sort("date", -1).to_list(length=100)
    
    return [
        ExpenseResponse(
            id=expense["_id"],
            user_id=expense["user_id"],
            category=expense["category"],
            amount=expense["amount"],
            date=expense["date"].isoformat(),
            description=expense.get("description")
        )
        for expense in expenses
    ]

@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: str,
    expense_data: ExpenseUpdate,
    current_user: TokenData = Depends(get_current_user)
):
    db = Database.get_db()
    
    expense = await db.expenses.find_one({"_id": expense_id, "user_id": current_user.user_id})
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    update_data = {}
    if expense_data.category is not None:
        update_data["category"] = expense_data.category
    if expense_data.amount is not None:
        update_data["amount"] = expense_data.amount
    if expense_data.date is not None:
        update_data["date"] = expense_data.date
    if expense_data.description is not None:
        update_data["description"] = expense_data.description
    
    update_data["updated_at"] = datetime.utcnow()
    
    if update_data:
        await db.expenses.update_one(
            {"_id": expense_id},
            {"$set": update_data}
        )
    
    updated_expense = await db.expenses.find_one({"_id": expense_id})
    
    return ExpenseResponse(
        id=updated_expense["_id"],
        user_id=updated_expense["user_id"],
        category=updated_expense["category"],
        amount=updated_expense["amount"],
        date=updated_expense["date"].isoformat(),
        description=updated_expense.get("description")
    )

@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    db = Database.get_db()
    
    result = await db.expenses.delete_one({"_id": expense_id, "user_id": current_user.user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Expense not found")
    
    return {"message": "Expense deleted successfully"}