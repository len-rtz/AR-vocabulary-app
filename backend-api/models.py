"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel
from typing import Optional


class TranslateRequest(BaseModel):
    """Request to get Romanian word for QR code"""
    marker_id: str
    participant_id: Optional[int] = None


class TranslateResponse(BaseModel):
    """Response with Romanian word and modality"""
    target_word: str      # Romanian word to display/play
    modality: str         # "AR_TEXT_AUDIO" or "TRADITIONAL_TEXT_AUDIO"
    object_name: str      # English object name
    session_id: Optional[int] = None


class RecallSubmissionResponse(BaseModel):
    """Response after saving voice recording"""
    recall_id: Optional[int]
    message: str
    audio_filename: str


class ParticipantRequest(BaseModel):
    """Request to register new participant"""
    age: int
    gender: str
    nationality: str
    language_experience: str
    condition_order: str  # "text_first" or "audio_first"


class ParticipantResponse(BaseModel):
    """Response after participant registration"""
    participant_id: Optional[int]
    message: str