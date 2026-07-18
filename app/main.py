from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.database import Database
from app.routes import auth, income, expense, budget, report
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await Database.connect_db()
    yield
    # Shutdown
    await Database.close_db()

app = FastAPI(title="Personal Finance Tracker API", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(income.router)
app.include_router(expense.router)
app.include_router(budget.router)
app.include_router(report.router)

@app.get("/")
async def root():
    return {"message": "Personal Finance Tracker API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)