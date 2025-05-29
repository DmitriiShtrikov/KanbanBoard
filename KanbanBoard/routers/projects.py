from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.crud import create_project, get_projects_for_user

projects_ns = Namespace('projects', description='Операции с проектами')

project_model = projects_ns.model('Project', {
    'ProjectID': fields.Integer(readonly=True),
    'Name': fields.String(required=True),
    'Description': fields.String(),
    'OwnerID': fields.Integer(readonly=True),
    'CreatedAt': fields.DateTime(readonly=True)
})

@projects_ns.route('/')
class ProjectList(Resource):
    @projects_ns.marshal_list_with(project_model)
    @jwt_required()
    def get(self):
        """Получение списка проектов пользователя"""
        user_id = get_jwt_identity()
        return get_projects_for_user(user_id)

    @projects_ns.expect(project_model)
    @projects_ns.marshal_with(project_model, code=201)
    @jwt_required()
    def post(self):
        """Создание нового проекта"""
        user_id = get_jwt_identity()
        data = projects_ns.payload
        project = create_project(data['Name'], data.get('Description'), user_id)
        return project, 201