from typing import Optional

from src.Model.User import User

from .DBConnector import DBConnector


class UserDAO:
    """
    Data Access Object (DAO) for interacting with the 'users' table in the database.
    Provides methods to retrieve and insert user data.
    """

    db_connector: DBConnector

    def __init__(self, db_connector: DBConnector, test: bool = False):
        self.db_connector = db_connector
        if test:
            self.schema = "project_test_database"
        else:
            self.schema = "project_database"

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Function that find a user by their username.

        Parameters
        ----------
        username : str
            Username of the user we want to find


        Returns
        -------
        User | None
            Returns a User if found, None otherwise
        """
        raw_user = self.db_connector.sql_query(
            "SELECT * FROM " + self.schema + ".users WHERE username=%s", [username], "one"
        )
        if raw_user is None:
            return None

        return User(
            username=raw_user["username"],
            firstname=raw_user.get("firstname", ""),
            lastname=raw_user.get("lastname", ""),
            password=raw_user.get("password", ""),
            salt=raw_user.get("salt", ""),
            account_type=raw_user.get("account_type", ""),
        )

    def create_user(self, user: User) -> bool:
        """
        Function that create an instance of user in the users database.

        Parameters
        ----------
        user : User
            Model of user which will be created


        Returns
        -------
        boolean
            Returns True if the user has been created, False otherwise.
        """
        if isinstance(user, User):
            raw_created_user = self.db_connector.sql_query(
                """
                INSERT INTO """
                + self.schema
                + """.users (username, firstname, lastname, password, salt, account_type)
                VALUES (%(username)s, %(firstname)s, %(lastname)s, %(password)s, %(salt)s, %(account_type)s)
                RETURNING *;
                """,
                {
                    "username": user.username,
                    "firstname": user.firstname,
                    "lastname": user.lastname,
                    "password": user.password,
                    "salt": user.salt,
                    "account_type": user.account_type,
                },
                "one",
            )
            return raw_created_user is not None
        else:
            return False

    def update_user(
        self,
        username: str,
        firstname: Optional[str] = None,
        lastname: Optional[str] = None,
        password: Optional[str] = None,
    ) -> bool:
        """
        Update an existing user's attributes.
        It could update any attribute among firstname, lastname and password.

        Parameters
        ---
        username: str
            User's username
        firstname: Optional[str] = None
            User's firstname
        lastname: Optional[str] = None
            User's lastname
        password: Optional[str] = None
            User's password

        Return
        ---
        bool
            Returns True if the update succeed, False otherwise.
        """
        if not isinstance(self.get_by_username(username), User):
            return False
        if firstname is None:
            firstname = self.get_by_username(username).firstname
        if lastname is None:
            lastname = self.get_by_username(username).lastname
        if password is None:
            password = self.get_by_username(username).password
        updated_rows = self.db_connector.sql_query(
            """
            UPDATE """
            + self.schema
            + """.users
            SET
                firstname = %(firstname)s,
                lastname = %(lastname)s,
                password = %(password)s
            WHERE username = %(username)s
            RETURNING *;
            """,
            {
                "username": username,
                "firstname": firstname,
                "lastname": lastname,
                "password": password,
            },
            "one",
        )

        return updated_rows is not None

    def delete_user(self, user: User) -> bool:
        """
        Function that delete a user.

        Parameters
        ----------
        user : User
            User we want to delete

        Returns
        -------
        boolean
            Returns True if the user is deleted, False otherwise
        """
        if not isinstance(user, User):
            return False
        deleted_row = self.db_connector.sql_query(
            """
            DELETE FROM """
            + self.schema
            + """.users
            WHERE username = %(username)s
            RETURNING *;
            """,
            {
                "username": user.username,
            },
            "one",
        )

        return deleted_row is not None
