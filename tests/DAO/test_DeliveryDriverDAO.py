
import pytest

from src.DAO.DBConnector import DBConnector
from src.DAO.DeliveryDriverDAO import DeliveryDriverDAO
from src.DAO.UserDAO import UserDAO
from src.Model.DeliveryDriver import DeliveryDriver
from src.Utils.reset_db import ResetDatabase


@pytest.fixture
def db_connector():
    db = DBConnector()
    yield db


@pytest.fixture
def user_dao(db_connector):
    return UserDAO(db_connector, test=True)


@pytest.fixture
def delivery_driver_dao(db_connector):
    return DeliveryDriverDAO(db_connector, test=True)


def test_create(delivery_driver_dao, user_dao):
    ResetDatabase().launch(True)
    user_to_be_driver = user_dao.get_by_username("futuredeliverydriver")
    driver_to_create = DeliveryDriver(
        username=user_to_be_driver.username,
        firstname=user_to_be_driver.firstname,
        lastname=user_to_be_driver.lastname,
        account_type=user_to_be_driver.account_type,
        password=user_to_be_driver.password,
        salt=user_to_be_driver.salt,
        vehicle="walking",
        is_available=True,
    )
    assert delivery_driver_dao.create(driver_to_create)


def test_create_errors(delivery_driver_dao, user_dao):
    ResetDatabase().launch(True)
    nonexistent_driver = None
    with pytest.raises(TypeError):
        delivery_driver_dao.create(nonexistent_driver)


def test_find_by_username(delivery_driver_dao):
    ResetDatabase().launch(True)
    found_driver = delivery_driver_dao.find_by_username("ernesto")
    assert found_driver is not None
    assert found_driver.username == "ernesto"
    assert found_driver.vehicle == "driving"
    assert not found_driver.is_available


def test_update_delivery_driver(delivery_driver_dao):
    ResetDatabase().launch(True)
    to_be_updated_driver = delivery_driver_dao.find_by_username("ernesto1")
    updated_driver = delivery_driver_dao.update_delivery_driver(to_be_updated_driver.username, vehicle="driving")
    missing_driver = None
    no_updated_driver = delivery_driver_dao.update_delivery_driver(missing_driver)
    assert updated_driver
    assert not no_updated_driver


def test_delete(delivery_driver_dao):
    ResetDatabase().launch(True)
    driver_to_delete = delivery_driver_dao.find_by_username("ernesto")
    deletion = delivery_driver_dao.delete(driver_to_delete)
    missing_driver = None
    false_deletion = delivery_driver_dao.delete(missing_driver)
    assert deletion
    assert not false_deletion


def test_drivers_available(delivery_driver_dao):
    ResetDatabase().launch(True)
    available_drivers = delivery_driver_dao.drivers_available()
    assert isinstance(available_drivers, list)
    assert len(available_drivers) == 1
    assert available_drivers[0].username == "ernesto1"


if __name__ == "__main__":
    pytest.main()
    ResetDatabase().launch(True)
