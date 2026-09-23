from typing import Optional

import pytest

from src.Model.Customer import Customer
from src.Model.Item import Item
from src.Model.Order import Order
from src.Service.CustomerService import CustomerService
from src.Service.GoogleMapService import GoogleMap

google_service = GoogleMap()


class MockCustomerRepo:
    def __init__(self):
        self.customers = {}

    def find_by_username(self, username: str) -> Optional[Customer]:
        return self.customers.get(username)


class MockItemRepo:
    def __init__(self):
        self.items = {}
        self.auto_id = 1

    def create_item(self, item: Item):
        item.id_item = self.auto_id
        self.auto_id += 1
        self.items[item.id_item] = item
        return True

    def find_all_exposed_item(self):
        return [item for item in self.items.values() if item.exposed]

    def find_all_item(self):
        return list(self.items.values())

    def find_item(self, id_item: int):
        return self.items.get(id_item)

    def find_item_by_name(self, name_item: str):
        for item in self.items.values():
            if item.name_item.lower() == name_item.lower():
                return item
        return None

    def update(self, item: Item):
        if item.id_item not in self.items:
            return False

        self.items[item.id_item] = item
        return True


class MockOrderRepo:
    def __init__(self):
        self.orders = {}
        self.auto_id = 1

    def create_order(self, order):
        order.id_order = self.auto_id
        self.auto_id += 1

        if order.username_customer not in self.orders:
            self.orders[order.username_customer] = []

        self.orders[order.username_customer].append(order)
        return True

    def find_order_by_user(self, username_customer):
        return self.orders.get(username_customer, [])


class MockDeliveryService:
    def __init__(self):
        self.created_deliveries = []

    def create(self, id_order, stops):
        return True


class MockDeliveryDAO:
    pass


deliverydao = MockDeliveryDAO()


@pytest.fixture
def item_repo():
    repo = MockItemRepo()

    repo.create_item(Item(name_item="galette saucisse", price=320, category="main course", stock=102, exposed=True))
    repo.create_item(Item(name_item="vegetarian galette", price=300, category="main dish", stock=30, exposed=False))
    repo.create_item(Item(name_item="cola", price=200, category="drink", stock=501, exposed=True))

    return repo


@pytest.fixture
def customer_repo():
    repo = MockCustomerRepo()

    repo.customers = {
        "bobbia": Customer(
            username="bobbia",
            firstname="Bob",
            lastname="Bia",
            password="tomato1111",
            salt="salt",
            account_type="Customer",
            address="13 Main St.",
        ),
        "charliz": Customer(
            username="charliz",
            firstname="Charles",
            lastname="Chic",
            password="chachacha",
            salt="saltysalt",
            account_type="Customer",
            address="4 Salty Spring Av.",
        ),
        "drdavid": Customer(
            username="drdavid",
            firstname="David",
            lastname="Douze",
            password="!pwd!mypwd",
            salt="pepper",
            account_type="Customer",
            address="Flat 5, Beverly Hills",
        ),
    }

    return repo


@pytest.fixture
def order_repo():
    repo = MockOrderRepo()

    repo.create_order(
        Order(
            id_order=None,
            username_customer="bobbia",
            username_delivery_driver="ernesto1",
            address="13 Main St.",
            items={"galette saucisse": 2, "cola": 1},
        )
    )
    repo.create_order(
        Order(
            id_order=None,
            username_customer="bobbia",
            username_delivery_driver="ernesto",
            address="13 Main St.",
            items={"galette saucisse": 39},
        )
    )
    repo.create_order(
        Order(
            id_order=None,
            username_customer="charliz",
            username_delivery_driver="ernesto1",
            address="4 Salty Spring Av.",
            items={"galette saucisse": 39, "cola": 2},
        )
    )

    return repo


@pytest.fixture
def delivery_service():
    return MockDeliveryService()


@pytest.fixture
def delivery_dao():
    return MockDeliveryDAO()


@pytest.fixture
def customer_service(item_repo, customer_repo, order_repo, delivery_dao, delivery_service):
    return CustomerService(item_repo, delivery_dao, customer_repo, order_repo, delivery_dao, delivery_service)


