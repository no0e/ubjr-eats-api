from typing import List, Optional

from src.Model.Item import Item

from .DBConnector import DBConnector


class ItemDAO:
    """
    Data Access Object (DAO) for interacting with the 'items' table in the database.
    Provides CRUD (Create, Read, Update, Delete) operations for Item objects.
    """

    def __init__(self, db_connector: DBConnector, test: bool = False):
        """
        Initialize the ItemDAO with a database connector.

        Parameters
        ----------
        db_connector : DBConnector
            Instance of DBConnector used to execute SQL queries.
        test : bool, optional
            If True, uses the test schema. Defaults to False.
        """
        self.db_connector = db_connector
        if test:
            self.schema = "project_test_database"
        else:
            self.schema = "project_database"

    def create_item(self, item: Item) -> bool:
        """
        Insert a new item into the database.

        Parameters
        ----------
        item : Item
            The Item object to insert.

        Returns
        -------
        bool
            True if insertion succeeded, False otherwise.
        """
        try:
            raw_item = self.db_connector.sql_query(
                """
                INSERT INTO """
                + self.schema
                + """.items (name_item, price, category, stock, exposed)
                VALUES (%(name_item)s, %(price)s, %(category)s, %(stock)s, %(exposed)s)
                RETURNING id_item;
                """,
                {
                    "name_item": item.name_item,
                    "price": item.price,
                    "category": item.category,
                    "stock": item.stock,
                    "exposed": item.exposed,
                },
                "one",
            )
            item.id_item = raw_item["id_item"]
            return True
        except Exception as e:
            print(f"[ItemDAO] Error creating item: {e}")
            raise e

    def update_item_exposed(self, id_item: int, exposed: bool) -> None:
        """
        Update the exposure status of an item in the database.

        Parameters
        ----------
        id_item : int
            The ID of the item to update.
        exposed : bool
            The new exposure status of the item.


        Returns
         -------
            None
        """
        query = (
            """
            UPDATE """
            + self.schema
            + """.items
            SET exposed = %s
            WHERE id_item = %s
            """
        )
        self.db_connector.sql_query(query, [exposed, id_item], "execute")

    def find_item(self, id_item: int) -> Optional[Item]:
        """
        Retrieve a single item by its ID.

        Parameters
        ----------
        id_item : int
            The ID of the item to find.

        Returns
        -------
        Optional[Item]
            An Item object if found, otherwise None.
        """
        raw_item = self.db_connector.sql_query(
            "SELECT * FROM " + self.schema + ".items WHERE id_item = %s;", [id_item], "one"
        )
        if raw_item is None:
            return None
        return Item(
            id_item=raw_item["id_item"],
            name_item=raw_item["name_item"],
            price=raw_item["price"],
            category=raw_item["category"],
            stock=raw_item["stock"],
            exposed=raw_item["exposed"],
        )

    def find_item_by_name(self, name_item: str) -> Optional[Item]:
        """
        Retrieve a single item by its name.

        Parameters
        ----------
        name_item : str
            The name of the item to find.

        Returns
        -------
        Optional[Item]
            An Item object if found, otherwise None.
        """
        raw_item = self.db_connector.sql_query(
            "SELECT * FROM " + self.schema + ".items WHERE name_item = %s;", [name_item], "one"
        )
        if raw_item is None:
            return None
        return Item(
            id_item=raw_item["id_item"],
            name_item=raw_item["name_item"],
            price=raw_item["price"],
            category=raw_item["category"],
            stock=raw_item["stock"],
            exposed=raw_item["exposed"],
        )

    def find_all_exposed_item(self) -> List[Item]:
        """
        Retrieve all items marked as exposed (available for customers).

        Returns
        -------
        List[Item]
            A list of Item objects that are exposed.
        """
        raw_items = self.db_connector.sql_query(
            "SELECT * FROM " + self.schema + ".items WHERE exposed = TRUE;", [], "all"
        )
        return [
            Item(
                id_item=row["id_item"],
                name_item=row["name_item"],
                price=row["price"],
                category=row["category"],
                stock=row["stock"],
                exposed=row["exposed"],
            )
            for row in raw_items
        ]

    def find_all_item(self) -> List[Item]:
        """
        Retrieve all items from the database.

        Returns
        -------
        List[Item]
            A list of all Item objects.
        """
        raw_items = self.db_connector.sql_query("SELECT * FROM " + self.schema + ".items", [], "all")
        return [
            Item(
                id_item=row["id_item"],
                name_item=row["name_item"],
                price=row["price"],
                category=row["category"],
                stock=row["stock"],
                exposed=row["exposed"],
            )
            for row in raw_items
        ]

    def update(self, item: Item) -> bool:
        """
        Update an existing item in the database.

        Parameters
        ----------
        item : Item
            The Item object containing updated data.

        Returns
        -------
        bool
            True if the update succeeded, False otherwise.
        """
        try:
            self.db_connector.sql_query(
                """
                UPDATE """
                + self.schema
                + """.items
                SET name_item = %(name_item)s,
                    price = %(price)s,
                    category = %(category)s,
                    stock = %(stock)s,
                    exposed = %(exposed)s
                WHERE id_item = %(id_item)s;
                """,
                {
                    "id_item": item.id_item,
                    "name_item": item.name_item,
                    "price": item.price,
                    "category": item.category,
                    "stock": item.stock,
                    "exposed": item.exposed,
                },
                "none",
            )
            return True
        except Exception as e:
            print(f"[ItemDAO] Error updating item: {e}")
            return False

    def delete(self, item: Item) -> bool:
        """
        Delete an item from the database.

        Parameters
        ----------
        item : Item
            The Item object to delete.

        Returns
        -------
        bool
            True if deletion succeeded, False otherwise.
        """
        try:
            self.db_connector.sql_query(
                "DELETE FROM " + self.schema + ".items WHERE id_item = %s;", [item.id_item], "none"
            )
            return True
        except Exception as e:
            print(f"[ItemDAO] Error deleting item: {e}")
            return False
