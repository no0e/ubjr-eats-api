import hashlib
import secrets
from typing import Optional

from src.DAO.UserDAO import UserDAO
from src.Model.User import User


def hash_password(password: str, salt: Optional[str] = None) -> str:
    """Function that hash a given password with its salt.

    Parameters
    ----------
    password : str
        raw password
    salt : str
        user's salt

    Returns
    -------
    str
        The hashed password with in str type.
    """
    if salt is None:
        salt = ""
    combined = (salt + password).encode("utf-8")
    return hashlib.sha256(combined).hexdigest()


def create_salt() -> str:
    """Function that creates a salt

    Returns
    -------
    str
        The salt generated.
    """
    return secrets.token_hex(128)


def check_password_strength(password: str):
    """Function that checks if the password is strong enough.

    Parameters
    ----------
    password : str
        raw password
    """
    if len(password) < 8:
        raise Exception("Password length must be at least 8 characters")


def validate_username_password(username: str, password: str, user_repo: UserDAO) -> User:
    """Function that check if the stored password for a user is the same as when hashed again.

    Parameters
    ----------
    username : str
        username of the user's password we want to check
    password : str
        raw password
    user_repo : UserDAO
        This user's repository with all its stored attributes

    Returns
    -------
    User
        It returns the user if found and if the password given is the same as the user's.
    """
    user: Optional[User] = user_repo.get_by_username(username=username)
    if user is None:
        raise Exception(f"user with username {username} not found")
    hashed_input = hash_password(password, user.salt)
    if hashed_input != user.password:
        raise Exception("Incorrect password")

    return user
