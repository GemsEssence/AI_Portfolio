import os
# import google.generativeai as genai
from google import genai
from google.genai import types
from dotenv import load_dotenv
from database.connection import engine
from sqlalchemy import text
from services.email_service import send_report_email
import time
# from google.api_core.exceptions import ResourceExhausted

load_dotenv()

# =================================================================
# 🔑 KEY ROTATION SETUP
# =================================================================
API_KEY_POOL = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3"),
    os.getenv("GEMINI_API_KEY_4"),
    os.getenv("GEMINI_API_KEY_5"),
]
API_KEY_POOL = [key for key in API_KEY_POOL if key]

if not API_KEY_POOL:
    API_KEY_POOL.append(os.getenv("GEMINI_API_KEY"))

CURRENT_KEY_INDEX = 0
current_client = None 
current_chat_session = None

def get_next_key():
    """Rotates to the next key in the pool."""
    global CURRENT_KEY_INDEX
    if len(API_KEY_POOL) <= 1:
        return API_KEY_POOL[0]
    CURRENT_KEY_INDEX = (CURRENT_KEY_INDEX + 1) % len(API_KEY_POOL)
    return API_KEY_POOL[CURRENT_KEY_INDEX]

# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_db_schema():
    return """
    buyers(id, name, address, city, state, country, contact_email, phone, website, industry_type, gst_number, registration_date, status),
    suppliers(id, name, address, city, state, country, contact_email, phone, website, business_type, gst_number, rating, status),
    products(id, hs_code, hs_description, product_name, category, subcategory, attributes, unit_price_usd, available_stock, supplier_id),
    ports(id, port_code, port_name, country, city, type),
    shipments(id, bill_of_lading_no, shipment_type, mode, date, hs_code, shipment_description, product_id, quantity, quantity_unit, weight_kg, value_usd, origin_country, destination_country, port_of_loading, port_of_discharge, container_count, carrier_name, supplier_id, buyer_id, shipment_status, expected_delivery_date, tracking_url),
    shipping_routes(id, origin_port, destination_port, distance_km, average_duration_days, carrier_name),
    payments(id, invoice_id, payment_date, amount_usd, payment_method, status, transaction_id, notes),
    invoices(id, shipment_id, invoice_number, invoice_date, amount_usd, paid, notes),
    shipment_events(id, shipment_id, event_type, event_timestamp, location, remarks),
    containers(id, container_number, container_type, capacity_cubic_m, shipment_id, status, last_location, last_update),
    port_congestion(id, port_id, congestion_level, ships_waiting, average_wait_time_hours, recorded_at),
    vessel_tracking(id, vessel_name, voyage_number, current_location, speed_knots, heading, last_update),
    carbon_emissions(id, shipment_id, co2_emission_kg, emission_source, recorded_at)

    -- INDEXED COLUMNS (for query performance):
    -- shipments.product_id
    -- shipments.hs_code
    -- products.hs_code

    JOIN RULES:
    shipments.supplier_id → suppliers.id
    shipments.buyer_id → buyers.id
    shipments.product_id → products.id
    shipments.port_of_loading → ports.id
    shipments.port_of_discharge → ports.id
    shipping_routes.origin_port → ports.id
    shipping_routes.destination_port → ports.id
    payments.invoice_id → invoices.id
    invoices.shipment_id → shipments.id
    shipment_events.shipment_id → shipments.id
    containers.shipment_id → shipments.id
    port_congestion.port_id → ports.id
    carbon_emissions.shipment_id → shipments.id
    """

def run_sql_query(sql: str):
    import decimal
    import datetime
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
                    if isinstance(value, decimal.Decimal): row_dict[key] = float(value)
                    elif isinstance(value, (datetime.date, datetime.datetime)): row_dict[key] = value.isoformat()
                    else: row_dict[key] = value
                rows.append(row_dict)
            return rows if rows else "No results."
    except Exception as e:
        return f"SQL Error: {e}"
    
# =================================================================
# 🤖 AGENT RECONFIGURATION (FIXED)
# =================================================================

