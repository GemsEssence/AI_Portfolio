import os
import google.generativeai as genai
from dotenv import load_dotenv
from database.connection import engine
from sqlalchemy import text
from services.email_service import send_report_email

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# ------------ SCHEMA FUNCTION ------------
def get_db_schema():
    return """
    suppliers(
        id, name, address, city, state, country,
        contact_email, phone, website, business_type
    )

    buyers(
        id, name, address, city, state, country,
        contact_email, phone, website, industry_type
    )

    products(
        id, hs_code, hs_description,
        product_name, category, subcategory, attributes
    )

    shipments(
        id, bill_of_lading_no, shipment_type, mode, date,
        hs_code, product_description,
        quantity, quantity_unit, weight_kg, value_usd,
        origin_country, destination_country,
        port_of_loading, port_of_discharge,
        container_count, carrier_name,
        supplier_id, buyer_id
    )

    JOIN RULES:
    shipments.supplier_id → suppliers.id
    shipments.buyer_id → buyers.id
    shipments.hs_code → products.hs_code
    """



def run_sql_query(sql: str):
    import decimal
    import datetime

    # Block unsafe SQL
    forbidden = ["drop", "delete", "update", "insert", "alter", "truncate"]
    if any(word in sql.lower() for word in forbidden):
        return "❌ READ-ONLY MODE — dangerous SQL blocked."

    try:
        print("📝 EXECUTING SQL QUERY:", sql)
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = []

            for row in result:
                row_dict = {}

                for key, value in row._mapping.items():

                    if isinstance(value, decimal.Decimal):
                        row_dict[key] = float(value)
                        
                    elif isinstance(value, (datetime.date, datetime.datetime)):
                        row_dict[key] = value.isoformat()

                    else:
                        row_dict[key] = value

                rows.append(row_dict)

            return rows if rows else "No results."

    except Exception as e:
        return f"SQL Error: {e}"

# ------------ BUILD AI AGENT ------------
def build_agent():

    tools = [
        get_db_schema,
        run_sql_query,
        send_report_email
    ]

    return genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        tools=tools,
        system_instruction="""
You are a smart SQL + Email Agent.

RULES:
1. ALWAYS inspect database schema using get_db_schema().
2. ALWAYS use run_sql_query() for SQL queries.
3. If SQL contains Decimal values, convert them using float().
4. When the user asks anything related to emails:
   - draft email
   - write email
   - preview email
   You MUST call send_report_email(recipient, subject, body, preview=True)
   to generate a preview first.
5. NEVER send email automatically.
6. After the user confirms sending, call send_report_email(recipient, subject, body, preview=False)
7. Always return the function_call result.
""")   


agent = build_agent()
chat = agent.start_chat(enable_automatic_function_calling=True)


# ------------ MAIN ASK FUNCTION ------------
def ask_agent(query: str):
    print("\n🤖 SENDING QUERY TO GEMINI:", query)

    response = chat.send_message(query)

    print("🔧 RAW MODEL RESPONSE:", response)
    print("🔎 TEXT OUTPUT:", response.text)
    print("=================================\n")
    return response.text
