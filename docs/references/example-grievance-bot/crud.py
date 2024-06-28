import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

db_name = os.getenv("POSTGRES_DATABASE_NAME")
db_user = os.getenv("POSTGRES_DATABASE_USERNAME")
db_password = os.getenv("POSTGRES_DATABASE_PASSWORD")
db_host = os.getenv("POSTGRES_DATABASE_HOST")
db_port = os.getenv("POSTGRES_DATABASE_PORT")
db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


engine = create_engine(db_url)

Session = sessionmaker(bind=engine)
session = Session()
session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
session.commit()
