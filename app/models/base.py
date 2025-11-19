from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import BIGINT
from typing import Annotated

bigintpk = Annotated[int, mapped_column(BIGINT, primary_key=True, autoincrement=True)]


class Base(DeclarativeBase):
    pass
