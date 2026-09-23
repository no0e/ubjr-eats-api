import pytest

from src.DAO.DBConnector import DBConnector
from src.DAO.UserDAO import UserDAO
from src.Model.User import User
from src.Utils.reset_db import ResetDatabase


@pytest.fixture
def db_connector():
    db = DBConnector()
    yield db


@pytest.fixture
def user_dao(db_connector):
    return UserDAO(db_connector, test=True)


def test_get_by_username(user_dao):
    ResetDatabase().launch(True)
    user_alice = user_dao.get_by_username("aliceasm")
    missing_user = user_dao.get_by_username("missing user")
    assert user_alice is not None
    assert user_alice.username == "aliceasm"
    assert user_alice.firstname == "Alice"
    assert user_alice.lastname == "Asm"
    assert user_alice.account_type == "Administrator"
    assert missing_user is None


def test_create_user(user_dao):
    ResetDatabase().launch(True)
    to_be_created_user = User(
        username="created_user",
        firstname="Created",
        lastname="User",
        password="pwdOfCreatedUser123",
        salt="saltOfCreatedUser",
        account_type="Customer",
    )
    created_user = user_dao.create_user(to_be_created_user)
    not_to_be_created_user = None
    not_created_user = user_dao.create_user(not_to_be_created_user)
    assert created_user
    assert not not_created_user


def test_update_user(user_dao):
    ResetDatabase().launch(True)
    new_lastname = "Vasselot"
    updated_user = user_dao.update_user(username="drdavid", lastname=new_lastname)
    missing_user = user_dao.update_user(username="missing user")
    assert updated_user
    assert not missing_user


def test_delete_user(user_dao):
    ResetDatabase().launch(True)
    user_to_delete = user_dao.get_by_username("drdavid")
    missing_user = None
    true_deletion = user_dao.delete_user(user_to_delete)
    false_deletion = user_dao.delete_user(missing_user)
    assert true_deletion
    assert not false_deletion


if __name__ == "__main__":
    pytest.main()
