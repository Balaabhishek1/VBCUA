FROM python:3.10-slim

# Install system dependencies required by librosa, soundfile, and whisper
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency list from the development phase
COPY "5. Project Development Phase/requirements.txt" .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download NLTK data for tokenizer compatibility
RUN python -c "import nltk; nltk.download('punkt')"

# Pre-cache Sentence-BERT and Whisper models during container build
# This avoids latency and internet requirements at runtime
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
RUN python -c "import whisper; whisper.load_model('base')"

# Copy all application files (including all phase folders)
COPY . .

# Set working directory to the development phase where code and configurations reside
WORKDIR "/app/5. Project Development Phase"

# Expose default Streamlit port
EXPOSE 8501

# Run application headlessly on container startup
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