def reconfigure_agent(key: str):
    """
    Initializes/Reconfigures the Gemini API and creates a new chat session.
    """
    global current_client # CRITICAL: Keep client alive globally
    print(f"🔄 Configuring with Key Index: {API_KEY_POOL.index(key)} / {len(API_KEY_POOL) - 1}")
    # genai.configure(api_key=key)
    current_client = genai.Client(api_key=key)

    tools = [
        get_db_schema,
        run_sql_query,
        send_report_email
    ]
    
    config = types.GenerateContentConfig(
        tools=tools,
        system_instruction="""
            You are a smart SQL + Email Agent.
            RULES:
            1. ALWAYS inspect database schema using get_db_schema().
            2. ALWAYS use run_sql_query() for SQL queries.
            3. If SQL contains Decimal values, convert them using float().
            4. For date filtering (e.g., 'last 6 months'), ONLY use this format: sh.date >= CURRENT_DATE - INTERVAL 'X months'.
            5. **AVG/SUM Data Handling:** When performing AVG() or SUM() on numeric columns that might be stored as text, 
               or for which you are unsure of the data type (e.g., congestion_level), you **MUST** cast the column to FLOAT 
               or REAL inside the aggregation function to prevent SQL type errors. 
               Example: AVG(CAST(pc.congestion_level AS FLOAT)).
               5a. **Categorical Handling (If Necessary):** ONLY use a CASE statement (like converting 'Low'/'Medium'/'High' to 1/2/3) 
               if the schema confirms the column is a text category that needs numeric conversion. Otherwise, use direct CAST (Rule 5).
            6. When the user asks for an email: Call send_report_email(recipient, subject, body, preview=True) first.
            7. NEVER send email automatically.
            8. After user confirmation, call send_report_email(recipient, subject, body, preview=False).
            9. **CRITICAL:** Use the minimum number of run_sql_query() calls possible. Generate a single, complete, optimized query.
            10. Always return the function_call result.
            """,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False)
    )

    # Create session tied to the global client
    chat_session = current_client.chats.create(
        model="gemini-2.0-flash", 
        config=config
    )
    return chat_session

    # agent = genai.GenerativeModel(
    #     model_name="gemini-2.5-flash", # Retain 'flash' for speed, as it supports tools
    #     tools=tools,
    #     system_instruction="""
    #         You are a smart SQL + Email Agent.
    #         RULES:
    #         1. ALWAYS inspect database schema using get_db_schema().
    #         2. ALWAYS use run_sql_query() for SQL queries.
    #         3. If SQL contains Decimal values, convert them using float().
    #         4. For date filtering (e.g., 'last 6 months'), ONLY use this format: 
    #            sh.date >= CURRENT_DATE - INTERVAL 'X months'.
    #         5. **AVG/SUM Data Handling:** When performing AVG() or SUM() on numeric columns that might be stored as text, 
    #            or for which you are unsure of the data type (e.g., congestion_level), you **MUST** cast the column to FLOAT 
    #            or REAL inside the aggregation function to prevent SQL type errors. 
    #            Example: AVG(CAST(pc.congestion_level AS FLOAT)).
    #         5a. **Categorical Handling (If Necessary):** ONLY use a CASE statement (like converting 'Low'/'Medium'/'High' to 1/2/3) 
    #            if the schema confirms the column is a text category that needs numeric conversion. Otherwise, use direct CAST (Rule 5).
    #         6. When the user asks for an email: Call send_report_email(recipient, subject, body, preview=True) first.
    #         7. NEVER send email automatically.
    #         8. After user confirmation, call send_report_email(recipient, subject, body, preview=False).
    #         9. **CRITICAL:** Use the minimum number of run_sql_query() calls possible. 
    #            Generate a single, complete, optimized query.
    #         10. Always return the function_call result.
    #         """)
    
    # return agent.start_chat(enable_automatic_function_calling=True)



current_chat_session = reconfigure_agent(API_KEY_POOL[CURRENT_KEY_INDEX])

