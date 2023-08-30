from pydantic import BaseModel

from dbconfig import DbConfig
from simplesql.sql import sql_connect

class Data(BaseModel):
    id: int
    key: str
    value: int

# Update this to
creds = DbConfig(
    database="slayton",
    username="slayton",
    password="password",
    hostname="localhost",
    log_queries=True
)

sql_connect(creds).query("TRUNCATE data RESTART IDENTITY").commit()

sql_connect(creds).query("INSERT INTO data (key, value) values (%(key)s, %(value)s) RETURNING *").bind({'key':'k1', 'value':1}).get(Data)
data = sql_connect(creds).query("SELECT * FROM data where id=%(id)s").bind({"id": 1}).get(Data)
print(data)

sql_connect(creds).query("INSERT INTO data (key, value) values (%(key)s, %(value)s) RETURNING *").bind({'key':'k2', 'value':2}).get(Data)

id_tuple = ((1,2,),)
data = sql_connect(creds).query("SELECT * FROM data where id in %s").bind(id_tuple).get_list(Data)
print(data)


# Select by ID
# SQL = sql_connect(creds)
# result =
# print(result)
#
# # Select by ID in list of ids
# id_tuple = ((1,2,),)
# SQL = sql_connect(creds) #Creds is an instance of models. dbconfig
# result = SQL.query("SELECT * FROM data where id in %s").bind(id_tuple).get_list(Data)
# print(result)

# Insert new row into database


