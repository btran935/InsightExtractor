from sqlmodel import SQLModel, create_engine
from models.models import Theme, Post
sqlite_file = "insights.db"
sqlite_url = f"sqlite:///{sqlite_file}"
engine = create_engine(sqlite_url, echo=True, connect_args={"check_same_thread": False})

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
create_db_and_tables()
