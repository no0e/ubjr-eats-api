from typing import Optional

from src.DAO.ItemDAO import ItemDAO
from src.Model.Item import Item


class ItemService:
    def __init__(self, item_dao: ItemDAO):
        self.item_dao = item_dao

    def view_storage(self) -> dict:
        """Function that shows all the items and their quantity even if they are not exposed

        Returns
        -------
        dict
            the items associated with their quantity stored.
        """
        storage = {}
        items = self.item_dao.find_all_item()
        for item in items:
            storage[item.name_item] = item.stock
        return storage

    def create_item(self, name_item: str, price: int, category: str, stock: int, exposed=False) -> Item:
        """Function that creates a new item.

        Parameters
        ----------
        name_item: str
            name of the item
        price: int
            price of the item in cents
        category: str
            category of the item
        stock: int
            quantity of the item
        exposed: bool
            if the item is ready to be sold, by default False

        Returns
        -------
        Item
            the item that has just been created.
        """

        if price < 0:
            raise ValueError("The item price should not be negative.")
        if category not in ("starter", "main course", "dessert", "drink"):
            raise TypeError("The category is not registered. Must be one of: starter, main course, dessert, drink.")
        if stock < 0:
            raise ValueError("Stock can't be negative.")

        all_exposed = self.item_dao.find_all_item()
        if any(item.name_item.lower() == name_item.lower() for item in all_exposed):
            raise TypeError("The item name is already attributed.")

        new_item = Item(name_item=name_item, price=price, category=category, stock=stock, exposed=exposed)

        success = self.item_dao.create_item(new_item)
        if not success:
            raise ValueError("Failed to create item in the database.")
        return new_item

    def delete_item(self, name_delete) -> str:
        """Function that deletes an item from the database.

        Parameters
        ----------
        name_delete: str
            name of the item to delete

        Returns
        -------
        str
            a message that confirms the item deletion.
        """
        items = self.item_dao.find_all_item()
        for item in items:
            if item.name_item.lower() == name_delete.lower():
                success = self.item_dao.delete(item)
                if not success:
                    raise ValueError("Failed to delete the item in the database.")
                return f"The item {name_delete} is deleted from the database"
        raise TypeError("The item to delete doesn't exist.")

    def update(
        self,
        name_item: str,
        new_name: Optional[str] = None,
        price: Optional[int] = None,
        category: Optional[str] = None,
        stock: Optional[int] = None,
        exposed: Optional[bool] = None,
    ):
        """Function that deletes an item from the database.

        Parameters
        ----------
        name_item: str
            name of the item to modify
        new_name: str
            new value for its name, by default None
        price: int
            new value for its price, by default None
        category: str
            new value for its category, by default None
        stock: int
            new value for its quantity, by default None
        exposed: bool
            availability of the item, by default None

        Returns
        -------
        Item
            the item after modification.
        """
        item = self.item_dao.find_item_by_name(name_item)
        if item is None:
            raise TypeError("This item does not exist.")
        items = self.item_dao.find_all_item()
        if new_name is not None:
            if any(item.name_item.lower() == new_name.lower() for item in items):
                raise TypeError("The new name is already attributed.")
            item.name_item = new_name
        if price is not None:
            if price < 0:
                raise ValueError("The item price should not be negative.")
            item.price = int(price * 100)
        if category is not None:
            if category not in ("starter", "main course", "dessert", "drink"):
                raise TypeError("The category is not registered. Must be one of: starter, main course, dessert, drink.")
            item.category = category
        if stock is not None:
            if stock < 0:
                raise ValueError("Stock can't be negative.")
            item.stock = stock
        if exposed is not None:
            item.exposed = exposed
        self.item_dao.update(item)
        return item
