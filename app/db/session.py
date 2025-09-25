from app.core.config import settings
from sqlalchemy import create_engine
from typing import Generator
from sqlalchemy.orm import sessionmaker, declarative_base

engine = create_engine(settings.DATABASE_URL, pool_pre_ping = True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()