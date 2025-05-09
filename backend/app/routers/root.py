from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def root():
    return {"status": "ok", "message": "Welcome to the FastAPI backend!"}

@router.get("/health")
def health():
    return {"status": "healthy"}
