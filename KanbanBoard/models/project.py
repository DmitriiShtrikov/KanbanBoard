from database import db
from datetime import datetime

class Project(db.Model):
    __tablename__ = 'projects'
    
    ProjectID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.Text)
    OwnerID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    
    columns = db.relationship('Column', backref='project', lazy=True)
    members = db.relationship('ProjectMember', backref='project', lazy=True)