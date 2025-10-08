from backend.models.recommendation_model import RecommendationModel
from backend.utils.preprocessing import process_customer, process_product, interaction_score

from langchain_community.llms import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from transformers import pipeline
import torch
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import torch.nn.functional as F

load_dotenv()

app = FastAPI(title="Personalized Shopping Recommendation")

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Serve Frontend ---
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
def read_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# --- GPU/CPU Device Selection with Safe Fallback ---
def get_safe_device():
    if torch.cuda.is_available():
        free_mem = torch.cuda.mem_get_info()[0] / (1024 ** 3)
        if free_mem > 1.5:
            print(f"[INFO] GPU available ({free_mem:.2f} GB free). Using GPU.")
            return 0
        else:
            print(f"[WARN] GPU memory low ({free_mem:.2f} GB free). Switching to CPU.")
            return -1
    else:
        print("[INFO] GPU not available. Using CPU.")
        return -1

device = get_safe_device()


# --- Hugging Face Model ---
# You can switch to a smaller model if BLOOM is too large
# hf_model_name = "bigscience/bloom-560m"
hf_model_name = "distilgpt2"  # lighter and faster

try:
    text_gen_pipeline = pipeline(
        "text-generation",
        model=hf_model_name,
        device=device,
        max_length=100,
        do_sample=True,
        temperature=0.7
    )
    llm = HuggingFacePipeline(pipeline=text_gen_pipeline)
    print(f"[INFO] Loaded {hf_model_name} on {'GPU' if device == 0 else 'CPU'}")
except Exception as e:
    print(f"[ERROR] Failed to load model {hf_model_name}: {e}")
    raise

# --- Prompt Template ---
template = """
Customer: {customer_name}, Age: {age}, Segment: {segment}.
Product: {product_name}, Category: {category}, Price: {price}.
Explain briefly why this product is suitable for this customer.
"""
prompt = PromptTemplate(
    input_variables=["customer_name", "age", "segment", "product_name", "category", "price"],
    template=template
)
chain = prompt | llm

# --- Recommendation Model ---
rec_model = RecommendationModel()

class Product(BaseModel):
    name: str
    category: str
    price: float
    brand: str
    explanation: str

class NewCustomer(BaseModel):
    age: int
    gender: str
    segment: str

# --- Routes ---
@app.get("/recommendations/{customer_id}", response_model=List[Product])
def get_recommendations(customer_id: str):
    customer_df = rec_model.customers[
        rec_model.customers['Customer_ID'].str.upper() == customer_id.strip().upper()
    ]
    if customer_df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Customer {customer_id} not found. Available IDs: {rec_model.customers['Customer_ID'].tolist()}"
        )

    customer = customer_df.iloc[0]
    products = rec_model.recommend(customer['Customer_ID'])

    response = []
    for p in products:
        try:
            explanation = chain.invoke({
                "customer_name": customer['Customer_ID'],
                "age": str(customer['Age']),
                "segment": customer['Customer_Segment'],
                "product_name": p['name'],
                "category": p['category'],
                "price": str(p['price'])
            })
        except Exception as e:
            print(f"[WARN] LLM explanation failed: {e}")
            explanation = "Recommended based on browsing and purchase history."

        response.append(Product(
            name=p["name"],
            category=p["category"],
            price=p["price"],
            brand=p["brand"],
            explanation=explanation
        ))

    return response


@app.post("/recommendations/new", response_model=List[Product])
def get_new_customer_recommendations(new_customer: NewCustomer):
    if new_customer.age <= 0 or new_customer.age > 120:
        raise HTTPException(status_code=400, detail="Invalid age provided.")
    if new_customer.gender not in ['Male', 'Female', 'Other']:
        raise HTTPException(status_code=400, detail="Invalid gender provided.")
    if new_customer.segment not in ['New Visitor', 'Occasional Shopper', 'Frequent Buyer']:
        raise HTTPException(status_code=400, detail="Invalid segment provided.")

    customer_features = process_customer(new_customer, rec_model.segment_map, rec_model.gender_map)
    products = []

    for _, product in rec_model.products.iterrows():
        product_features = process_product(product, rec_model.category_map)
        score = 0
        similarity = torch.dot(customer_features, product_features) + score
        explanation = "Recommended based on customer profile."

        products.append({
            "product": Product(
                name=f"{product['Category']} - {product['Subcategory']}",
                category=product['Category'],
                price=product['Price'],
                brand=product['Brand'],
                explanation=explanation
            ),
            "similarity": similarity.item()
        })

    products = sorted(products, key=lambda x: x['similarity'], reverse=True)[:3]
    return [p['product'] for p in products]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
