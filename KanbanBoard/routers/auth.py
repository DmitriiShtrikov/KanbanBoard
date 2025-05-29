from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from database.crud import create_user, get_user_by_username
from models.user import User

auth_ns = Namespace('auth', description='Аутентификация')

# Модели для Swagger
user_model = auth_ns.model('User', {
    'Username': fields.String(required=True),
    'Email': fields.String(required=True),
    'Password': fields.String(required=True)
})

login_model = auth_ns.model('Login', {
    'Username': fields.String(required=True),
    'Password': fields.String(required=True)
})

@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(user_model)
    def post(self):
        """Регистрация пользователя"""
        data = auth_ns.payload
        if get_user_by_username(data['Username']):
            return {'message': 'Username already exists'}, 400
        create_user(data['Username'], data['Email'], data['Password'])
        return {'message': 'User created successfully'}, 201

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        """Аутентификация пользователя"""
        data = auth_ns.payload
        user = get_user_by_username(data['Username'])
        if not user or not user.check_password(data['Password']):
            return {'message': 'Invalid credentials'}, 401
        access_token = create_access_token(identity=user.UserID)
        return {'access_token': access_token}, 200