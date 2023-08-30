# Simple SQL

Simple SQL is a thin wrapper around Psycopg2 that is meant to simplify the mechanisms for querying a database and 
returning results as a pydantic model. 

It requires the user to write raw sql (trust me this is a feature) and abstracts away a lot of the 
boiler plate code you need with psycopg2.

## Examples:
See `examples.py`

Query a single row by id:
```python
SQL = connect(config) #Creds is an instance of models. dbconfig
result = SQL.query("SELECT * FROM data where id=%(id)s").bind({"id": 2}).get_result(Data) #Data is a pydantic model
```

Query within a collection of ids:
```python
id_tuple = (1,2,3)
SQL = connect(config) #Creds is an instance of models. dbconfig
result = SQL.query("SELECT * FROM data where id=%(id)s").bind({"id": 2}).get_result(Data) #Data is a pydantic model
```