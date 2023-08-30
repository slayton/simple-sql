import psycopg2

from dbconfig import DbConfig

creds = DbConfig(
    database="slayton",
    username="slayton",
    password="password",
    hostname="localhost",
    log_queries=True
)

conn_str = "dbname='{database}' user='{username}' host='{hostname}' password='{password}'".format_map(creds.model_dump())
connection = psycopg2.connect(conn_str)

# Get in tuple, where single column applied
with connection.cursor() as cursor:
    print("TEST 1")
    cursor.execute("SELECT * FROM data WHERE key in %s", (('age','num'),))
    result = cursor.fetchall()
    print(result)

# Get in tuple, where multiple columns are filtered
with connection.cursor() as cursor:
    print("TEST 2")
    t1 = ('age', 34)
    t2 = ('num', 3)
    in_tuples = (t1, t2)
    cursor.execute("SELECT * FROM data WHERE (key, value) in %s", (in_tuples,))
    result = cursor.fetchall()
    print(result)