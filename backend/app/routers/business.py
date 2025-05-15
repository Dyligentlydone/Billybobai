from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.business import Business
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/api/businesses", tags=["businesses"])

class BusinessCreate(BaseModel):
    id: str
    name: str
    description: str = None
    domain: str = None

class BusinessOut(BaseModel):
    id: str
    name: str
    description: str = None
    domain: str = None

@router.get("/", response_model=List[BusinessOut])
@router.get("", response_model=List[BusinessOut])
def get_businesses(db: Session = Depends(get_db)):
    businesses = db.query(Business).all()
    return [
        BusinessOut(
            id=b.id,
            name=b.name,
            description=b.description,
            domain=getattr(b, "domain", None)
        ) for b in businesses
    ]

@router.post("/", response_model=BusinessOut, status_code=201)
@router.post("", response_model=BusinessOut, status_code=201)
def create_business(business: BusinessCreate, db: Session = Depends(get_db)):
    # Check if business already exists
    existing = db.query(Business).filter(Business.id == business.id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Business with this ID already exists")
    new_business = Business(
        id=business.id,
        name=business.name,
        description=business.description or f"Business {business.id}",
        domain=business.domain or f"business-{business.id}.com"
    )
    db.add(new_business)
    try:
        db.commit()
        db.refresh(new_business)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating business: {str(e)}")
    return BusinessOut(
        id=new_business.id,
        name=new_business.name,
        description=new_business.description,
        domain=getattr(new_business, "domain", None)
    )

@router.get("/{business_id}", response_model=BusinessOut)
def get_business(business_id: str, db: Session = Depends(get_db)):
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return BusinessOut(
        id=business.id,
        name=business.name,
        description=business.description,
        domain=getattr(business, "domain", None)
    )
