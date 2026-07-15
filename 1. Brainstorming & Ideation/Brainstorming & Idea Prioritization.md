# Brainstorming & Idea Prioritization

**Project Name:** Vocal and Behavioral Candidate Evaluation System (VBCUA)
**Team ID:** (not a team leader and team leader is not in contact)
**Date:** 29 June 2026

## Ideas Generated
| Idea ID | Description | Pros | Cons |
|---------|-------------|------|------|
| 1 | A system that analyzes interview audio to detect filler words. | Easy to build. | Doesn't evaluate content accuracy. |
| 2 | A platform comparing spoken text against academic reference answers using AI. | High value for users. | Ignores vocal delivery aspects. |
| 3 | A dashboard analyzing acoustic confidence (RMS, ZCR) and semantic accuracy. | Comprehensive evaluation of both delivery and content. | Requires complex integration of audio and LLM pipelines. |

## Selected Idea
**Idea 3 (VBCUA)** - We chose to combine acoustic feature extraction (using Librosa) with semantic similarity (Sentence-BERT) and qualitative AI feedback (Gemini Pro) to provide a holistic evaluation system for candidates.
