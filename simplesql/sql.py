from enum import IntEnum
from typing import Type, List, Union

import psycopg2
from psycopg2.extras import RealDictCursor, DictCursor

from pydantic import BaseModel, TypeAdapter

_primitive_types = [int, float, str, bool]
_accepted_types = Union[int, float, str, bool, BaseModel]
_return_types = Union[
    None,
    int,
    float,
    str,
    bool,
    BaseModel,
    list[int],
    list[float],
    list[str],
    list[bool],
    list[BaseModel],
]


class DbConfig(BaseModel):
    hostname: str
    database: str
    port: int = 5432
    username: str
    password: str
    log_queries: bool = False


def _parse_result(cursor, result_type: _accepted_types, as_list: bool) -> _return_types:
    if isinstance(result_type, type):
        return _parse_primitive(cursor, result_type, as_list)
    else:
        return _parse_pydantic(cursor, result_type, as_list)


def _parse_primitive(cursor, expected_type: type, as_list: bool) -> _return_types:

    if as_list:
        result = cursor.fetchall()
        return [expected_type(row[0]) for row in result]
    else:
        if cursor.rowcount == 0:
            return None
        result = cursor.fetchone()
        return expected_type(result[0])


def _parse_pydantic(cursor, result_type: _accepted_types, as_list: bool) -> _return_types:
    if as_list:
        if cursor.rowcount == 0:
            return []
        result = cursor.fetchall()
        return TypeAdapter(list[result_type]).validate_python(result)
    else:
        if cursor.rowcount == 0:
            return None
        result = cursor.fetchone()
        return result_type.model_validate(result)


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
        if isinstance(args, BaseModel):
            self.args = args.model_dump()
        else:
            self.args = args
        return self

    def run_query(
        self, model_type: _accepted_types = None, as_list: bool = False
    ) -> _return_types:
        cf = DictCursor if model_type in _primitive_types else RealDictCursor
        with self.connection.cursor(cursor_factory=cf) as cursor:
            cursor.execute(self.query_string, self.args)
            self.connection.commit()
            if model_type is None:
                return
            return _parse_result(cursor, model_type, as_list)


def sql_connect(credentials: DbConfig) -> SQL:
    conn_str = "dbname='{database}' user='{username}' host='{hostname}' password='{password}'".format_map(
        credentials.model_dump()
    )
    connection = psycopg2.connect(conn_str)
    return SQL(connection, verbose=credentials.log_queries)
