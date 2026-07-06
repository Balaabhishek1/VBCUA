from semantic_eval import compute_similarity

def test_compute_similarity_identical():
    """
    Checks that identical strings return a similarity score of 1.0 (or extremely close to 1.0).
    """
    text = "Machine learning is a subset of artificial intelligence that learns from data."
    score = compute_similarity(text, text)
    assert abs(score - 1.0) < 0.01

def test_compute_similarity_empty():
    """
    Verifies that empty string inputs return a similarity score of 0.0.
    """
    assert compute_similarity("", "Machine learning") == 0.0
    assert compute_similarity("Machine learning", "") == 0.0

def test_compute_similarity_different():
    """
    Checks that unrelated texts yield a low similarity score,
    while related texts yield a moderate/high similarity score.
    """
    concept_ref = "Machine learning focuses on training algorithms on datasets to recognize patterns."
    related_input = "Algorithms are trained on data to find patterns in machine learning."
    unrelated_input = "A database index is a B-Tree structure designed to speed up read queries."
    
    score_related = compute_similarity(related_input, concept_ref)
    score_unrelated = compute_similarity(unrelated_input, concept_ref)
    
    assert score_related > 0.5
    assert score_unrelated < 0.3
    assert score_related > score_unrelated
