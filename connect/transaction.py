from contextlib import contextmanager
import psycopg2.pool
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()
from threading import local


print("Connected to "+ os.getenv('DB_NAME'))

connection_data = local()
connection_data.connection = None
connection_data.pool = None


class Credentials(BaseModel):
    username: str
    password: str
    hostname: str
    port: int
    database: str
    min_connections: int = 1
    max_connections: int = 100


class ConnectionWrapper():
    def __init__(self, connection, is_transaction: bool = False):
        self.connection = connection
        self.is_transaction = is_transaction

    def commit(self):
        self.connection.commit()


def __build_connection_pool(creds: Credentials):
    if connection_data.pool is not None:
        return connection_data.pool
    else:
        connection_data.pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=creds.min_connections,
            maxconn=creds.max_connections,
            user=creds.username,
            password=creds.password,
            host=creds.hostname,
            port=creds.port,
            database=creds.database,
            # sslmode='verify-ca',
            # sslrootcert=os.getenv('CERTS_DIR')
        )


def get_connection(credentials: Credentials):
    if connection_data.pool is None:
        __build_connection_pool(credentials)
    if connection_data.connection is not None:
        return ConnectionWrapper(connection_data.connection, is_transaction=True)
    return ConnectionWrapper(connection_data.pool.getconn(), is_transaction=False)


@contextmanager
def transaction():
    if connection_data.connection is not None:
        raise ValueError("Cannot open transaction inside another transaction")

    try:
        connection_data.connection = connection_data.pool.getconn()
        yield connection_data.connection
        connection_data.connection.commit()

    except Exception as e:
        #TODO add logging on the rollback
        connection_data.connection.rollback()
        connection_data.connection = None
    finally:
        connection_data.pool.putconn(connection_data.connection)
        connection_data.connection = None
