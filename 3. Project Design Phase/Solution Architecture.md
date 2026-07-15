# Solution Architecture

**Project Name:** Vocal and Behavioral Candidate Evaluation System (VBCUA)
**Team ID:** (not a team leader and team leader is not in contact)
**Date:** 30 June 2026

## Architecture Components

1. **Presentation Layer (Streamlit):** Handles UI interactions, audio capture, and visualization rendering.
2. **Processing Layer (Python):**
   - **Audio Extractor:** Uses `Librosa` to plot waveforms and calculate energy metrics.
   - **Transcriber:** Feeds audio to `Whisper` for text conversion.
   - **Evaluator:** Calculates cosine similarity with `Sentence-BERT` and filler counts with `NLTK`.
3. **External APIs:** Calls `Gemini Pro` for qualitative feedback generation.
4. **Data Layer:** Uses `SQLAlchemy` ORM to save records to a local `SQLite` database.
5. **Export Module:** Uses `ReportLab` to compile PDFs.
