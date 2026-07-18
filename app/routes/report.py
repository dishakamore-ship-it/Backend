from fastapi import APIRouter, Depends
from app.config.database import Database
from app.utils.auth import get_current_user
from app.schemas.user import TokenData
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/summary")
async def get_summary(current_user: TokenData = Depends(get_current_user)):
    db = Database.get_db()
    
    # Get current month
    now = datetime.utcnow()
    month_start = datetime(now.year, now.month, 1)
    next_month = datetime(now.year + (now.month // 12), (now.month % 12) + 1, 1)
    
    # Total income this month
    income_aggregate = await db.incomes.aggregate([
        {
            "$match": {
                "user_id": current_user.user_id,
                "date": {"$gte": month_start, "$lt": next_month}
            }
        },
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$amount"}
            }
        }
    ]).to_list(length=1)
    
    total_income = income_aggregate[0]["total"] if income_aggregate else 0
    
    # Total expenses this month
    expense_aggregate = await db.expenses.aggregate([
        {
            "$match": {
                "user_id": current_user.user_id,
                "date": {"$gte": month_start, "$lt": next_month}
            }
        },
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$amount"}
            }
        }
    ]).to_list(length=1)
    
    total_expenses = expense_aggregate[0]["total"] if expense_aggregate else 0
    
    # Expenses by category
    category_expenses = await db.expenses.aggregate([
        {
            "$match": {
                "user_id": current_user.user_id,
                "date": {"$gte": month_start, "$lt": next_month}
            }
        },
        {
            "$group": {
                "_id": "$category",
                "total": {"$sum": "$amount"}
            }
        },
        {"$sort": {"total": -1}}
    ]).to_list(length=100)
    
    # Get budgets
    budgets = await db.budgets.find({
        "user_id": current_user.user_id,
        "month": now.strftime("%Y-%m")
    }).to_list(length=100)
    
    budget_data = {}
    for budget in budgets:
        budget_data[budget["category"]] = budget["amount"]
    
    # Calculate budget status
    budget_status = []
    for expense in category_expenses:
        category = expense["_id"]
        budget_limit = budget_data.get(category, 0)
        spent = expense["total"]
        
        budget_status.append({
            "category": category,
            "budget": budget_limit,
            "spent": spent,
            "remaining": budget_limit - spent if budget_limit > 0 else 0,
            "percentage": (spent / budget_limit * 100) if budget_limit > 0 else 0
        })
    
    # Income breakdown by source
    income_by_source = await db.incomes.aggregate([
        {
            "$match": {
                "user_id": current_user.user_id,
                "date": {"$gte": month_start, "$lt": next_month}
            }
        },
        {
            "$group": {
                "_id": "$source",
                "total": {"$sum": "$amount"}
            }
        },
        {"$sort": {"total": -1}}
    ]).to_list(length=100)
    
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": total_income - total_expenses,
        "category_expenses": category_expenses,
        "budget_status": budget_status,
        "income_by_source": income_by_source,
        "month": now.strftime("%Y-%m"),
        "transaction_count": {
            "income": len(await db.incomes.find({"user_id": current_user.user_id, "date": {"$gte": month_start, "$lt": next_month}}).to_list(length=1000)),
            "expenses": len(await db.expenses.find({"user_id": current_user.user_id, "date": {"$gte": month_start, "$lt": next_month}}).to_list(length=1000))
        }
    }