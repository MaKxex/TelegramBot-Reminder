from db import get_engine
from sqlalchemy import DateTime, Table,String, Column, Integer, String, MetaData, Boolean

meta = MetaData()


Tasks = Table(
    "tasks", meta,
    Column("id", Integer, primary_key=True),
    Column("userid", Integer),
    Column("datetime", DateTime),
    Column("repeat", Boolean),
    Column("text", String)
)

meta.create_all(get_engine())