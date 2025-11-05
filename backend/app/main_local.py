from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Use local config and database for testing
from app.core.database_sqlite import engine, Base
from app.routers import auth, categories, transactions, budgets, analytics

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Expense Tracker API",
    description="A comprehensive personal finance management API with expense tracking, budgeting, and analytics",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Expense Tracker API (Local Testing Mode)",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "mode": "local"}
