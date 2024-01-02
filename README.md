# Connect Postgres Py

Connect Postgres Py is a thin wrapper around Psycopg2 that is meant to simplify the mechanisms for querying a database and 
returning results as a pydantic model. 

It requires the user to write raw sql (trust me this is a feature) and abstracts away a lot of the 
boiler plate code you need with psycopg2.

It supports python dictionaries as well as Pydantic objects natively.

The basic template is user write their queries in native SQL as a string. Variables in the query use Psycopg2 syntax and
are defined with `%(VARNAME)s`. Inputs to the query are specified by calling `bind` with either a python `dict` or an
instance of Pydantic object.

The query is executed by calling `exec()`. Results from the query can be captured by providing a `type` in the `run_query`
arguments. Accepted types are `int`, `float`, `str`, `bool` and types that extend `BaseModel`. 

## Examples:
See `examples.py`

These examples assume you have Postgres running somewhere. Connection information about that database is defined in an
instance of DbConfig and you have a Pydantic model you want to deserialize into:
```python
# Example Pydantic Model
from pydantic import BaseModel
class MyModel(BaseModel):
    id: int
    value: str
```

## Queries
Query a single row by id using a `dict`:
```python
data = {"id": 2}
result = SingleRowQuery("SELECT * FROM data where id=%(id)s").bind(data).exec(PydanticModel)
```

Query a single row by id using a `Pydantic` mode;:
```python
data = MyModel(id=1, value="Hello World")
result = SingleRowQuery("SELECT * FROM data where id=%(id)s").bind(data).exec(PydanticModel)
```

Query for a list of results
```python
data = {"id": 2}
result = MultiRowQuery("SELECT * FROM data where id>%(id)s").bind(data).exec(PydanticModel)
```

Query within a collection of ids:
```python

data = {"ids": (1,2,3)}
result = MultiRowQuery("SELECT * FROM data where id=%(ids)s").bind(data).exec(PydanticModel)
```

### Inserts & Updates

```python 

data = MyModel(id=1, value="hello world")
conn = connect(creds)
result = SingleRowQuery("INSERT INTO data (id, value) VALUES (%(id)s, %(value)s)").bind(data).exec() 

new_data = MyModel(id=1, value="New Value")
result = SingleRowQuery("UPDATE data SET value=%(value)s WHERE id=%(id)s").bind(new_data).exec()
```
## Transaction Support
```python
data1 = MyModel(id=1, value="hello world")
data2 = MyModel(id=2, value="hello moon")
with transaction():
    # Do some work
    SingleRowQuery("INSERT INTO data (id, value) VALUES (%(id)s, %(value)s)").bind(data1).exec()
    # Do some more work
    SingleRowQuery("INSERT INTO data (id, value) VALUES (%(id)s, %(value)s)").bind(data2).exec()
```
