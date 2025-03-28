from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import analytics, business, messages, webhooks

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5176"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics.router)
app.include_router(business.router)
app.include_router(messages.router)
app.include_router(webhooks.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Twilio Automation Hub API"}
