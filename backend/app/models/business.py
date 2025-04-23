from app.db import db

class Business(db.Model):
    __tablename__ = 'businesses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(1000))
    domain = db.Column(db.String(255), nullable=False, default="example.com") 
    workflows = db.relationship("Workflow", back_populates="business")
    config = db.relationship("BusinessConfig", back_populates="business", uselist=False)

class BusinessConfig(db.Model):
    __tablename__ = 'business_configs'

    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.Integer, db.ForeignKey('businesses.id'), nullable=False)
    business = db.relationship("Business", back_populates="config")
    
    # Brand voice settings
    tone = db.Column(db.String(50), default='professional')  # professional, casual, friendly, etc.
    language = db.Column(db.String(10), default='en')  # en, es, fr, etc.
    
    # AI configuration
    ai_settings = db.Column(db.JSON, default={})  # temperature, max_tokens, etc.
    custom_instructions = db.Column(db.String(2000))  # Additional AI instructions
    
    # Response templates
    greeting_template = db.Column(db.String(500))
    fallback_message = db.Column(db.String(500))
    
    # Business hours
    business_hours = db.Column(db.JSON, default={})  # Format: {"mon": {"start": "09:00", "end": "17:00"}, ...}
    timezone = db.Column(db.String(50), default='UTC')
    
    # Integration settings
    calendly_settings = db.Column(db.JSON, nullable=True)  # Calendly integration settings
    twilio_settings = db.Column(db.JSON, nullable=True)  # Twilio specific settings
