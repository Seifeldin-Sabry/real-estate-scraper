from dataclasses import dataclass

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum, Column

from enums.enums import TypeOfTransaction


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

    def __repr__(self):
        return f"""
        <Property(id={self.id}, price={self.price}, type_of_transaction={self.type_of_transaction}, 
        locality={self.locality})>
        """

