import os
import numpy as np
import librosa
import soundfile as sf
import matplotlib.pyplot as plt

def load_audio(file_path: str):
    """
    Loads an audio file and handles format validation.
    Returns:
        y: audio time series
        sr: sampling rate
        duration: duration in seconds
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
        
    try:
        # Check file viability using soundfile
        info = sf.info(file_path)
        # Use librosa to load audio
        y, sr = librosa.load(file_path, sr=None)
        duration = len(y) / sr
        return y, sr, duration
    except Exception as e:
        raise ValueError(f"Failed to load or parse audio file. Ensure it is a valid audio format. Error: {str(e)}")

def extract_audio_features(y, sr, top_db: float = 30.0):
    """
    Extracts acoustic features from the loaded audio signal.
    Returns a dictionary of:
        - pause_ratio
        - rms_energy
        - zero_crossing_rate
        - duration_sec
    """
    duration = len(y) / sr
    if duration == 0:
        return {
            "pause_ratio": 0.0,
            "rms_energy": 0.0,
            "zero_crossing_rate": 0.0,
            "duration_sec": 0.0
        }
        
    # Calculate Pause Ratio using librosa's non-silent intervals split
    # Any signal segment below top_db threshold relative to reference is considered silence (pause)
    intervals = librosa.effects.split(y, top_db=top_db)
    
    non_silent_samples = sum(end - start for start, end in intervals)
    non_silent_duration = non_silent_samples / sr
    
    silent_duration = max(0.0, duration - non_silent_duration)
    pause_ratio = silent_duration / duration
    
    # Calculate Root-Mean-Square (RMS) Energy
    rms_frames = librosa.feature.rms(y=y)
    mean_rms = float(np.mean(rms_frames))
    
    # Calculate Zero Crossing Rate (ZCR)
    zcr_frames = librosa.feature.zero_crossing_rate(y=y)
    mean_zcr = float(np.mean(zcr_frames))
    
    return {
        "pause_ratio": min(1.0, max(0.0, pause_ratio)),
        "rms_energy": mean_rms,
        "zero_crossing_rate": mean_zcr,
        "duration_sec": duration
    }

def generate_waveform_plot(y, sr, output_png_path: str):
    """
    Generates a professional dark-themed waveform plot with a glowing cyan hue.
    """
    # Create figure with a transparent background
    fig, ax = plt.subplots(figsize=(10, 3.5), facecolor='none')
    ax.set_facecolor('none')
    
    time = np.linspace(0, len(y) / sr, num=len(y))
    
    # Sleek cyan line with subtle fill
    ax.plot(time, y, color="#06b6d4", alpha=0.9, linewidth=0.9, label="Waveform")
    ax.fill_between(time, y, color="#0891b2", alpha=0.2)
    
    ax.set_title("Acoustic Signal Waveform", fontsize=11, fontweight="bold", color="#f8fafc", pad=12)
    ax.set_xlabel("Time (seconds)", fontsize=9, color="#94a3b8")
    ax.set_ylabel("Amplitude", fontsize=9, color="#94a3b8")
    
    # Style spines and axes for dark theme
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#334155')
    ax.spines['bottom'].set_color('#334155')
    ax.tick_params(colors='#94a3b8', labelsize=8)
    
    # Custom dark grid
    ax.grid(True, linestyle=":", alpha=0.3, color="#475569")
    plt.tight_layout()
    
    # Save the waveform plot
    plt.savefig(output_png_path, dpi=200, transparent=True)
    plt.close()

