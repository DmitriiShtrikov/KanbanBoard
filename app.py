"""
Kanban Board API с использованием Flask-RESTx, SQLAlchemy и JWT аутентификации
Комментированная версия с дополнительными методами
"""

# Импорт необходимых библиотек
from flask import Flask, request  # Основные компоненты Flask
from flask_sqlalchemy import SQLAlchemy  # ORM для работы с БД
from flask_restx import Api, Resource, fields, Namespace  # Для создания API
from werkzeug.security import generate_password_hash, check_password_hash  # Для хеширования паролей
from flask_jwt_extended import (  # Для JWT аутентификации
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
import os  # Для работы с переменными окружения
from datetime import datetime  # Для работы с датами
from dotenv import load_dotenv  # Для загрузки .env файла
import logging  # Для логирования

# Настройка логирования
logging.basicConfig(level=logging.INFO)  # Установка уровня логирования
logger = logging.getLogger(__name__)  # Создание логгера

# Загрузка переменных окружения из файла .env
load_dotenv()

# Функция создания Flask приложения
def create_app():
    """Фабрика для создания Flask приложения с конфигурацией"""
    app = Flask(__name__)  # Создание экземпляра Flask
    
    # Конфигурация приложения
    app.config.update({
        # URI подключения к БД (по умолчанию SQLite)
        'SQLALCHEMY_DATABASE_URI': os.getenv(
            'DB_CONNECTION_STRING',
            'sqlite:///kanban.db'
        ),
        # Отключение системы отслеживания модификаций
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        # Секретный ключ для JWT
        'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY', 'super-secret-key'),
        # Время жизни токена (1 час)
        'JWT_ACCESS_TOKEN_EXPIRES': 3600  
    })
    
    # Инициализация расширений
    db.init_app(app)  # Инициализация SQLAlchemy
    jwt.init_app(app)  # Инициализация JWTManager
    
    # Регистрация API
    api.init_app(app)  # Инициализация Flask-RESTx API
    
    return app  # Возврат созданного приложения

# Инициализация расширений вне контекста приложения
db = SQLAlchemy()  # Создание экземпляра SQLAlchemy
jwt = JWTManager()  # Создание экземпляра JWTManager

# Настройка Swagger API документации
api = Api(
    title='Kanban Board API',  # Название API
    version='1.0',  # Версия API
    description='API для управления канбан-доской с JWT аутентификацией',  # Описание
    doc='/docs/',  # URL для Swagger UI
    authorizations={  # Настройки авторизации
        'Bearer Auth': {
            'type': 'apiKey',  # Тип авторизации
            'in': 'header',  # Где передается токен
            'name': 'Authorization',  # Имя заголовка
            'description': 'JWT токен в формате: Bearer {token}'  # Описание
        }
    },
    security='Bearer Auth'  # Использовать JWT по умолчанию
)

# Модель пользователя для БД
class User(db.Model):
    """Модель пользователя в системе"""
    __tablename__ = 'users'  # Имя таблицы
    
    # Поля таблицы
    id = db.Column(db.Integer, primary_key=True)  # ID пользователя
    username = db.Column(db.String(50), unique=True, nullable=False)  # Логин
    email = db.Column(db.String(100), unique=True, nullable=False)  # Email
    password_hash = db.Column(db.String(255), nullable=False)  # Хеш пароля
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Дата создания
    tasks = db.relationship('Task', backref='user', lazy=True)  # Связь с задачами

    # Метод для установки пароля
    def set_password(self, password):
        """Генерация хеша пароля"""
        self.password_hash = generate_password_hash(password)  # Хеширование

    # Метод проверки пароля
    def check_password(self, password):
        """Проверка соответствия пароля хешу"""
        return check_password_hash(self.password_hash, password)  # Сравнение

# Модель статусов задач
class TaskStatus(db.Model):
    """Модель статусов задач (To Do, In Progress, Done)"""
    __tablename__ = 'task_statuses'  # Имя таблицы
    
    # Поля таблицы
    id = db.Column(db.Integer, primary_key=True)  # ID статуса
    name = db.Column(db.String(50), unique=True, nullable=False)  # Название
    order_index = db.Column(db.Integer, nullable=False, default=0)  # Порядок
    tasks = db.relationship('Task', backref='status', lazy=True)  # Связь с задачами

