from sqlalchemy import create_engine
from sqlalchemy import URL

url_object = URL.create(
    "postgresql",
    username="user",
    password="password",
    host="localhost",
    port=5433,
    database="real_estate",
)


engine = create_engine(url_object)