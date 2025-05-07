#!/usr/bin/env python3
"""
Migration script to sync data from Message.is_opted_out to SMSConsent table.
This ensures a smooth transition to using the SMSConsent table for opt-out status tracking.
"""

import sys
import os
import logging
from datetime import datetime

# Add the project root to the Python path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    # Import necessary models
    from app.db import db
    from app.models.message import Message
    from app.models.workflow import Workflow
    from app.models.sms_consent import SMSConsent
    
    logger.info("Starting migration to sync opt-out data")
    
    # Find all distinct phone numbers with opt-out status in the messages table
    opted_out_records = db.session.query(
        Message.phone_number, 
        Message.workflow_id
    ).filter(
        Message.is_opted_out == True
    ).distinct().all()
    
    logger.info(f"Found {len(opted_out_records)} opted-out records to migrate")
    
    # Counters for reporting
    records_processed = 0
    records_created = 0
    records_updated = 0
    records_skipped = 0
    
    # For each opted-out phone number, create or update SMSConsent record
    for phone_number, workflow_id in opted_out_records:
        try:
            # Find workflow's business ID
            workflow = Workflow.query.get(workflow_id)
            if not workflow:
                logger.warning(f"Skipping record - could not find workflow with ID {workflow_id}")
                records_skipped += 1
                continue
                
            business_id = workflow.business_id
            
            # Find or create consent record
            consent = SMSConsent.query.filter_by(
                phone_number=phone_number,
                business_id=str(business_id)
            ).first()
            
            if consent:
                # Update status if not already declined
                if consent.status != 'DECLINED':
                    consent.status = 'DECLINED'
                    consent.updated_at = datetime.utcnow()
                    records_updated += 1
                    logger.info(f"Updated consent record for {phone_number} with business {business_id}")
                else:
                    records_skipped += 1
                    logger.info(f"Skipped - already declined: {phone_number} with business {business_id}")
            else:
                # Create new record with DECLINED status
                import time
                import random
                consent = SMSConsent(
                    id=int(time.time() * 1000) + random.randint(1, 999),
                    phone_number=phone_number,
                    business_id=str(business_id),
                    status='DECLINED',
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(consent)
                records_created += 1
                logger.info(f"Created new consent record for {phone_number} with business {business_id}")
                
            records_processed += 1
            
            # Commit in batches to avoid transaction issues
            if records_processed % 10 == 0:
                db.session.commit()
                logger.info(f"Committed batch - processed {records_processed} records so far")
                
        except Exception as e:
            logger.error(f"Error processing record for {phone_number}: {str(e)}")
            records_skipped += 1
            # Continue with next record even if this one fails
            continue
    
    # Final commit for any remaining records
    db.session.commit()
    
    logger.info("Migration completed successfully!")
    logger.info(f"Records processed: {records_processed}")
    logger.info(f"Records created: {records_created}")
    logger.info(f"Records updated: {records_updated}")
    logger.info(f"Records skipped: {records_skipped}")
    
except Exception as e:
    logger.error(f"Migration failed: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)
