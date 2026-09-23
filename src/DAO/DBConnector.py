import os
from typing import Any, Dict, List, Literal, Optional, Union

import logging

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()

logger = logging.getLogger(__name__)


class DBConnector:
    """
    Class which connect our database to our DAO classes.
    """

    def __init__(self, config=None):
        if config is not None:
            self.host = config["host"]
            self.port = config["port"]
            self.database = config["database"]
            self.user = config["user"]
            self.password = config["password"]
            self.schema = config["schema"]
        else:
            self.host = os.environ["POSTGRES_HOST"]
            self.port = os.environ["POSTGRES_PORT"]
            self.database = os.environ["POSTGRES_DATABASE"]
            self.user = os.environ["POSTGRES_USER"]
            self.password = os.environ["POSTGRES_PASSWORD"]
            self.schema = os.environ["POSTGRES_SCHEMA"]

    def sql_query(
        self,
        query: str,
        data: Optional[Union[tuple, list, dict]] = None,
        return_type: Optional[Literal["one", "all"]] = None,
    ) -> Optional[Dict[str, Any]] | List[Dict[str, Any]] | bool:
        """Execute a SQL query on the database and return results based on the specified type.

        Parameters
        ----------
        query : str
            The SQL query to execute
        data : Optional[Union[tuple, list, dict]], optional
            Data to pass for parameterized queries.
            Example: `(1,)` for `WHERE id = %s`, or `{"id": 1}` for `WHERE id = %(id)s`.
            Defaults to `None`.
        return_type : Optional[Literal["one", "all"]], optional
            Determines the return format:
            - "one": Return a single row (or `None` if no results).
            - "all": Return all rows.
            - `None`: Return `True` to confirm query execution.
            Defaults to `None`.

        Returns
        -------
        Optional[Dict[str, Any]] | List[Dict[str, Any]] | bool
            - If `return_type="one"`: A dictionary representing a single row, or `None`.
            - If `return_type="all"`: A list of dictionaries (all rows).
            - If `return_type=None`: `True` to confirm query execution.
        """
        try:
            with psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                options=f"-c search_path={self.schema}",
                cursor_factory=RealDictCursor,
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, data)
                    connection.commit()
                    if return_type == "one":
                        return cursor.fetchone()
                    elif return_type == "all":
                        return cursor.fetchall()
                    else:
                        return True
        except Exception as exception:
            logger.error("Query failed: %s", exception)
            raise
