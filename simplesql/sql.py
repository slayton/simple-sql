from enum import IntEnum
from typing import Type

import psycopg2
from psycopg2.extras import RealDictCursor

from pydantic import BaseModel

from models.dbconfig import DbConfig

class QueryType(IntEnum):
    undefined = 0
    select = 1
    insert = 2
    delete = 3
    update = 4
    truncate = 5

class SQL:

    _COMMIT_TYPES = {QueryType.delete, QueryType.insert, QueryType.update}
    def __init__(self, connection, verbose: bool = False):
        self.connection = connection
        self.verbose = verbose
        self.query_string: str = ""
        self.args: tuple = tuple()
        self.query_type = QueryType.select

    def query(self, query: str):
        self.query_string = query
        if self.query_string.startswith("SELECT"):
            self.query_type = QueryType.select
        elif self.query_string.startswith("INSERT INTO"):
            self.query_type = QueryType.insert
        elif self.query_string.startswith("DELETE FROM"):
            self.query_string = QueryType.delete
        elif self.query_string.startswith("UPDATE"):
            self.query_type = QueryType.update

        return self

    def bind(self, args):
        self.args = args
        return self

    def commit(self):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(self.query_string, self.args)
            self.connection.commit()

    def get(self, model_type: Type[BaseModel]) -> BaseModel:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(self.query_string, self.args)
            if self.query_type in self._COMMIT_TYPES:
                self.connection.commit()
            result = cursor.fetchone()
            return model_type.model_validate(result)

    def get_list(self, model_type: Type[BaseModel]) -> list[BaseModel]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(self.query_string, self.args)
            if self.query_type in self._COMMIT_TYPES:
                self.connection.commit()
            results = cursor.fetchall()
            return [model_type.model_validate(row) for row in results]

    def get_int(self) -> int:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(self.query_string, self.args)
            if self.query_type in self._COMMIT_TYPES:
                self.connection.commit()
            return cursor.fetchone()




def sql_connect(credentials: DbConfig) -> SQL:
    conn_str = "dbname='{database}' user='{username}' host='{hostname}' password='{password}'".format_map(credentials.model_dump())
    connection = psycopg2.connect(conn_str)
    return SQL(connection, verbose=credentials.log_queries)



