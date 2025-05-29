from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models.task import Task
from models.column import Column
from models.project_member import ProjectMember
from models.task_log import TaskLog
from datetime import datetime

tasks_ns = Namespace('tasks', description='Операции с задачами')

task_model = tasks_ns.model('Task', {
    'TaskID': fields.Integer(readonly=True, description='ID задачи'),
    'Title': fields.String(required=True, example='Новая задача', description='Заголовок задачи'),
    'Description': fields.String(example='Описание задачи', description='Подробное описание'),
    'ColumnID': fields.Integer(required=True, example=1, description='ID колонки'),
    'CreatedBy': fields.Integer(readonly=True, description='ID создателя'),
    'CreatedAt': fields.DateTime(readonly=True, description='Дата создания'),
    'UpdatedAt': fields.DateTime(readonly=True, description='Дата обновления')
})

# Добавим модель для создания задачи без обязательных полей, которые заполняются автоматически
task_create_model = tasks_ns.model('TaskCreate', {
    'Title': fields.String(required=True, example='Новая задача'),
    'Description': fields.String(example='Описание задачи'),
    'ColumnID': fields.Integer(required=True, example=1)
})

@tasks_ns.route('/column/<int:column_id>')
class TaskList(Resource):
    @tasks_ns.doc(security='Bearer Auth')
    @tasks_ns.marshal_list_with(task_model)
    @jwt_required()
    def get(self, column_id):
        """Получение задач колонки"""
        # Проверка доступа
        column = Column.query.get_or_404(column_id)
        user_id = get_jwt_identity()
        if not ProjectMember.query.filter_by(ProjectID=column.ProjectID, UserID=user_id).first():
            return {'message': 'Доступ запрещен'}, 403
            
        return Task.query.filter_by(ColumnID=column_id).all()

    @tasks_ns.doc(security='Bearer Auth')
    @tasks_ns.expect(task_create_model)
    @tasks_ns.marshal_with(task_model, code=201)
    @jwt_required()
    def post(self, column_id):
        """Создание новой задачи"""
        data = tasks_ns.payload
        
        # Валидация данных
        if not data.get('Title'):
            return {'message': 'Title обязательно'}, 422
            
        column = Column.query.get_or_404(column_id)
        user_id = get_jwt_identity()
        
        # Проверка доступа
        if not ProjectMember.query.filter_by(ProjectID=column.ProjectID, UserID=user_id).first():
            return {'message': 'Доступ запрещен'}, 403
            
        task = Task(
            Title=data['Title'],
            Description=data.get('Description', ''),
            ColumnID=column_id,
            CreatedBy=user_id
        )
        
        db.session.add(task)
        db.session.commit()
        
        return task, 201
    
@tasks_ns.route('/<int:task_id>')
class TaskResource(Resource):
    @tasks_ns.marshal_with(task_model)
    @jwt_required()
    def get(self, task_id):
        """Получение задачи по ID"""
        task = Task.query.get_or_404(task_id)
        user_id = get_jwt_identity()
        column = Column.query.get(task.ColumnID)
        # Проверка доступа
        if not ProjectMember.query.filter_by(ProjectID=column.ProjectID, UserID=user_id).first():
            return {'message': 'Доступ запрещен'}, 403
        return task

    @tasks_ns.expect(task_model)
    @tasks_ns.marshal_with(task_model)
    @jwt_required()
    def put(self, task_id):
        """Обновление задачи"""
        task = Task.query.get_or_404(task_id)
        user_id = get_jwt_identity()
        column = Column.query.get(task.ColumnID)
        # Проверка доступа
        if not ProjectMember.query.filter_by(ProjectID=column.ProjectID, UserID=user_id).first():
            return {'message': 'Доступ запрещен'}, 403
            
        data = tasks_ns.payload
        old_column_id = task.ColumnID
        
        task.Title = data.get('Title', task.Title)
        task.Description = data.get('Description', task.Description)
        
        # Логирование изменения колонки
        if 'ColumnID' in data and data['ColumnID'] != old_column_id:
            new_column = Column.query.get_or_404(data['ColumnID'])
            task.ColumnID = data['ColumnID']
            
            log = TaskLog(
                TaskID=task.TaskID,
                UserID=user_id,
                Action='move',
                Message=f'Задача перемещена из колонки {old_column_id} в {task.ColumnID}'
            )
            db.session.add(log)
        
        db.session.commit()
        return task

    @jwt_required()
    def delete(self, task_id):
        """Удаление задачи"""
        task = Task.query.get_or_404(task_id)
        user_id = get_jwt_identity()
        column = Column.query.get(task.ColumnID)
        # Проверка доступа
        if not ProjectMember.query.filter_by(ProjectID=column.ProjectID, UserID=user_id).first():
            return {'message': 'Доступ запрещен'}, 403
            
        db.session.delete(task)
        db.session.commit()
        return {'message': 'Задача удалена'}, 200