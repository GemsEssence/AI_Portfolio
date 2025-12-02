from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from services.agent_service import ask_agent
from database.connection import SessionLocal
from database.models import Supplier, Shipment, Product
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

    # ---------- 1. TOP EXPORT CATEGORIES (Using Product Name) ----------
    top_categories = (
        db.query(
            func.coalesce(Product.product_name, literal("Unknown")).label("product_name"),
            func.sum(Shipment.value_usd).label("total_value")
        )
        .join(Product, Shipment.hs_code == Product.hs_code, isouter=True)
        .group_by(Product.product_name)
        .order_by(func.sum(Shipment.value_usd).desc())
        .limit(4)
        .all()
    )

    total_export_value = db.query(func.sum(Shipment.value_usd)).scalar() or 1

    formatted_categories = [
        {
            "category": row.product_name,
            "percentage": round((row.total_value / total_export_value) * 100, 1)
        }
        for row in top_categories
    ]

    # ---------- 2. FASTEST GROWING MARKETS ----------
    current_month = func.date_trunc('month', func.current_date())
    previous_month = func.date_trunc('month', func.current_date() - text("interval '1 month'"))

    current_data = dict(
        db.query(
            Shipment.destination_country,
            func.coalesce(func.sum(Shipment.value_usd), 0)
        )
        .filter(func.date_trunc('month', Shipment.date) == current_month)
        .group_by(Shipment.destination_country)
        .all()
    )

    previous_data = dict(
        db.query(
            Shipment.destination_country,
            func.coalesce(func.sum(Shipment.value_usd), 0)
        )
        .filter(func.date_trunc('month', Shipment.date) == previous_month)
        .group_by(Shipment.destination_country)
        .all()
    )

    growing_markets = []
    for country, current_value in current_data.items():
        prev_value = previous_data.get(country, 0)
        growth = ((current_value - prev_value) / prev_value * 100) if prev_value > 0 and current_value > prev_value else 0
        growing_markets.append({
            "country": country,
            "growth": round(growth, 1)
        })

    growing_markets = sorted(growing_markets, key=lambda x: x["growth"], reverse=True)[:4]

    # ---------- 3. BEST SUPPLIERS ----------
    top_suppliers = (
        db.query(
            Supplier.name,
            func.sum(Shipment.value_usd).label("score")
        )
        .join(Shipment, Shipment.supplier_id == Supplier.id)
        .filter(func.date_trunc('month', Shipment.date) == current_month)
        .group_by(Supplier.name)
        .order_by(func.sum(Shipment.value_usd).desc())
        .limit(4)
        .all()
    )

    # Sum of all scores
    total_score = sum(row.score for row in top_suppliers)

    # Convert each score to percentage
    formatted_suppliers = [
        {"name": row.name, "score": int(row.score), "percentage": round((row.score / total_score) * 100, 2)}
        for row in top_suppliers
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


