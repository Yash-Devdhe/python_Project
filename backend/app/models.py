from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
import datetime as dt

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    sku = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True)
    price = Column(Float)

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    customer_id = Column(String, unique=True, index=True)
    name = Column(String)
    email = Column(String, index=True)
    region = Column(String, index=True)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    order_id = Column(String, unique=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    customer_id = Column(Integer, ForeignKey("customers.id"))
    quantity = Column(Integer)
    revenue = Column(Float)
    order_date = Column(DateTime, index=True)

    product = relationship("Product")
    customer = relationship("Customer")
