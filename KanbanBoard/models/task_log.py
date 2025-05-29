from database import db
from datetime import datetime

class TaskLog(db.Model):
    __tablename__ = 'task_logs'
    
    LogID = db.Column(db.Integer, primary_key=True)
    TaskID = db.Column(db.Integer, db.ForeignKey('tasks.TaskID'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    Action = db.Column(db.String(50), nullable=False)
    Message = db.Column(db.Text, nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)