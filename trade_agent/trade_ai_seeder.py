#!/usr/bin/env python3
"""
trade_ai_seeder_full.py

Seeder for Trade AI Schema v3
Generates realistic fake data for buyers, suppliers, products, shipments, containers, payments, invoices, ports, vessel tracking, carbon emissions, port congestion, and shipping routes.
"""

import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta
from psycopg2.extras import Json


# -----------------------------
# Setup Faker and Seeds
# -----------------------------
fake = Faker()
Faker.seed(42)
random.seed(42)

# -----------------------------
# Database connection
# -----------------------------
conn = psycopg2.connect(
    dbname="trade_db_v3",
    user="postgres",
    password="123456",
    host="localhost",
    port="5432"
)
cur = conn.cursor()


# -------------------------
# EXISTING PREDEFINED EMAILS (for reference)
# -------------------------
EXISTING_EMAILS = [
    "vishal.yadav@gemsessence.com",
    "yogesh.kushwah@gemsessence.com",
    "kanak.gupta@gemsessence.com",
    "yogendra.prajapati@gemsessence.com",
    "ashish.tagwale@gemsessence.com",
    "sumit.sharma@gemsessence.com",
    "vishal.soni@gemsessence.com",
    "ritu.rekwar@gemsessence.com",
    "ankita.mandloi@gemsessence.com",
    "ishika.gadwe@gemsessence.com",
    "mohit.suryavanshi@gemsessence.com",
    "rahul.khatri@gemsessence.com",
    "priya.dubey@gemsessence.com",
    "aditya.pandey@gemsessence.com",
    "swati.tiwari@gemsessence.com",
    "vikas.chaudhary@gemsessence.com",
    "sneha.patel@gemsessence.com",
    "arjun.jain@gemsessence.com",
    "deepak.shukla@gemsessence.com",
    "komal.shrivastava@gemsessence.com",
    "manish.bera@gemsessence.com",
    "saurabh.rathore@gemsessence.com",
    "neha.jangid@gemsessence.com",
    "pankaj.saxena@gemsessence.com",
    "shruti.goswami@gemsessence.com",
    "abhay.sisodiya@gemsessence.com",
    "nidhi.khare@gemsessence.com",
    "sanjay.makwana@gemsessence.com",
    "pooja.rawat@gemsessence.com",
    "amar.singhal@gemsessence.com",
    "krishna.lodha@gemsessence.com",
    "harshil.modi@gemsessence.com",
    "sunil.kasera@gemsessence.com",
    "anjali.mittal@gemsessence.com",
    "kiran.rathod@gemsessence.com",
    "mahesh.prajapati@gemsessence.com",
    "jyoti.lodhi@gemsessence.com",
    "kuldeep.sengar@gemsessence.com",
    "preeti.kamble@gemsessence.com",
    "sagar.nayak@gemsessence.com",
    "nilesh.more@gemsessence.com",
    "meena.chaurasia@gemsessence.com",
    "amit.banerjee@gemsessence.com",
    "alok.mahajan@gemsessence.com",
    "reena.malhotra@gemsessence.com",
    "gaurav.bhadoria@gemsessence.com",
    "abhishek.trivedi@gemsessence.com",
    "john.doe@example.com",
    "jane.smith@example.com",
    "rajesh.sharma@tradeglobal.com",
    "priyanka.verma@exportershub.com",
    "amit.kumar@industrialsupply.com",
    "neha.gupta@tradingcorp.com",
    "sanjay.jain@globaltraders.com",
    "anita.singh@supplychain.com",
    "vivek.mishra@exportpartners.com",
    "pooja.yadav@tradeleaders.com",
    "rohit.choudhary@industryhub.com",
    "divya.agarwal@globalexports.com",
    "manoj.tiwari@tradenetwork.com",
    "sneha.reddy@supplyhub.com",
    "alok.singh@exportcorp.com",
    "kavita.malhotra@tradeconnect.com",
    "rahul.verma@industrysolutions.com",
    "sonal.mehta@globalpartners.com",
    "vikram.yadav@tradelink.com",
    "meera.patel@exportglobal.com",
    "anil.kumar@supplynetwork.com",
    "swati.sharma@tradealliance.com",
    "deepak.joshi@industryleaders.com",
    "ritu.gupta@globaltrading.com",
    "naveen.agarwal@exportenterprise.com",
    "monika.singh@tradepro.com",
    "harish.chandra@supplypro.com",
    "pallavi.mishra@globalhub.com",
    "suresh.yadav@exportnetwork.com",
    "kiran.verma@tradeventure.com",
    "ajay.tiwari@industrypro.com",
    "radhika.sharma@globalconnect.com",
    "karan.mehta@tradevision.com",
    "lata.sen@exportmatrix.com",
    "harshal.jain@supplyorbit.com",
    "mitali.pandey@logihub.com",
    "siddharth.rao@connecttrade.com",
    "bhavna.patel@exportlane.com",
    "varun.singh@tradexone.com",
    "shreya.kapoor@metalmovers.com",
    "gautam.nair@globalroutes.com",
    "riya.mehra@shipproconnect.com",
    "tarun.kumar@indusnetwork.com",
    "devika.sen@tradefusion.com",
    "suresh.patel@maritimeworld.com",
    "aarti.chaudhary@flowexport.com",
    "chetan.shah@blueoceantrade.com",
    "gauri.dave@exportflow.com",
    "naman.verma@tradesyncworld.com",
    "ridhi.singh@commercebase.com",
    "arjun.rathod@globalchain.com",
    "tanvi.parekh@exportline.com",
    "prateek.jain@megatradecorp.com",
    "shikha.agarwal@tradegear.com",
    "manav.thakur@supplyvista.com",
    "juhi.bhatt@exportorbit.com",
    "niraj.sharma@connectglobal.com",
    "nisha.jain@industrialtrade.com",
    "devansh.gupta@exportunit.com",
    "keshav.bhadoria@tradeportals.com",
    "rhea.patel@shiptrade.com",
    "amitabh.singh@tradelinkworld.com",
    "chiranjibi.das@zentrixel.com",
    "bhushan.dhonge@zentrixel.com",
    "vikram.mahapatra@zentrixel.com"
    
]

