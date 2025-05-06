import pandas as pd
import os
import re

BASE_PATH = os.path.join(os.path.dirname(__file__), 'data')

# Load CSV files from the data/ folder
base_df = pd.read_csv(os.path.join(BASE_PATH, "Base.csv"))
apparel_df = pd.read_csv(os.path.join(BASE_PATH, "Apparel.csv"))
construction_df = pd.read_csv(os.path.join(BASE_PATH, "Construction.csv"))
energy_df = pd.read_csv(os.path.join(BASE_PATH, "Energy.csv"))
hospitality_df = pd.read_csv(os.path.join(BASE_PATH, "Hospitality.csv"))
transportation_df = pd.read_csv(os.path.join(BASE_PATH, "Transportation.csv"))

# Map industries to DataFrames
industry_dfs = {
    "Apparel": apparel_df,
    "Construction": construction_df,
    "Energy": energy_df,
    "Hospitality": hospitality_df,
    "Transportation": transportation_df
}

# Helper function to extract digits from a string (e.g., 'Net 5' -> 5)
def extract_digits(value):
    match = re.search(r'\d+', str(value))  # Find the first occurrence of digits
    return int(match.group()) if match else 0  # Return 0 if no digits are found

def get_recommendation(product_name, industry):
    base_product = base_df[base_df["Base Name"] == product_name]
    if base_product.empty:
        return {"error": "Product not found"}

    reco_product = product_name
    reco_code = base_product["Base Code"].values[0]
    moq = int(base_product["Minimum Order Quantity"].values[0])

    # Extract numeric value for Payment Terms (e.g., 'Net 5' -> 5)
    terms_str = base_product["Payment Terms"].values[0]
    terms = extract_digits(terms_str)

    if industry in industry_dfs:
        df = industry_dfs[industry]
        match = df[df[df.columns[0]].str.startswith(product_name)]
        if not match.empty:
            reco_product = match[df.columns[0]].values[0]
            reco_code = match[df.columns[1]].values[0]
            moq = int(match["Minimum Order Quantity"].values[0])

            # Extract numeric value for Payment Terms
            terms_str = match["Payment Terms"].values[0]
            terms = extract_digits(terms_str)

    return {
        "Product": product_name,
        "Industry": industry,
        "Recommended Product": reco_product,
        "Recommended Code": reco_code,
        "MOQ": moq,
        "Payment Terms": terms
    }
