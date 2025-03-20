from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass


class Property(Base):
    __tablename__ = 'property'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    price: Mapped[float] = mapped_column()
    description: Mapped[str] = mapped_column()
    link: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()
    postal_code: Mapped[str] = mapped_column()

    def __repr__(self):
        return f"""
        <Property(id={self.id}, title={self.title}, price={self.price}, link={self.link}, city={self.city}
        """