# -----------------------------
# Sample Data Lists / Dictionaries
# -----------------------------
countries = [
    "United States", "Germany", "China", "India", "Japan", "Brazil", "South Korea", "France", "Italy",
    "United Kingdom", "Canada", "Australia", "Singapore", "UAE", "Netherlands", "Spain", "Mexico",
    "Thailand", "Indonesia", "Vietnam", "Malaysia", "Saudi Arabia", "Turkey", "South Africa",
    "Egypt", "Russia", "Argentina", "Chile", "Bangladesh", "Pakistan", "Philippines", "New Zealand",
    "Belgium", "Sweden", "Norway", "Poland", "Denmark", "Portugal", "Switzerland", "Austria", "Greece",
    "Colombia", "Peru", "Nigeria", "Kenya"
]

country_codes = {
    "United States": "+1", "Germany": "+49", "China": "+86", "India": "+91", "Japan": "+81",
    "Brazil": "+55", "South Korea": "+82", "France": "+33", "Italy": "+39", "United Kingdom": "+44",
    "Canada": "+1", "Australia": "+61", "Singapore": "+65", "UAE": "+971", "Netherlands": "+31",
    "Spain": "+34", "Mexico": "+52", "Thailand": "+66", "Indonesia": "+62", "Vietnam": "+84",
    "Malaysia": "+60", "Saudi Arabia": "+966", "Turkey": "+90", "South Africa": "+27", "Egypt": "+20",
    "Russia": "+7", "Argentina": "+54", "Chile": "+56", "Bangladesh": "+880", "Pakistan": "+92",
    "Philippines": "+63", "New Zealand": "+64", "Belgium": "+32", "Sweden": "+46", "Norway": "+47",
    "Poland": "+48", "Denmark": "+45", "Portugal": "+351", "Switzerland": "+41", "Austria": "+43",
    "Greece": "+30", "Colombia": "+57", "Peru": "+51", "Nigeria": "+234", "Kenya": "+254"
}

