import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    role = Column(String(20), default="Student")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    sessions = relationship("Session", back_populates="user")
    audio_files = relationship("AudioFile", back_populates="user")

class Session(Base):
    __tablename__ = "sessions"
    
    session_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="Active")
    
    user = relationship("User", back_populates="sessions")
    evaluation_results = relationship("EvaluationResult", back_populates="session")

class AudioFile(Base):
    __tablename__ = "audio_files"
    
    audio_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    duration_sec = Column(Float, default=0.0)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String(20), default="Uploaded")
    
    user = relationship("User", back_populates="audio_files")
    transcript = relationship("Transcript", uselist=False, back_populates="audio_file")
    audio_feature = relationship("AudioFeature", uselist=False, back_populates="audio_file")
    evaluation_results = relationship("EvaluationResult", back_populates="audio_file")

class ReferenceConcept(Base):
    __tablename__ = "reference_concepts"
    
    ref_concept_id = Column(Integer, primary_key=True, index=True)
    concept_title = Column(String(255), unique=True, index=True, nullable=False)
    concept_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    semantic_similarities = relationship("SemanticSimilarity", back_populates="reference_concept")
    evaluation_results = relationship("EvaluationResult", back_populates="reference_concept")

class Transcript(Base):
    __tablename__ = "transcripts"
    
    transcript_id = Column(Integer, primary_key=True, index=True)
    audio_id = Column(Integer, ForeignKey("audio_files.audio_id"), nullable=False)
    transcript_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    audio_file = relationship("AudioFile", back_populates="transcript")
    filler_word_stats = relationship("FillerWordStats", uselist=False, back_populates="transcript")
    semantic_similarities = relationship("SemanticSimilarity", back_populates="transcript")

class FillerWordStats(Base):
    __tablename__ = "filler_word_stats"
    
    filler_id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(Integer, ForeignKey("transcripts.transcript_id"), nullable=False)
    filler_word_count = Column(Integer, default=0)
    total_words = Column(Integer, default=0)
    filler_ratio = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    transcript = relationship("Transcript", back_populates="filler_word_stats")

class SemanticSimilarity(Base):
    __tablename__ = "semantic_similarities"
    
    similarity_id = Column(Integer, primary_key=True, index=True)
    transcript_id = Column(Integer, ForeignKey("transcripts.transcript_id"), nullable=False)
    ref_concept_id = Column(Integer, ForeignKey("reference_concepts.ref_concept_id"), nullable=False)
    similarity_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    transcript = relationship("Transcript", back_populates="semantic_similarities")
    reference_concept = relationship("ReferenceConcept", back_populates="semantic_similarities")

class AudioFeature(Base):
    __tablename__ = "audio_features"
    
    feature_id = Column(Integer, primary_key=True, index=True)
    audio_id = Column(Integer, ForeignKey("audio_files.audio_id"), nullable=False)
    pause_ratio = Column(Float, default=0.0)
    rms_energy = Column(Float, default=0.0)
    zero_crossing_rate = Column(Float, default=0.0)
    duration_sec = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    audio_file = relationship("AudioFile", back_populates="audio_feature")

class EvaluationResult(Base):
    __tablename__ = "evaluation_results"
    
    result_id = Column(Integer, primary_key=True, index=True)
    audio_id = Column(Integer, ForeignKey("audio_files.audio_id"), nullable=False)
    ref_concept_id = Column(Integer, ForeignKey("reference_concepts.ref_concept_id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.session_id"), nullable=True)
    overall_score = Column(Float, default=0.0)
    understanding_level = Column(String(20), nullable=False) # 'Strong', 'Moderate', 'Poor'
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    audio_file = relationship("AudioFile", back_populates="evaluation_results")
    reference_concept = relationship("ReferenceConcept", back_populates="evaluation_results")
    session = relationship("Session", back_populates="evaluation_results")
    report = relationship("Report", uselist=False, back_populates="evaluation_result")

class Report(Base):
    __tablename__ = "reports"
    
    report_id = Column(Integer, primary_key=True, index=True)
    result_id = Column(Integer, ForeignKey("evaluation_results.result_id"), nullable=False)
    pdf_path = Column(String(255), nullable=False)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)
    file_size_kb = Column(Integer, default=0)
    
    evaluation_result = relationship("EvaluationResult", back_populates="report")
