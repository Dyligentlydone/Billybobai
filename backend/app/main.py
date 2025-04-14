from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from config.database import init_db, get_db
from .routers import analytics, business, conversations, messages, webhooks

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
app.include_router(analytics.router, prefix="/api", tags=["analytics"])
app.include_router(business.router, prefix="/api")
app.include_router(conversations.router, prefix="/api", tags=["conversations"])
app.include_router(messages.router, prefix="/api")
app.include_router(webhooks.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "SMS Automation Hub API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