CITIES = {
    "United States": ["New York", "Los Angeles", "Houston", "Miami", "Seattle", "Chicago", "San Francisco"],
    "Germany": ["Hamburg", "Frankfurt", "Berlin", "Munich", "Bremen", "Cologne", "Dusseldorf"],
    "China": ["Shanghai", "Shenzhen", "Guangzhou", "Tianjin", "Beijing", "Ningbo", "Qingdao"],
    "India": ["Mumbai", "Delhi", "Chennai", "Kolkata", "Bangalore", "Hyderabad", "Ahmedabad"],
    "Japan": ["Tokyo", "Osaka", "Yokohama", "Nagoya", "Kobe", "Kawasaki", "Chiba"],
    "Brazil": ["Sao Paulo", "Rio de Janeiro", "Salvador", "Brasilia", "Recife", "Fortaleza", "Manaus"],
    "South Korea": ["Busan", "Seoul", "Incheon", "Gwangju", "Daegu", "Ulsan", "Daejeon"],
    "France": ["Le Havre", "Marseille", "Paris", "Bordeaux", "Lyon", "Nice", "Toulouse"],
    "Italy": ["Genoa", "Venice", "Naples", "Trieste", "La Spezia", "Milano", "Palermo"],
    "United Kingdom": ["London", "Liverpool", "Southampton", "Felixstowe", "Bristol", "Manchester", "Glasgow"],
    "Canada": ["Vancouver", "Montreal", "Toronto", "Halifax", "Quebec City", "Calgary", "Edmonton"],
    "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth", "Adelaide", "Darwin", "Hobart"],
    "Singapore": ["Singapore"],
    "UAE": ["Dubai", "Abu Dhabi", "Sharjah"],
    "Netherlands": ["Rotterdam", "Amsterdam", "The Hague"],
    "Spain": ["Barcelona", "Valencia", "Madrid", "Bilbao"],
    "Mexico": ["Mexico City", "Guadalajara", "Monterrey"],
    "Thailand": ["Bangkok", "Laem Chabang", "Sri Racha"],
    "Indonesia": ["Jakarta", "Surabaya", "Medan", "Semarang", "Makassar"],
    "Vietnam": ["Ho Chi Minh City", "Hanoi", "Haiphong", "Da Nang"],
    "Malaysia": ["Kuala Lumpur", "Penang", "Johor Bahru", "Port Klang"],
    "Saudi Arabia": ["Riyadh", "Jeddah", "Dammam", "Mecca", "Medina"],
    "Turkey": ["Istanbul", "Ankara", "Izmir", "Antalya", "Bursa"],
    "South Africa": ["Cape Town", "Durban", "Johannesburg", "Port Elizabeth"],
    "Egypt": ["Cairo", "Alexandria", "Port Said", "Giza"],
    "Russia": ["Moscow", "St. Petersburg", "Novosibirsk", "Vladivostok"],
    "Argentina": ["Buenos Aires", "Córdoba", "Rosario", "Mendoza"],
    "Chile": ["Santiago", "Valparaiso", "Concepción"],
    "Bangladesh": ["Dhaka", "Chittagong", "Khulna"],
    "Pakistan": ["Karachi", "Lahore", "Islamabad", "Faisalabad"],
    "Philippines": ["Manila", "Cebu City", "Davao City"],
    "New Zealand": ["Auckland", "Wellington", "Christchurch"],
    "Belgium": ["Antwerp", "Brussels", "Ghent"],
    "Sweden": ["Stockholm", "Gothenburg", "Malmö"],
    "Norway": ["Oslo", "Bergen", "Stavanger"],
    "Poland": ["Warsaw", "Gdansk", "Krakow"],
    "Denmark": ["Copenhagen", "Aarhus", "Odense"]
}

