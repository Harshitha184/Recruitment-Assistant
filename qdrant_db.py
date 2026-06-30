# Standard library
import os

# Third-party
from langfuse import observe
from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    VectorParams,
    Distance
)

COLLECTION_NAME = "resumes"

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# -------------------------------------------------------------------
# Create collection automatically if it doesn't exist
# -------------------------------------------------------------------
if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=384,          # all-MiniLM-L6-v2 embedding size
            distance=Distance.COSINE
        )
    )

# -------------------------------------------------------------------
# Search
# -------------------------------------------------------------------
@observe()
def search_candidates(jd_embedding, limit=10):

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=jd_embedding,
        limit=limit
    )

    return results.points


# -------------------------------------------------------------------
# Get all vectors
# -------------------------------------------------------------------
def get_all_vectors():

    points, _ = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=100,
        with_payload=True,
        with_vectors=True
    )

    return points


# -------------------------------------------------------------------
# Save embedding
# -------------------------------------------------------------------
def save_embedding(
    candidate_id,
    candidate_name,
    candidate_email,
    score,
    embedding
):

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=candidate_id,
                vector=embedding,
                payload={
                    "name": candidate_name,
                    "email": candidate_email,
                    "score": score
                }
            )
        ]
    )