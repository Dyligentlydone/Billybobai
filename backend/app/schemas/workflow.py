from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class TwilioConfig(BaseModel):
    businessId: str
    accountSid: str
    authToken: str
    phoneNumber: str
    messagingServiceSid: Optional[str]
    webhookUrl: str
    fallbackUrl: Optional[str]
    statusCallback: Optional[str]
    retryCount: int

class BrandToneConfig(BaseModel):
    voiceType: str
    wordsToAvoid: List[str]
    greetings: List[str]

class AITrainingConfig(BaseModel):
    openAIKey: str
    qaPairs: List[Dict[str, str]]
    faqDocuments: List[Dict[str, str]]
    chatHistory: List[Dict[str, str]]

class ContextConfig(BaseModel):
    memoryWindow: int
    knowledgeBase: List[Dict[str, str]]
    intentExamples: List[Dict[str, Any]]
    contextualTriggers: List[Dict[str, Any]]

class ResponseConfig(BaseModel):
    messageStructure: List[Dict[str, Any]]
    fallbackMessage: str
    templates: List[Dict[str, Any]]

class MonitoringConfig(BaseModel):
    alertThresholds: Dict[str, Any]
    slackNotifications: Dict[str, Any]

class CalendlyConfig(BaseModel):
    enabled: bool
    access_token: Optional[str]

class ZendeskConfig(BaseModel):
    enabled: bool
    email: str
    apiToken: str
    subdomain: str
    defaultPriority: str
    createTickets: bool
    updateExisting: bool

class WebhookIntegrationConfig(BaseModel):
    enabled: bool
    url: str
    method: str
    headers: Dict[str, str]
    events: List[str]

class SystemIntegrationConfig(BaseModel):
    zendesk: ZendeskConfig
    calendly: CalendlyConfig
    webhook: WebhookIntegrationConfig

class WorkflowConfig(BaseModel):
    twilio: TwilioConfig
    brandTone: BrandToneConfig
    aiTraining: AITrainingConfig
    context: ContextConfig
    response: ResponseConfig
    monitoring: MonitoringConfig
    systemIntegration: SystemIntegrationConfig
