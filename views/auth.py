from flask import request
from flask_restx import Resource, Namespace, fields

from implemented import auth_service

auth_ns = Namespace('auth')

# Define api model for documentation
auth_model = auth_ns.model('Authentication', {
    'username': fields.String(required=True),
    'password': fields.String(required=True)
})

tokens_model = auth_ns.model('Tokens', {
    'access_token': fields.String(required=True),
    'refresh_token': fields.String(required=True)
})


@auth_ns.route('/')
class AuthView(Resource):
    @auth_ns.doc(description='Send authentication info', body=auth_model)
    @auth_ns.response(201, 'Tokens created', tokens_model)
    @auth_ns.response(400, 'Bad Request')
    @auth_ns.response(401, 'Unauthorized')
    @auth_ns.response(404, 'Not Found')
    def post(self):
        # Get and check credentials passed
        data = request.json
        username = data.get('username')
        password = data.get('password')
        if None in [username, password]:
            return "", 400

        # Generate tokens
        tokens = auth_service.generate_tokens(username, password)
        return tokens, 201

    @auth_ns.doc(description='Update user by id')
    @auth_ns.response(201, 'Tokens created', tokens_model)
    @auth_ns.response(404, 'Not Found')
    def put(self):
        data = request.json
        refresh_token = data.get('refresh_token')
        tokens = auth_service.approve_token(refresh_token)
        return tokens, 201
