from sqlalchemy import create_engine

from database.models import Base

SQLITE_URI = "sqlite:///habr_career.db"


class Database:
    def __init__(self):
        self.engine = create_engine(SQLITE_URI)
        Base.metadata.create_all(self.engine)
