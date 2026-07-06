import os
import tempfile
import time
import re
import streamlit as st
import numpy as np

# Self-healing check for Windows winget FFmpeg path injection
FFMPEG_WIN_PATH = r"C:\Users\sksam\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin"
if os.path.exists(FFMPEG_WIN_PATH) and FFMPEG_WIN_PATH not in os.environ["PATH"]:
    os.environ["PATH"] = FFMPEG_WIN_PATH + os.pathsep + os.environ["PATH"]


# Import database and models
from database import engine, SessionLocal
import models

# Import ML and processing utilities
from audio_utils import load_audio, extract_audio_features, generate_waveform_plot
from speech_to_text import transcribe_audio
from semantic_eval import compute_similarity
from scoring_engine import (
    analyze_filler_words, calculate_evaluation_score, generate_ai_feedback, DEFAULT_FILLERS
)
from report_generator import generate_pdf_report
from audio_recorder_streamlit import audio_recorder

# Ensure SQLite tables exist on launch
models.Base.metadata.create_all(bind=engine)

# UI Theme styling (Technological Glassmorphism & Minimalist Combined Theme)
st.set_page_config(
    page_title="VBCUA Intelligent Assessor",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deep styled injection of a dark cybernetic glassmorphic interface
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Clean Reset and Cyber Typography */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #f8fafc;
    }
    
    /* Deep space background with glowing cyber circles */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #080d1a 0%, #020408 100%) !important;
        background-attachment: fixed !important;
    }
    
    /* Subtle neon background glow spots */
    .stApp::before {
        content: "";
        position: fixed;
        width: 600px;
        height: 600px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, rgba(0,0,0,0) 70%);
        top: -10%;
        left: -10%;
        z-index: -1;
        pointer-events: none;
    }
    .stApp::after {
        content: "";
        position: fixed;
        width: 600px;
        height: 600px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(6, 182, 212, 0.06) 0%, rgba(0,0,0,0) 70%);
        bottom: -10%;
        right: -10%;
        z-index: -1;
        pointer-events: none;
    }

    /* Completely hide Streamlit branding elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    div.stDeployButton {display: none;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stHeader"] {background: rgba(0,0,0,0); height: 0;}
    
    /* Clean padding margins */
    [data-testid="block-container"] {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
    }

    /* Frosted Glass Sidebar Styling */
    [data-testid="stSidebar"] {
        background: rgba(3, 7, 18, 0.6) !important;
        backdrop-filter: blur(25px) !important;
        -webkit-backdrop-filter: blur(25px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.04) !important;
    }
    [data-testid="stSidebarUserContent"] {
        padding-top: 2rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }

    /* Technological Frosted Glass Card */
    .glass-card {
        background: rgba(15, 23, 42, 0.35) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 20px !important;
        padding: 2rem;
        box-shadow: 0 20px 40px 0 rgba(0, 0, 0, 0.4) !important;
        margin-bottom: 1.5rem !important;
    }
    .glass-card-title {
        font-size: 1.15rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #ffffff;
        margin-top: 0;
        margin-bottom: 1.2rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        border-bottom: 1px solid rgba(255,255,255,0.05);
        padding-bottom: 0.8rem;
    }

    /* Glassmorphic Title Banner */
    .glass-header {
        background: rgba(15, 23, 42, 0.25);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.5rem 2.2rem;
        margin-bottom: 1.8rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 10px 30px 0 rgba(0, 0, 0, 0.15);
    }
    .glass-title-text {
        font-size: 1.7rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .glass-subtitle-text {
        font-size: 0.9rem;
        color: #94a3b8;
        margin-top: 0.1rem;
        margin-bottom: 0;
    }

    /* Glass Metrics Panel */
    .glass-metrics-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.2rem;
        margin-bottom: 1.5rem;
    }
    .glass-metric-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 14px;
        padding: 1.2rem;
        text-align: left;
        transition: border 0.3s ease;
    }
    .glass-metric-card:hover {
        border-color: rgba(6, 182, 212, 0.3);
    }
    .glass-metric-card-lbl {
        font-size: 0.72rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .glass-metric-card-val {
        font-size: 2rem;
        font-weight: 800;
        color: #ffffff;
        margin-top: 0.2rem;
        margin-bottom: 0.5rem;
    }
    .glass-metric-card-val span {
        font-size: 1rem;
        font-weight: 500;
        color: #64748b;
    }

    /* Glass Progress Bar */
    .glass-progress-track {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 6px;
        height: 6px;
        width: 100%;
        overflow: hidden;
    }
    .glass-progress-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }

    /* Glowing Understanding Badges */
    .glass-status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.4rem 1.2rem;
        border-radius: 30px;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .glass-status-badge::before {
        content: '';
        display: inline-block;
        width: 7px;
        height: 7px;
        border-radius: 50%;
    }
    .badge-strong { background-color: rgba(16, 185, 129, 0.08); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.2); }
    .badge-strong::before { background-color: #34d399; box-shadow: 0 0 8px #34d399; }
    
    .badge-moderate { background-color: rgba(245, 158, 11, 0.08); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.2); }
    .badge-moderate::before { background-color: #fbbf24; box-shadow: 0 0 8px #fbbf24; }
    
    .badge-poor { background-color: rgba(239, 68, 68, 0.08); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.2); }
    .badge-poor::before { background-color: #f87171; box-shadow: 0 0 8px #f87171; }

    /* Frosted Splitting Textboxes */
    .textbox-split-glass {
        background: rgba(15, 23, 42, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 1.2rem;
        font-size: 0.92rem;
        line-height: 1.6;
        height: 280px;
        overflow-y: auto;
        color: #cbd5e1;
    }
    .split-title-glass {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        color: #94a3b8;
        margin-bottom: 0.5rem;
        letter-spacing: 0.08em;
    }

    /* Cyber Glowing Highlight for Fillers */
    .filler-highlight {
        background-color: rgba(253, 224, 71, 0.12);
        color: #fde047;
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
        font-weight: 600;
        border: 1px solid rgba(253, 224, 71, 0.3);
        margin: 0 0.08rem;
        box-shadow: 0 0 10px rgba(253, 224, 71, 0.15);
    }

    /* Cyber tabs style */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1.5rem !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding-bottom: 0.2rem !important;
    }
    .stTabs [data-baseweb="tab"] {
        padding-left: 0.2rem !important;
        padding-right: 0.2rem !important;
        background-color: transparent !important;
        font-weight: 600 !important;
        color: #64748b !important;
        border: none !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
        border-bottom: 2px solid #06b6d4 !important;
    }

    /* 2x2 grid for metrics */
    .metric-grid-cyber {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
        margin-top: 1rem;
    }
    .metric-grid-cyber-item {
        background-color: rgba(255, 255, 255, 0.01);
        border: 1px solid rgba(255, 255, 255, 0.04);
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
    }
    .metric-grid-cyber-lbl {
        font-size: 0.72rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-grid-cyber-val {
        font-size: 1.2rem;
        font-weight: 700;
        color: #ffffff;
        margin-top: 0.15rem;
    }

    /* Frosted Dropzone for Uploader */
    section[data-testid="stFileUploadDropzone"] {
        border: 1px dashed rgba(255, 255, 255, 0.12) !important;
        border-radius: 14px !important;
        background-color: rgba(255, 255, 255, 0.01) !important;
        padding: 2rem !important;
    }
    section[data-testid="stFileUploadDropzone"]:hover {
        border-color: rgba(6, 182, 212, 0.5) !important;
    }
    
    /* Glowing button styling */
    div.stButton > button {
        background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.25) !important;
        transition: all 0.2s ease-in-out !important;
        width: 100% !important;
        height: 2.8rem !important;
    }
    div.stButton > button:hover {
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.45) !important;
        transform: translateY(-1px) !important;
    }
    div.stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* Styled Selectbox and expanders to match glass look */
    div[data-baseweb="select"] {
        background-color: rgba(15, 23, 42, 0.5) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    .st-d0, .st-d1, .st-d2 {
        color: white !important;
    }
    .stDetails {
        background-color: rgba(15, 23, 42, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)


# Database Seeding
def seed_database():
    db = SessionLocal()
    try:
        if db.query(models.ReferenceConcept).count() == 0:
            concepts = [
                models.ReferenceConcept(
                    concept_title="Machine Learning",
                    concept_text="Machine learning is a subset of artificial intelligence focused on building systems that learn from data and improve their accuracy over time without being explicitly programmed. It involves training algorithms on large datasets to recognize patterns, make predictions, and adapt to new inputs. Key methodologies include supervised learning, where models are trained on labeled data; unsupervised learning, which finds hidden structures in unlabeled data; and reinforcement learning, which uses rewards and penalties to guide decision-making. Core components include features, training labels, model parameters, and cost functions that measure error during learning."
                ),
                models.ReferenceConcept(
                    concept_title="Cloud Computing",
                    concept_text="Cloud computing is the on-demand delivery of computing services over the internet, including servers, storage, databases, networking, software, and analytics. Instead of buying and maintaining physical data centers, organizations rent access to resources from cloud providers like AWS, Microsoft Azure, or Google Cloud. It is typically structured into three main service models: Infrastructure as a Service (IaaS), Platform as a Service (PaaS), and Software as a Service (SaaS). Key benefits of cloud computing include cost efficiency via pay-as-you-go pricing, global scalability, high availability, disaster recovery, and rapid development speed."
                ),
                models.ReferenceConcept(
                    concept_title="Database Indexes",
                    concept_text="A database index is a data structure designed to speed up the retrieval of records from a database table at the cost of additional storage space and slower write operations. It works similarly to a book index, allowing the database engine to find rows quickly without performing a full table scan. Indexes are typically implemented using structures like B-Trees, B+ Trees, or Hash tables. While indexes dramatically improve the performance of SELECT queries, they add overhead to INSERT, UPDATE, and DELETE operations, as the database must update the index whenever data changes. Creating indexes on highly searched columns is a primary method of database query optimization."
                )
            ]
            db.add_all(concepts)
            db.commit()
            
        if db.query(models.User).count() == 0:
            default_user = models.User(
                name="Jane Doe",
                email="jane.doe@example.com",
                role="Student"
            )
            db.add(default_user)
            db.commit()
    except Exception as e:
        st.error(f"Error seeding database: {e}")
    finally:
        db.close()

seed_database()

# Session State & DB Load
db = SessionLocal()
default_user = db.query(models.User).first()
db.close()

if "user_id" not in st.session_state:
    st.session_state.user_id = default_user.user_id if default_user else 1
if "user_name" not in st.session_state:
    st.session_state.user_name = default_user.name if default_user else "Jane Doe"
if "session_id" not in st.session_state:
    db = SessionLocal()
    new_session = models.Session(user_id=st.session_state.user_id, status="Active")
    db.add(new_session)
    db.commit()
    st.session_state.session_id = new_session.session_id
    db.close()
    
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False
if "result_data" not in st.session_state:
    st.session_state.result_data = {}


# Filler Highlight Converter
def highlight_fillers_in_html(text: str, fillers=DEFAULT_FILLERS) -> str:
    """
    Wraps detected filler words inside customized span labels.
    """
    words = text.split()
    highlighted = []
    for word in words:
        clean = re.sub(r'[^\w]', '', word.lower())
        if clean in fillers:
            highlighted.append(f"<span class='filler-highlight'>{word}</span>")
        else:
            highlighted.append(word)
    return " ".join(highlighted)


# Sidebar layout with minimal design
with st.sidebar:
    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #ffffff; margin-top: 0; font-weight: 800; letter-spacing: -0.02em;'>Concept Assessor</h3>", unsafe_allow_html=True)
    
    db = SessionLocal()
    concepts = db.query(models.ReferenceConcept).all()
    concept_titles = [c.concept_title for c in concepts]
    db.close()
    
    selected_concept_title = st.selectbox("Select Target Concept", concept_titles)
    
    db = SessionLocal()
    selected_concept = db.query(models.ReferenceConcept).filter_by(concept_title=selected_concept_title).first()
    db.close()
    
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Engine Speeds Option (Addressing lagging and performance optimization transparency)
    st.markdown("<div style='font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; margin-bottom: 0.5rem;'>Speech Engine Configuration</div>", unsafe_allow_html=True)
    selected_whisper_model = st.selectbox(
        "Whisper Speech Model",
        ["tiny (fastest - recommended)", "base (balanced)"],
        index=0,
        help="Select 'tiny' for near-instantaneous transcription on CPU. Select 'base' for slightly higher accuracy with longer execution latency."
    )
    # Parse selected model
    whisper_model_key = "tiny" if "tiny" in selected_whisper_model else "base"
    
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
    
    st.markdown("<div style='font-size: 0.8rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; margin-bottom: 0.5rem;'>Expected Concept Definition</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 0.85rem; color: #cbd5e1; line-height: 1.5; background-color: rgba(15,23,42,0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 0.8rem 1rem;'>{selected_concept.concept_text}</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    
    # Session Details
    with st.expander("Session Details"):
        st.write(f"Candidate: {st.session_state.user_name}")
        st.write(f"Session ID: #{st.session_state.session_id}")


# Top Header
st.markdown(f"""
<div class='glass-header'>
    <div>
        <div class='glass-title-text'>VBCUA Assessment System</div>
        <div class='glass-subtitle-text'>Evaluate conceptual knowledge and speech delivery metrics from verbal descriptions.</div>
    </div>
    <div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.05); padding: 0.5rem 1rem; border-radius: 8px; font-size: 0.85rem; font-weight: 600; color: #06b6d4; box-shadow: 0 0 10px rgba(6,182,212,0.1);'>
        Active Model: Whisper {whisper_model_key.upper()}
    </div>
</div>
""", unsafe_allow_html=True)


col_left, col_right = st.columns([5, 7])

# Left side: Voice Acquisition
with col_left:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3 class='glass-card-title'>🎙️ Spoken Input Handler</h3>", unsafe_allow_html=True)
    
    input_tab1, input_tab2 = st.tabs(["🔴 Live Microphone", "📁 WAV File Upload"])
    
    audio_source = None
    audio_bytes = None
    
    with input_tab1:
        st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)
        st.write("Click microphone to start recording:")
        audio_bytes = audio_recorder(
            text="Tap to Record",
            recording_color="#e11d48",
            neutral_color="#06b6d4",
            icon_size="2x"
        )
        if audio_bytes:
            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            st.success("Recording captured successfully.")
            st.audio(audio_bytes, format="audio/wav")
            audio_source = "record"
            
    with input_tab2:
        st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload audio explanation (WAV format only)", type=["wav"], label_visibility="collapsed")
        if uploaded_file is not None:
            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            st.success("Audio file loaded successfully.")
            st.audio(uploaded_file, format="audio/wav")
            audio_source = "upload"
            
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
    
    has_audio = (audio_source == "record" and audio_bytes) or (audio_source == "upload" and uploaded_file)
    
    if st.button("Evaluate Spoken Explanation", use_container_width=True, disabled=not has_audio):
        with st.spinner("Processing speech transcription & delivery evaluation..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                if audio_source == "record":
                    temp_file.write(audio_bytes)
                else:
                    temp_file.write(uploaded_file.read())
                temp_audio_path = temp_file.name
                
            try:
                db = SessionLocal()
                audio_entry = models.AudioFile(
                    user_id=st.session_state.user_id,
                    file_name="microphone_record.wav" if audio_source == "record" else uploaded_file.name,
                    file_path=temp_audio_path,
                    status="Processing"
                )
                db.add(audio_entry)
                db.commit()
                
                # Audio extraction
                y, sr, duration = load_audio(temp_audio_path)
                audio_entry.duration_sec = duration
                db.commit()
                
                features = extract_audio_features(y, sr)
                audio_features_entry = models.AudioFeature(
                    audio_id=audio_entry.audio_id,
                    pause_ratio=features["pause_ratio"],
                    rms_energy=features["rms_energy"],
                    zero_crossing_rate=features["zero_crossing_rate"],
                    duration_sec=features["duration_sec"]
                )
                db.add(audio_features_entry)
                
                # Speech-to-Text Transcription (Using selected optimized model name)
                transcript_text = transcribe_audio(temp_audio_path, model_name=whisper_model_key)
                transcript_entry = models.Transcript(
                    audio_id=audio_entry.audio_id,
                    transcript_text=transcript_text
                )
                db.add(transcript_entry)
                db.commit()
                
                # Filler Words
                filler_stats = analyze_filler_words(transcript_text)
                filler_entry = models.FillerWordStats(
                    transcript_id=transcript_entry.transcript_id,
                    filler_word_count=filler_stats["filler_word_count"],
                    total_words=filler_stats["total_words"],
                    filler_ratio=filler_stats["filler_ratio"]
                )
                db.add(filler_entry)
                
                # Semantic Similarity
                similarity_val = compute_similarity(transcript_text, selected_concept.concept_text)
                similarity_entry = models.SemanticSimilarity(
                    transcript_id=transcript_entry.transcript_id,
                    ref_concept_id=selected_concept.ref_concept_id,
                    similarity_score=similarity_val
                )
                db.add(similarity_entry)
                db.commit()
                
                # Scores Calculation
                scores = calculate_evaluation_score(
                    similarity_score=similarity_val,
                    pause_ratio=features["pause_ratio"],
                    filler_ratio=filler_stats["filler_ratio"]
                )
                
                # Gemini Feedback
                feedback = generate_ai_feedback(
                    concept_title=selected_concept.concept_title,
                    reference_text=selected_concept.concept_text,
                    transcript=transcript_text,
                    scores=scores,
                    audio_features={**features, **filler_stats}
                )
                
                evaluation_entry = models.EvaluationResult(
                    audio_id=audio_entry.audio_id,
                    ref_concept_id=selected_concept.ref_concept_id,
                    session_id=st.session_state.session_id,
                    overall_score=scores["overall_score"],
                    understanding_level=scores["understanding_level"],
                    notes=feedback
                )
                db.add(evaluation_entry)
                db.commit()
                
                # Waveform PNG plot
                waveform_png_path = os.path.join(tempfile.gettempdir(), f"wave_{audio_entry.audio_id}.png")
                generate_waveform_plot(y, sr, waveform_png_path)
                
                # Report PDF
                pdf_filename = f"report_{evaluation_entry.result_id}.pdf"
                pdf_output_path = os.path.join(tempfile.gettempdir(), pdf_filename)
                generate_pdf_report(
                    output_pdf_path=pdf_output_path,
                    user_name=st.session_state.user_name,
                    concept_title=selected_concept.concept_title,
                    reference_text=selected_concept.concept_text,
                    transcribed_text=transcript_text,
                    scores={**scores, "feedback_text": feedback},
                    audio_features={**features, **filler_stats},
                    waveform_png_path=waveform_png_path
                )
                
                report_size_kb = int(os.path.getsize(pdf_output_path) / 1024)
                report_entry = models.Report(
                    result_id=evaluation_entry.result_id,
                    pdf_path=pdf_output_path,
                    file_size_kb=report_size_kb
                )
                db.add(report_entry)
                
                # Finalize
                audio_entry.status = "Analyzed"
                db.commit()
                
                st.session_state.result_data = {
                    "transcript": transcript_text,
                    "scores": scores,
                    "features": features,
                    "fillers": filler_stats,
                    "feedback": feedback,
                    "waveform_path": waveform_png_path,
                    "pdf_path": pdf_output_path
                }
                st.session_state.analysis_complete = True
                db.close()
                st.rerun()
                
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                if 'db' in locals():
                    db.rollback()
                    db.close()
                    
    st.markdown("</div>", unsafe_allow_html=True)


# Right side: Visual Dashboard
with col_right:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h3 class='glass-card-title'>📊 Evaluation Results</h3>", unsafe_allow_html=True)
    
    if st.session_state.analysis_complete:
        res = st.session_state.result_data
        
        # Color coding configuration
        lvl = res['scores']['understanding_level']
        badge_style = "badge-strong" if lvl == "Strong" else "badge-moderate" if lvl == "Moderate" else "badge-poor"
        bar_color = "#34d399" if lvl == "Strong" else "#fbbf24" if lvl == "Moderate" else "#f87171"
        
        # Beautiful Custom Glass Metrics Cards Grid
        st.markdown(f"""
        <div class='glass-metrics-grid'>
            <div class='glass-metric-card'>
                <div class='glass-metric-card-lbl'>Overall Score</div>
                <div class='glass-metric-card-val'>{res['scores']['overall_score']}<span>/100</span></div>
                <div class='glass-progress-track'>
                    <div class='glass-progress-fill' style='width: {res['scores']['overall_score']}%; background-color: {bar_color}; box-shadow: 0 0 8px {bar_color};'></div>
                </div>
            </div>
            <div class='glass-metric-card'>
                <div class='glass-metric-card-lbl'>Comprehension</div>
                <div class='glass-metric-card-val'>{res['scores']['comprehension_score']}%</div>
                <div class='glass-progress-track'>
                    <div class='glass-progress-fill' style='width: {res['scores']['comprehension_score']}%; background-color: #06b6d4; box-shadow: 0 0 8px #06b6d4;'></div>
                </div>
            </div>
            <div class='glass-metric-card'>
                <div class='glass-metric-card-lbl'>Speech Fluency</div>
                <div class='glass-metric-card-val'>{res['scores']['fluency_score']}%</div>
                <div class='glass-progress-track'>
                    <div class='glass-progress-fill' style='width: {res['scores']['fluency_score']}%; background-color: #6366f1; box-shadow: 0 0 8px #6366f1;'></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Understanding rating
        st.markdown(f"""
        <div style='margin-bottom: 1.8rem; text-align: left;'>
            <span class='glass-status-badge {badge_style}'>{lvl} Conceptual Understanding</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Streamlit Tabs
        res_tab1, res_tab2, res_tab3 = st.tabs(["📝 Transcription Comparison", "📈 Acoustic Waveform", "🤖 Qualitative Feedback"])
        
        with res_tab1:
            st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)
            highlighted_transcript = highlight_fillers_in_html(res["transcript"])
            
            c_ref, c_trans = st.columns(2)
            with c_ref:
                st.markdown("<div class='split-title-glass'>Target Concept Definition</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='textbox-split-glass' style='border-left: 3px solid #06b6d4;'>{selected_concept.concept_text}</div>", unsafe_allow_html=True)
            with c_trans:
                st.markdown("<div class='split-title-glass'>Transcribed Speech (Yellow badges are filler words)</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='textbox-split-glass' style='border-left: 3px solid #34d399;'>{highlighted_transcript}</div>", unsafe_allow_html=True)
                
        with res_tab2:
            st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)
            if os.path.exists(res["waveform_path"]):
                st.image(res["waveform_path"], use_container_width=True)
            
            ft = res["features"]
            fl = res["fillers"]
            
            st.markdown("<div class='split-title-glass'>Delivery Performance Metrics</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='metric-grid-cyber'>
                <div class='metric-grid-cyber-item'>
                    <div class='metric-grid-cyber-lbl'>Pause Ratio</div>
                    <div class='metric-grid-cyber-val'>{round(ft['pause_ratio']*100, 1)}% <span style='font-size: 0.75rem; font-weight: 500; color: #94a3b8;'>(Ideal: 15% - 25%)</span></div>
                </div>
                <div class='metric-grid-cyber-item'>
                    <div class='metric-grid-cyber-lbl'>Filler Words Count</div>
                    <div class='metric-grid-cyber-val'>{fl['filler_word_count']} words <span style='font-size: 0.75rem; font-weight: 500; color: #94a3b8;'>(Ratio: {round(fl['filler_ratio']*100, 1)}%)</span></div>
                </div>
                <div class='metric-grid-cyber-item'>
                    <div class='metric-grid-cyber-lbl'>Speech Duration</div>
                    <div class='metric-grid-cyber-val'>{round(ft['duration_sec'], 1)} seconds</div>
                </div>
                <div class='metric-grid-cyber-item'>
                    <div class='metric-grid-cyber-lbl'>RMS Energy (Loudness)</div>
                    <div class='metric-grid-cyber-val'>{round(ft['rms_energy'], 4)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with res_tab3:
            st.markdown("<div style='margin-bottom: 0.8rem;'></div>", unsafe_allow_html=True)
            st.markdown(res["feedback"])
            
        # PDF Download Button
        st.markdown("---")
        if os.path.exists(res["pdf_path"]):
            with open(res["pdf_path"], "rb") as pdf_file:
                pdf_data = pdf_file.read()
            st.download_button(
                label="📥 Download Detailed Evaluation PDF Report",
                data=pdf_data,
                file_name=f"VBCUA_Assessment_{selected_concept_title.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
    else:
        st.info("Please record your speech or upload a WAV audio file on the left panel, and click 'Evaluate Spoken Explanation' to generate the assessment results.")
        
    st.markdown("</div>", unsafe_allow_html=True)
