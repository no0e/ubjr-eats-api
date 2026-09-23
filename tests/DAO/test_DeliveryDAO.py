import pytest

from src.DAO.DBConnector import DBConnector
from src.DAO.DeliveryDAO import DeliveryDAO
from src.Model.Delivery import Delivery
from src.Utils.reset_db import ResetDatabase


@pytest.fixture
def db_connector():
    db = DBConnector()
    yield db


@pytest.fixture
def delivery_dao(db_connector):
    return DeliveryDAO(db_connector, test=True)


def test_create(delivery_dao):
    ResetDatabase().launch(True)
    created_delivery = Delivery(
        id_order=[3, 4],
        stops=["13 Main St.", "4 Salty Spring Av."],
        is_accepted=False,
    )
    creation = delivery_dao.create(created_delivery)
    assert creation is True
    with pytest.raises(TypeError):
        delivery_dao.create(1)


def test_get_available_deliveries(delivery_dao):
    ResetDatabase().launch(True)
    available_deliveries = delivery_dao.get_available_deliveries()
    assert len(available_deliveries) == 1


def test_get_by_id(delivery_dao):
    ResetDatabase().launch(True)
    delivery = delivery_dao.get_by_id(1)
    assert delivery.username_delivery_driver == "ernesto"
    assert delivery.duration == 50
    assert delivery.id_orders == [1, 2]
    assert delivery.stops == ["13 Main St.", "4 Salty Spring Av."]
    assert delivery.is_accepted is True
    with pytest.raises(TypeError):
        delivery_dao.get_by_id("1")


def test_set_delivery_accepted(delivery_dao):
    id_delivery = 2
    username_delivery_driver = "ernesto1"
    update = delivery_dao.set_delivery_accepted(
        id_delivery=id_delivery,
        username_delivery_driver=username_delivery_driver,
    )
    assert update is None
    updated_delivery = delivery_dao.get_by_id(2)
    assert updated_delivery.is_accepted is True


def test_find_delivery_by_driver(delivery_dao):
    ResetDatabase().launch(True)
    deliveries = delivery_dao.find_delivery_by_driver("ernesto1", test=True)
    assert deliveries is not None
    for d in deliveries:
        assert d.username_delivery_driver == "ernesto1"
    assert delivery_dao.find_delivery_by_driver("unknown_user", test=True) is None

    def test_delete(order_dao):
        ResetDatabase().launch(True)
        delivery = Delivery(
            id_delivery=1,
            username_delivery_driver="ernesto",
            duration=50,
            id_orders=[1, 2],
            stops=["13 Main St.", "4 Salty Spring Av."],
            is_accepted=True,
        )
        assert delivery_dao.delete(delivery, test=True) is True
        assert delivery_dao.find_delivery_by_id(1, test=True) is None


if __name__ == "__main__":
    pytest.main()
    ResetDatabase().launch(True)