FAKE_PRODUCT_LIST = [
    "Industrial Gear Systems", "Medical Equipment Parts", "Automotive Sensors",
    "Construction Steel Beams", "Agricultural Fertilizers", "Telecom Equipment",
    "Solar Inverters", "Wind Turbine Components", "Electric Vehicle Batteries",
    "Pharmaceutical Raw Materials", "Cosmetic Ingredients", "Packaging Machinery",
    "Robotic Arms", "3D Printing Filaments", "Semiconductor Chips",
    "LED Lighting Systems", "Water Purification Equipment", "Air Conditioning Units",
    "Industrial Pumps", "Hydraulic Systems", "Conveyor Belts",
    "Safety Equipment", "Fire Suppression Systems", "Laboratory Instruments",
    "Marine Equipment", "Aerospace Components", "Railway Parts",
    "Aerospace Parts", "Renewable Energy Equipment", "Mining Tools",
    "Oilfield Supplies", "Robotics Components", "Navigation Systems",
    "Cotton T-Shirts", "Men's Denim Jeans", "Sports Shoes", "Leather Wallets",
    "LED Televisions", "Mobile Phone Covers", "Bluetooth Earbuds",
    "Office Chairs", "Wooden Furniture", "Plastic Storage Boxes",
    "Ceramic Dinner Plates", "Stainless Steel Bottles", "Kitchen Cookware Set",
    "Organic Green Tea", "Packaged Basmati Rice", "Instant Coffee Mix",
    "Olive Oil", "Frozen Vegetables", "Pet Food Pack", "Baby Diapers",
    "Hand Sanitizer", "Cosmetic Lipstick", "Skin Care Moisturizer",
    "Hair Shampoo", "Notebook Paper A4", "Ballpoint Pens", "Laptop Bags",
    "Travel Suitcases", "Car Seat Covers", "Machine Spare Parts",
    "Steel Pipes", "Plastic Raw Material", "Copper Wires", "Electronic Chips",
    "Solar Panels", "Battery Packs", "Medical Gloves", "Surgical Masks",
    "Pharmaceutical Tablets", "Organic Chemicals", "PVC Granules",
    "Construction Cement", "Building Bricks", "Natural Marble Tiles",
    "Granite Slabs", "Cotton Yarn", "Textile Fabric Rolls", "Rubber Sheets",
    "Packaging Cartons", "Glass Bottles", "Aluminum Foils", "Wooden Pallets",
    "Industrial Adhesives", "Cleaning Chemicals", "Pest Control Products",
    "Welding Machines", 
    "High-Pressure Hydraulic Valves",
    "Industrial Conveyor Rollers",
    "Automotive Brake Assemblies",
    "Pharmaceutical Filtration Units",
    "Medical-Grade Syringes",
    "Electronic Control Modules",
    "Graphite Electrodes",
    "Copper Winding Wires",
    "Cryogenic Storage Tanks",
    "Laser Cutting Machines",
    "Plastic Injection Moulds",
    "Food Processing Mixers",
    "Cold Storage Compressors",
    "Heavy Duty Chains",
    "Industrial Air Blowers",
    "Biodegradable Packaging Films",
    "Synthetic Lubricants",
    "Alloy Steel Forgings",
    "Precision CNC Tools",
    "Aerospace Fastener Kits",
    "Composite Fiber Sheets",
    "Industrial Gas Regulators",
    "Smart Meter Devices",
    "Automotive Fuel Pumps",
    "Bulk Chemicals—Solvents",
    "Agricultural Drip Systems",
    "High-Tensile Steel Rods",
    "Stainless Steel Fasteners",
    "Industrial Heat Exchangers",
    "HVAC Control Panels",
    "Solar Mounting Structures",
    "Battery Management Systems",
    "Oil & Gas Drilling Tools",
    "Fire-Retardant Sheets",
    "Marine Lubrication Systems",
    "Wind Energy Controllers",
    "LED Display Modules",
    "Telecom Antenna Parts",
    "Precision Bearing Units",
]

