from sqlalchemy import Column, Integer, Text, Date, Numeric, ForeignKey, JSON
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# -----------------------------
# SUPPLIER
# -----------------------------
class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    address = Column(Text)
    city = Column(Text)
    state = Column(Text)
    country = Column(Text)
    contact_email = Column(Text)
    phone = Column(Text)
    website = Column(Text)
    business_type = Column(Text)

    shipments = relationship("Shipment", back_populates="supplier")

# -----------------------------
# BUYER
# -----------------------------
class Buyer(Base):
    __tablename__ = "buyers"
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    address = Column(Text)
    city = Column(Text)
    state = Column(Text)
    country = Column(Text)
    contact_email = Column(Text)
    phone = Column(Text)
    website = Column(Text)
    industry_type = Column(Text)

    shipments = relationship("Shipment", back_populates="buyer")

# -----------------------------
# PRODUCT
# -----------------------------
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    hs_code = Column(Text)
    hs_description = Column(Text)
    product_name = Column(Text)
    category = Column(Text)
    subcategory = Column(Text)
    attributes = Column(JSON)

# -----------------------------
# PORT (missing earlier)
# -----------------------------
class Port(Base):
    __tablename__ = "ports"
    id = Column(Integer, primary_key=True)
    port_code = Column(Text)
    port_name = Column(Text)
    country = Column(Text)
    city = Column(Text)
    type = Column(Text)

# -----------------------------
# SHIPMENT
# -----------------------------
class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True)
    bill_of_lading_no = Column(Text)
    shipment_type = Column(Text)
    mode = Column(Text)
    date = Column(Date)

    hs_code = Column(Text)
    product_description = Column(Text)

    quantity = Column(Numeric)
    quantity_unit = Column(Text)
    weight_kg = Column(Numeric)
    value_usd = Column(Numeric)

    origin_country = Column(Text)
    destination_country = Column(Text)

    # These were missing in your model
    port_of_loading = Column(Text)
    port_of_discharge = Column(Text)

    container_count = Column(Integer)
    carrier_name = Column(Text)

    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    buyer_id = Column(Integer, ForeignKey("buyers.id"))

    supplier = relationship("Supplier", back_populates="shipments")
    buyer = relationship("Buyer", back_populates="shipments")
