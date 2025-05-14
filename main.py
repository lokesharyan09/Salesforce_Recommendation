import os
from fastapi import FastAPI
import openai
from pydantic import BaseModel
from typing import List, Optional
from recommendation import get_recommendation
from deal_probability import get_deal_probability
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd  # <-- NEW: for reading CSV

client = OpenAI()

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize FastAPI app
app = FastAPI()

# Define ProductItem model
class ProductItem(BaseModel):
    productName: str
    industry: str

# UnifiedRequest to accept both products and prompt
class UnifiedRequest(BaseModel):
    products: Optional[List[ProductItem]] = None
    prompt: Optional[str] = None

# NEW: Function to load product data from CSV
def get_relevant_products_from_csv(industry_filter: Optional[str] = None) -> list:
    try:
        df = pd.read_csv("data/Base.csv")  # <-- Adjust path if needed
        if industry_filter:
            df = df[df["Industry"].str.lower() == industry_filter.lower()]
        return df[["Name", "Industry", "MOQ", "Payment Terms"]].to_dict(orient="records")
    except Exception as e:
        return []

# NEW: Build enriched prompt with product data
def build_prompt_with_product_data(user_prompt: str, products: list) -> str:
    if not products:
        return user_prompt
    product_lines = "\n".join(
        f"- Product: {p['Name']}, Industry: {p['Industry']}, MOQ: {p['MOQ']}, Payment Terms: {p['Payment Terms']}"
        for p in products
    )
    return (
        "You are a B2B sales assistant that recommends products to clients based on their industry.\n\n"
        "You are a Experienced and knowledgeable B2B sales assistant that recommends products to clients. "
        "Only use the product information listed below when answering. "
        "Do not hallucinate or invent new products.\n\n"
        f"Here is some product data:\n{product_lines}\n\n"
        f"Now answer the user's query:\n{user_prompt}"
    )

# Function to get LLM response
async def get_llm_response(prompt: str):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error interacting with LLM: {str(e)}"

# POST endpoint to process both product list and LLM prompt
@app.post("/receive-data")
async def receive_data(request: UnifiedRequest):
    results = []
    errors = []
    llm_response = None

    # Handle product list processing
    if request.products:
        for item in request.products:
            try:
                recommendation = get_recommendation(item.productName, item.industry)
                if "error" in recommendation:
                    errors.append(f"Product '{item.productName}' not found in base data.")
                    continue

                # Dummy sales context
                sales_context = {
                    "discount": "10%",
                    "stage": "Proposal",
                    "quote_amount": "$5000",
                    "customer_type": "New",
                    "region": "North"
                }

                deal_probability = get_deal_probability(
                    item.productName,
                    item.industry,
                    recommendation["MOQ"],
                    recommendation["Payment Terms"],
                    sales_context
                )

                results.append({
                    **recommendation,
                    "Deal Probability": deal_probability
                })

            except Exception as e:
                errors.append(f"Error processing '{item.productName}': {str(e)}")

    # Handle LLM prompt
    if request.prompt:
        industry_filter = request.products[0].industry if request.products else None
        product_data = get_relevant_products_from_csv(industry_filter)
        enriched_prompt = build_prompt_with_product_data(request.prompt, product_data)
        llm_response = await get_llm_response(enriched_prompt)

    return {
        "message": "Processed successfully",
        "results": results,
        "errors": errors,
        "llm_response": llm_response
    }
