from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from Config import Config


DATABASE_URL = (
    f'postgresql+psycopg://postgres:{Config.DB_PASSWORD}@localhost/{Config.DB_NAME}'
)

engine = create_engine(
    DATABASE_URL,
    echo=True,  # shows SQL queries in console
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass

def get_db():
    
    db=SessionLocal()
    
    try:
        yield db
    finally:
        db.close()