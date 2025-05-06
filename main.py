import re
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from recommendation import get_recommendation
from deal_probability import get_deal_probability

app = FastAPI()

class ProductItem(BaseModel):
    productName: str
    industry: str

class ProductList(BaseModel):
    products: List[ProductItem]

@app.post("/receive-data")
async def receive_data(product_list: ProductList):
    results = []
    errors = []

    for item in product_list.products:
        try:
            recommendation = get_recommendation(item.productName, item.industry)
            if "error" in recommendation:
                errors.append(f"Product '{item.productName}' not found in base data.")
                continue  # skip if product not found
                
                terms_str = base_product["Payment Terms"].values[0]
                terms = int(re.search(r'\d+', str(terms_str)).group())  # extract digits only

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

    return {
        "message": "Processed successfully",
        "results": results,
        "errors": errors
    }
