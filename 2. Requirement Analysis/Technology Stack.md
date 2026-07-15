# Technology Stack

**Project Name:** Vocal and Behavioral Candidate Evaluation System (VBCUA)
**Team ID:** (not a team leader and team leader is not in contact)
**Date:** 15 March 2024

## Stack Details

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend/UI** | Streamlit (Python) | Rapid development of interactive dashboard and audio recording widget. |
| **Database** | SQLite & SQLAlchemy | Lightweight, local persistence of candidate scores and metrics. |
| **Transcription** | OpenAI Whisper | High-accuracy, local Speech-to-Text inference. |
| **Semantic Engine** | Sentence-BERT (`all-MiniLM-L6-v2`) | Computing cosine similarity between user answers and academic references. |
| **Acoustic Engine** | Librosa & Soundfile | Audio waveform processing, plotting, and feature extraction. |
| **LLM Integration** | Google Gemini Pro API | Providing intelligent, qualitative feedback on the candidate's response. |
| **Reporting** | ReportLab | Compiling metrics and waveform plots into professional PDF documents. |
