from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    UserID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(50), unique=True, nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(255), nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    
    projects = db.relationship('Project', backref='owner', lazy=True)
    
    def set_password(self, password):
        self.PasswordHash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.PasswordHash, password)