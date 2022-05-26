import base64
import hashlib
import hmac
from typing import List

from constants import PWD_HASH_ITERATIONS, PWD_HASH_SALT
from dao.user import UserDAO
from dao.model.user import User


class UserService:
    def __init__(self, dao: UserDAO) -> None:
        self.dao = dao

    def get_one(self, uid: int) -> User:
        """Get user by id"""
        return self.dao.get_one(uid)

    def get_all(self) -> List[User]:
        """Get all users"""
        return self.dao.get_all()

    def create(self, user_d: dict) -> User:
        """Add user to the database"""
        # Hash password
        user_d['password'] = self.create_hash(user_d.get('password'))
        # Add to the database
        user = self.dao.create(user_d)
        return user

    def update(self, user_d: dict) -> None:
        """Update user"""
        # Hash password
        user_d['password'] = self.create_hash(user_d.get('password'))
        # Update in the database
        self.dao.update(user_d)

    def delete(self, uid: int) -> None:
        """Delete user"""
        self.dao.delete(uid)

    def create_hash(self, password: str) -> bytes:
        """Hash password passed with sha256"""
        # Hash password
        hash_digest = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            PWD_HASH_SALT,
            PWD_HASH_ITERATIONS
        )
        # Encode with base64 for storage
        encoded_digest = base64.b64encode(hash_digest)
        return encoded_digest

    def get_by_username(self, username: str) -> User:
        """Get user data by username"""
        user = self.dao.get_by_username(username)
        return user

    def compare_passwords(self, password_hash: str, password_passed: str) -> bool:
        """Compare password passed with user password in db"""

        # Decode password from the database into binary
        decoded_digest = base64.b64decode(password_hash)

        # Hash password passed
        passed_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password_passed.encode('utf-8'),
            PWD_HASH_SALT,
            PWD_HASH_ITERATIONS
        )

        is_equal = hmac.compare_digest(decoded_digest, passed_hash)

        return is_equal
