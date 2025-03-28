from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import analytics, business, conversations, messages, webhooks

app = FastAPI(title="SMS Automation Hub API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5176"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics.router, tags=["analytics"])
app.include_router(business.router)
app.include_router(conversations.router, tags=["conversations"])
app.include_router(messages.router)
app.include_router(webhooks.router)

@app.get("/")
async def root():
    return {"message": "SMS Automation Hub API"}
