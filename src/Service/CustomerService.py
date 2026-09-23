from typing import List, Literal, Optional

from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.DeliveryDAO import DeliveryDAO
from src.DAO.DeliveryDriverDAO import DeliveryDriverDAO
from src.DAO.ItemDAO import ItemDAO
from src.DAO.OrderDAO import OrderDAO
from src.Model.Customer import Customer
from src.Model.Order import Order
from src.Service.DeliveryService import DeliveryService
from src.Service.GoogleMapService import GoogleMap

google_service = GoogleMap()


class CustomerService:
    def __init__(
        self,
        item_dao: ItemDAO = None,
        deliverydriver_dao: DeliveryDriverDAO = None,
        customer_dao: CustomerDAO = None,
        order_dao: OrderDAO = None,
        delivery_dao: DeliveryDAO = None,
        delivery_service: DeliveryService = None,
    ):
        db = DBConnector()
        self.item_dao = item_dao or ItemDAO(db)
        self.deliverydriver_dao = deliverydriver_dao or DeliveryDriverDAO(db)
        self.customer_dao = customer_dao or CustomerDAO(db)
        self.order_dao = order_dao or OrderDAO(db)
        self.delivery_dao = delivery_dao or DeliveryDAO(db)
        self.delivery_service = delivery_service or DeliveryService(
            delivery_repo=self.delivery_dao, google_maps=google_service
        )
        self.active_carts = {}

    def get_customer(self, username: str) -> Customer | None:
        """Function that gives a customer by the username given.

        Parameters
        ----------
        username : str
            customer's username to search

        Returns
        -------
        Customer
            Instance of the customer with the assiociated username given.
        """
        return self.customer_dao.find_by_username(username)

    def view_menu(self) -> list[dict]:
        """Function that returns all the items available

        Returns
        -------
        list[dict]
            a list of all the exposed items.
        """
        items = self.item_dao.find_all_exposed_item()

        menu = [
            {
                "name_item": item.name_item,
                "price": float(round(item.price / 100, 2)),
                "category": item.category,
                "stock": item.stock,
            }
            for item in items
        ]

        return menu

    def get_cart_for_user(self, username: str) -> dict:
        """Function that returns the user's cart.

        Parameters
        ----------
        username: str
            username of the active customer

        Returns
        -------
        dict
            Returns the cart of the active customer.
        """
        return self.active_carts.get(username)

    def add_item_cart(self, username: str, cart: dict, name_items: List[str], quantities: List[int]) -> dict:
        """Function that adds the quantity of the item choose into the cart

        Parameters
        ----------
        username: str
            username of the customer we want to manage the cart
        name_item : str
             the name of the item wanted
        number_item : int
            the quantoty wanted

        Returns
        -------
        dict
            Returns the cart after modification.
        """
        items = self.item_dao.find_all_exposed_item()
        items_dict = {item.name_item.lower(): item for item in items}
        for name_item, quantity in zip(name_items, quantities, strict=True):
            name_item = name_item.lower()
            if name_item not in items_dict:
                raise TypeError(f"Item '{name_item}' not found or not available.")

            item = items_dict[name_item]

            if quantity > item.stock:
                raise ValueError(f"The quantity requested for '{name_item}' exceeds available stock.")

            if item.name_item in cart:
                raise TypeError(f"The item '{name_item}' is already in the cart.")
            else:
                cart[item.name_item] = quantity

        return cart

    def modify_cart(self, cart: dict, name_item: str, new_number_item: int) -> dict:
        """Function that modifies the cart by changing the quantity wanted of an item

        Parameters
        ----------
        cart: dict
            the cart of the user
        name_item: str
            name of the item that the user want to update
        new_number_item: int
            the new quantity wanted

        Returns
        -------
        dict
            Returns the cart after modification.
        """
        all_item_available = self.item_dao.find_all_exposed_item()
        for item in all_item_available:
            if item.name_item.lower() == name_item.lower():
                if new_number_item > item.stock:
                    raise ValueError("The quantity requested exceeds the stock available.")
                if name_item.lower() not in [key.lower() for key in cart.keys()]:
                    raise TypeError(f"{name_item} is not in the cart")
                if new_number_item == 0:
                    del cart[item.name_item]
                else:
                    cart[item.name_item] = new_number_item
                return cart

        raise ValueError(f"Item '{name_item}' not found in the list of items available.")

    def delete_item(self, cart: dict, name_item: str) -> dict:
        """Function that removes an item from the cart

        Parameters
        ----------
        cart: dict
            the current user's cart
        name_item: str
            name of the item that the user wants to delete

        Returns
        -------
        dict
            Returns the cart after modification.
        """
        all_item_available = self.item_dao.find_all_exposed_item()
        for item in all_item_available:
            if item.name_item.lower() == name_item.lower():
                if item.name_item not in cart:
                    raise TypeError(f"{name_item} is not in the cart")
                del cart[item.name_item]
                return cart
        raise TypeError(f"{name_item} is not in the cart")

    def validate_cart(
        self, cart: dict, username_customer: str, validate: Literal["yes", "no"], address: Optional[str] = None
    ) -> Order:
        """Function that removes an item from the cart

        Parameters
        ----------
        cart: dict
            the current user's cart
        username_customer: str
            customer's username
        validate: str
            whether the customer wants to validate ("yes") their cart or not ("no")
        address: str
            delivery's address, by default None

        Returns
        -------
        Order
            Returns the order that has just been created.
        """
        if address is None:
            customer = self.get_customer(username_customer)
            address = customer.address
        else:
            google_service.geocoding_address(address)
        if validate == "yes":
            order = Order(
                id_order=None,
                username_customer=username_customer,
                username_delivery_driver=None,
                address=address,
                items=cart,
            )
            success = self.order_dao.create_order(order)
            self.delivery_service.create([self.order_dao.find_order_by_user(username_customer)[-1].id_order], [address])
            if not success:
                raise ValueError("Failed to create order in the database.")
            for name_item, quantity in cart.items():
                items = self.item_dao.find_all_item()
                for item in items:
                    if item.name_item == name_item:
                        id_item = item.id_item
                item = self.item_dao.find_item(id_item)
                if item:
                    if item.stock >= quantity:
                        item.stock -= quantity
                        update_success = self.item_dao.update(item)
                        if not update_success:
                            raise ValueError(f"Failed to update stock for item {item.name_item}")
                    else:
                        raise ValueError(f"Not enough stock for item {item.name_item}")
                else:
                    raise ValueError(f"Item {name_item} not found in the database")

            return order

        raise TypeError("If you want to validate your cart you must enter: yes")

    def view_order(self, username_customer: str) -> Order:
        """Function that returns the last order of a customer.

        Parameters
        ----------
        username_customer: str
            the name of the customer

        Returns
        -------
        Order
            Returns the last user's order.
        """
        order_user = self.order_dao.find_order_by_user(username_customer)
        if not order_user:
            raise ValueError(f"No orders found for user {username_customer}")

        last_order = max(order_user, key=lambda order: order.id_order)
        return last_order

    def view_cart(self, cart: dict) -> dict:
        """Function that returns the cart with its total amount.

        Parameters
        ----------
        cart: dict
            the customer's active cart

        Returns
        -------
        dict
            Returns the user's cart with its price.
        """
        items = self.item_dao.find_all_item()
        price_cart = sum(item.price * cart[item.name_item] for item in items if item.name_item in cart)

        return {"cart": cart, "price": round(price_cart / 100, 2)}
