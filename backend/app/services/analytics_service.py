from datetime import datetime, timedelta
from typing import Dict, Any, List

from sqlalchemy.orm import Session
from sqlalchemy import func, case

from ..models.message import Message, MessageStatus, MessageDirection, MessageChannel
from ..models.workflow import Workflow
from ..models.sms_consent import SMSConsent  # Opt-out information

DEFAULT_LOOKBACK_DAYS = 30


class AnalyticsService:
    """Centralised analytics calculations for SMS / Voice / Email.

    At the moment only SMS metrics are fully implemented; the other
    channels return empty shells so the API contract remains stable.
    """

    def __init__(self, db: Session):
        self.db = db

    # ---------------------------------------------------------------------
    # Public helpers
    # ---------------------------------------------------------------------
    def get_analytics(self, business_id: str, *, start_date: datetime | None = None,
                       end_date: datetime | None = None) -> Dict[str, Any]:
        start_date, end_date = self._coerce_daterange(start_date, end_date)

        sms_metrics = self._get_sms_metrics(business_id, start_date, end_date)
        # Stubs – future voice/email logic will mirror SMS calculations
        voice_metrics: Dict[str, Any] = {
            "totalCount": "0",
            "inboundCalls": 0,
            "outboundCalls": 0,
            "averageDuration": 0,
            "successRate": 0,
            "hourlyActivity": [],
        }
        email_metrics: Dict[str, Any] = {
            "totalCount": "0",
            "responseTime": "0s",
            "openRate": 0,
            "clickRate": 0,
            "bounceRate": 0,
            "hourlyActivity": [],
        }

        overview = self._build_overview(sms_metrics, voice_metrics, email_metrics)

        return {
            "sms": sms_metrics,
            "voice": voice_metrics,
            "email": email_metrics,
            "overview": overview,
            "dateRange": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _coerce_daterange(self, start: datetime | None, end: datetime | None):
        end = end or datetime.utcnow()
        start = start or (end - timedelta(days=DEFAULT_LOOKBACK_DAYS))
        return start, end

    def _get_sms_metrics(self, business_id: str, start: datetime, end: datetime) -> Dict[str, Any]:
        # Messages don't carry business_id directly, so join via Workflow
        q = (
            self.db.query(Message)
            .join(Workflow, Message.workflow_id == Workflow.id)
            .filter(
                Workflow.business_id == business_id,
                Message.channel == MessageChannel.SMS,
                Message.created_at >= start,
                Message.created_at <= end,
            )
        )
        messages: List[Message] = q.all()

        total_messages = len(messages)
        if total_messages == 0:
            return self._empty_sms_metrics()

        # Delivered / failed counts
        delivered_count = sum(1 for m in messages if m.status == MessageStatus.DELIVERED)
        failed_count = sum(1 for m in messages if m.status == MessageStatus.FAILED)
        delivery_rate = delivered_count / total_messages if total_messages else 0

        # Opt-out rate based on SMSConsent table if present
        opt_out_total = (
            self.db.query(SMSConsent).filter(
                SMSConsent.business_id == business_id,
                SMSConsent.opted_in.is_(False),
            ).count()
            if SMSConsent.__table__.exists(bind=self.db.get_bind()) else 0
        )
        unique_contacts = (
            self.db.query(Message.phone_number)
            .filter(Message.business_id == business_id)
            .distinct()
            .count()
        ) or 1
        opt_out_rate = opt_out_total / unique_contacts

        # Average response time – only look at messages that have response_time set
        response_times = [getattr(m, "response_time", None) for m in messages]
        response_times = [rt for rt in response_times if rt is not None]
        avg_response_time = (sum(response_times) / len(response_times)) if response_times else 0

        # Hourly activity – 0-indexed array length 24
        hourly_counts = [0] * 24
        for m in messages:
            if m.created_at:
                hourly_counts[m.created_at.hour] += 1
        hourly_activity = [{"hour": h, "count": c} for h, c in enumerate(hourly_counts)]

        # TODO: AI and Twilio costs once columns exist – default 0 for now.
        ai_cost_sum = sum(getattr(m, "ai_cost", 0) or 0 for m in messages)
        twilio_cost_sum = sum(getattr(m, "sms_cost", 0) or 0 for m in messages)

        # Return dict matching frontend SMSMetrics interface
        return {
            "totalCount": str(total_messages),
            "responseTime": f"{avg_response_time:.1f}s",
            "deliveryRate": delivery_rate,
            "optOutRate": opt_out_rate,
            "aiCost": ai_cost_sum,
            "serviceCost": twilio_cost_sum,
            "qualityMetrics": [],  # placeholder until we compute
            "responseTypes": [],  # placeholder – requires NLP tagging
            "dailyCosts": [],  # can be derived later
            "hourlyActivity": hourly_activity,
            "conversations": [],  # conversation aggregation TBD
        }

    def _build_overview(self, sms: Dict[str, Any], voice: Dict[str, Any], email: Dict[str, Any]):
        total_interactions = (
            int(sms["totalCount"]) + int(voice["totalCount"]) + int(email["totalCount"])
        )
        total_cost = sms["aiCost"] + sms["serviceCost"]  # extend for voice/email later
        # Convert responseTime strings like "1.2s" to float seconds
        def _parse_seconds(s: str) -> float:
            try:
                return float(s.replace("s", ""))
            except Exception:
                return 0.0

        avg_resp = _parse_seconds(sms["responseTime"])
        return {
            "totalInteractions": str(total_interactions),
            "totalCost": total_cost,
            "averageResponseTime": f"{avg_resp:.1f}s",
            "successRate": sms["deliveryRate"] if total_interactions else 0,
        }

    @staticmethod
    def _empty_sms_metrics():
        return {
            "totalCount": "0",
            "responseTime": "0s",
            "deliveryRate": 0,
            "optOutRate": 0,
            "aiCost": 0,
            "serviceCost": 0,
            "qualityMetrics": [],
            "responseTypes": [],
            "dailyCosts": [],
            "hourlyActivity": [],
            "conversations": [],
        }
