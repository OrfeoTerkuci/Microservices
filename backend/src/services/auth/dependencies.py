"""
Dependencies for the API.

This module contains all the dependencies for the API, such as the security and roles.
"""

# Imports
from typing import Optional

import bcrypt
from wrapper import get_all_users, UserModel

# Constants


def verify_password(plain_password: str, crypt_password: str) -> bool:
    """
    Verify the password.

    :param plain_password: Plain password
    :param crypt_password: Hashed password
    :return: True if password is verified, False otherwise
    """
    return bcrypt.checkpw(plain_password.encode(), crypt_password.encode())


def get_password_hash(password: str) -> str:
    """
    Get password hash.

    :param password: Password
    :return: Hashed password
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def authenticate_user(username: str, password: str) -> Optional[UserModel]:
    """
    Authenticate user.

    :param username: Username
    :param password: Password
    :return: UserModel if user is found, None otherwise
    """
    users = get_all_users()

    for user in users:
        if user.username == username and verify_password(password, str(user.password)):  # type: ignore
            return user
    return None
