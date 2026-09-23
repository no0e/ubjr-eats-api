import pytest

from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.UserDAO import UserDAO
from src.Model.Customer import Customer
from src.Utils.reset_db import ResetDatabase


@pytest.fixture
def db_connector():
    db = DBConnector()
    yield db


@pytest.fixture
def user_dao(db_connector):
    return UserDAO(db_connector, test=True)


@pytest.fixture
def customer_dao(db_connector):
    return CustomerDAO(db_connector, test=True)


def test_create(customer_dao, user_dao):
    ResetDatabase().launch(True)
    user_to_be_customer = user_dao.get_by_username("futurecustomer")
    customer_to_create = Customer(
        username=user_to_be_customer.username,
        firstname=user_to_be_customer.firstname,
        lastname=user_to_be_customer.lastname,
        account_type=user_to_be_customer.account_type,
        password=user_to_be_customer.password,
        salt=user_to_be_customer.salt,
        address="51 Rue Blaise Pascal, 35170 Bruz",
    )
    assert customer_dao.create(customer_to_create) is True
    with pytest.raises(TypeError):
        customer_dao.create(1)


def test_find_by_username(customer_dao):
    ResetDatabase().launch(True)
    found_customer = customer_dao.find_by_username("charliz")
    nonexistentcustomer = customer_dao.find_by_username("nonexistentcustomer")
    assert found_customer is not None
    assert nonexistentcustomer is None
    with pytest.raises(TypeError):
        customer_dao.find_by_username(1)


def test_delete(customer_dao):
    ResetDatabase().launch(True)
    with pytest.raises(TypeError):
        customer_dao.delete("not a customer, just a string")
    nonexistentcustomer = Customer(
        username="nonexistent",
        firstname="non",
        lastname="existent",
        password="pwd",
        salt="salt",
        account_type="Customer",
        address="no adress",
    )
    with pytest.raises(ValueError):
        customer_dao.delete(nonexistentcustomer)
    charliz = customer_dao.find_by_username("charliz")
    deletion = customer_dao.delete(charliz)
    assert deletion is True


if __name__ == "__main__":
    pytest.main()
    ResetDatabase().launch(True)
