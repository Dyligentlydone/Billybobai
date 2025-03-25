from datetime import datetime
import uuid
from typing import Optional, List
from ..models.business import Business, BusinessConfig
from ..database import db

class BusinessService:
    def __init__(self):
        self.collection = db.businesses

    async def create_business(self, name: str, domain: str, contact_email: str, config: BusinessConfig) -> Business:
        """Create a new business."""
        business = Business(
            id=str(uuid.uuid4()),
            name=name,
            domain=domain,
            contact_email=contact_email,
            config=config
        )
        
        await self.collection.insert_one(business.dict())
        return business

    async def get_business(self, business_id: str) -> Optional[Business]:
        """Get business by ID."""
        data = await self.collection.find_one({"id": business_id})
        return Business(**data) if data else None

    async def get_business_by_domain(self, domain: str) -> Optional[Business]:
        """Get business by domain."""
        data = await self.collection.find_one({"domain": domain})
        return Business(**data) if data else None

    async def update_business_config(self, business_id: str, config: BusinessConfig) -> bool:
        """Update business configuration."""
        result = await self.collection.update_one(
            {"id": business_id},
            {
                "$set": {
                    "config": config.dict(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0

    async def list_businesses(self) -> List[Business]:
        """List all businesses."""
        cursor = self.collection.find({"active": True})
        businesses = []
        async for doc in cursor:
            businesses.append(Business(**doc))
        return businesses

    async def get_business_config(self, business_id: str) -> Optional[BusinessConfig]:
        """Get business configuration."""
        business = await self.get_business(business_id)
        return business.config if business else None

    async def deactivate_business(self, business_id: str) -> bool:
        """Deactivate a business."""
        result = await self.collection.update_one(
            {"id": business_id},
            {
                "$set": {
                    "active": False,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0

    def extract_business_id(self, email_address: str) -> Optional[str]:
        """Extract business ID from email address domain."""
        try:
            domain = email_address.split('@')[1]
            return domain
        except:
            return None
