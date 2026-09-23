from typing import Optional
from unittest.mock import patch

from src.Model.Administrator import Administrator
from src.Model.User import User
from src.Service.AdministratorService import AdministratorService


class MockAdminRepo:
    def __init__(self):
        self.admins = {}

    def create_admin(self, admin: Administrator) -> bool:
        self.admins[admin.username] = admin
        return True


class MockUserRepo:
    def __init__(self):
        self.users = {}

    def create_user(self, user):
        self.users[user.username] = user

    def get_by_username(self, username: str):
        return self.users.get(username)

    def get_user(self, username: str):
        return self.get_by_username(username)

    def delete_user(self, user):
        if user.username in self.users:
            del self.users[user.username]

    def update_user(
        self,
        username: str,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        password: Optional[str] = None,
    ):
        user = self.get_by_username(username)
        if user is None:
            return None
        if firstname is not None:
            user.firstname = firstname
        if lastname is not None:
            user.lastname = lastname
        if password is not None:
            user.password = password
        return user


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


user_repo = MockUserRepo()
admin_repo = MockAdminRepo()
driver_repo = MockDriverRepo()
customer_repo = MockCustomerRepo()

service = AdministratorService(user_repo, admin_repo, driver_repo, customer_repo)


admin_repo.create_admin(
    Administrator(
        username="janjak",
        firstname="Jean-Jacques",
        lastname="John",
        salt="sodium",
        password="hashed_pass",
        account_type="Customer",
    )
)

user_repo.create_user(
    User(
        username="Pat", firstname="Patric", lastname="Pic", password="mdpsecured", salt="salt", account_type="Customer"
    )
)


def test_create_user_success():
    user = service.create_user("janjon", "Jean", "John", "mdpsecure", account_type="Customer")
    assert user.username == "janjon"
    assert user_repo.get_by_username("janjon") is not None
    assert customer_repo.customers["janjon"].firstname == "Jean"


def test_get_user_success():
    administrator = service.get_user("Pat")
    assert administrator.username == "Pat"
    assert administrator.firstname == "Patric"
    assert administrator.lastname == "Pic"
    assert administrator.password == "mdpsecured"
    assert administrator.salt == "salt"
    assert administrator.account_type == "Customer"


def test_username_exists_success():
    exist = service.username_exists("Pat")
    assert exist is True


def test_username_exists_failed():
    exist = service.username_exists("Jules")
    assert exist is False


def test_update_user_success():
    user_repo.create_user(
        User(
            username="Maelys",
            firstname="Mael",
            lastname="Lys",
            password="mdpsecure",
            salt="salt",
            account_type="Customer",
        )
    )
    new_name_user = service.update_user("Maelys", firstname="Miss")
    assert new_name_user.firstname == "Miss"
    new_lastname_user = service.update_user("Maelys", lastname="Lis")
    assert new_lastname_user.lastname == "Lis"

    with (
        patch("src.Service.AdministratorService.check_password_strength") as mock_check_password_strength,
        patch("src.Service.AdministratorService.create_salt") as mock_create_salt,
        patch("src.Service.AdministratorService.hash_password") as mock_hash_password,
    ):
        mock_create_salt.return_value = "random_salt"
        mock_hash_password.return_value = "new_hashed_password"

        updated_user = service.update_user(username="Maelys", password="newpassword")
        mock_check_password_strength.assert_called_once_with("newpassword")
        mock_create_salt.assert_called_once()
        mock_hash_password.assert_called_once_with("newpassword", "random_salt")
        assert updated_user.password == "new_hashed_password"
