import datetime
import calendar
from typing import Union

import jwt
from flask import request
from flask_restx import abort

from constants import JWT_SECRET, JWT_ALGORITHM
from .user import UserService


class AuthService:
    def __init__(self, user_service: UserService) -> None:
        self.user_service = user_service

    def generate_tokens(self, username: str, password: Union[str, None], is_refresh=False) -> dict:
        """
        Generate access and refresh JWT tokens

        :raises HTTPException: If no user found or password is incorrect
        """

        # Get user and check existence
        user = self.user_service.get_by_username(username)
        if not user:
            abort(404, 'User not found')

        # Compare passwords
        if not is_refresh:
            password_is_correct = self.user_service.compare_passwords(user.password, password)
            if not password_is_correct:
                abort(401, 'Password is incorrect')

        # Generate token data
        data = {
            'username': user.username,
            'role': user.role
        }

        # Generate access token
        min30 = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        data['exp'] = calendar.timegm(min30.timetuple())
        access_token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)

        # Generate refresh token
        day130 = datetime.datetime.utcnow() + datetime.timedelta(days=130)
        data['exp'] = calendar.timegm(day130.timetuple())
        refresh_token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    def approve_token(self, refresh_token: str) -> dict:
        """Approve refresh token and generate a new pair of tokens"""
        data = jwt.decode(refresh_token, JWT_SECRET, algorithms=JWT_ALGORITHM)
        username = data.get('username')
        return self.generate_tokens(username, None, is_refresh=True)

    @staticmethod
    def auth_required(func):
        """Check token passed is correct"""
        def wrapper(*args, **kwargs):
            # Check if authorization credentials were passed and get token
            if 'Authorization' not in request.headers:
                abort(401, 'No authorization data passed')

            data = request.headers['Authorization']
            token = data.split("Bearer ")[-1]

            # Decode token
            try:
                jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
            except Exception as e:
                abort(401, f'JWT decode error {e}')

            return func(*args, **kwargs)

        return wrapper

    @staticmethod
    def admin_required(func):
        """Check if the role is admin"""
        def wrapper(*args, **kwargs):
            # Check if authorization credentials were passed and get token
            if 'Authorization' not in request.headers:
                abort(401)

            data = request.headers['Authorization']
            token = data.split("Bearer ")[-1]

            # Decode token and check role
            try:
                token_decoded = jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)
                role = token_decoded.get('role')
                if role != 'admin':
                    abort(401, 'Role is not admin')
            except Exception as e:
                abort(401, f'JWT decode error {e}')

            return func(*args, **kwargs)

        return wrapper
