# InsightExtractor

InsightExtractor is a Python-based application that ingests RSS feeds, extracts posts, semantically groups them into themes using sentence embeddings, and stores the results in a database. It provides API endpoints to ingest new feeds and retrieve themes with their related posts.


To activate virtual env and run on windows powershell: .\venv\Scripts\Activate.ps1 ; python InsightExtractor.py

OpenAPI spec is found at GET /openapi.yaml

API Endpoints are: POST /ingest, GET /themes, and GET /themes/{id}


Design Decisions: Service was made using MCV architecture and consists of 3 REST endpoints.  

Future work: Can add more endpoints to micro-service for expanded scope. Examples could include an endpoint to allow user to filter posts based on theme. We will also need a security filter layer to provide authentication for our APIs hence there are no current .env variables for this service. 