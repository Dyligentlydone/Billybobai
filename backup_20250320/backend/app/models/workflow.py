from app.database import db
from sqlalchemy.dialects.postgresql import JSON

class Workflow(db.Model):
    __tablename__ = 'workflows'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='draft')  # draft, active, archived
    actions = db.Column(JSON, default={})
    conditions = db.Column(JSON, default={})
    client_id = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Workflow {self.name}>'
