from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from config.database import init_db, get_db
from .routers import (
    analytics, business as business_router, conversations,
    auth, clients, workflow, calendly, webhooks, integrations, root
)

app = FastAPI(title="SMS Automation Hub API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Include routers
app.include_router(root.router)
app.include_router(auth.router)
app.include_router(analytics.router)
app.include_router(business_router.router)
app.include_router(conversations.router)
app.include_router(workflow.router)
app.include_router(clients.router)
app.include_router(calendly.router)
app.include_router(webhooks.router)
app.include_router(integrations.router)

@app.get("/")
async def root():
    return {"message": "SMS Automation Hub API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
