from typing import Optional

import pytest

from src.Model.Customer import Customer
from src.Model.User import User
from src.Service.UserService import UserService


class MockUserRepo:
    def __init__(self, customer_repo, admin_repo, driver_repo):
        self.users = {}
        self.customer_repo = customer_repo
        self.admin_repo = admin_repo
        self.driver_repo = driver_repo

    def create_user(self, user: User) -> bool:
        self.users[user.username] = user

        if user.account_type == "Customer":
            self.customer_repo.create(user)
        elif user.account_type == "Administrator":
            self.admin_repo.create(user)
        elif user.account_type == "DeliveryDriver":
            self.driver_repo.create(user)
        return True

    def get_by_username(self, username: str) -> Optional[User]:
        return self.users.get(username)

    def update_user(self, username: str, firstname: str, lastname: str, password: str):
        if username in self.users:
            user = self.users[username]
            user.firstname = firstname
            user.lastname = lastname
            user.password = password
            self.users[username] = user

    def delete_user(self, user: User):
        if user and user.username in self.users:
            del self.users[user.username]


class MockAdminRepo:
    def __init__(self):
        self.admins = {}

    def create(self, admin):
        self.admins[admin.username] = admin


class MockDriverRepo:
    def __init__(self):
        self.drivers = {}

    def create(self, driver):
        self.drivers[driver.username] = driver


class MockCustomerRepo:
    def __init__(self):
        self.customers = {}

    def create(self, customer):
        self.customers[customer.username] = customer

    def delete(self, customer):
        if isinstance(customer, Customer) or hasattr(customer, "username"):
            key = customer.username
        else:
            key = customer
        self.customers.pop(key, None)

    def find_by_username(self, username):
        return self.customers.get(username)


admin_repo = MockAdminRepo()
driver_repo = MockDriverRepo()
customer_repo = MockCustomerRepo()
user_repo = MockUserRepo(customer_repo, admin_repo, driver_repo)

service = UserService(user_repo, admin_repo, driver_repo, customer_repo)


user_repo.create_user(
    User(
        username="janjak",
        firstname="Jean-Jacques",
        lastname="John",
        salt="sodium",
        password="hashed_pass",
        account_type="Customer",
    )
)


def test_create_user_success():
    user = service.create_user("janjon", "Jean", "John", "mdpsecure", account_type="Customer")
    assert user.username == "janjon"
    assert user_repo.get_by_username("janjon") is not None
    assert customer_repo.customers["janjon"].firstname == "Jean"


def test_create_user_existing_username():
    with pytest.raises(ValueError) as error_username:
        service.create_user("janjak", "Jeanette", "Johnny", "mdpsecure2", account_type="Customer")
    assert str(error_username.value) == "Username already taken."


def test_create_user_weak_password():
    with pytest.raises(Exception) as error_password:
        service.create_user("janjok", "Jeanne", "Johnas", "mdp", account_type="Customer")
    assert "Password length must be at least 8 characters" in str(error_password.value)


def test_create_user_admin_and_driver():
    service.create_user("adm1", "Alice", "Admin", "securePass1", account_type="Administrator")
    assert admin_repo.admins["adm1"].username == "adm1"

    service.create_user("driver1", "Bob", "Drive", "securePass2", account_type="DeliveryDriver")
    assert driver_repo.drivers["driver1"].username == "driver1"
    assert driver_repo.drivers["driver1"].vehicle == "driving"


def test_get_user():
    found = service.get_user("janjak")
    assert found.username == "janjak"
    assert found.firstname == "Jean-Jacques"
    assert service.get_user("unknown") is None


def test_username_exists():
    assert service.username_exists("janjak") is True
    assert service.username_exists("noexist") is False


def test_update_user(monkeypatch):
    user_repo.create_user(
        User(
            username="update_test",
            firstname="Old",
            lastname="Name",
            salt="salt",
            password="pass",
            account_type="Customer",
        )
    )

    service.update_user("update_test", firstname="New", lastname=None, password=None)
    updated = user_repo.get_by_username("update_test")
    assert updated.firstname == "New"
    assert updated.lastname == "Name"


def test_delete_user():
    user_repo.create_user(
        User(username="delete_me", firstname="Del", lastname="Me", salt="s", password="p", account_type="Customer")
    )
    assert user_repo.get_by_username("delete_me") is not None
    assert customer_repo.find_by_username("delete_me") is not None
    service.delete_user("delete_me")
    assert user_repo.get_by_username("delete_me") is None
    assert customer_repo.find_by_username("delete_me") is None
