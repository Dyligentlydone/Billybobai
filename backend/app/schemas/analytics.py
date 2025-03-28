from pydantic import BaseModel
from typing import Dict, Any, List, Optional

class MetricCategory(BaseModel):
    enabled: bool
    name: str
    description: str
    metrics: Dict[str, Any]
    charts: Optional[List[Dict[str, Any]]] = None

class SMSMetrics(BaseModel):
    delivery_metrics: MetricCategory
    engagement_metrics: Optional[MetricCategory]
    quality_compliance: MetricCategory
    cost_efficiency: MetricCategory
    performance_metrics: MetricCategory
    business_impact: MetricCategory
    ai_specific: MetricCategory
    security_fraud: MetricCategory

class EmailMetrics(BaseModel):
    pass  # To be implemented

class VoiceMetrics(BaseModel):
    pass  # To be implemented

class Overview(BaseModel):
    totalInteractions: int
    totalCost: float
    averageResponseTime: float
    successRate: float

class DateRange(BaseModel):
    start: str
    end: str

class AnalyticsData(BaseModel):
    sms: SMSMetrics
    email: Dict[str, Any]  # To be implemented
    voice: Dict[str, Any]  # To be implemented
    overview: Overview
    dateRange: DateRange