industries = ["Electronics","Textiles","Automotive","Pharma","Agriculture","Machinery","Food & Beverage","Chemicals","Metals","Logistics"]
first_names = ["alex","michael","sarah","david","lisa","robert","maria","james","emma","william","john","olivia","daniel","sophia","andrew","grace","kevin","chloe","ryan","hannah","noah","ava","ethan","mia","nathan","isabella","jackson","amelia","logan","ella"]
last_names = ["johnson","brown","garcia","martinez","lee","wilson","anderson","thomas","taylor","moore","martin","clark","walker","hall","allen","young","hernandez","king","wright","lopez","scott","green","adams","baker","nelson","carter","mitchell","roberts","turner","phillips"]

colors = ["Red","Blue","Green","Black","White","Silver","Gray","Yellow","Orange","Brown","Beige","Navy","Copper","Gold"]
materials = ["Stainless Steel","ABS Plastic","100% Cotton","Solid Wood","Genuine Leather","Aluminum","Carbon Fiber","Polycarbonate","Reinforced Steel","Rubber","Ceramic","Glass","Nylon"]
grades = ["A","B","Premium","Commercial","Industrial","Military","Food Grade","Medical Grade"]

# Other lists (buyers, suppliers, ports, carriers, etc.)
BUYER_INDUSTRIES = ["Retail","Wholesale","E-commerce","Manufacturing","Pharmaceuticals","Construction","Food & Beverage","Automotive","Electronics","Textiles","Healthcare","Energy","Telecom","Logistics","Real Estate"]
SUPPLIER_BUSINESS_TYPES = ["Manufacturer","Exporter","Trader","Distributor","Wholesaler","Retailer","Service Provider","Contractor","OEM","Importer"]
carrier_names = ["Maersk Line","Mediterranean Shipping","CMA CGM Group","COSCO Shipping","Hapag-Lloyd","Evergreen Marine","Ocean Network Express","Yang Ming Marine","Hyundai Merchant Marine","Zim Integrated Shipping"]
port_types = ["Seaport","Airport","Rail Terminal","Inland Terminal","Dry Port","River Port","Container Terminal","Bulk Cargo Port","Oil Terminal","Gas Terminal"]
quantity_units = ['kg','pcs','liters','tons']
INVOICE_STATUS = ["paid", "partially_paid", "unpaid"]


def random_email():
    return random.choice(EXISTING_EMAILS) if random.random() < 0.5 else fake.email()

def fake_product():
    return random.choice(FAKE_PRODUCT_LIST)
# -----------------------------
# Insert Buyers
# -----------------------------
buyers_ids = []
for _ in range(100):
    country = random.choice(countries)
    cur.execute("""
        INSERT INTO buyers (name, address, city, state, country, contact_email, phone, website, industry_type, gst_number, registration_date)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
    """, (
        f"{fake.first_name()} {fake.last_name()}",
        fake.street_address(),
        fake.city(),
        fake.state(),
        country,
        random_email(),
        fake.phone_number(),
        fake.url(),
        random.choice(industries),
        fake.bothify(text="??######???"),
        fake.date_between(start_date='-5y', end_date='today')
    ))
    buyers_ids.append(cur.fetchone()[0])
conn.commit()

