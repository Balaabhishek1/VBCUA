# Vocal and Behavioral Candidate Evaluation System (VBCUA)

VBCUA is an advanced, AI-driven educational dashboard and evaluation engine designed to assess spoken explanations against academic reference concepts. By leveraging local machine learning models (OpenAI Whisper for transcription, Sentence-BERT for semantic similarity) and the Gemini Pro API for qualitative reporting, VBCUA evaluates candidate performance across delivery, content accuracy, and acoustic features.

## 🚀 Key Features
*   **Speech-to-Text Transcription:** Instant local CPU transcription using OpenAI Whisper (`tiny`).
*   **Semantic Similarity Analysis:** Cosine similarity analysis of transcripts against standard reference profiles using Sentence-BERT (`all-MiniLM-L6-v2`).
*   **Acoustic Feature Extraction:** Computes Root Mean Square (RMS) energy, Zero Crossing Rate (ZCR), and pause ratios using Librosa and Soundfile.
*   **Modern Glassmorphic UI:** Features radial space glows, frosted cards, progress bar widgets, and dynamic glowing cyan waveforms.
*   **Automated Evaluation Reports:** Compiles candidate details, semantic scores, acoustic parameters, and waveform charts into a PDF report using ReportLab.

---

## 📁 Repository Structure
This repository follows the structured layout of the **AI-ML and Gen AI Track Project Template**:

1. **`1. Brainstorming & Ideation/`**: Contains ideas, empathetic maps, and problem definitions.
2. **`2. Requirement Analysis/`**: Technology stack selection, customer journey mapping, and solution requirements.
3. **`3. Project Design Phase/`**: Architecture diagrams, schema diagrams (SQLite/SQLAlchemy), and problem-solution fits.
4. **`4. Project Planning Phase/`**: Project plans and milestones.
5. **`5. Project Development Phase/`**: The core application codebase.
    *   `app.py`: Streamlit glassmorphic dashboard.
    *   `speech_to_text.py`: Whisper audio transcriber.
    *   `semantic_eval.py`: Sentence-BERT semantic comparator.
    *   `audio_utils.py`: Librosa extraction and waveform plotter.
    *   `scoring_engine.py`: NLTK filler detector, composite scorer, and Gemini feedback.
    *   `report_generator.py`: PDF compiler using ReportLab.
    *   `database.py` & `models.py`: Database ORM layer containing 10 tables.
    *   `run.py`: Automation launcher script.
    *   `tests/`: Suite of unit tests.
6. **`6.Project Testing/`**: Testing logs, performance tests, and verification plans.
7. **`7.Project Documentation/`**: User manuals, execution guides, and documentation.
8. **`8.Project Demonstration/`**: Communication decks and demonstration outlines.

---

## 🛠️ Getting Started (Local Setup)

### Prerequisites
*   Python 3.10+
*   FFmpeg (Required for audio processing)
    *   *Windows Gyan.FFmpeg is dynamically loaded by our self-healing path runner if installed via `winget install Gyan.FFmpeg`.*

### Installation & Execution
Navigate to the development directory:
```bash
cd "5. Project Development Phase"
```

Start the Streamlit application:
```bash
python run.py
```

### Running Tests
Execute the test suite to verify code integrity:
```bash
vbcu_env\Scripts\pytest
```
