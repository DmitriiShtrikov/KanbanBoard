from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Инициализация расширений
db = SQLAlchemy()
jwt = JWTManager()

def init_db(app):
    """Инициализация базы данных"""
    db.init_app(app)
    jwt.init_app(app)
    
    with app.app_context():
        db.create_all()
        init_default_data()

def init_default_data():
    """Инициализация начальных данных"""
    from models.column import Column
    if Column.query.count() == 0:
        default_columns = [
            Column(Name='To Do', OrderIndex=1),
            Column(Name='In Progress', OrderIndex=2),
            Column(Name='Done', OrderIndex=3)
        ]
        db.session.bulk_save_objects(default_columns)
        db.session.commit()