# -----------------------------
# Insert Suppliers
# -----------------------------
suppliers_ids = []
for _ in range(100):
    country = random.choice(countries)
    cur.execute("""
        INSERT INTO suppliers (name, address, city, state, country, contact_email, phone, website, business_type, gst_number, rating)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
    """, (
        fake.company(),
        fake.street_address(),
        fake.city(),
        fake.state(),
        country,
        random_email(),
        fake.phone_number(),
        fake.url(),
        random.choice(industries),
        fake.bothify(text="??######???"),
        round(random.uniform(1,5),2)
    ))
    suppliers_ids.append(cur.fetchone()[0])
conn.commit()

# -----------------------------
# Insert Ports
# -----------------------------
ports_ids = []
for _ in range(50):
    country = random.choice(countries)
    cur.execute("""
        INSERT INTO ports (port_code, port_name, country, city, type)
        VALUES (%s,%s,%s,%s,%s) RETURNING id
    """, (
        fake.unique.bothify(text="???###"),
        fake.company(),
        country,
        fake.city(),
        random.choice(port_types)
    ))
    ports_ids.append(cur.fetchone()[0])
conn.commit()

# -----------------------------
# Insert Products
# -----------------------------
products_ids = []
for _ in range(150):
    supplier_id = random.choice(suppliers_ids)
    cur.execute("""
        INSERT INTO products (hs_code, hs_description, product_name, category, subcategory, attributes, unit_price_usd, available_stock, supplier_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
    """, (
        f"{random.randint(1000,9999)}.{random.randint(10,99)}",
        fake.sentence(),
        random.choice(FAKE_PRODUCT_LIST),
        random.choice(industries),
        random.choice(["Raw Material","Finished Goods","Components","Equipment"]),
        Json({
            "color": random.choice(colors),
            "material": random.choice(materials),
            "grade": random.choice(grades),
            "weight": f"{random.randint(1,500)} kg",
            "origin": random.choice(countries)
        }),
        round(random.uniform(10,1000),2),
        random.randint(10,5000),
        supplier_id
    ))
    products_ids.append(cur.fetchone()[0])
conn.commit()

# -----------------------------
# Insert Shipments
# -----------------------------
shipments_ids = []
for _ in range(200):
    product_id = random.choice(products_ids)
    supplier_id = random.choice(suppliers_ids)
    buyer_id = random.choice(buyers_ids)
    port_of_loading = random.choice(ports_ids)
    port_of_discharge = random.choice(ports_ids)
    cur.execute("""
        INSERT INTO shipments (bill_of_lading_no, shipment_type, date, hs_code, shipment_description, product_id,
                               quantity, quantity_unit, weight_kg, value_usd, origin_country, destination_country,
                               port_of_loading, port_of_discharge, mode, container_count, carrier_name, supplier_id,
                               buyer_id, shipment_status, expected_delivery_date, tracking_url)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
    """, (
        fake.unique.bothify(text="BL#####"),
        random.choice(["Import","Export"]),
        fake.date_between(start_date='-2y', end_date='today'),
        f"{random.randint(1000,9999)}.{random.randint(10,99)}",
        fake.sentence(),
        product_id,
        random.randint(1,1000),
        random.choice(quantity_units),
        random.randint(100,10000),
        round(random.uniform(500,50000),2),
        random.choice(countries),
        random.choice(countries),
        port_of_loading,
        port_of_discharge,
        random.choice(["Sea","Air","Rail","Road"]),
        random.randint(1,10),
        random.choice(carrier_names),
        supplier_id,
        buyer_id,
        random.choice(["in_transit","delivered","pending"]),
        fake.date_between(start_date='today', end_date='+90d'),
        fake.url()
    ))
    shipments_ids.append(cur.fetchone()[0])
conn.commit()

# -----------------------------
# Insert Shipment Events
# -----------------------------
for shipment_id in shipments_ids:
    for _ in range(random.randint(1,4)):
        cur.execute("""
            INSERT INTO shipment_events (shipment_id, event_type, event_timestamp, location, remarks)
            VALUES (%s,%s,%s,%s,%s)
        """, (
            shipment_id,
            random.choice(['Loaded','Dispatched','In Transit','Arrived at Port','Customs Clearance']),
            fake.date_time_this_year(),
            fake.city(),
            fake.sentence()
        ))
