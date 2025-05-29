from models import User, Project, Column, Task, TaskLog
from database import db

# CRUD операции для пользователей
def create_user(username, email, password):
    user = User(Username=username, Email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user

def get_user_by_username(username):
    return User.query.filter_by(Username=username).first()

# CRUD операции для проектов
def create_project(name, description, owner_id):
    project = Project(Name=name, Description=description, OwnerID=owner_id)
    db.session.add(project)
    db.session.commit()
    return project

def get_projects_for_user(user_id):
    return Project.query.filter_by(OwnerID=user_id).all()

# Другие CRUD операции...