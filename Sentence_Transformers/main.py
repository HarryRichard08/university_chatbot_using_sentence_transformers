from fastapi import FastAPI, HTTPException
from elasticsearch import Elasticsearch
from pydantic import BaseModel
from typing import List, Optional
from sentence_transformers import SentenceTransformer

app = FastAPI()

model = SentenceTransformer('all-MiniLM-L6-v2')

# Establish connection to Elasticsearch
es = Elasticsearch("http://localhost:9200")

# Define the request model for user query
class UserQuery(BaseModel):
    question: str
    top_n: Optional[int] = 3  # Number of top results to return, default is 3

@app.post("/search/")
async def search_faqs(query: UserQuery):
    query_embedding = query_to_embedding(query.question)
    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                "params": {"query_vector": query_embedding}
            }
        }
    }
    
    try:
        response = es.search(
            index="university-info",  
            body={
                "query": script_query,
                "_source": ["Section", "Content", "URL"],  # Adjusted to capitalized field names and added "URL"
                "size": query.top_n
            }
        )

        results = [
            {
                "Section": hit['_source']['Section'],  # Adjusted to capitalized field name
                "Content": hit['_source']['Content'],  # Adjusted to capitalized field name
                "URL": hit['_source'].get('URL', ''),  # Get URL if available, default to empty string
                "Score": hit['_score']  # Keep the score as is, but it can be rounded if necessary
            }
            for hit in response['hits']['hits']
        ]

        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def query_to_embedding(query: str) -> List[float]:
    try:
        embedding = model.encode(query)
        return embedding.tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error encoding query to embedding: {e}")
