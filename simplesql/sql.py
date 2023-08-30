from typing import Type

import psycopg2
from psycopg2.extras import RealDictCursor

from pydantic import BaseModel

from models.dbconfig import DbConfig


class SQL:
    def __init__(self, connection, verbose: bool = False):
        self.connection = connection
        self.verbose = verbose
        self.query_string: str = ""
        self.args: tuple = tuple()

    def query(self, query: str):
        self.query_string = query
        return self

    def bind(self, args):
        self.args = args
        return self

    def get_single(self, model_type: Type[BaseModel]) -> BaseModel:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(self.query_string, self.args)
            result = cursor.fetchone()
            return model_type.model_validate(result)

    def get_list(self, model_type: Type[BaseModel]) -> list[BaseModel]:

        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(self.query_string, self.args)
            results = cursor.fetchall()
            return [model_type.model_validate(row) for row in results]


def connect(credentials: DbConfig) -> SQL:
    conn_str = "dbname='{database}' user='{username}' host='{hostname}' password='{password}'".format_map(credentials.model_dump())
    connection = psycopg2.connect(conn_str)
    return SQL(connection, verbose=credentials.log_queries)