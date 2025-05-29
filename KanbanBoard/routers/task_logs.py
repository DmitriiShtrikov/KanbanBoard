from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.task_log import TaskLog
from models.task import Task
from models.column import Column
from models.project_member import ProjectMember

task_logs_ns = Namespace('task_logs', description='Логи задач')

log_model = task_logs_ns.model('TaskLog', {
    'LogID': fields.Integer(readonly=True),
    'TaskID': fields.Integer(required=True),
    'UserID': fields.Integer(required=True),
    'Action': fields.String(required=True),
    'Message': fields.String(required=True),
    'CreatedAt': fields.DateTime(readonly=True)
})

@task_logs_ns.route('/task/<int:task_id>')
class TaskLogList(Resource):
    @task_logs_ns.marshal_list_with(log_model)
    @jwt_required()
    def get(self, task_id):
        """Получение логов задачи"""
        task = Task.query.get_or_404(task_id)
        user_id = get_jwt_identity()
        column = Column.query.get(task.ColumnID)
        # Проверка доступа
        if not ProjectMember.query.filter_by(ProjectID=column.ProjectID, UserID=user_id).first():
            return {'message': 'Доступ запрещен'}, 403
            
        return TaskLog.query.filter_by(TaskID=task_id).order_by(TaskLog.CreatedAt.desc()).all()