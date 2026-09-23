from typing import List, Optional

from src.DAO.OrderDAO import OrderDAO
from src.Model.Delivery import Delivery

from .DBConnector import DBConnector

db_connector = DBConnector()
order_dao = OrderDAO(db_connector)


class DeliveryDAO:
    """
    Data Access Object (DAO) for interacting with the 'deliveries' table in the database.
    Provides methods to retrieve and insert user data.
    """

    def __init__(self, db_connector: DBConnector, test: bool = False):
        self.db = db_connector
        if test:
            self.schema = "project_test_database"
        else:
            self.schema = "project_database"

    def create(self, delivery: Delivery) -> bool:
        """
        Function that create an instance of delivery in the deliveries database.

        Parameters
        ----------
        delivery : Delivery
            Model of Delivery which will be created


        Returns
        -------
        boolean
            Returns True if the delivery has been created, False otherwise.
        """
        if not isinstance(delivery, Delivery):
            raise TypeError(f"The type of {delivery} should be Delivery.")
        id_orders = delivery.id_orders
        stops = delivery.stops
        query = (
            """
            INSERT INTO """
            + self.schema
            + """.deliveries
            (username_delivery_driver, duration, id_orders, stops, is_accepted)
            VALUES ( %(username_delivery_driver)s, %(duration)s, %(id_orders)s, %(stops)s, %(is_accepted)s)
            RETURNING id_delivery;
        """
        )
        try:
            id_delivery = self.db.sql_query(
                query,
                {
                    "username_delivery_driver": delivery.username_delivery_driver,
                    "duration": delivery.duration,
                    "id_orders": id_orders,
                    "stops": stops,
                    "is_accepted": delivery.is_accepted,
                },
                return_type="one",
            )["id_delivery"]
            delivery.id_delivery = id_delivery
            return True
        except Exception as e:
            print(f"[DeliveryDAO] Error creating delivery: {e}")
            return False

    def get_available_deliveries(self) -> List[Delivery]:
        """
        Function that shows all available deliveries.

        Returns
        -------
        List[Delivery]
            List of all available deliveries
        """
        query = "SELECT * FROM " + self.schema + ".deliveries WHERE is_accepted = FALSE;"
        rows = self.db.sql_query(query, return_type="all") or []
        return [Delivery(**r) for r in rows]

    def get_by_id(self, id_delivery: int) -> Delivery | None:
        """
        Function that find a delivery by their id.

        Parameters
        ----------
        id_delivery : str
            Id of the delivery we want to find


        Returns
        -------
        Delivery | None
            Returns a Delivery if found, None otherwise
        """
        if not isinstance(id_delivery, int):
            raise TypeError(f"Your id_delivery is {id_delivery} but should be int.")
        query = "SELECT * FROM " + self.schema + ".deliveries WHERE id_delivery = %(id_delivery)s"
        row = self.db.sql_query(query, {"id_delivery": id_delivery}, return_type="one")
        if not row:
            raise ValueError(f"Delivery of id {id_delivery} does not exist.")
        stops_raw = row.get("stops", [])
        if isinstance(stops_raw, str):
            stops = stops_raw.strip("{}").split(",")
        elif isinstance(stops_raw, list):
            stops = stops_raw
        else:
            stops = []
        id_orders_raw = row["id_orders"]
        if isinstance(id_orders_raw, str):
            id_orders = [int(x) for x in id_orders_raw.strip("{}").split(",") if x]
        elif isinstance(id_orders_raw, list):
            id_orders = id_orders_raw
        else:
            id_orders = []
        delivery = Delivery(
            id_delivery=row["id_delivery"],
            username_delivery_driver=row["username_delivery_driver"],
            duration=row["duration"],
            id_orders=id_orders,
            stops=stops,
            is_accepted=row["is_accepted"],
        )
        return delivery if row else None

    def set_delivery_accepted(self, id_delivery: int, username_delivery_driver: str):
        """Mark a delivery as accepted and assign a delivery driver to both the delivery and its associated order.

        Updates the deliveries table to set `is_accepted` to `TRUE` and assigns the delivery driver's username.
        Also updates the orders table to assign the same delivery driver to the most recent order
        associated with the delivery.

        Parameters
        ----------
        id_delivery : int
            The unique identifier of the delivery to be accepted.
        username_delivery_driver : str
            The username of the delivery driver assigned to the delivery.

        Returns
        -------
        None
        """
        query = (
            """
            UPDATE """
            + self.schema
            + """.deliveries
            SET is_accepted = TRUE, username_delivery_driver = %(username_delivery_driver)s
            WHERE id_delivery = %(id_delivery)s AND is_accepted = FALSE
        """
        )
        self.db.sql_query(
            query,
            {"id_delivery": id_delivery, "username_delivery_driver": username_delivery_driver},
        )
        delivery = self.get_by_id(id_delivery)
        if not delivery or not delivery.id_orders:
            raise ValueError("Delivery or orders not found")
        id_order = delivery.id_orders[-1]
        query = (
            """
            UPDATE """
            + self.schema
            + """.orders
            SET username_delivery_driver = %(username_delivery_driver)s
            WHERE id_order = %(id_order)s
        """
        )
        self.db.sql_query(query, {"id_order": id_order, "username_delivery_driver": username_delivery_driver})

    def find_delivery_by_driver(self, username_delivery_driver: str, test: bool = False) -> Optional[List[Delivery]]:
        """
        Retrieve a single delivery by the username of its delivery driver.

        Parameters
        ----------
        username_delivery_driver : str
            The username of the delivery driver whose we want to find their deliveries.

        Returns
        -------
        Optional[List[Delivery]]
            An Delivery object if found, otherwise None.
        """
        schema = "project_test_database" if test else "project_database"
        raw_deliveries = self.db.sql_query(
            f"SELECT * FROM {schema}.deliveries WHERE username_delivery_driver = %s;",
            [username_delivery_driver],
            "all",
        )
        if not raw_deliveries:
            return None

        deliveries = [
            Delivery(
                id_order=d["id_delivery"],
                username_delivery_driver=d["username_delivery_driver"],
                duration=d["duration"],
                id_orders=d["id_orders"],
                stops=d["stops"],
                is_accepted=d["is_accepted"],
            )
            for d in raw_deliveries
        ]
        return deliveries

    def delete(self, delivery: Delivery, test: bool = False) -> bool:
        """
        Delete a delivery from the database.

        Parameters
        ----------
        delivery : Delivery
            The Delivery object to delete.

        Returns
        -------
        bool
            True if deletion succeeded, False otherwise.
        """
        try:
            schema = "project_test_database" if test else "project_database"
            self.db.sql_query(
                f"DELETE FROM {schema}.deliveries WHERE id_delivery = %s;",
                [delivery.id_delivery],
                "none",
            )
            return True
        except Exception as e:
            print(f"[OrderDAO] Error deleting order: {e}")
            return False
