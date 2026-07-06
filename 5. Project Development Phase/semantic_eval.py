from sentence_transformers import SentenceTransformer, util
import streamlit as st

@st.cache_resource
def get_sentence_bert_model(model_name: str = "all-MiniLM-L6-v2"):
    """
    Loads and caches the Sentence-BERT model using Streamlit's cache_resource to prevent reload latency.
    """
    return SentenceTransformer(model_name)

def compute_similarity(transcript: str, reference_text: str, model_name: str = "all-MiniLM-L6-v2") -> float:
    """
    Computes semantic similarity score (normalized to a scale of 0.0 to 1.0) 
    between the user's transcript and the reference concept text.
    """
    if not transcript.strip() or not reference_text.strip():
        return 0.0
        
    model = get_sentence_bert_model(model_name)
    
    # Generate embeddings
    embeddings1 = model.encode(transcript, convert_to_tensor=True)
    embeddings2 = model.encode(reference_text, convert_to_tensor=True)
    
    # Calculate cosine similarity
    cosine_score = util.cos_sim(embeddings1, embeddings2)
    
    # Extract scalar from tensor and clamp to [0.0, 1.0] range
    similarity = float(cosine_score.cpu().numpy()[0][0])
    return max(0.0, min(1.0, similarity))
