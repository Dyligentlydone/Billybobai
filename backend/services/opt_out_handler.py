from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message
from sqlalchemy import update, select, func, case

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
        """Mark phone number as opted out in all messages"""
        now = datetime.utcnow()
        
        # Update all messages for this phone number and business
        stmt = (
            update(Message)
            .where(Message.phone_number == phone_number)
            .where(Message.workflow_id.in_(
                select(Message.workflow_id)
                .join(Message.workflow)
                .where(Message.workflow.has(business_id=business_id))
            ))
            .values(is_opted_out=True, opted_out_at=now)
        )
        
        await self.db.execute(stmt)
        
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
        """Remove opt-out marking from all messages for this number"""
        stmt = (
            update(Message)
            .where(Message.phone_number == phone_number)
            .where(Message.workflow_id.in_(
                select(Message.workflow_id)
                .join(Message.workflow)
                .where(Message.workflow.has(business_id=business_id))
            ))
            .values(is_opted_out=False, opted_out_at=None)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        
        # Return whether any records were updated
        return result.rowcount > 0
    
    async def is_opted_out(self, phone_number: str, business_id: int) -> bool:
        """Check if a number is opted out for a business"""
        stmt = (
            select(Message)
            .where(Message.phone_number == phone_number)
            .where(Message.workflow_id.in_(
                select(Message.workflow_id)
                .join(Message.workflow)
                .where(Message.workflow.has(business_id=business_id))
            ))
            .where(Message.is_opted_out == True)
            .limit(1)
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().first() is not None
    
    async def get_opt_out_stats(self, business_id: int):
        """Get opt-out statistics for a business"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Count of opted out messages
        stmt = (
            select(
                func.count().label('total_opt_outs'),
                func.count(
                    case(
                        (Message.opted_out_at >= thirty_days_ago, 1)
                    )
                ).label('recent_opt_outs'),
                func.count(func.distinct(Message.phone_number)).label('unique_numbers')
            )
            .where(Message.workflow_id.in_(
                select(Message.workflow_id)
                .join(Message.workflow)
                .where(Message.workflow.has(business_id=business_id))
            ))
            .where(Message.is_opted_out == True)
        )
        
        result = await self.db.execute(stmt)
        return dict(result.mappings().first())
