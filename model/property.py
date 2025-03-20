from dataclasses import dataclass

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum, Column, DATETIME

from db.engine import engine
from enums.enums import TypeOfTransaction
from datetime import datetime


class Base(DeclarativeBase):
    pass


@dataclass
class Property(Base):
    __tablename__ = 'property'

    id: Mapped[int] = mapped_column(primary_key=True)
    price: Mapped[str] = mapped_column()
    type_of_transaction = Column(Enum(TypeOfTransaction), nullable=False)
    locality: Mapped[str] = mapped_column()
    link: Mapped[str] = mapped_column()
    date_added: Mapped[datetime] = mapped_column(default=datetime.now())

    def __repr__(self):
        return f"""
        Property: {self.locality} - {self.price} - {self.type_of_transaction.value}
        """

    def __eq__(self, other):
        return self.link == other.link


Base.metadata.create_all(engine)
