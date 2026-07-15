# Performance Testing

**Project Name:** Vocal and Behavioral Candidate Evaluation System (VBCUA)
**Team ID:** Solo Developer

## Testing Strategy
- **Unit Testing:** A suite of tests utilizing `pytest` is included in the `tests/` directory.
- **Coverage:** Tests cover audio processing functions, semantic evaluation, scoring logic, and database schemas.
- **Execution Time:** The entire test suite executes in approximately 18-20 seconds on standard hardware.

## Performance Metrics
- **Transcription Latency:** Whisper `tiny` transcribes 30-second audio clips in under 5 seconds on modern CPUs.
- **Dashboard Load Time:** Streamlit UI renders in under 2 seconds.
- **Model Caching:** `@st.cache_resource` is used extensively to prevent reloading heavy PyTorch/Transformer models during UI interactions, significantly improving performance.
