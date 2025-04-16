from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from models.opt_out import OptOut
from models.sms_message import SMSMessage

class OptOutHandler:
    OPT_OUT_KEYWORDS = {'stop', 'unsubscribe', 'cancel', 'end', 'quit'}
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    def is_opt_out_message(self, message: str) -> bool:
        """Check if a message contains opt-out keywords"""
        return message.lower().strip() in self.OPT_OUT_KEYWORDS
    
    async def handle_opt_out(self, phone_number: str, business_id: int, reason: str = None) -> OptOut:
        """Record a new opt-out"""
        opt_out = OptOut(
            phone_number=phone_number,
            business_id=business_id,
            opted_out_at=datetime.utcnow(),
            reason=reason
        )
        
        self.db.add(opt_out)
        
        # Mark all pending messages as opted out
        await self.db.execute(
            """
            UPDATE sms_messages 
            SET is_opted_out = 1,
                status = 'cancelled'
            WHERE to_number = :phone
            AND business_id = :business_id
            AND status IN ('queued', 'scheduled')
            """,
            {'phone': phone_number, 'business_id': business_id}
        )
        
        await self.db.commit()
        return opt_out
    
    async def is_opted_out(self, phone_number: str, business_id: int) -> bool:
        """Check if a number is opted out for a business"""
        result = await self.db.execute(
            """
            SELECT 1 FROM opt_outs
            WHERE phone_number = :phone
            AND business_id = :business_id
            LIMIT 1
            """,
            {'phone': phone_number, 'business_id': business_id}
        )
        return bool(result.scalar())
    
    async def get_opt_out_stats(self, business_id: int):
        """Get opt-out statistics for a business"""
        result = await self.db.execute(
            """
            SELECT 
                COUNT(*) as total_opt_outs,
                COUNT(CASE WHEN opted_out_at >= datetime('now', '-30 days') THEN 1 END) as recent_opt_outs,
                COUNT(DISTINCT phone_number) as unique_numbers
            FROM opt_outs
            WHERE business_id = :business_id
            """,
            {'business_id': business_id}
        )
        return dict(result.fetchone())
