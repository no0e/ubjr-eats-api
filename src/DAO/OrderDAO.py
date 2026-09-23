import json
from typing import List, Optional

from src.Model.Order import Order

from .DBConnector import DBConnector


class OrderDAO:
    """
    Data Access Object (DAO) for interacting with the 'users' table in the database.
    Provides methods to retrieve and insert user data.
    Note : the attribute items is a dict.
    """

    db_connector: DBConnector

    def __init__(self, db_connector: DBConnector):
        self.db_connector = db_connector

    def create_order(self, order: Order, test: bool = False) -> bool:
        """
        Insert a new order into the database.

        Parameters
        ----------
        order : Order
            The Order object to insert.

        Returns
        -------
        bool
            True if insertion succeeded, False otherwise.
        """
        try:
            schema = "project_test_database" if test else "project_database"
            if not isinstance(order.items, dict):
                raise TypeError("Order.items must be a dictionary {item_name: quantity}.")

            for item_name, quantity in order.items.items():
                if not isinstance(item_name, str) or not isinstance(quantity, int):
                    raise TypeError("All item names must be strings and quantities integers.")
                if quantity <= 0:
                    raise ValueError("Quantities must be positive integers.")

            items_json = json.dumps(order.items)
            query = f"""
                INSERT INTO {schema}.orders
                    (username_customer, username_delivery_driver, address, items)
                VALUES
                    (%(username_customer)s, %(username_delivery_driver)s, %(address)s, %(items)s)
                RETURNING id_order;
            """

            result = self.db_connector.sql_query(
                query,
                {
                    "username_customer": order.username_customer,
                    "username_delivery_driver": order.username_delivery_driver,
                    "address": order.address,
                    "items": items_json,
                },
                return_type="one",
            )
            order.id_order = result["id_order"]
            return True

        except Exception as e:
            print(f"[OrderDAO] Error creating order: {e}")
            return False

    def find_order_by_id(self, id_order: int, test: bool = False) -> Optional[Order]:
        """
        Retrieve a single order by its ID.

        Parameters
        ----------
        id_order : int
            The ID of the order to find.

        Returns
        -------
        Optional[Order]
            An Order object if found, otherwise None.
        """
        schema = "project_test_database" if test else "project_database"
        raw_order = self.db_connector.sql_query(
            f"SELECT * FROM {schema}.orders WHERE id_order = %s;",
            [id_order],
            "one",
        )
        if raw_order is None:
            return None

        raw_items = raw_order.get("items") or {}
        items_dict = json.loads(raw_items) if isinstance(raw_items, str) else raw_items

        return Order(
            id_order=raw_order["id_order"],
            username_customer=raw_order["username_customer"],
            username_delivery_driver=raw_order["username_delivery_driver"],
            address=raw_order["address"],
            items=items_dict,
        )

    def find_order_by_user(self, username_customer: str, test: bool = False) -> Optional[List[Order]]:
        """
        Retrieve a single order by the username of its customer.

        Parameters
        ----------
        username_customer : str
            The username of the customer whose we want to find their orders.

        Returns
        -------
        Optional[Order]
            An Order object if found, otherwise None.
        """
        schema = "project_test_database" if test else "project_database"
        raw_orders = self.db_connector.sql_query(
            f"SELECT * FROM {schema}.orders WHERE username_customer = %s;",
            [username_customer],
            "all",
        )
        if not raw_orders:
            return None

        orders = []
        for raw_order in raw_orders:
            raw_items = raw_order.get("items") or {}
            items_dict = json.loads(raw_items) if isinstance(raw_items, str) else raw_items

            orders.append(
                Order(
                    id_order=raw_order["id_order"],
                    username_customer=raw_order["username_customer"],
                    username_delivery_driver=raw_order["username_delivery_driver"],
                    address=raw_order["address"],
                    items=items_dict,
                )
            )
        return orders

    def find_order_by_driver(self, username_delivery_driver: str, test: bool = False) -> Optional[List[Order]]:
        """
        Retrieve a single order by the username of its delivery driver.

        Parameters
        ----------
        username_delivery_driver : str
            The username of the delivery driver whose we want to find their orders.

        Returns
        -------
        Optional[Order]
            An Order object if found, otherwise None.
        """
        schema = "project_test_database" if test else "project_database"
        raw_orders = self.db_connector.sql_query(
            f"SELECT * FROM {schema}.orders WHERE username_delivery_driver = %s;",
            [username_delivery_driver],
            "all",
        )
        if not raw_orders:
            return None

        orders = []
        for raw_order in raw_orders:
            raw_items = raw_order.get("items") or {}
            items_dict = json.loads(raw_items) if isinstance(raw_items, str) else raw_items

            orders.append(
                Order(
                    id_order=raw_order["id_order"],
                    username_customer=raw_order["username_customer"],
                    username_delivery_driver=raw_order["username_delivery_driver"],
                    address=raw_order["address"],
                    items=items_dict,
                )
            )
        return orders

    def update(self, order: Order, test: bool = False) -> bool:
        """
        Update an existing order in the database.

        Parameters
        ----------
        order : Order
            The Order object containing updated data.

        Returns
        -------
        bool
            True if the update succeeded, False otherwise.
        """
        try:
            schema = "project_test_database" if test else "project_database"

            for item_name, quantity in order.items.items():
                if not isinstance(item_name, str) or not isinstance(quantity, int):
                    raise TypeError("All item names must be strings and quantities integers.")
                if quantity <= 0:
                    raise ValueError("Quantities must be positive integers.")

            items_json = json.dumps(order.items)
            self.db_connector.sql_query(
                f"""
                UPDATE {schema}.orders
                SET username_customer = %(username_customer)s,
                    username_delivery_driver = %(username_delivery_driver)s,
                    address = %(address)s,
                    items = %(items)s
                WHERE id_order = %(id_order)s;
                """,
                {
                    "id_order": order.id_order,
                    "username_customer": order.username_customer,
                    "username_delivery_driver": order.username_delivery_driver,
                    "address": order.address,
                    "items": items_json,
                },
                "none",
            )
            return True
        except Exception as e:
            print(f"[OrderDAO] Error updating order: {e}")
            return False

    def delete(self, order: Order, test: bool = False) -> bool:
        """
        Delete an order from the database.

        Parameters
        ----------
        order : Order
            The Order object to delete.

        Returns
        -------
        bool
            True if deletion succeeded, False otherwise.
        """
        try:
            schema = "project_test_database" if test else "project_database"
            self.db_connector.sql_query(
                f"DELETE FROM {schema}.orders WHERE id_order = %s;",
                [order.id_order],
                "none",
            )
            return True
        except Exception as e:
            print(f"[OrderDAO] Error deleting order: {e}")
            return False
