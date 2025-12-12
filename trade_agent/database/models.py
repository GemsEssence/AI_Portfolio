from sqlalchemy import (
    Column, Integer, Text, Date, Numeric, ForeignKey, JSON, Boolean, DateTime
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# -----------------------------
# BUYER
# -----------------------------
class Buyer(Base):
    __tablename__ = "buyers"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    address = Column(Text)
    city = Column(Text)
    state = Column(Text)
    country = Column(Text)
    contact_email = Column(Text)
    phone = Column(Text)
    website = Column(Text)
    industry_type = Column(Text)
    gst_number = Column(Text)
    registration_date = Column(Date)
    status = Column(Text, default="active")

    shipments = relationship("Shipment", back_populates="buyer")


# -----------------------------
# SUPPLIER
# -----------------------------
class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    address = Column(Text)
    city = Column(Text)
    state = Column(Text)
    country = Column(Text)
    contact_email = Column(Text)
    phone = Column(Text)
    website = Column(Text)
    business_type = Column(Text)
    gst_number = Column(Text)
    rating = Column(Numeric(3, 2))
    status = Column(Text, default="active")

    shipments = relationship("Shipment", back_populates="supplier")
    products = relationship("Product", back_populates="supplier")


# -----------------------------
# PRODUCT
# -----------------------------
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    hs_code = Column(Text)
    hs_description = Column(Text)
    product_name = Column(Text, nullable=False)
    category = Column(Text)
    subcategory = Column(Text)
    attributes = Column(JSON)
    unit_price_usd = Column(Numeric)
    available_stock = Column(Numeric)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="SET NULL"))

    supplier = relationship("Supplier", back_populates="products")
    shipments = relationship("Shipment", back_populates="product")


# -----------------------------
# PORT
# -----------------------------
class Port(Base):
    __tablename__ = "ports"
    id = Column(Integer, primary_key=True)
    port_code = Column(Text, unique=True, nullable=False)
    port_name = Column(Text, nullable=False)
    country = Column(Text)
    city = Column(Text)
    type = Column(Text)


# -----------------------------
# SHIPMENT
# -----------------------------
class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True)
    bill_of_lading_no = Column(Text, unique=True)
    shipment_type = Column(Text)
    date = Column(Date)
    hs_code = Column(Text)
    product_description = Column(Text)

    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"))

    quantity = Column(Numeric)
    quantity_unit = Column(Text)
    weight_kg = Column(Numeric)
    value_usd = Column(Numeric)
    origin_country = Column(Text)
    destination_country = Column(Text)

    port_of_loading = Column(Integer, ForeignKey("ports.id"))
    port_of_discharge = Column(Integer, ForeignKey("ports.id"))

    mode = Column(Text)
    container_count = Column(Integer)
    carrier_name = Column(Text)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="SET NULL"))
    buyer_id = Column(Integer, ForeignKey("buyers.id", ondelete="SET NULL"))
    shipment_status = Column(Text, default="in_transit")
    expected_delivery_date = Column(Date)
    tracking_url = Column(Text)

    supplier = relationship("Supplier", back_populates="shipments")
    buyer = relationship("Buyer", back_populates="shipments")
    product = relationship("Product", back_populates="shipments")
    events = relationship("ShipmentEvent", back_populates="shipment")
    containers = relationship("Container", back_populates="shipment")
    payments = relationship("Payment", back_populates="shipment")
    invoices = relationship("Invoice", back_populates="shipment")
    carbon_emissions = relationship("CarbonEmission", back_populates="shipment")


# -----------------------------
# SHIPMENT EVENTS
# -----------------------------
class ShipmentEvent(Base):
    __tablename__ = "shipment_events"
    id = Column(Integer, primary_key=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id", ondelete="CASCADE"))
    event_type = Column(Text)
    event_timestamp = Column(DateTime, default=datetime.utcnow)
    location = Column(Text)
    remarks = Column(Text)

    shipment = relationship("Shipment", back_populates="events")


# -----------------------------
# CONTAINERS
# -----------------------------
class Container(Base):
    __tablename__ = "containers"
    id = Column(Integer, primary_key=True)
    container_number = Column(Text, unique=True)
    container_type = Column(Text)
    capacity_cubic_m = Column(Numeric)
    shipment_id = Column(Integer, ForeignKey("shipments.id", ondelete="SET NULL"))
    status = Column(Text, default="in_transit")
    last_location = Column(Text)
    last_update = Column(DateTime, default=datetime.utcnow)

    shipment = relationship("Shipment", back_populates="containers")


# -----------------------------
# PAYMENTS
# -----------------------------
class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id", ondelete="CASCADE"))  # ✅ Add this
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=True)
    payment_date = Column(Date)
    amount_usd = Column(Numeric)
    payment_method = Column(Text)
    status = Column(Text, default="pending")
    transaction_id = Column(Text)
    notes = Column(Text)

    shipment = relationship("Shipment", back_populates="payments")
    invoice = relationship("Invoice", back_populates="payments")



# -----------------------------
# INVOICES
# -----------------------------
class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id", ondelete="CASCADE"))
    invoice_number = Column(Text, unique=True)
    invoice_date = Column(Date)
    amount_usd = Column(Numeric)
    paid = Column(Boolean, default=False)
    notes = Column(Text)

    shipment = relationship("Shipment", back_populates="invoices")
    payments = relationship("Payment", back_populates="invoice")  # ✅ Add this for reverse relation



# -----------------------------
# SHIPPING ROUTES
# -----------------------------
class ShippingRoute(Base):
    __tablename__ = "shipping_routes"
    id = Column(Integer, primary_key=True)
    origin_port = Column(Integer, ForeignKey("ports.id"))
    destination_port = Column(Integer, ForeignKey("ports.id"))
    distance_km = Column(Numeric)
    average_duration_days = Column(Integer)
    carrier_name = Column(Text)


# -----------------------------
# PORT CONGESTION
# -----------------------------
class PortCongestion(Base):
    __tablename__ = "port_congestion"
    id = Column(Integer, primary_key=True)
    port_id = Column(Integer, ForeignKey("ports.id"))
    congestion_level = Column(Text)
    ships_waiting = Column(Integer)
    average_wait_time_hours = Column(Numeric)
    recorded_at = Column(DateTime, default=datetime.utcnow)


# -----------------------------
# VESSEL TRACKING
# -----------------------------
class VesselTracking(Base):
    __tablename__ = "vessel_tracking"
    id = Column(Integer, primary_key=True)
    vessel_name = Column(Text)
    voyage_number = Column(Text)
    current_location = Column(Text)
    speed_knots = Column(Numeric)
    heading = Column(Text)
    last_update = Column(DateTime, default=datetime.utcnow)


# -----------------------------
# CARBON EMISSIONS
# -----------------------------
class CarbonEmission(Base):
    __tablename__ = "carbon_emissions"
    id = Column(Integer, primary_key=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id", ondelete="CASCADE"))
    co2_emission_kg = Column(Numeric)
    emission_source = Column(Text)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    shipment = relationship("Shipment", back_populates="carbon_emissions")
