import os
import sys
import subprocess

def main():
    """
    Orchestration script to run the Streamlit app inside the custom virtual environment.
    """
    # Define paths
    if os.name == "nt":
        streamlit_path = os.path.join("vbcu_env", "Scripts", "streamlit.exe")
    else:
        streamlit_path = os.path.join("vbcu_env", "bin", "streamlit")
        
    if not os.path.exists(streamlit_path):
        print(f"[VBCUA System Error] Streamlit binary not found at '{streamlit_path}'.")
        print("Please verify that Epic 1 installation completed successfully.")
        sys.exit(1)
        
    # Check for .env file
    if not os.path.exists(".env"):
        print("[VBCUA System Warning] .env file not found. System will load SQLite default defaults.")
        
    print("----------------------------------------------------------------------")
    print("Starting Voice-Based Concept Understanding Analyser (VBCUA)...")
    print("----------------------------------------------------------------------")
    
    # Run streamlit
    try:
        subprocess.run([streamlit_path, "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n[VBCUA System] Streamlit server stopped by user.")
    except Exception as e:
        print(f"\n[VBCUA System] Failed to start Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
