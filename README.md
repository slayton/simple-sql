# Simple SQL

Simple SQL is a thin wrapper around Psycopg2 that is meant to simplify the mechanisms for querying a database and 
returning results as a pydantic model. 

It requires the user to write raw sql (trust me this is a feature) and abstracts away a lot of the 
boiler plate code you need with psycopg2.

## Examples:
See `examples.py`

These examples assume you have Postgres running somewhere. Connection information about that database is defined in an
instance of DbConfig and you have a Pydantic model you want to deserialize into:

### Queries
Query a single row by id:
```python
SQL = connect(config)
data = {"id": 2}
result = SQL.query("SELECT * FROM data where id=%(id)s").bind(data).run_query(PydanticModel)
```

Query for a list of results
```python
SQL = connect(config)
data = {"id": 2}
result = SQL.query("SELECT * FROM data where id>%(id)s").bind(data).run_query(list[PydanticModel])
```

Query within a collection of ids:
```python


SQL = connect(config) #Creds is an instance of models. dbconfig
data = {"ids": (1,2,3)}
result = SQL.query("SELECT * FROM data where id=%(ids)s").bind(data).run_query(list[PydanticModel])
```

### Inserts & Updates

```python 
class MyModel(BaseModel):
    id: int
    value: str

data = MyModel(id=1, value="hello world")

SQL = connect(config) #Creds is an instance of models. dbconfig
data = {"ids": (1,2,3)}
result = SQL.query("INSERT INTO data (id, value) VALUES (%(id)s, %(value)s)").bind(data).run_query() 

new_data = MyModel(id=1, value="New Value")
result = SQL.query("UPDATE data SET value=%(value)s WHERE id=%(id)s).bind(data).run_query()
```
## Transaction Support
All queries are contained in their own transaction. Transactional support across multiple queries is a WIP