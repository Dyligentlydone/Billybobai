from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from config.database import init_db, get_db
from .routers import (
    analytics, business as business_router, conversations,
    auth, clients, workflow, calendly, webhooks, integrations, root,
    sms, messages  # Add the messages router
)
from .routes import calendly, calendly_debug, calendly_raw_debug

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
print("Business router included for /api/businesses")
app.include_router(conversations.router)
app.include_router(workflow.router)
app.include_router(clients.router)
app.include_router(calendly.router)
app.include_router(webhooks.router)
app.include_router(integrations.router)
app.include_router(sms.router)  # Add the new SMS router
print("SMS router included for /api/sms/webhook endpoints")
app.include_router(messages.router)  # Add the new messages router
print("Messages router included for /api/messages endpoints")
app.include_router(calendly_debug.router)
print("Calendly diagnostic router included for /calendly-debug endpoints")
app.include_router(calendly_raw_debug.router)
print("Raw Calendly diagnostic router included for /calendly-raw endpoints")

@app.get("/")
async def root():
    return {"message": "SMS Automation Hub API"}

@app.get("/routes")
def list_routes():
    route_list = []
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            route_list.append({
                "path": route.path,
                "methods": list(route.methods)
            })
    return route_list

@app.get("/health")
def health_check():
    return {"status": "healthy"}
