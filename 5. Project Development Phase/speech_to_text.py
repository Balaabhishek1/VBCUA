import os
import whisper
import streamlit as st

# Self-healing check for Windows winget FFmpeg path injection
FFMPEG_WIN_PATH = r"C:\Users\sksam\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin"
if os.path.exists(FFMPEG_WIN_PATH) and FFMPEG_WIN_PATH not in os.environ["PATH"]:
    os.environ["PATH"] = FFMPEG_WIN_PATH + os.pathsep + os.environ["PATH"]

@st.cache_resource
def get_whisper_model(model_name: str = "tiny"):
    """
    Loads and caches the Whisper model using Streamlit's cache_resource.
    Uses 'tiny' as default for extremely fast CPU transcription.
    """
    # Load model on CPU. FP16=False is required for CPU execution.
    return whisper.load_model(model_name, device="cpu")

def transcribe_audio(file_path: str, model_name: str = "tiny") -> str:
    """
    Transcribes a WAV file into text using OpenAI Whisper.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
        
    model = get_whisper_model(model_name)
    
    # Transcribe audio file. fp16=False prevents CPU-related performance warnings.
    result = model.transcribe(file_path, fp16=False, language="en")
    
    return result.get("text", "").strip()
