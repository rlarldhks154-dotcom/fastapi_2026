from sqlalchemy import (
    Column, String, Integer, DateTime, Numeric, UniqueConstraint
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Menu(Base):
    __tablename__ = 'menu'

    메뉴코드 = Column(String(10), primary_key=True)
    메뉴명 = Column(String(50), nullable=False)
    가격 = Column(Integer, nullable=False)

    def __repr__(self):
        return f'<Menu {self.메뉴코드} {self.메뉴명} {self.가격}>'


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    주문일시 = Column(DateTime, nullable=False)
    테이블번호 = Column(Integer, nullable=False)
    메뉴코드 = Column(String(10), nullable=False)
    수량 = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint('주문일시', '테이블번호', '메뉴코드', name='uq_orders_key'),
    )

    def __repr__(self):
        return f'<Order {self.주문일시} T{self.테이블번호} {self.메뉴코드} x{self.수량}>'