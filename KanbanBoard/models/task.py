from database import db
from datetime import datetime

class Task(db.Model):
    __tablename__ = 'tasks'
    
    TaskID = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.Text)
    ColumnID = db.Column(db.Integer, db.ForeignKey('columns.ColumnID'), nullable=False)
    CreatedBy = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    UpdatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    logs = db.relationship('TaskLog', backref='task', lazy=True)