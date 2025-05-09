from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.business import Business
from typing import List

router = APIRouter(prefix="/api/businesses", tags=["businesses"])

@router.get("/", response_model=List[dict])
def get_businesses(db: Session = Depends(get_db)):
    businesses = db.query(Business).all()
    return [
        {
            "id": b.id,
            "name": b.name,
            "description": b.description
        } for b in businesses
    ]

@router.get("/{business_id}", response_model=dict)
def get_business(business_id: str, db: Session = Depends(get_db)):
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return {
        "id": business.id,
        "name": business.name,
        "description": business.description
    }
