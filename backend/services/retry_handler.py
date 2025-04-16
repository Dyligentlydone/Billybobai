import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import logging

class RetryHandler:
    # Retry configuration
    MAX_ATTEMPTS = 3
    INITIAL_DELAY = 5  # seconds
    MAX_DELAY = 30    # seconds
    BACKOFF_FACTOR = 2
    
    # Status that should trigger retries
    RETRYABLE_STATUSES = {
        'failed',           # Generic failure
        'undelivered',     # Message was not delivered
        'queued',          # Message stuck in queue
        'failed-pricing',  # Pricing error
        'failed-carrier',  # Carrier error
    }
    
    # Error codes that should not be retried
    NON_RETRYABLE_ERRORS = {
        '21610',  # Attempt to send to unsubscribed recipient
        '21611',  # Message body is required
        '21612',  # Invalid phone number
        '21408',  # Account suspended
        '21609',  # Message blocked
    }

    def __init__(self, twilio_client: Client, db_session):
        self.twilio_client = twilio_client
        self.db = db_session
        self.logger = logging.getLogger(__name__)

    async def should_retry(
        self,
        status: str,
        error_code: Optional[str],
        attempt: int
    ) -> bool:
        """Determine if a message should be retried"""
        if attempt >= self.MAX_ATTEMPTS:
            return False
            
        if error_code in self.NON_RETRYABLE_ERRORS:
            return False
            
        return status in self.RETRYABLE_STATUSES

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for next retry using exponential backoff"""
        delay = self.INITIAL_DELAY * (self.BACKOFF_FACTOR ** (attempt - 1))
        return min(delay, self.MAX_DELAY)

    async def update_message_status(
        self,
        message_id: int,
        status: str,
        error_code: Optional[str] = None,
        attempt: int = None
    ):
        """Update message status in database"""
        query = """
            UPDATE sms_messages
            SET status = :status,
                error_code = :error_code,
                retry_attempt = :attempt,
                updated_at = :updated_at
            WHERE id = :message_id
        """
        await self.db.execute(
            query,
            {
                'status': status,
                'error_code': error_code,
                'attempt': attempt,
                'updated_at': datetime.utcnow(),
                'message_id': message_id
            }
        )
        await self.db.commit()

    async def retry_send(
        self,
        message_id: int,
        to_number: str,
        from_number: str,
        body: str,
        attempt: int = 1,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Attempt to resend a failed message with retry logic
        Returns True if message was sent successfully
        """
        try:
            # Calculate delay based on attempt number
            delay = self.calculate_delay(attempt)
            await asyncio.sleep(delay)
            
            # Attempt to send message
            message = await self.twilio_client.messages.create(
                to=to_number,
                from_=from_number,
                body=body,
                status_callback=metadata.get('status_callback') if metadata else None
            )
            
            # Update message status
            await self.update_message_status(
                message_id=message_id,
                status='sent',
                attempt=attempt,
            )
            
            self.logger.info(f"Retry attempt {attempt} successful for message {message_id}")
            return True
            
        except TwilioRestException as e:
            error_code = str(e.code)
            status = 'failed'
            
            # Update message status
            await self.update_message_status(
                message_id=message_id,
                status=status,
                error_code=error_code,
                attempt=attempt
            )
            
            # Check if we should retry
            if await self.should_retry(status, error_code, attempt):
                self.logger.info(f"Scheduling retry attempt {attempt + 1} for message {message_id}")
                return await self.retry_send(
                    message_id=message_id,
                    to_number=to_number,
                    from_number=from_number,
                    body=body,
                    attempt=attempt + 1,
                    metadata=metadata
                )
            
            self.logger.error(f"Final retry attempt {attempt} failed for message {message_id}: {str(e)}")
            return False
            
        except Exception as e:
            self.logger.error(f"Unexpected error in retry attempt {attempt} for message {message_id}: {str(e)}")
            await self.update_message_status(
                message_id=message_id,
                status='failed',
                error_code='UNKNOWN_ERROR',
                attempt=attempt
            )
            return False

    async def process_failed_message(
        self,
        message_id: int,
        status: str,
        error_code: Optional[str] = None
    ):
        """Handle a failed message and initiate retry if appropriate"""
        # Get message details from database
        query = """
            SELECT id, to_number, from_number, body, retry_attempt, metadata
            FROM sms_messages
            WHERE id = :message_id
        """
        result = await self.db.execute(query, {'message_id': message_id})
        message = result.fetchone()
        
        if not message:
            self.logger.error(f"Message {message_id} not found in database")
            return
            
        current_attempt = message.retry_attempt or 0
        
        if await self.should_retry(status, error_code, current_attempt):
            self.logger.info(f"Initiating retry for message {message_id}")
            await self.retry_send(
                message_id=message_id,
                to_number=message.to_number,
                from_number=message.from_number,
                body=message.body,
                attempt=current_attempt + 1,
                metadata=message.metadata
            )
        else:
            self.logger.info(f"Message {message_id} will not be retried: status={status}, error_code={error_code}, attempts={current_attempt}")
            await self.update_message_status(
                message_id=message_id,
                status='failed',
                error_code=error_code,
                attempt=current_attempt
            )
