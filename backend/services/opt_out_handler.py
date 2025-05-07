from datetime import datetime, timedelta
from sqlalchemy import select, update, case, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.message import Message
from app.models.sms_consent import SMSConsent
import random
import time

class OptOutHandler:
    OPT_OUT_KEYWORDS = {'stop', 'unsubscribe', 'cancel', 'end', 'quit'}
    OPT_IN_KEYWORDS = {'start', 'unstop', 'subscribe', 'begin', 'yes'}
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    def is_opt_out_message(self, message: str) -> bool:
        """Check if a message contains opt-out keywords"""
        return message.lower().strip() in self.OPT_OUT_KEYWORDS
    
    def is_opt_in_message(self, message: str) -> bool:
        """Check if a message contains opt-in keywords"""
        return message.lower().strip() in self.OPT_IN_KEYWORDS
    
    async def handle_opt_out(self, phone_number: str, business_id: int, reason: str = None):
        """Mark phone number as opted out using SMSConsent table"""
        now = datetime.utcnow()
        
        # Find or create consent record
        stmt = select(SMSConsent).where(
            SMSConsent.phone_number == phone_number,
            SMSConsent.business_id == str(business_id)  # Convert to string as business_id is stored as string in SMSConsent
        )
        result = await self.db.execute(stmt)
        consent = result.scalars().first()
        
        if consent:
            # Update existing record
            consent.status = 'DECLINED'
            consent.updated_at = now
        else:
            # Create new record with DECLINED status
            consent = SMSConsent(
                id=int(time.time() * 1000) + random.randint(1, 999),  # Generate ID as done in the model
                phone_number=phone_number,
                business_id=str(business_id),  # Convert to string
                status='DECLINED',
                created_at=now,
                updated_at=now
            )
            self.db.add(consent)
        
        # Also cancel any pending messages
        stmt = (
            update(Message)
            .where(Message.phone_number == phone_number)
            .where(Message.workflow_id.in_(
                select(Message.workflow_id)
                .join(Message.workflow)
                .where(Message.workflow.has(business_id=business_id))
            ))
            .where(Message.status.in_(['pending', 'queued', 'scheduled']))
            .values(status='cancelled')
        )
        
        await self.db.execute(stmt)
        await self.db.commit()
        return True
    
    async def handle_opt_in(self, phone_number: str, business_id: int) -> bool:
        """Mark phone number as opted in using SMSConsent table"""
        now = datetime.utcnow()
        
        # Find or create consent record
        stmt = select(SMSConsent).where(
            SMSConsent.phone_number == phone_number,
            SMSConsent.business_id == str(business_id)  # Convert to string
        )
        result = await self.db.execute(stmt)
        consent = result.scalars().first()
        
        if consent:
            # Update existing record
            consent.status = 'CONFIRMED'
            consent.updated_at = now
            await self.db.commit()
            return True
        else:
            # Create new record with CONFIRMED status
            consent = SMSConsent(
                id=int(time.time() * 1000) + random.randint(1, 999),  # Generate ID as done in the model
                phone_number=phone_number,
                business_id=str(business_id),  # Convert to string
                status='CONFIRMED',
                created_at=now,
                updated_at=now
            )
            self.db.add(consent)
            await self.db.commit()
            return True
    
    async def is_opted_out(self, phone_number: str, business_id: int) -> bool:
        """Check if a number is opted out for a business using SMSConsent table"""
        stmt = select(SMSConsent).where(
            SMSConsent.phone_number == phone_number,
            SMSConsent.business_id == str(business_id),  # Convert to string
            SMSConsent.status == 'DECLINED'
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().first() is not None
    
    async def get_opt_out_stats(self, business_id: int):
        """Get opt-out statistics for a business using SMSConsent table"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Count of opted out numbers
        stmt = select(
            func.count().label('total_opt_outs'),
            func.count(
                case(
                    (SMSConsent.updated_at >= thirty_days_ago, 1)
                )
            ).label('recent_opt_outs'),
            func.count(func.distinct(SMSConsent.phone_number)).label('unique_numbers')
        ).where(
            SMSConsent.business_id == str(business_id),  # Convert to string
            SMSConsent.status == 'DECLINED'
        )
        
        result = await self.db.execute(stmt)
        return dict(result.mappings().first())
