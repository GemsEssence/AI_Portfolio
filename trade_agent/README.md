# Trade Ai Agent
## folder structure 
``` bash
trade_agent/
│
├── .env                     # Configuration keys (API, DB, Email)
├── requirements.txt         # List of libraries to install
├── main.py                  # The entry point (FastAPI Server)
│
├── database/                # Database Logic
│   ├── __init__.py          # (Create an empty file with this name)
│   ├── connection.py        # Connects to DB & seeds fake data
│   └── models.py            # Database Table definitions
│
├── services/                # Business Logic
│   ├── __init__.py          # (Create an empty file with this name)
│   ├── agent_service.py     # The AI Agent (Gemini)
│   └── email_service.py     # Email sending logic
│
└── templates/               # Frontend UI
    └── index.html           # The Dashboard & Chatbot HTML
    └── chatbot.html 

```
### Installation & Setup

###  Clone the repository
 ``` bash
git clone https://github.com/GemsEssence/AI_Portfolio.git
cd trade_agent
```
### Create and activate a virtual environment
``` bash
python -m venv venv
source venv/bin/activate        # (On Windows: venv\Scripts\activate)
```

### Install dependencies
``` bash
pip install -r requirements.txt
```

### Create data base
```bash 
CREATE DATABASE trade_ai_db;
```
### Connect to the database:
```bash
\c trade_ai_db
```
### Create Tables
### 1. buyers
``` bash
CREATE TABLE buyers (
    id SERIAL PRIMARY KEY,
    name TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    contact_email TEXT,
    phone TEXT,
    website TEXT,
    industry_type TEXT
);
```
### 2. ports
``` bash
CREATE TABLE ports (
    id SERIAL PRIMARY KEY,
    port_code TEXT,
    port_name TEXT,
    country TEXT,
    city TEXT,
    type TEXT
);

```
### 3. products
``` bash
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    hs_code TEXT,
    hs_description TEXT,
    product_name TEXT,
    category TEXT,
    subcategory TEXT,
    attributes JSON
);

```
### 4. search_logs
``` bash
CREATE TABLE search_logs (
    id SERIAL PRIMARY KEY,
    user_id TEXT,
    query_text TEXT,
    generated_sql TEXT,
    response_time_ms INTEGER,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

```
### 5. suppliers
``` bash
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    country TEXT,
    contact_email TEXT,
    phone TEXT,
    website TEXT,
    business_type TEXT
);
```
### 6. shipments
``` bash
CREATE TABLE shipments (
    id SERIAL PRIMARY KEY,
    bill_of_lading_no TEXT,
    shipment_type TEXT,
    date DATE,
    hs_code TEXT,
    product_description TEXT,
    quantity NUMERIC,
    quantity_unit TEXT,
    weight_kg NUMERIC,
    value_usd NUMERIC,
    origin_country TEXT,
    destination_country TEXT,
    port_of_loading TEXT,
    port_of_discharge TEXT,
    mode TEXT,
    container_count INTEGER,
    carrier_name TEXT,
    supplier_id INTEGER REFERENCES suppliers(id),
    buyer_id INTEGER REFERENCES buyers(id)
);
```


### Create a .env file and add your API key
``` bash
GEMINI_API_KEY=your_gemini_api_key_here
# DB
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trade_ai_db
DB_USER=postgres
DB_PASSWORD=password

# EMAIL
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USER=xyz@gemsessence.com
EMAIL_PASSWORD="password"
```


### Running the App

Start the FastAPI development server:
``` bash
uvicorn main:app --reload

```

### Now open your browser and visit:
👉 http://127.0.0.1:8000




