from contextlib import contextmanager
import psycopg2.pool
import os
from dotenv import load_dotenv
load_dotenv()
from threading import local

pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=100,
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_SERVER'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
    # sslmode='verify-ca',
    # sslrootcert=os.getenv('CERTS_DIR')
)

print("Connected to "+ os.getenv('DB_NAME'))

tx_data = local()
tx_data.connection = None


class ConnectionWrapper():
    def __init__(self, connection, is_transaction: bool = False):
        self.connection = connection
        self.is_transaction = is_transaction

    def commit(self):
        self.connection.commit()


def get_connection():
    if tx_data.connection is not None:
        return ConnectionWrapper(tx_data.connection, is_transaction=True)
    return ConnectionWrapper(pool.getconn(), is_transaction=False)


@contextmanager
def transaction():
    if tx_data.connection is not None:
        raise ValueError("Cannot open transaction inside another transaction")

    try:
        tx_data.connection = pool.getconn()
        yield tx_data.connection
        tx_data.connection.commit()

    except Exception as e:
        #TODO add logging on the rollback
        tx_data.connection.rollback()
        tx_data.connection = None
    finally:
        pool.putconn(tx_data.connection)
        tx_data.connection = None
