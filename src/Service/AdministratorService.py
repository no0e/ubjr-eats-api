from typing import Optional

from src.DAO.AdministratorDAO import AdministratorDAO
from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.DeliveryDriverDAO import DeliveryDriverDAO
from src.DAO.UserDAO import UserDAO
from src.Model.User import User
from src.Service.PasswordService import check_password_strength, create_salt, hash_password
from src.Service.UserService import UserService


class AdministratorService:
    """Class with all Service methods of an administrator."""

    def __init__(
        self,
        user_repo: UserDAO,
        admin_repo: AdministratorDAO,
        driver_repo: DeliveryDriverDAO,
        customer_repo: CustomerDAO,
    ):
        self.user_repo = user_repo
        self.admin_repo = admin_repo
        self.driver_repo = driver_repo
        self.customer_repo = customer_repo

    def create_user(self, username: str, firstname: str, lastname: str, password: str, account_type: str) -> User:
        """Function that creates a user from its attributes.

        Parameters
        ----------
        username : str
            user's username
        firstname : str
            user's firstname
        lastname : str
            user's lastname
        password : str
            user's password
        account_type : str
            user's account type

        Returns
        -------
        User
            Returns the user that has been created.
        """
        return UserService(self.user_repo, self.admin_repo, self.driver_repo, self.customer_repo).create_user(
            username=username,
            firstname=firstname,
            lastname=lastname,
            password=password,
            account_type=account_type,
        )

    def get_user(self, user_username: str) -> User | None:
        """Function that gives a user by the username given.

        Parameters
        ----------
        user_username : str
            user's username to search

        Returns
        -------
        User
            Instance of the user with the assiociated username given.
        """
        user = self.user_repo.get_by_username(user_username)

        if user is None:
            raise ValueError(f"User with username '{user_username}' not found.")
        return user

    def username_exists(self, username: str) -> bool:
        """Function that checks if a given username is already existing in the database.

        Parameters
        ----------
        username : str
            username to check

        Returns
        -------
        bool
            True if the username is already existing, False otherwise.
        """
        return self.user_repo.get_by_username(username) is not None

    def update_user(
        self,
        username: str,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """Function that update the user's attributes.

        Parameters
        ----------
        username : str
            user's username
        firstname : str | None
            user's firstname
        lastname : str | None
            user's lastname
        password : str | None
            user's password

        Returns
        -------
        User
            Returns the user with updated information.
        """
        if firstname is not None:
            self.user_repo.get_user(username).firstname = firstname
        if lastname is not None:
            self.user_repo.get_user(username).lastname = lastname
        if password is not None:
            check_password_strength(password)
            salt = create_salt()
            self.user_repo.get_user(username).password = hash_password(password, salt)
        return self.user_repo.get_user(username)