# Модель задачи
class Task(db.Model):
    """Модель задачи канбан-доски"""
    __tablename__ = 'tasks'  # Имя таблицы
    
    # Поля таблицы
    id = db.Column(db.Integer, primary_key=True)  # ID задачи
    title = db.Column(db.String(100), nullable=False)  # Заголовок
    description = db.Column(db.Text)  # Описание
    status_id = db.Column(db.Integer, db.ForeignKey('task_statuses.id'), nullable=False)  # Ссылка на статус
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Ссылка на пользователя
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Дата создания
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Дата обновления

# Создание пространств имен API
auth_ns = Namespace('auth', description='Операции аутентификации')  # Для аутентификации
tasks_ns = Namespace('tasks', description='Операции с задачами')  # Для задач
statuses_ns = Namespace('statuses', description='Операции со статусами задач')  # Для статусов

# Регистрация пространств имен в API
api.add_namespace(auth_ns)  # Добавление auth
api.add_namespace(tasks_ns)  # Добавление tasks
api.add_namespace(statuses_ns)  # Добавление statuses

# Модель данных пользователя для Swagger
user_model = api.model('User', {
    'username': fields.String(required=True, example='user123'),  # Логин
    'email': fields.String(required=True, example='user@example.com'),  # Email
    'password': fields.String(required=True, example='strongpassword')  # Пароль
})

# Модель данных для входа
login_model = api.model('Login', {
    'username': fields.String(required=True, example='user123'),  # Логин
    'password': fields.String(required=True, example='strongpassword')  # Пароль
})

# Модель данных задачи
task_model = api.model('Task', {
    'id': fields.Integer(readonly=True),  # ID задачи
    'title': fields.String(required=True, example='Реализовать фичу X'),  # Заголовок
    'description': fields.String(example='Подробное описание задачи'),  # Описание
    'status_id': fields.Integer(required=True, example=1),  # ID статуса
    'user_id': fields.Integer(readonly=True),  # ID пользователя
    'created_at': fields.DateTime(readonly=True),  # Дата создания
    'updated_at': fields.DateTime(readonly=True)  # Дата обновления
})

# Модель данных статуса
status_model = api.model('Status', {
    'id': fields.Integer(readonly=True),  # ID статуса
    'name': fields.String(required=True, example='В работе'),  # Название
    'order_index': fields.Integer(example=2)  # Порядок
})

# Эндпоинт регистрации
@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(user_model)  # Ожидаемая модель данных
    @auth_ns.response(201, 'Пользователь успешно зарегистрирован')  # Успешный ответ
    @auth_ns.response(400, 'Ошибка валидации')  # Ошибка
    def post(self):
        """Регистрация нового пользователя"""
        data = request.get_json()  # Получение данных
        
        # Проверка уникальности логина
        if User.query.filter_by(username=data['username']).first():
            return {'message': 'Пользователь с таким именем уже существует'}, 400
            
        # Проверка уникальности email
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Пользователь с таким email уже существует'}, 400
            
        # Создание пользователя
        user = User(
            username=data['username'],
            email=data['email']
        )
        user.set_password(data['password'])  # Хеширование пароля
        
        db.session.add(user)  # Добавление в сессию
        db.session.commit()  # Сохранение в БД
        
        return {'message': 'Пользователь успешно создан'}, 201  # Ответ

# Эндпоинт входа
@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)  # Ожидаемая модель данных
    @auth_ns.response(200, 'Успешный вход')  # Успешный ответ
    @auth_ns.response(401, 'Неверные учетные данные')  # Ошибка
    def post(self):
        """Аутентификация пользователя"""
        data = request.get_json()  # Получение данных
        user = User.query.filter_by(username=data['username']).first()  # Поиск пользователя
        
        # Проверка пользователя и пароля
        if not user or not user.check_password(data['password']):
            return {'message': 'Неверное имя пользователя или пароль'}, 401
            
        # Генерация JWT токена
        access_token = create_access_token(identity=user.id)
        return {'access_token': access_token}, 200  # Ответ с токеном

