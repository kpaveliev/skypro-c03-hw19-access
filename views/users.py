from flask import request
from flask_restx import Resource, Namespace, fields
from marshmallow import ValidationError

from dao.model.user import UserSchema
from implemented import user_service

user_ns = Namespace('users')

# Define api model for documentation
user_model = user_ns.model('User', {
    'id': fields.Integer(required=False),
    'username': fields.String(required=True),
    'password': fields.String(required=True),
    'role': fields.String(required=True)
})


@user_ns.route('/')
class UsersView(Resource):
    @user_ns.doc(description='Get users')
    @user_ns.response(200, 'Success', user_model)
    def get(self):
        all_users = user_service.get_all()
        res = UserSchema(many=True).dump(all_users)
        return res, 200

    @user_ns.doc(description='Add new user', body=user_model)
    @user_ns.response(201, 'Created')
    @user_ns.response(400, 'ValidationError')
    def post(self):
        data = request.json
        try:
            user_dict = UserSchema().dump(data)
        except ValidationError as e:
            return f"{e}", 400
        else:
            user = user_service.create(user_dict)
            return "", 201, {"location": f"/users/{user.id}"}


@user_ns.route('/<int:uid>')
class UserView(Resource):
    @user_ns.doc(description='Get user by id')
    @user_ns.response(200, 'Success', user_model)
    @user_ns.response(404, 'Not Found')
    def get(self, uid):
        user = user_service.get_one(uid)
        if not user:
            return "", 404
        user_dict = UserSchema().dump(user)
        return user_dict, 200

    @user_ns.doc(description='Update user by id')
    @user_ns.response(201, 'User updated', user_model)
    @user_ns.response(404, 'Not Found')
    def put(self, uid):
        # Check if user exist
        user = user_service.get_one(uid)
        if not user:
            return "", 404

        # Update with data passed if found
        data = request.json
        if "id" not in data:
            data["id"] = uid

        user_service.update(data)
        return "", 201

    @user_ns.doc(description='Delete user by id')
    @user_ns.response(204, 'User deleted', user_model)
    @user_ns.response(404, 'Not Found')
    def delete(self, uid):
        # Check if user exist
        user = user_service.get_one(uid)
        if not user:
            return "", 404

        # Delete if found
        user_service.delete(uid)
        return "", 204
