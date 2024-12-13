import uuid
from app import db

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    images = db.relationship('Image', backref='document', lazy='dynamic', cascade='all, delete-orphan',order_by='Image.file_number')
    
    def __repr__(self):
        return f'<Document {self.name}>'

    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        super().__init__(**kwargs)
        
