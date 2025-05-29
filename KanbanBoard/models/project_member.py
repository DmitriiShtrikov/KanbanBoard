from database import db

class ProjectMember(db.Model):
    __tablename__ = 'project_members'
    
    MemberID = db.Column(db.Integer, primary_key=True)
    ProjectID = db.Column(db.Integer, db.ForeignKey('projects.ProjectID'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    Role = db.Column(db.String(50), nullable=False, default='member')
    
    user = db.relationship('User', backref='project_memberships')