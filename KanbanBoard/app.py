from flask import Flask
from flask_restx import Api
from dotenv import load_dotenv
import os
from database.database import db, jwt, init_db

def create_app():
    """Фабрика приложений"""
    load_dotenv()
    
    app = Flask(__name__)
    app.config.update({
        'SQLALCHEMY_DATABASE_URI': os.getenv('DB_CONNECTION_STRING'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET_KEY': os.getenv('JWT_SECRET')
    })
    
    # Инициализация API
    api = Api(
        title='Kanban Board API',
        version='1.0',
        description='API для управления канбан-доской',
        doc='/docs/',
        authorizations={
            'Bearer Auth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'JWT токен в формате: Bearer {token}'
            }
        },
        security='Bearer Auth'
    )
    
    # Инициализация базы данных
    init_db(app)
    
    # Регистрация маршрутов
    from routers.auth import auth_ns
    from routers.projects import projects_ns
    from routers.columns import columns_ns
    from routers.tasks import tasks_ns
    from routers.task_logs import task_logs_ns
    from routers.project_members import members_ns
    
    api.add_namespace(auth_ns)
    api.add_namespace(projects_ns)
    api.add_namespace(columns_ns)
    api.add_namespace(tasks_ns)
    api.add_namespace(task_logs_ns)
    api.add_namespace(members_ns)
    
    app.api = api
    api.init_app(app)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)