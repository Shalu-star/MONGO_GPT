from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import json
import os
from llm_utils import get_mongo_query_from_user_input
from mongo_db import get_collection

app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def query_data(request: QueryRequest):
    intent, mongo_query_str, mongo_query, projection = get_mongo_query_from_user_input(request.query)
    print("Raw LLM output:", mongo_query_str)  # Debug print

    if not mongo_query_str or mongo_query_str.strip() == "":
        return {
            "mongo_query": mongo_query_str,
            "mongo_query_obj": None,
            "error": "LLM returned an empty MongoDB query string."
        }

    if mongo_query is None:
        return {
            "mongo_query": mongo_query_str,
            "mongo_query_obj": None,
            "error": f"Failed to parse MongoDB query string. Raw response: {mongo_query_str}"
        }

    db_name = os.getenv("MONGO_DB_NAME", "test_db")
    collection_name = os.getenv("MONGO_COLLECTION_NAME", "orders")
    collection = get_collection(db_name, collection_name)

    print("Mongo Query Used:", mongo_query)  # Debug print

    if intent == "count_query":
        count = collection.count_documents(mongo_query)
        print("Count Returned:", count)  # Debug print
        return {
            "mongo_query": mongo_query_str,
            "mongo_query_obj": mongo_query,
            "count": count
        }

    elif intent == "aggregation_query":
        return {
            "mongo_query": mongo_query_str,
            "mongo_query_obj": mongo_query,
            "error": "Aggregation queries are not yet supported."
        }

    else:
        results = list(collection.find(mongo_query, projection if intent == "find_with_projection" else {"_id": 0}))
        print("Results Returned:", results)  # Debug print
        return {
            "mongo_query": mongo_query_str,
            "mongo_query_obj": mongo_query,
            "results": results
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
