import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import json

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_API_BASE")
)

DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME_4o")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME")

def get_mongo_query_from_user_input(user_input: str):
    """
    Given a user input (natural language), return the MongoDB query, intent, and projection.
    """
    prompt = f"""
You are a MongoDB expert. Convert the following natural language query into a MongoDB filter object and detect the user's intent.
- Return a valid JSON object with three keys: "intent", "query", and optionally "projection".
- "intent" should be one of: "count_query", "find_query", "find_with_projection", "aggregation_query", "other".
- "query" should be a valid MongoDB filter object, e.g. {{"field": "value"}}.
- "projection" should be a valid MongoDB projection object, e.g. {{"email": 1, "_id": 0}}, only if intent is "find_with_projection".
- Do NOT include any explanation, comments, or extra text.
- If the query cannot be answered, return: {{"intent": "other", "query": {{}}, "projection": {{}}}}.
Query: "{user_input}"
Database: {MONGO_DB_NAME}
Collection: {MONGO_COLLECTION_NAME}
Return only the JSON object.
"""

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    mongo_query_str = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(mongo_query_str)
        intent = parsed.get("intent", "other")
        query_obj = parsed.get("query", {})
        projection = parsed.get("projection", {})
    except Exception:
        intent = "other"
        query_obj = None
        projection = {}

    return intent, mongo_query_str, query_obj, projection
