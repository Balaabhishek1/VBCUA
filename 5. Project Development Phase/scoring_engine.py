import re
import os
import nltk
from google import generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Setup Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Try downloading NLTK tokenizers with a fallback for offline execution
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
    except Exception:
        pass  # Will use regex fallback if this fails

# List of common filler words to detect in transcribed text
DEFAULT_FILLERS = [
    "um", "uh", "uhm", "like", "so", "ah", "er", "okay", "you know", "basically", "actually"
]

def analyze_filler_words(transcript: str, filler_list=None) -> dict:
    """
    Analyzes the transcribed text to count filler words and compute ratios.
    """
    if filler_list is None:
        filler_list = DEFAULT_FILLERS
        
    text = transcript.lower().strip()
    if not text:
        return {
            "filler_word_count": 0,
            "total_words": 0,
            "filler_ratio": 0.0,
            "filler_details": {}
        }
        
    # Tokenize the text (using NLTK word_tokenize with a regex fallback)
    try:
        words = nltk.word_tokenize(text)
    except Exception:
        # Resilient fallback: splits by word boundaries
        words = re.findall(r'\b\w+\b', text)
        
    total_words = len(words)
    if total_words == 0:
        return {
            "filler_word_count": 0,
            "total_words": 0,
            "filler_ratio": 0.0,
            "filler_details": {}
        }
        
    # Count occurrences of individual filler words
    filler_counts = {}
    filler_word_count = 0
    
    # 1. Single word fillers
    for word in words:
        if word in filler_list:
            filler_counts[word] = filler_counts.get(word, 0) + 1
            filler_word_count += 1
            
    # 2. Multi-word phrases (e.g. "you know")
    for filler in filler_list:
        if " " in filler:
            # Count exact phrase occurrences using regex
            matches = len(re.findall(rf'\b{re.escape(filler)}\b', text))
            if matches > 0:
                filler_counts[filler] = matches
                # Adjust word counts: subtract individual words counted, add as 1 phrase unit
                # but to keep it simple, we just count the matches in the overall count
                filler_word_count += matches

    filler_ratio = filler_word_count / total_words
    
    return {
        "filler_word_count": filler_word_count,
        "total_words": total_words,
        "filler_ratio": filler_ratio,
        "filler_details": {k: v for k, v in filler_counts.items() if v > 0}
    }

def calculate_evaluation_score(similarity_score: float, pause_ratio: float, filler_ratio: float) -> dict:
    """
    Combines semantic similarity and fluency metrics (filler words and pauses) 
    into a final educational assessment score and category.
    """
    # 1. Comprehension score (from Sentence-BERT cosine similarity, 0.0 to 1.0)
    comprehension_score = similarity_score * 100.0
    
    # 2. Fluency Score (out of 100)
    # Penalize high filler word usage
    # E.g., if filler ratio is 10% (0.10), deduct 15 points
    filler_penalty = min(40.0, filler_ratio * 150.0)
    
    # Penalize suboptimal pause ratio (target pause ratio is around 15% - 25%)
    # If pause ratio is outside this healthy zone, deduct points
    target_lower = 0.15
    target_upper = 0.25
    if pause_ratio < target_lower:
        pause_penalty = min(30.0, (target_lower - pause_ratio) * 150.0)
    elif pause_ratio > target_upper:
        pause_penalty = min(30.0, (pause_ratio - target_upper) * 100.0)
    else:
        pause_penalty = 0.0
        
    fluency_score = max(0.0, 100.0 - filler_penalty - pause_penalty)
    
    # 3. Overall composite score (70% Semantic Comprehension, 30% Fluency)
    overall_score = (0.7 * comprehension_score) + (0.3 * fluency_score)
    overall_score = round(overall_score, 1)
    
    # Determine qualitative level
    if overall_score >= 75.0:
        level = "Strong"
    elif overall_score >= 50.0:
        level = "Moderate"
    else:
        level = "Poor"
        
    return {
        "comprehension_score": round(comprehension_score, 1),
        "fluency_score": round(fluency_score, 1),
        "overall_score": overall_score,
        "understanding_level": level
    }

def generate_ai_feedback(concept_title: str, reference_text: str, transcript: str, scores: dict, audio_features: dict) -> str:
    """
    Utilizes Google Gemini to generate qualitative educational feedback.
    Falls back to a structured template if the API Key is not set or calls fail.
    """
    # Fallback feedback template
    fallback_feedback = f"""### Conceptual Understanding Evaluation
- **Similarity Analysis**: The transcript shares a {scores['comprehension_score']}% conceptual alignment with the target reference concept '{concept_title}'.
- **Key Coverage**: {
    "The explanation captures a majority of the core concepts." if scores['comprehension_score'] >= 70.0 
    else "The explanation covers several basic ideas but lacks details on key tenets." if scores['comprehension_score'] >= 45.0 
    else "The explanation misses critical pillars of the reference concept."
}

### Speech Fluency & Pacing
- **Filler Word Usage**: The filler ratio is {scores['fluency_score']}% (Detected {audio_features.get('filler_word_count', 0)} filler words).
- **Pacing**: The pause ratio is {round(audio_features.get('pause_ratio', 0) * 100, 1)}%. {
    "Your pacing is natural with appropriate pausing." if 0.15 <= audio_features.get('pause_ratio', 0) <= 0.25
    else "You speak with very few pauses, which may make the delivery sound rushed." if audio_features.get('pause_ratio', 0) < 0.15
    else "You have frequent or long silences, which makes the explanation sound hesitant."
}

### Actionable Recommendations
1. Practice explaining this topic without relying on words like "like", "so", or "um".
2. Focus on hitting key terms from the definition to increase understanding coverage.
"""

    if not GEMINI_API_KEY:
        return fallback_feedback.strip()
        
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        You are an expert academic evaluator. Analyze the spoken explanation of a student compared to the reference concept, and provide structured, constructive educational feedback.
        
        Target Topic: {concept_title}
        Reference Concept Definition:
        \"\"\"{reference_text}\"\"\"
        
        Student Spoken Transcription:
        \"\"\"{transcript}\"\"\"
        
        System Assessment Metrics:
        - Conceptual Similarity Alignment: {scores['comprehension_score']}%
        - Overall Evaluation Score: {scores['overall_score']}/100 ({scores['understanding_level']} Understanding level)
        - Speech Pause Ratio: {round(audio_features.get('pause_ratio', 0) * 100, 1)}% (ideal: 15-25%)
        - Filler Word Ratio: {round(audio_features.get('filler_ratio', 0) * 100, 1)}% (ideal: <5%)
        
        Instructions:
        Provide your assessment in a clean markdown format containing three sections:
        1. **Conceptual Understanding Analysis**: Compare the student's explanation to the reference concept. Identify what core elements they got right and what specific details or sub-concepts they missed.
        2. **Fluency & Communication Delivery**: Provide feedback on their speaking delivery based on the pause ratio and filler word usage.
        3. **Actionable Recommendations**: Give 3-4 concrete tips for the student to improve both their knowledge coverage and speech delivery.
        
        Be encouraging, objective, and professional.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        # Log error or return fallback gracefully
        return f"[System Note: Gemini API feedback generation failed. Falling back to default heuristics]\n\n" + fallback_feedback.strip()
