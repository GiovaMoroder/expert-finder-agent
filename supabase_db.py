import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

url = os.environ["DATABASE_URL"]

engine = create_engine(
    url,
    pool_pre_ping=True,
)

with engine.connect() as conn:
    print(conn.execute(text("select now()")).scalar())