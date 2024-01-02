import types
import typing
from abc import ABC, abstractmethod
from typing import Union

from psycopg2.extras import RealDictCursor, DictCursor, execute_batch
from pydantic import BaseModel, TypeAdapter
from transaction import get_connection, ConnectionWrapper

_primitive_types = {int, float, str, bool}
_accepted_types = Union[int, float, str, bool, type, BaseModel]
_returned_singletons = Union[None, int, float, str, bool, type, BaseModel]
_returned_lists = Union[
    None,
    list[int],
    list[float],
    list[str],
    list[bool],
    list[BaseModel],
]


def _parse_result(cursor, result_type: _accepted_types):
    as_list = isinstance(result_type, types.GenericAlias)
    parse_type = typing.get_args(result_type)[0] if as_list else result_type

    if parse_type in _primitive_types:
        return _parse_primitive(cursor, parse_type, as_list)
    else:
        return _parse_pydantic(cursor, parse_type, as_list)


def _parse_primitive(cursor, expected_type: type, as_list: bool):

    if as_list:
        result = cursor.fetchall()
        return [expected_type(row[0]) for row in result]
    else:
        if cursor.rowcount == 0:
            return None
        result = cursor.fetchone()
        return expected_type(result[0])


def _parse_pydantic(cursor, result_type: _accepted_types, as_list: bool):
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


class BaseQuery(ABC):
    def __init__(self, query: str, verbose: bool = False):
        self.connection_wrapper = get_connection()
        self.verbose = verbose
        self.query_string: str = ""
        self.args: tuple = tuple()
        self.query_string = query

    @abstractmethod
    def bind(self, args):
        pass

    def exec(self, model_type: _accepted_types = None):
        is_primitive = model_type in _primitive_types
        cf = DictCursor if is_primitive else RealDictCursor

        with self.connection_wrapper.connection.cursor(cursor_factory=cf) as cursor:
            self._exec(cursor)
            if not self.connection_wrapper.is_transaction:
                self.connection_wrapper.commit()
            if model_type is None:
                return
            if is_primitive:
                return _parse_primitive(cursor, model_type, as_list=self._as_list())
            else:
                return _parse_pydantic(cursor, model_type, as_list=self._as_list())

    @abstractmethod
    def _exec(self, cursor):
        pass

    @abstractmethod
    def _as_list(self):
        pass


class Query(BaseQuery):
    def _exec(self, cursor):
        cursor.execute(self.query_string, self.args)

    def _as_list(self):
        return False

    def bind(self, args):
        if isinstance(args, BaseModel):
            self.args = args.model_dump()
        else:
            self.args = args
        return self


class MultiRowQuery(BaseQuery):
    def _exec(self, cursor):
        cursor.execute(self.query_string, self.args)

    def _as_list(self):
        return True

    def bind(self, args):
        if isinstance(args, BaseModel):
            self.args = args.model_dump()
        else:
            self.args = args
        return self


class BatchInsert(BaseQuery):

    def _exec(self, cursor):
        execute_batch(cursor, self.query_string, self.args)

    def _as_list(self):
        return True

    def bind(self, args):
        if isinstance(args[0], BaseModel):
            self.args = [a.model_dump() for a in args]
        else:
            self.args = args
        return self
