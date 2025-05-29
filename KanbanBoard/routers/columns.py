from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models.column import Column
from models.project import Project
from models.project_member import ProjectMember

columns_ns = Namespace('columns', description='Операции с колонками')

column_model = columns_ns.model('Column', {
    'ColumnID': fields.Integer(readonly=True),
    'Name': fields.String(required=True),
    'OrderIndex': fields.Integer(required=True),
    'ProjectID': fields.Integer(required=True)
})

@columns_ns.route('/project/<int:project_id>')
class ColumnList(Resource):
    @columns_ns.marshal_list_with(column_model)
    @jwt_required()
    def get(self, project_id):
        """Получение всех колонок проекта"""
        user_id = get_jwt_identity()
        # Проверка что пользователь имеет доступ к проекту
        if not ProjectMember.query.filter_by(ProjectID=project_id, UserID=user_id).first():
            return {'message': 'Доступ запрещен'}, 403
        return Column.query.filter_by(ProjectID=project_id).order_by(Column.OrderIndex).all()

    @columns_ns.expect(column_model)
    @columns_ns.marshal_with(column_model, code=201)
    @jwt_required()
    def post(self, project_id):
        """Создание новой колонки"""
        user_id = get_jwt_identity()
        # Проверка что пользователь владелец проекта
        project = Project.query.filter_by(ProjectID=project_id, OwnerID=user_id).first()
        if not project:
            return {'message': 'Только владелец может создавать колонки'}, 403
            
        data = columns_ns.payload
        column = Column(
            Name=data['Name'],
            OrderIndex=data['OrderIndex'],
            ProjectID=project_id
        )
        db.session.add(column)
        db.session.commit()
        return column, 201

@columns_ns.route('/<int:column_id>')
class ColumnResource(Resource):
    @columns_ns.marshal_with(column_model)
    @jwt_required()
    def get(self, column_id):
        """Получение колонки по ID"""
        column = Column.query.get_or_404(column_id)
        user_id = get_jwt_identity()
        # Проверка доступа
        if not ProjectMember.query.filter_by(ProjectID=column.ProjectID, UserID=user_id).first():
            return {'message': 'Доступ запрещен'}, 403
        return column

    @columns_ns.expect(column_model)
    @columns_ns.marshal_with(column_model)
    @jwt_required()
    def put(self, column_id):
        """Обновление колонки"""
        column = Column.query.get_or_404(column_id)
        user_id = get_jwt_identity()
        # Проверка что пользователь владелец
        if not Project.query.filter_by(ProjectID=column.ProjectID, OwnerID=user_id).first():
            return {'message': 'Только владелец может изменять колонки'}, 403
            
        data = columns_ns.payload
        column.Name = data.get('Name', column.Name)
        column.OrderIndex = data.get('OrderIndex', column.OrderIndex)
        db.session.commit()
        return column

    @jwt_required()
    def delete(self, column_id):
        """Удаление колонки"""
        column = Column.query.get_or_404(column_id)
        user_id = get_jwt_identity()
        # Проверка что пользователь владелец
        if not Project.query.filter_by(ProjectID=column.ProjectID, OwnerID=user_id).first():
            return {'message': 'Только владелец может удалять колонки'}, 403
            
        db.session.delete(column)
        db.session.commit()
        return {'message': 'Колонка удалена'}, 200