# base.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

db_string_con = os.environ.get("DB_STRING_CON")
engine = create_engine(db_string_con)
Session = sessionmaker(bind=engine, expire_on_commit=False)
Base = declarative_base()