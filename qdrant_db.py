from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from langfuse import observe
import os
client = QdrantClient(
    host=os.getenv("QDRANT_HOST"),
    port=os.getenv("QDRANT_PORT")
)
@observe()
def search_candidates(jd_embedding, limit=10):

    results = client.query_points(
        collection_name="resumes",
        query=jd_embedding,
        limit=limit
    )
    
    return results.points
def get_all_vectors():

    points, _ = client.scroll(
        collection_name="resumes",
        limit=100,
        with_payload=True,
        with_vectors=True
    )

    return points

def save_embedding(
    candidate_id,
    candidate_name,
    candidate_email,
    score,
    embedding
):

    client.upsert(
        collection_name="resumes",
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