def ask_agent(query: str):
    global current_chat_session # Need access to the global chat session
    
    print("\n🤖 SENDING QUERY TO GEMINI:", query)

    MAX_RETRIES = len(API_KEY_POOL) + 1 
    INITIAL_WAIT_TIME = 5  # seconds

    # --- New variable to track the query that should be sent ---
    current_message_to_send = query

    for attempt in range(MAX_RETRIES):
        try:
            # response = current_chat_session.send_message(current_message_to_send)
            response = current_chat_session.send_message(message=current_message_to_send)
            
            if response.text:
                print("🔧 RAW MODEL RESPONSE RECEIVED")
                print("🔎 TEXT OUTPUT:", response.text)
                print("=================================\n")
                return response.text
            else:
                return "The model processed the request but returned no text."
        except Exception as e:
            error_msg = str(e)
            
            # Case 1: Client was closed or Garbage Collected
            if "closed" in error_msg.lower() or "not initialized" in error_msg.lower():
                print("⚠️ Client connection lost. Restarting agent...")
                current_chat_session = reconfigure_agent(API_KEY_POOL[CURRENT_KEY_INDEX])
                # Retry this specific attempt
                response = current_chat_session.send_message(message=current_message_to_send)
                return response.text

            # Case 2: Quota Exceeded (429)
            if "429" in error_msg or "quota" in error_msg.lower():
                print(f"❌ [429] Quota Exceeded. Attempt {attempt + 1}/{MAX_RETRIES}...")
                
                if attempt < MAX_RETRIES:
                    next_key = get_next_key()
                    wait_time = INITIAL_WAIT_TIME * (2 ** attempt)
                    print(f"😴 Waiting {wait_time}s and switching keys...")
                    time.sleep(wait_time)
                    current_chat_session = reconfigure_agent(next_key)
                    continue # Retry loop with new key
                else:
                    return "❌ All API keys exhausted."

            # Case 3: Other Errors
            print(f"❌ Unexpected Error: {e}")
            return f"Error: {e}"
    return "Error: Agent failed to respond."

            # If successful, exit the loop and return
            # print("🔧 RAW MODEL RESPONSE:", response)
            # print("🔎 TEXT OUTPUT:", response.text)
            # print("=================================\n")
            # return response.text

        # except ResourceExhausted as e:
        #     # Handle the 429 Quota Exceeded error
        #     print(f"\n❌ [ERROR 429] Quota Exceeded on Attempt {attempt + 1}/{MAX_RETRIES}. Waiting and Rotating...")
            
        #     if attempt < len(API_KEY_POOL):
        #         # We have unused keys left to try
        #         next_key = get_next_key()
                
        #         wait_time = INITIAL_WAIT_TIME * (2 ** attempt) 
        #         print(f"😴 Waiting {wait_time:.2f} seconds before rotating key...")
        #         time.sleep(wait_time)
        #         current_chat_session = reconfigure_agent(next_key)
        #         current_message_to_send = query 

        #     else:
        #         error_msg = f"❌ FAILED: All {len(API_KEY_POOL)} keys are exhausted. Cannot proceed."
        #         print(error_msg)
        #         print("=================================\n")
        #         return error_msg

        # # except Exception as e:
        # #     error_msg = f"❌ An unexpected error occurred on attempt {attempt + 1}: {e}"
        # #     print(error_msg)
        # #     print("=================================\n")
        # #     return error_msg
        # except Exception as e:
        #     error_msg = str(e)
            
        #     # 🔍 DEBUG: Check specifically for Quota or "Closed Client"
        #     if "closed" in error_msg.lower():
        #         print("⚠️ Client was closed. Re-initializing...")
        #         current_chat_session = reconfigure_agent(API_KEY_POOL[CURRENT_KEY_INDEX])
        #         # Don't increment attempt, just retry once with fresh client
        #         continue

        #     if "429" in error_msg or "quota" in error_msg.lower():
        #         print(f"❌ Quota Exceeded. Rotating key (Attempt {attempt+1})...")
        #         if attempt < MAX_RETRIES:
        #             next_key = get_next_key()
        #             time.sleep(INITIAL_WAIT_TIME * (2 ** attempt))
        #             current_chat_session = reconfigure_agent(next_key)
        #             continue
            
        #     # If it's a different error, report it
        #     print(f"❌ Unexpected Error: {e}")
        #     return f"Error: {e}"
        
    # return "Error: Agent failed to respond after exhausting all keys."