# Эндпоинт списка задач
@tasks_ns.route('/')
class TaskList(Resource):
    @tasks_ns.marshal_list_with(task_model)  # Форматирование ответа
    @jwt_required()  # Требуется аутентификация
    def get(self):
        """Получение всех задач текущего пользователя"""
        user_id = get_jwt_identity()  # Получение ID из токена
        return Task.query.filter_by(user_id=user_id).all()  # Возврат задач

    @tasks_ns.expect(task_model)  # Ожидаемая модель данных
    @tasks_ns.marshal_with(task_model)  # Форматирование ответа
    @tasks_ns.response(201, 'Задача создана')  # Успешный ответ
    @jwt_required()  # Требуется аутентификация
    def post(self):
        """Создание новой задачи"""
        data = request.get_json()  # Получение данных
        user_id = get_jwt_identity()  # Получение ID из токена
        
        # Проверка существования статуса
        if not TaskStatus.query.get(data['status_id']):
            return {'message': 'Неверный ID статуса'}, 400
            
        # Создание задачи
        task = Task(
            title=data['title'],
            description=data.get('description'),
            status_id=data['status_id'],
            user_id=user_id
        )
        
        db.session.add(task)  # Добавление в сессию
        db.session.commit()  # Сохранение в БД
        
        return task, 201  # Возврат созданной задачи

# Эндпоинт для работы с конкретной задачей
@tasks_ns.route('/<int:task_id>')
class TaskResource(Resource):
    @tasks_ns.marshal_with(task_model)  # Форматирование ответа
    @jwt_required()  # Требуется аутентификация
    def get(self, task_id):
        """Получение задачи по ID"""
        user_id = get_jwt_identity()  # Получение ID из токена
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()  # Поиск задачи
        
        if not task:  # Проверка существования
            return {'message': 'Задача не найдена'}, 404
            
        return task  # Возврат задачи

    @tasks_ns.expect(task_model)  # Ожидаемая модель данных
    @tasks_ns.marshal_with(task_model)  # Форматирование ответа
    @jwt_required()  # Требуется аутентификация
    def put(self, task_id):
        """Обновление задачи"""
        user_id = get_jwt_identity()  # Получение ID из токена
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()  # Поиск задачи
        
        if not task:  # Проверка существования
            return {'message': 'Задача не найдена'}, 404
            
        data = request.get_json()  # Получение данных
        
        # Обновление полей
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'status_id' in data:
            if not TaskStatus.query.get(data['status_id']):  # Проверка статуса
                return {'message': 'Неверный ID статуса'}, 400
            task.status_id = data['status_id']
        
        db.session.commit()  # Сохранение изменений
        return task  # Возврат обновленной задачи

    @jwt_required()  # Требуется аутентификация
    def delete(self, task_id):
        """Удаление задачи"""
        user_id = get_jwt_identity()  # Получение ID из токена
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()  # Поиск задачи
        
        if not task:  # Проверка существования
            return {'message': 'Задача не найдена'}, 404
            
        db.session.delete(task)  # Удаление задачи
        db.session.commit()  # Сохранение изменений
        return {'message': 'Задача удалена'}, 200  # Ответ

# Функция инициализации начальных данных
def init_default_data():
    """Создание стандартных статусов задач при первом запуске"""
    if TaskStatus.query.count() == 0:  # Проверка наличия статусов
        default_statuses = [  # Стандартные статусы
            TaskStatus(name='To Do', order_index=1),
            TaskStatus(name='In Progress', order_index=2),
            TaskStatus(name='Done', order_index=3)
        ]
        db.session.bulk_save_objects(default_statuses)  # Массовое сохранение
        db.session.commit()  # Сохранение в БД
        logger.info("Стандартные статусы задач инициализированы")  # Логирование

# Корневой эндпоинт
@api.route('/')
class Home(Resource):
    def get(self):
        """Перенаправление на документацию API"""
        return {'message': 'Используйте /docs/ для доступа к документации API'}, 302, {'Location': '/docs/'}

# Точка входа
if __name__ == '__main__':
    app = create_app()  # Создание приложения
    
    with app.app_context():  # Контекст приложения
        db.create_all()  # Создание таблиц в БД
        init_default_data()  # Инициализация данных
    
    app.run(host='0.0.0.0', port=5000, debug=True)  # Запуск сервера