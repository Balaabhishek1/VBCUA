from scoring_engine import analyze_filler_words, calculate_evaluation_score

def test_filler_word_analysis_empty():
    """
    Verifies that empty transcript strings return zero counts and ratio.
    """
    res = analyze_filler_words("")
    assert res["filler_word_count"] == 0
    assert res["total_words"] == 0
    assert res["filler_ratio"] == 0.0

def test_filler_word_analysis_normal():
    """
    Checks if filler words (e.g. 'um', 'like', 'so') are counted correctly.
    """
    transcript = "So, machine learning is like a sub-field of AI, um, which learns from data."
    res = analyze_filler_words(transcript)
    
    # Fillers present: "so", "like", "um"
    assert res["filler_word_count"] >= 3
    assert res["total_words"] > 5
    assert res["filler_ratio"] > 0.0
    
    # Check details contain individual counts
    assert "like" in res["filler_details"]
    assert "um" in res["filler_details"]
    assert "so" in res["filler_details"]

def test_calculate_evaluation_score_strong():
    """
    Verifies that high similarity and ideal pause/filler metrics result in a 'Strong' rating.
    """
    # 90% semantic similarity, 20% pauses (ideal), 2% filler words (low)
    scores = calculate_evaluation_score(
        similarity_score=0.9,
        pause_ratio=0.20,
        filler_ratio=0.02
    )
    
    assert scores["comprehension_score"] == 90.0
    assert scores["overall_score"] >= 75.0
    assert scores["understanding_level"] == "Strong"

def test_calculate_evaluation_score_poor():
    """
    Verifies that low similarity, high filler ratio, and high pause ratio yield a 'Poor' rating.
    """
    # 20% semantic similarity, 50% pauses (hesitant), 25% filler words (extremely high)
    scores = calculate_evaluation_score(
        similarity_score=0.2,
        pause_ratio=0.50,
        filler_ratio=0.25
    )
    
    assert scores["comprehension_score"] == 20.0
    assert scores["overall_score"] < 50.0
    assert scores["understanding_level"] == "Poor"
