from database import db

class Column(db.Model):
    __tablename__ = 'columns'
    
    ColumnID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50), nullable=False)
    OrderIndex = db.Column(db.Integer, nullable=False, default=0)
    ProjectID = db.Column(db.Integer, db.ForeignKey('projects.ProjectID'), nullable=False)
    
    tasks = db.relationship('Task', backref='column', lazy=True)