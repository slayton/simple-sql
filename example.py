from pydantic import BaseModel

from connect.transaction import connect, transaction
from connect.postgres import BatchInsert, Query


class Data(BaseModel):
    id: int
    key: str
    value: int


Query("INSERT INTO data (key, value) values (%(key)s, %(value)s) RETURNING *").bind({'key': 'k1', 'value':1}).exec(Data)
data = Query(connect(creds), "SELECT * FROM data where id=%(id)s").bind({"id": 1}).exec(Data)
print(data)

Query("INSERT INTO data (key, value) values (%(key)s, %(value)s) RETURNING *").bind({'key': 'k2', 'value':2}).exec(Data)

id_tuple = ((1,2,),)
BatchInsert("SELECT * FROM data where id in %s").bind(id_tuple).exec(Data)
print(data)


