from typing import Optional
from datetime import date, datetime
from os import environ
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlalchemy import Column, Integer, String, Date, DateTime, Float, ForeignKey

def connect():
    sqlite_url = f"sqlite:///{environ.get('DATABASE_PATH')}"
    connect_args = {"check_same_thread": False}
    engine = create_engine(sqlite_url, connect_args=connect_args)
    return engine

def get_data(engine):
    with Session(engine) as session:
        query = select(Orders, Customers, Employees) \
            .join(Customers, Orders.customer_id == Customers.customer_id) \
            .join(Employees, Orders.employee_id == Employees.employee_id) \
            .order_by(Orders.order_date)
        results = session.exec(query).all()
        return results

class Categories(SQLModel, table=True):
    __tablename__ = "categories"
    category_id: Optional[int] = Field(
        sa_column=Column("CategoryID", Integer, primary_key=True)
    )
    category_name: Optional[str] = Field(
        default=None,
        sa_column=Column("CategoryName", String)
    )
    description: Optional[str] = Field(
        default=None,
        sa_column=Column("Description", String)
    )

class Customers(SQLModel, table=True):
    __tablename__ = "customers"
    customer_id: Optional[int] = Field(
        sa_column=Column("CustomerID", Integer, primary_key=True)
    )
    customer_name: Optional[str] = Field(
        default=None,
        sa_column=Column("CustomerName", String)
    )
    contact_name: Optional[str] = Field(
        default=None,
        sa_column=Column("ContactName", String)
    )
    address: Optional[str] = Field(
        default=None,
        sa_column=Column("Address", String)
    )
    city: Optional[str] = Field(
        default=None,
        sa_column=Column("City", String)
    )
    postal_code: Optional[str] = Field(
        default=None,
        sa_column=Column("PostalCode", String)
    )
    country: Optional[str] = Field(
        default=None,
        sa_column=Column("Country", String)
    )

class Employees(SQLModel, table=True):
    __tablename__ = "employees"
    employee_id: Optional[int] = Field(
        sa_column=Column("EmployeeID", Integer, primary_key=True)
    )
    last_name: Optional[str] = Field(
        default=None,
        sa_column=Column("LastName", String)
    )
    first_name: Optional[str] = Field(
        default=None,
        sa_column=Column("FirstName", String)
    )
    birth_date: Optional[date] = Field(
        default=None,
        sa_column=Column("BirthDate", Date)
    )
    photo: Optional[str] = Field(
        default=None,
        sa_column=Column("Photo", String)
    )
    notes: Optional[str] = Field(
        default=None,
        sa_column=Column("Notes", String)
    )

class Shippers(SQLModel, table=True):
    __tablename__ = "shippers"
    shipper_id: Optional[int] = Field(
        sa_column=Column("ShipperID", Integer, primary_key=True)
    )
    shipper_name: Optional[str] = Field(
        default=None,
        sa_column=Column("ShipperName", String)
    )
    phone: Optional[str] = Field(
        default=None,
        sa_column=Column("Phone", String)
    )

class Suppliers(SQLModel, table=True):
    __tablename__ = "suppliers"
    supplier_id: Optional[int] = Field(
        sa_column=Column("SupplierID", Integer, primary_key=True)
    )
    supplier_name: Optional[str] = Field(
        default=None,
        sa_column=Column("SupplierName", String)
    )
    contact_name: Optional[str] = Field(
        default=None,
        sa_column=Column("ContactName", String)
    )
    address: Optional[str] = Field(
        default=None,
        sa_column=Column("Address", String)
    )
    city: Optional[str] = Field(
        default=None,
        sa_column=Column("City", String)
    )
    postal_code: Optional[str] = Field(
        default=None,
        sa_column=Column("PostalCode", String)
    )
    country: Optional[str] = Field(
        default=None,
        sa_column=Column("Country", String)
    )
    phone: Optional[str] = Field(
        default=None,
        sa_column=Column("Phone", String)
    )

class Products(SQLModel, table=True):
    __tablename__ = "products"
    product_id: Optional[int] = Field(
        sa_column=Column("ProductID", Integer, primary_key=True)
    )
    product_name: Optional[str] = Field(
        default=None,
        sa_column=Column("ProductName", String)
    )
    supplier_id: Optional[int] = Field(
        default=None,
        sa_column=Column("SupplierID", Integer, ForeignKey("suppliers.SupplierID"))
    )
    category_id: Optional[int] = Field(
        default=None,
        sa_column=Column("CategoryID", Integer, ForeignKey("categories.CategoryID"))
    )
    unit: Optional[str] = Field(
        default=None,
        sa_column=Column("Unit", String)
    )
    price: Optional[float] = Field(
        default=0,
        sa_column=Column("Price", Float)
    )

class Orders(SQLModel, table=True):
    __tablename__ = "orders"
    order_id: Optional[int] = Field(
        sa_column=Column("OrderID", Integer, primary_key=True)
    )
    customer_id: Optional[int] = Field(
        default=None,
        sa_column=Column("CustomerID", Integer, ForeignKey("customers.CustomerID"))
    )
    employee_id: Optional[int] = Field(
        default=None,
        sa_column=Column("EmployeeID", Integer, ForeignKey("employees.EmployeeID"))
    )
    order_date: Optional[datetime] = Field(
        default=None,
        sa_column=Column("OrderDate", DateTime)
    )
    shipper_id: Optional[int] = Field(
        default=None,
        sa_column=Column("ShipperID", Integer, ForeignKey("shippers.ShipperID"))
    )

class OrderDetails(SQLModel, table=True):
    __tablename__ = "orderdetails"
    order_detail_id: Optional[int] = Field(
        sa_column=Column("OrderDetailID", Integer, primary_key=True)
    )
    order_id: Optional[int] = Field(
        default=None,
        sa_column=Column("OrderID", Integer, ForeignKey("orders.OrderID"))
    )
    product_id: Optional[int] = Field(
        default=None,
        sa_column=Column("ProductID", Integer, ForeignKey("products.ProductID"))
    )
    quantity: Optional[int] = Field(
        default=None,
        sa_column=Column("Quantity", Integer)
    )
