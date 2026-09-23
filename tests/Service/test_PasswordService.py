from typing import Optional

import pytest

from src.Model.User import User
from src.Service.PasswordService import check_password_strength, create_salt, hash_password, validate_username_password


def test_hash_password():
    password = "soleil1234"
    hashed_password = hash_password(password)
    assert hashed_password == "a88c648411492422ee9a1f4b03d3f5b71705499786f4415a59b51b255611ba50"


def test_hash_password_with_salt():
    password = "soleil1234"
    salt = "jambon"
    hashed_password = hash_password(password, salt)
    assert hashed_password == "56d25b0190eb6fcdab76f20550aa3e85a37ee48d520ac70385ae3615deb7d53a"
    password2 = "mdpdefou"
    salt2 = ("39f0d92428e5c38db7ad4b7289f03e0eb0a7dccf71e27cc9cc906b47f991c2bb43bff68251"
    "305b9d438b802848900636090b2e52f32329a15a78bd1cae910d4541ba4a1e8c963bd055ccdc95fdf6a6"
    "05523b243bf662a3f1c239457b6ed2e632212d0380cdc49d3f0de28dab4e63eec3078d320a70471677465a"
    "6b885d69be8f")
    assert hash_password(password2, salt2) == "69281057d9885dcf68342f727155925545f112816740fee4d1d4a39ffa1c034f"


def test_create_salt():
    salt = create_salt()
    assert len(salt) == 256


def test_check_password_strength():
    with pytest.raises(Exception) as exception_password:
        check_password_strength("coucou")
    assert str(exception_password.value) == "Password length must be at least 8 characters"


class MockUserRepo:
    def get_by_username(self, username: str) -> Optional[User]:
        if username == "janjak":
            return User(
                username="janjak",
                firstname="Jean-Jacques",
                lastname="John",
                salt="jambon",
                password="56d25b0190eb6fcdab76f20550aa3e85a37ee48d520ac70385ae3615deb7d53a",
                account_type="Customer",
            )
        else:
            return None


user_repo = MockUserRepo()


def test_validate_username_password_is_ok():
    janjak = validate_username_password("janjak", "soleil1234", user_repo)
    assert janjak.username == "janjak"


def test_validate_username_password_unknown_user():
    with pytest.raises(Exception) as exception_info:
        validate_username_password("Jean-Jacques", "soleil1234", user_repo)
    assert str(exception_info.value) == "user with username Jean-Jacques not found"


def test_validate_username_password_incorrect_password():
    with pytest.raises(Exception) as exception_info:
        validate_username_password("janjak", "wrongpassword", user_repo)
    assert str(exception_info.value) == "Incorrect password"
    assert validate_username_password("janjak", "soleil1234", user_repo) == User(
        username="janjak",
        firstname="Jean-Jacques",
        lastname="John",
        salt="jambon",
        password="56d25b0190eb6fcdab76f20550aa3e85a37ee48d520ac70385ae3615deb7d53a",
        account_type="Customer",
    )
    assert (
        user_repo.get_by_username("janjak").password
        == "56d25b0190eb6fcdab76f20550aa3e85a37ee48d520ac70385ae3615deb7d53a"
    )
    assert user_repo.get_by_username("janjak").salt == "jambon"
