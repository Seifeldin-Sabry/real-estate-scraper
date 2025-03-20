from typing import Type, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from db.engine import engine
from model.property import Property


def get_latest_properties() -> list[Property]:
    """
    Queries the Database for the latest properties.
    """
    with Session(engine) as session:
        statement = select(Property).order_by(Property.date_added.desc())
        result = session.execute(statement)
        properties = result.scalars().all()

    return list(properties)


def add_properties(properties: List[Property]):
    """
    Adds a list of properties to the Database.
    """
    with Session(engine) as session:
        session.add_all(properties)
        session.commit()


def delete_properties(properties: List[Property]):
    """
    Deletes a list of properties from the Database.
    """
    with Session(engine) as session:
        for prop in properties:
            session.delete(prop)
        session.commit()
