# MONGO_GPT

A small utility that converts natural-language queries into MongoDB queries using an LLM and exposes a simple API and Streamlit frontend to run those queries against a MongoDB collection.

Key components
- backend/: FastAPI service that accepts a natural language query, asks an LLM to generate a MongoDB filter/projection and returns query results (or counts).
- backend/llm_utils.py: wraps the Azure OpenAI client and converts user text to a JSON object describing intent, query and optional projection.
- backend/mongo_db.py: simple helper to get a PyMongo collection using environment-configured URI, DB name and collection name.
- frontend/: Streamlit app that calls the backend `/query` endpoint and displays the generated query and results.
- backend/example_data/: placeholder example files for schema and examples.

Repository structure

```
MONGO_GPT/
├─ backend/
│  ├─ main.py           # FastAPI app
│  ├─ llm_utils.py      # LLM wrapper to build MongoDB JSON from NL
│  ├─ mongo_db.py       # PyMongo helpers
│  └─ example_data/
│     ├─ examples.json
│     └─ schema.json
├─ frontend/
│  └─ app.py            # Streamlit UI
├─ requirements.txt
└─ README.md
```

Requirements

This project targets Python 3.10+ and depends on the packages listed in `requirements.txt`. At minimum the project uses:

- fastapi, uvicorn
- streamlit
- pymongo
- openai (Azure OpenAI client)
- python-dotenv

See `requirements.txt` for the exact, pinned packages.

Environment variables

Create a `.env` file or export these variables before running the services. The names below are what the code expects:

- MONGO_URI: MongoDB connection string (default: mongodb://localhost:27017)
- MONGO_DB_NAME: Database name used by the app (e.g. `test_db`)
- MONGO_COLLECTION_NAME: Collection name used by the app (e.g. `orders`)
- AZURE_OPENAI_API_KEY: Azure OpenAI API key
- AZURE_OPENAI_API_VERSION: Azure OpenAI API version (e.g. 2023-05-15)
- AZURE_OPENAI_API_BASE: Azure endpoint base (e.g. https://your-resource.openai.azure.com/)
- AZURE_OPENAI_DEPLOYMENT_NAME_4o: The deployment/model name used by the LLM calls

Note: Do not commit secrets to source control. Use `.env` locally and a secure secrets store in production.

Quick start (Windows - cmd.exe)

1. Create a virtual environment and install dependencies

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with the required environment variables, for example:

```text
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=test_db
MONGO_COLLECTION_NAME=orders
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_API_VERSION=2023-05-15
AZURE_OPENAI_API_BASE=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME_4o=your-deployment-name
```

3. Run the backend (FastAPI)

You can run the app either directly with Python (the module calls uvicorn in __main__) or with uvicorn for the reload option:

```cmd
python backend\main.py
```

or (recommended for development):

```cmd
pip install uvicorn
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

4. Run the frontend (Streamlit)

```cmd
streamlit run frontend\app.py
```

How it works

- The Streamlit frontend sends a JSON POST request to the backend `/query` endpoint with payload: `{ "query": "<natural language>" }`.
- The backend calls `get_mongo_query_from_user_input` in `backend/llm_utils.py` which constructs a prompt and sends it to Azure OpenAI.
- The LLM is expected to return a JSON object containing `intent`, `query`, and optionally `projection`.
- The backend parses that JSON, runs the corresponding MongoDB operation (find or count), and returns a JSON response containing the original LLM output, parsed query object, and the results or count.

API contract

POST /query
- Request body: { "query": "<natural-language-query>" }
- Response (successful find):

```json
{
	"mongo_query": "<raw LLM JSON string>",
	"mongo_query_obj": { ...parsed query object... },
	"results": [ ... ]
}
```

Response (count):

```json
{
	"mongo_query": "<raw LLM JSON string>",
	"mongo_query_obj": { ... },
	"count": 123
}
```

If the LLM output is empty or cannot be parsed the API returns an `error` field describing the problem.

Security notes and limitations

- The project relies on LLM outputs to create database queries. LLM responses can be unpredictable. Treat LLM-generated queries as untrusted input in production.
- The code currently does NOT execute server-side validation nor sandboxing of aggregation pipelines — use caution and restrict access to the API and MongoDB.
- Aggregation queries are recognized by intent but are not executed by the backend (the current implementation returns an error for `aggregation_query`).

Example usage

In Streamlit enter a query like:

```
How many orders placed in 2024 have total > 100?
```

The app will show the LLM-generated MongoDB JSON and the query results (or count) returned from MongoDB.

Troubleshooting

- If you get connection issues to MongoDB: verify `MONGO_URI`, `MONGO_DB_NAME` and `MONGO_COLLECTION_NAME`. Use the `mongo` shell or MongoDB Compass to confirm connectivity.
- If LLM responses fail to parse: check your Azure OpenAI config, deployment name, and that the model is returning a plain JSON object as requested by the prompt.
- Streamlit can't reach backend: make sure backend is running on port 8000 and not blocked by the firewall. The Streamlit app posts to `http://localhost:8000/query`.

Next steps / enhancements

- Add server-side validation and a safe query execution layer to prevent malicious or expensive queries.
- Support and safely execute aggregation pipelines.
- Add authentication to the API and Streamlit app.
- Add unit tests and CI checks.

License

This repository is provided as-is. Add a license file if you intend to open-source or share.

Contact

If you need help with setup or features, open an issue or contact the repository owner.
