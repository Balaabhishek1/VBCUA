import os
import tempfile
import numpy as np
import soundfile as sf
import pytest
from audio_utils import load_audio, extract_audio_features

def test_load_audio_non_existent():
    """
    Verifies that loading a non-existent file raises a FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError):
        load_audio("non_existent_file.wav")

def test_load_audio_invalid_format():
    """
    Verifies that loading an invalid file format raises a ValueError.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp.write(b"Not an audio file")
        tmp_path = tmp.name
        
    try:
        with pytest.raises(ValueError):
            load_audio(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def test_extract_audio_features_synthetic():
    """
    Generates a synthetic 2-second WAV file (1 second sine wave, 1 second silence) 
    and checks if the feature extraction module accurately detects duration, 
    energy, and the 50% pause ratio.
    """
    sr = 16000
    # 1 second of 440Hz tone
    t = np.linspace(0, 1.0, sr, endpoint=False)
    tone = 0.5 * np.sin(2 * np.pi * 440.0 * t)
    # 1 second of silence
    silence = np.zeros(sr)
    # Combine signals
    signal = np.concatenate([tone, silence])
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp_path = tmp.name
        sf.write(tmp_path, signal, sr)
        
    try:
        y, loaded_sr, duration = load_audio(tmp_path)
        assert loaded_sr == sr
        assert abs(duration - 2.0) < 0.05
        
        # Analyze features using 30dB threshold
        features = extract_audio_features(y, sr, top_db=30)
        
        assert features["duration_sec"] == duration
        assert features["rms_energy"] > 0.0
        # Since tone is 50% of the duration and silence is 50%, pause ratio should be around 0.5
        assert 0.4 <= features["pause_ratio"] <= 0.6
        assert features["zero_crossing_rate"] > 0.0
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
