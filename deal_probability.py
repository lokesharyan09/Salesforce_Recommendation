import random

# NOTE: later you can uncomment the OpenAI logic here

def get_deal_probability(product, industry, moq, payment_terms, sales_context):
    """
    Placeholder: returns random probability 50–85%
    """
    # === Future OpenAI logic ===
    # import openai
    # openai.api_key = "your_openai_key"
    # prompt = ...
    # response = openai.ChatCompletion.create(...)
    # return extracted probability

    probability = random.randint(50, 95)
    return f"{probability}%"
