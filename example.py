from pydantic import BaseModel

from simplesql import set_credentials, Credentials
from simplesql.postgres import BatchInsert, Query


class Data(BaseModel):
    id: int
    key: str
    value: int


creds = Credentials(
        user="user",
        password="password",
        host="localhost",
        port=5432)

set_credentials(creds)


Query("INSERT INTO data (key, value) values (%(key)s, %(value)s) RETURNING *").bind({'key': 'k1', 'value':1}).exec(Data)
data = Query("SELECT * FROM data where id=%(id)s").bind({"id": 1}).exec(Data)
print(data)

Query("INSERT INTO data (key, value) values (%(key)s, %(value)s) RETURNING *").bind({'key': 'k2', 'value':2}).exec(Data)

id_tuple = ((1,2,),)
BatchInsert("SELECT * FROM data where id in %s").bind(id_tuple).exec(Data)
print(data)


