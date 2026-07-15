# Data Flow Diagram

**Project Name:** Vocal and Behavioral Candidate Evaluation System (VBCUA)
**Team ID:** (not a team leader and team leader is not in contact)
**Date:** 29 June 2026

## System Data Flow

1. **Input:** User records or uploads audio via the Streamlit Interface.
2. **Audio Processing:** 
   - Audio is routed to `OpenAI Whisper` for local speech-to-text transcription.
   - Audio is routed to `Librosa` for acoustic feature extraction (RMS, Zero-Crossing Rate).
3. **Semantic Analysis:** The transcription is passed to `Sentence-BERT` to compute semantic similarity against standard reference profiles.
4. **Qualitative Feedback:** Transcription and context are passed to `Gemini Pro API` to generate qualitative insights.
5. **Storage:** All metrics (Filler words, similarity score, RMS) are saved to a local `SQLite` database via `SQLAlchemy`.
6. **Output:** 
   - Visualizations are rendered on the `Streamlit` dashboard.
   - A downloadable PDF report is generated using `ReportLab`.
