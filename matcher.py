from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from langfuse import observe
model = SentenceTransformer("all-MiniLM-L6-v2")
@observe()
def calculate_match_score(resume_text, jd_text):
    embeddings = model.encode([
        resume_text,
        jd_text
    ])
    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]
    print("Resume Embedding:")
    print(embeddings[0])
    print("\nJD Embedding:")
    print(embeddings[1])
    return similarity * 100