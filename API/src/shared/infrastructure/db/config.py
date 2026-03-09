from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from API.src.shared.infrastructure.db.base import Base
from src.config.settings import Settings
from API.src.auth.infrastructure.models.auth_token import AuthToken
from API.src.users.infrastructure.models.user import User

class Config:
    engine = None
    def __init__(self):
        self.settings = Settings()
        self.conn_string = self.settings.POSTGRES_CONNECTION_STRING_NEW_DB
        self.engine = create_engine(self.conn_string, echo=True)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        # Create tables
        Base.metadata.create_all(
            bind=self.engine, 
            tables=[
                table for _, table in Base.metadata.tables.items() 
                if table.name != "products" and table.schema != "raw"
            ]
        )

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()