import logging

import dotenv

from src.DAO.DBConnector import DBConnector
from src.Utils.log_decorator import log
from src.Utils.singleton import Singleton


class ResetDatabase(metaclass=Singleton):
    """
    Reinitialisation de la base de données
    """

    @log
    def launch(self, test_dao=False):
        """Lancement de la réinitialisation des données
        Si test_dao = True : réinitialisation des données de test"""

        if test_dao:
            # mock.patch.dict(os.environ, {"POSTGRES_SCHEMA": "projet_test_dao"}).start()
            init_data_path = "data/init_test_db.sql"
            pop_data_path = "data/pop_db_test.sql"
        else:
            init_data_path = "data/init_db.sql"
            pop_data_path = "data/pop_db.sql"

        dotenv.load_dotenv()

        init_db = open(init_data_path, encoding="utf-8")
        init_db_as_string = init_db.read()
        init_db.close()

        pop_db = open(pop_data_path, encoding="utf-8")
        pop_db_as_string = pop_db.read()
        pop_db.close()

        db_connector = DBConnector()

        try:
            db_connector.sql_query(init_db_as_string)
            db_connector.sql_query(pop_db_as_string)
        except Exception as e:
            logging.info(e)
            raise

        return True


if __name__ == "__main__":
    ResetDatabase().launch()
    ResetDatabase().launch(True)
    print("Database was reset.")
