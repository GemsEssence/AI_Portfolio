from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from services.agent_service import ask_agent
from database.connection import SessionLocal
from database.models import Supplier, Shipment, Product, Payment
from pydantic import BaseModel
from sqlalchemy import func, text, literal


app = FastAPI()
templates = Jinja2Templates(directory="templates")

class QueryRequest(BaseModel):
    query: str
    
class SearchRequest(BaseModel):
    query: str
@app.get("/")
def ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chatbot_page(request: Request):
    return templates.TemplateResponse("chatbot.html", {"request": request})

@app.post("/agent")
async def chatbot_post(body: QueryRequest):
    print("POST /agent =>", body.query)
    response = ask_agent(body.query)
    return {"response": response}

@app.get("/api/dashboard-stats")
def get_stats():
    db = SessionLocal()

    suppliers = db.query(Supplier).count()
    countries = db.query(Shipment.origin_country).distinct().count()

    total_volume = db.query(func.coalesce(func.sum(Shipment.value_usd), 0)).scalar()

    current_month = func.date_trunc('month', func.current_date())
    previous_month = func.date_trunc('month', func.current_date() - text('interval \'1 month\''))

    current_month_volume = db.query(func.coalesce(func.sum(Shipment.value_usd), 0)).filter(
        func.date_trunc('month', Shipment.date) == current_month
    ).scalar()

    previous_month_volume = db.query(func.coalesce(func.sum(Shipment.value_usd), 0)).filter(
        func.date_trunc('month', Shipment.date) == previous_month
    ).scalar()

    if previous_month_volume == 0:
        growth_percentage = 0
    else:
        growth_percentage = ((current_month_volume - previous_month_volume) / previous_month_volume) * 100

    growth_percentage = abs(growth_percentage) 

    db.close()

    return {
        "suppliers": suppliers,
        "countries": countries,
        "volume": format_number(total_volume),      # 👉 53.4M format
        "growth": f"{growth_percentage:.2f}%",
        "current_month_volume": format_number(current_month_volume),
        "previous_month_volume": format_number(previous_month_volume)
    }
@app.get("/api/dashboard-insights")
def get_dashboard_insights():
    db = SessionLocal()

    date_window = func.current_date() - text("interval '6 months'")

    # 1. Top 5 Export Categories
    top_categories_raw = (
        db.query(
            func.coalesce(Product.product_name, literal("Misc Products")).label("product_name"),
            func.coalesce(func.sum(Shipment.value_usd), 0).label("total_value")
        )
        .outerjoin(Product, Shipment.product_id == Product.id)
        .filter(Shipment.date >= date_window)
        .group_by(func.coalesce(Product.product_name, literal("Misc Products")))
        .order_by(func.sum(Shipment.value_usd).desc())
        .limit(5)
        .all()
    )

    total_export_value = sum([c.total_value for c in top_categories_raw]) or 1
    formatted_categories = [
        {"category": c.product_name, "percentage": round((c.total_value / total_export_value) * 100, 1)}
        for c in top_categories_raw
    ]

    # 2. Fastest Growing Markets
    current_data = dict(
        db.query(
            Shipment.destination_country,
            func.coalesce(func.sum(Shipment.value_usd), 0)
        )
        .filter(Shipment.date >= date_window)
        .group_by(Shipment.destination_country)
        .all()
    )

    previous_data = dict(
        db.query(
            Shipment.destination_country,
            func.coalesce(func.sum(Shipment.value_usd), 0)
        )
        .filter(Shipment.date < date_window)
        .filter(Shipment.date >= func.current_date() - text("interval '12 months'"))
        .group_by(Shipment.destination_country)
        .all()
    )

    growing_markets = [
        {
            "country": country or "Unknown",
            "growth": round(((current_value - previous_data.get(country, 0)) / previous_data.get(country, 1) * 100)
                            if previous_data.get(country, 0) else (100 if current_value > 0 else 0), 1)
        }
        for country, current_value in current_data.items()
    ]

    growing_markets = sorted(growing_markets, key=lambda x: x["growth"], reverse=True)[:5]

    # 3. Best Suppliers
    top_suppliers_raw = (
        db.query(
            Supplier.name.label("supplier_name"),
            func.coalesce(func.sum(Shipment.value_usd), 0).label("total_value")
        )
        .join(Shipment, Supplier.id == Shipment.supplier_id)
        .filter(Shipment.date >= date_window)
        .group_by(Supplier.name)
        .order_by(func.sum(Shipment.value_usd).desc())
        .limit(5)
        .all()
    )

    total_score = sum([row.total_value for row in top_suppliers_raw]) or 1
    formatted_suppliers = [
        {"name": row.supplier_name or "Unknown", "percentage": round((row.total_value / total_score) * 100, 2),
         "score": int(row.total_value)}
        for row in top_suppliers_raw
    ]

    db.close()

    return {
        "top_categories": formatted_categories,
        "fastest_growing_markets": growing_markets,
        "best_suppliers": formatted_suppliers
    }
@app.post("/api/search")
def search_shipments(body: SearchRequest):
    db = SessionLocal()
    query_text = body.query.lower()
    results = db.query(Shipment).filter(
        Shipment.product_description.ilike(f"%{query_text}%")
    ).limit(10).all()

    data = [
        {
            "Bill of Lading No": r.bill_of_lading,
            "Date": r.date.strftime("%Y-%m-%d"),
            "Product": r.product_description,
            "Quantity": r.quantity,
            "Unit": r.unit,
            "Value (USD)": r.value,
            "Origin": r.origin_country,
            "Destination": r.destination_country,
            "Carrier": r.carrier_name
        } for r in results
    ]
    db.close()
    return {"results": data}


def format_number(n):
    if n >= 1_000_000_000:
        return f"{n/1_000_000_000:.1f}B"
    elif n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


