from dotenv import load_dotenv

from src.DAO.DBConnector import DBConnector

load_dotenv()


def test_connection():
    db = DBConnector()
    try:
        result = db.sql_query("SELECT 1;", return_type="one")
        print("Connection successful! Result:", result)
    except Exception as e:
        print("Connection failed:", e)


if __name__ == "__main__":
    test_connection()
