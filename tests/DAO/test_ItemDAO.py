import pytest

from src.DAO.DBConnector import DBConnector
from src.DAO.ItemDAO import ItemDAO
from src.Model.Item import Item
from src.Utils.reset_db import ResetDatabase


@pytest.fixture
def db_connector():
    db = DBConnector()
    yield db


@pytest.fixture
def item_dao(db_connector):
    return ItemDAO(db_connector, test=True)


def test_create_item(item_dao):
    ResetDatabase.launch(True)
    item = Item(id_item=None, name_item="galette test", price=4, category="main dish", stock=1000, exposed=False)
    result = item_dao.create_item(item)
    assert result is True


def test_delete_item(item_dao):
    ResetDatabase().launch(True)
    deletion = item_dao.delete(item_dao.find_item_by_name("galette saucisse"))
    assert deletion is True
    assert item_dao.find_item_by_name("galette saucisse") is None


def test_update_item_exposed(item_dao):
    ResetDatabase().launch(True)
    # The item 1 has exposed=True
    item_dao.update_item_exposed(1, False)
    # The item 2 already has exposed=False
    item_dao.update_item_exposed(2, False)
    assert item_dao.find_item(1).exposed is False
    assert item_dao.find_item(2).exposed is False
    item_dao.update_item_exposed(1, True)


def test_find_item(item_dao):
    ResetDatabase().launch(True)
    item = item_dao.find_item(1)
    missing_item = item_dao.find_item(56)  # non existent id
    assert item.id_item == 1
    assert item.name_item == "galette saucisse"
    assert item.price == 320
    assert item.category == "main dish"
    assert item.stock == 102
    assert item.exposed is True
    assert missing_item is None


def test_find_item_by_name(item_dao):
    ResetDatabase().launch(True)
    item = item_dao.find_item_by_name("galette saucisse")
    missing_item = item_dao.find_item_by_name("disgusting galette")
    assert item.id_item == 1
    assert item.name_item == "galette saucisse"
    assert item.price == 320
    assert item.category == "main dish"
    assert item.stock == 102
    assert item.exposed is True
    assert missing_item is None


def test_all_exposed_item(item_dao):
    ResetDatabase().launch(True)
    exposed_items = item_dao.find_all_exposed_item()
    assert isinstance(exposed_items, list)
    assert len(exposed_items) == 2


def test_find_all_item(item_dao):
    ResetDatabase().launch(True)
    all_item = item_dao.find_all_item()
    assert isinstance(all_item, list)
    assert len(all_item) == 3


def test_update_item(item_dao):
    ResetDatabase().launch(True)
    future_updated_item = Item(
        id_item=1, name_item="galette saucisse update", price=420, category="starter", stock=100, exposed=False
    )
    upated_item = item_dao.update(future_updated_item)
    assert upated_item is True


if __name__ == "__main__":
    pytest.main()
    ResetDatabase().launch(True)
