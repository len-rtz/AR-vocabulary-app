"""
Main API Server
FastAPI backend for handling QR code translations and voice recordings
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
from datetime import datetime
from typing import Optional

# Import modules
from database import (
    init_database, 
    register_participant,
    log_translation_session,
    log_recall_attempt,
    export_to_csv
)
from vocabulary import get_word_for_marker, get_all_marker_ids
from models import (
    TranslateRequest,
    TranslateResponse,
    RecallSubmissionResponse,
    ParticipantRequest,
    ParticipantResponse
)

# Initialize FastAPI app
app = FastAPI(title="AR Vocabulary Learning Experiment")

# Enable CORS for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create recordings directory
RECORDINGS_DIR = Path("voice_recordings")
RECORDINGS_DIR.mkdir(exist_ok=True)

# Initialize database on startup
init_database()

# API ENDPOINTS
@app.get("/")
async def root():
    """Health check and system info"""
    return {
        "status": "running",
        "message": "AR Vocabulary Learning Experiment Backend",
        "experiment_design": {
            "practice_items": 3,
            "traditional_items": 3,
            "AR_items": 3,
            "total_qr_codes": len(get_all_marker_ids())
        }
    }


@app.post("/participant/register", response_model=ParticipantResponse)
async def register_participant_endpoint(request: ParticipantRequest):
    """
    Register a new participant at the start of the experiment.
    Records demographic information and counterbalanced condition order.
    """
    participant_id = register_participant(
        age=request.age,
        gender=request.gender,
        nationality=request.nationality,
        language_experience=request.language_experience,
        condition_order=request.condition_order
    )
    
    print(f"Participant {participant_id} registered")
    print(f"Demographics: {request.age}yo, {request.gender}")
    print(f"Condition order: {request.condition_order}")
    
    return ParticipantResponse(
        participant_id=participant_id,
        message=f"Participant {participant_id} registered. Ready to start experiment."
    )


@app.post("/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """
    Call when QR code is scanned.
    Returns the Romanian word and display modality.
    Logs the translation event to database.
    """
    marker_id = request.marker_id
    
    # Get vocabulary data for this QR code
    vocab_data = get_word_for_marker(marker_id)
    
    if not vocab_data:
        raise HTTPException(
            status_code=404,
            detail=f"QR code '{marker_id}' not recognized. Valid codes: {get_all_marker_ids()}"
        )
    
    # Log this translation session to database
    session_id = None
    if request.participant_id:
        session_id = log_translation_session(
            participant_id=request.participant_id,
            marker_id=marker_id,
            object_name=vocab_data["object_name"],
            target_word=vocab_data["target_word"],
            modality=vocab_data["modality"],
            phase=vocab_data.get("phase", "unknown")
        )
        
        print(f"QR scanned: {marker_id} → '{vocab_data['target_word']}'")
        print(f"Participant: {request.participant_id}, Session: {session_id}")
        print(f"Modality: {vocab_data['modality']}")
    
    # Return word info to frontend
    return TranslateResponse(
        target_word=vocab_data["target_word"],
        modality=vocab_data["modality"],
        object_name=vocab_data["object_name"],
        session_id=session_id
    )

@app.post("/recall", response_model=RecallSubmissionResponse)
async def recall(
    audio_file: UploadFile = File(...),
    target_word: str = Form(...),
    marker_id: str = Form(...),
    participant_id: Optional[int] = Form(None),
    session_id: Optional[int] = Form(None)
):
    """
    Called when user records their pronunciation.
    Saves the audio file and logs the attempt.
    """
    # Generate structured filename for easy identification
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
    
    # Filename format: P{id}_{timestamp}_{marker}_{word}.m4a
    participant_prefix = f"P{participant_id:03d}" if participant_id else "P000"
    filename = f"{participant_prefix}_{timestamp}_{marker_id}_{target_word}.m4a"
    file_path = RECORDINGS_DIR / filename
    
    # Save audio file
    try:
        contents = await audio_file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        file_size_kb = len(contents) / 1024
        print(f"Voice recorded: {filename}")
        print(f"Size: {file_size_kb:.1f} KB")
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to save audio file: {str(e)}"
        )
    
    # Log recall attempt to database
    recall_id = None
    if participant_id:
        recall_id = log_recall_attempt(
            session_id=session_id,
            participant_id=participant_id,
            marker_id=marker_id,
            target_word=target_word,
            audio_file_path=str(file_path)
        )
        
        print(f"Database: Recall #{recall_id} logged")
    
    return RecallSubmissionResponse(
        recall_id=recall_id,
        message="Voice recording saved.",
        audio_filename=filename
    )


@app.get("/export/csv")
async def export_to_csv_endpoint():
    """
    Export all data to CSV files for analysis.
    Creates separate files for participants, sessions, and recordings.
    """
    row_counts = export_to_csv()

    print("Data exported to CSV files.")
    
    return {
        "message": "Data exported successfully",
        "files": [
            "export_participants.csv",
            "export_translation_sessions.csv",
            "export_recall_attempts.csv",
            "export_combined_data.csv"
        ],
        "row_counts": row_counts
    }

# STARTUP

if __name__ == "__main__":
    print("AR vocabulary app backend starting...")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)