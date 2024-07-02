import mariadb
import requests
def connect():
    try:
        conn = mariadb.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="root")

        cur = conn.cursor()

        print("Columns in query results:")

        conn.close()

    except Exception as e:
        print(f"Error: {e}")
if __name__ == '__main__':

    connect()