# Solution Requirements

**Project Name:** Vocal and Behavioral Candidate Evaluation System (VBCUA)
**Team ID:** (not a team leader and team leader is not in contact)
**Date:** 29 June 2026

## Functional Requirements
- **FR1:** The system must allow users to upload or record audio directly from the browser.
- **FR2:** The system must transcribe audio to text locally using OpenAI Whisper.
- **FR3:** The system must compute semantic similarity against a predefined reference text using Sentence-BERT.
- **FR4:** The system must detect and count filler words (e.g., um, ah) using NLTK.
- **FR5:** The system must calculate acoustic parameters (RMS, ZCR) from the audio signal.
- **FR6:** The system must generate a downloadable PDF report summarizing the evaluation.

## Non-Functional Requirements
- **NFR1 (Performance):** Transcription and analysis must complete in near real-time (under 30 seconds for short clips).
- **NFR2 (Usability):** The UI must be intuitive and utilize modern glassmorphic design principles.
- **NFR3 (Privacy):** Audio processing (Whisper) must occur locally on the user's machine to protect sensitive interview data.
