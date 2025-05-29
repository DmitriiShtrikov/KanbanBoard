from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db
from models.project import Project
from models.project_member import ProjectMember
from models.user import User

members_ns = Namespace('project_members', description='Управление участниками проектов')

member_model = members_ns.model('ProjectMember', {
    'MemberID': fields.Integer(readonly=True),
    'ProjectID': fields.Integer(required=True),
    'UserID': fields.Integer(required=True),
    'Role': fields.String(required=True)
})

@members_ns.route('/project/<int:project_id>')
class ProjectMemberList(Resource):
    @members_ns.marshal_list_with(member_model)
    @jwt_required()
    def get(self, project_id):
        """Получение списка участников проекта"""
        user_id = get_jwt_identity()
        # Проверка что пользователь участник проекта
        if not ProjectMember.query.filter_by(ProjectID=project_id, UserID=user_id).first():
            return {'message': 'Доступ запрещен'}, 403
            
        return ProjectMember.query.filter_by(ProjectID=project_id).all()

    @members_ns.expect(member_model)
    @members_ns.marshal_with(member_model, code=201)
    @jwt_required()
    def post(self, project_id):
        """Добавление участника в проект"""
        current_user_id = get_jwt_identity()
        project = Project.query.get_or_404(project_id)
        
        # Проверка что текущий пользователь владелец проекта
        if project.OwnerID != current_user_id:
            return {'message': 'Только владелец может добавлять участников'}, 403
            
        data = members_ns.payload
        user = User.query.get_or_404(data['UserID'])
        
        # Проверка что пользователь еще не участник
        if ProjectMember.query.filter_by(ProjectID=project_id, UserID=data['UserID']).first():
            return {'message': 'Пользователь уже участник проекта'}, 400
            
        member = ProjectMember(
            ProjectID=project_id,
            UserID=data['UserID'],
            Role=data.get('Role', 'member')
        )
        db.session.add(member)
        db.session.commit()
        return member, 201

@members_ns.route('/<int:member_id>')
class ProjectMemberResource(Resource):
    @jwt_required()
    def delete(self, member_id):
        """Удаление участника из проекта"""
        member = ProjectMember.query.get_or_404(member_id)
        current_user_id = get_jwt_identity()
        project = Project.query.get(member.ProjectID)
        
        # Проверка что текущий пользователь владелец проекта
        if project.OwnerID != current_user_id:
            return {'message': 'Только владелец может удалять участников'}, 403
            
        db.session.delete(member)
        db.session.commit()
        return {'message': 'Участник удален из проекта'}, 200