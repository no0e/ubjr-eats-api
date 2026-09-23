import pytest

from src.DAO.DBConnector import DBConnector
from src.DAO.OrderDAO import OrderDAO
from src.Model.Order import Order
from src.Utils.reset_db import ResetDatabase


@pytest.fixture
def db_connector():
    db = DBConnector()
    yield db


@pytest.fixture
def order_dao(db_connector):
    return OrderDAO(db_connector)


def test_create_order(order_dao):
    ResetDatabase().launch(True)
    order = Order(
        username_customer="bobbia",
        username_delivery_driver="ernesto",
        address="123 Test St",
        items={"galette saucisse": 2, "cola": 1},
    )
    assert order_dao.create_order(order, test=True)


def test_find_order_by_id(order_dao):
    ResetDatabase().launch(True)
    order = order_dao.find_order_by_id(1, test=True)
    assert order is not None
    assert order.id_order == 1
    assert order.username_customer == "bobbia"
    assert order.items == {"galette saucisse": 2, "cola": 1}


def test_find_order_by_user(order_dao):
    ResetDatabase().launch(True)
    orders = order_dao.find_order_by_user("bobbia", test=True)
    assert orders is not None
    for o in orders:
        assert o.username_customer == "bobbia"
        assert isinstance(o.items, dict)
    assert order_dao.find_order_by_user("unknown_user", test=True) is None


def test_find_order_by_driver(order_dao):
    ResetDatabase().launch(True)
    orders = order_dao.find_order_by_driver("ernesto1", test=True)
    assert orders is not None
    for o in orders:
        assert o.username_delivery_driver == "ernesto1"
        assert isinstance(o.items, dict)
    assert order_dao.find_order_by_driver("unknown_user", test=True) is None


def test_update(order_dao):
    ResetDatabase().launch(True)
    order = Order(
        id_order=1,
        username_customer="bobbia",
        username_delivery_driver="ernesto1",
        address="51 Rue Blaise Pascal",
        items={"galette saucisse": 1, "vegetarian galette": 3},
    )
    assert order_dao.update(order, test=True)
    updated_order = order_dao.find_order_by_id(1, test=True)
    assert updated_order.items == {"galette saucisse": 1, "vegetarian galette": 3}
    assert updated_order.address == "51 Rue Blaise Pascal"


def test_delete(order_dao):
    ResetDatabase().launch(True)
    order = Order(
        id_order=1,
        username_customer="bobbia",
        username_delivery_driver="ernesto1",
        address="123 Test St",
        items={"galette saucisse": 2},
    )
    assert order_dao.delete(order, test=True) is True
    assert order_dao.find_order_by_id(1, test=True) is None