conn.commit()

# -----------------------------
# Insert Containers
# -----------------------------
for shipment_id in shipments_ids:
    for _ in range(random.randint(1,3)):
        cur.execute("""
            INSERT INTO containers (container_number, container_type, capacity_cubic_m, shipment_id, status, last_location)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (
            fake.unique.bothify(text='C#######'),
            random.choice(['20ft','40ft','Reefer','Open Top','Tank']),
            random.randint(10,100),
            shipment_id,
            random.choice(['in_transit','delivered']),
            fake.city()
        ))
conn.commit()

# -----------------------------
# Insert Invoices & Payments
# -----------------------------
invoices_ids = []
for shipment_id in shipments_ids:
    status = random.choice(INVOICE_STATUS)
    paid_flag = True if status == "paid" else False

    cur.execute("""
        INSERT INTO invoices (shipment_id, invoice_number, invoice_date, amount_usd, paid, notes)
        VALUES (%s,%s,%s,%s,%s,%s) RETURNING id
    """, (
        shipment_id,
        fake.unique.bothify(text="INV#####"),
        fake.date_this_year(),
        round(random.uniform(500,50000),2),
        paid_flag,
        fake.sentence()
    ))
    invoice_id = cur.fetchone()[0]
    invoices_ids.append(invoice_id)

    # Payment for each invoice
    cur.execute("""
        INSERT INTO payments (invoice_id, payment_date, amount_usd, payment_method, status, transaction_id, notes)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        invoice_id,
        fake.date_this_year(),
        round(random.uniform(500,50000),2),
        random.choice(['Wire Transfer','Credit Card','PayPal','Bank Draft']),
        random.choice(['pending','completed','failed']),
        fake.bothify(text='TXN#####'),
        fake.sentence()
    ))
conn.commit()

# -----------------------------
# Insert Vessel Tracking
# -----------------------------
for _ in range(50):
    cur.execute("""
        INSERT INTO vessel_tracking (vessel_name, voyage_number, current_location, speed_knots, heading)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        fake.company(),
        fake.bothify(text='VY#####'),
        fake.city(),
        round(random.uniform(10,30),2),
        random.choice(['N','S','E','W','NE','NW','SE','SW'])
    ))
conn.commit()

# -----------------------------
# Insert Carbon Emissions
# -----------------------------
for shipment_id in shipments_ids:
    cur.execute("""
        INSERT INTO carbon_emissions (shipment_id, co2_emission_kg, emission_source)
        VALUES (%s,%s,%s)
    """, (
        shipment_id,
        round(random.uniform(100,10000),2),
        random.choice(['Sea','Air','Road','Rail'])
    ))
conn.commit()

# -----------------------------
# Insert Port Congestion
# -----------------------------
for port_id in ports_ids:
    cur.execute("""
        INSERT INTO port_congestion (port_id, congestion_level, ships_waiting, average_wait_time_hours)
        VALUES (%s,%s,%s,%s)
    """, (
        port_id,
        random.choice(['Low','Medium','High','Critical']),
        random.randint(0,50),
        round(random.uniform(1,72),2)
    ))
conn.commit()

# -----------------------------
# Insert Shipping Routes
# -----------------------------
for _ in range(50):
    cur.execute("""
        INSERT INTO shipping_routes (origin_port, destination_port, distance_km, average_duration_days, carrier_name)
        VALUES (%s,%s,%s,%s,%s)
    """, (
        random.choice(ports_ids),
        random.choice(ports_ids),
        round(random.uniform(100,20000),2),
        random.randint(1,60),
        random.choice(carrier_names)
    ))
conn.commit()

# -----------------------------
# Close Connection
# -----------------------------
cur.close()
conn.close()
print("Fake data inserted successfully for trade_db_v4!")