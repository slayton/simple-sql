from pydantic import BaseModel


class DbConfig(BaseModel):
    hostname: str
    database: str
    port: int = 5432
    username: str
    password: str
    log_queries: bool = False
