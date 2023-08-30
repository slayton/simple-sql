from pydantic import BaseModel

from dbconfig import DbConfig
from simplesql.sql import connect

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


SQL = connect(creds)
result = SQL.query("SELECT * FROM data where id=%(id)s").bind({"id": 2}).get_result(Data)

print(result)