def test_get_customer_success(customer_service):
    customer = customer_service.get_customer("bobbia")
    assert customer.username == "bobbia"
    assert customer.firstname == "Bob"
    assert customer.lastname == "Bia"
    assert customer.password == "tomato1111"
    assert customer.salt == "salt"
    assert customer.account_type == "Customer"
    assert customer.address == "13 Main St."


def test_view_menu_success(customer_service):
    menu = customer_service.view_menu()
    assert menu == [
        {
            "name_item": "galette saucisse",
            "price": 3.2,
            "category": "main course",
            "stock": 102,
        },
        {
            "name_item": "cola",
            "price": 2.0,
            "category": "drink",
            "stock": 501,
        },
    ]


def test_add_item_cart_success(customer_service):
    cart_old = {}
    cart = customer_service.add_item_cart("bobbia", cart_old, ["galette saucisse", "cola"], [3, 5])

    assert cart == {"galette saucisse": 3, "cola": 5}


def test_add_item_cart_failed(customer_service):
    with pytest.raises(TypeError) as error_name:
        cart_old = {}
        customer_service.add_item_cart("bobbia", cart_old, ["galette", "cola"], [3, 5])
    assert str(error_name.value) == "Item 'galette' not found or not available."
    with pytest.raises(ValueError) as error_quantity:
        cart_old = {}
        customer_service.add_item_cart("bobbia", cart_old, ["galette saucisse", "cola"], [120, 5])
    assert str(error_quantity.value) == "The quantity requested for 'galette saucisse' exceeds available stock."
    with pytest.raises(TypeError) as error_twice:
        cart_old = {"galette saucisse": 3, "cola": 5}
        customer_service.add_item_cart("bobbia", cart_old, ["galette saucisse"], [3])
    assert str(error_twice.value) == "The item 'galette saucisse' is already in the cart."


def test_delete_item_success(customer_service):
    cart = {"galette saucisse": 3, "cola": 5}
    cart_new = customer_service.delete_item(cart, "galette saucisse")
    assert cart_new == {"cola": 5}


def test_delete_item_failed(customer_service):
    with pytest.raises(TypeError) as error_name:
        cart_old = {"cola": 5}
        customer_service.delete_item(cart_old, "galette saucisse")
    assert str(error_name.value) == "galette saucisse is not in the cart"
    with pytest.raises(TypeError) as error_name2:
        cart_old = {"cola": 5}
        customer_service.delete_item(cart_old, "sausage")
    assert str(error_name2.value) == "sausage is not in the cart"


def test_validate_cart_success(customer_service):
    cart = {"galette saucisse": 3, "cola": 5}
    order = customer_service.validate_cart(cart, "bobbia", "yes")
    assert order.id_order == 4
    assert order.username_customer == "bobbia"
    assert order.username_delivery_driver is None
    assert order.address == "13 Main St."
    assert order.items == {"galette saucisse": 3, "cola": 5}


def test_validate_cart_failed(customer_service):
    with pytest.raises(TypeError) as error_validate:
        cart = {"galette saucisse": 3, "cola": 5}
        customer_service.validate_cart(cart, "bobbia", "none")
    assert str(error_validate.value) == "If you want to validate your cart you must enter: yes"


def test_view_order_success(customer_service):
    order = customer_service.view_order("charliz")
    assert order.id_order == 3
    assert order.username_customer == "charliz"
    assert order.username_delivery_driver == "ernesto1"
    assert order.address == "4 Salty Spring Av."
    assert order.items == {"galette saucisse": 39, "cola": 2}


def test_view_order_failed(customer_service):
    with pytest.raises(ValueError) as error_username:
        customer_service.view_order("drdavid")
    assert str(error_username.value) == "No orders found for user drdavid"


def test_view_cart_success(customer_service):
    cart = {"galette saucisse": 3, "cola": 5}
    cart_new = customer_service.view_cart(cart)
    assert cart_new == {"cart": {"galette saucisse": 3, "cola": 5}, "price": 19.6}
