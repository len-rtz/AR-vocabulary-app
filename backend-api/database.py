"""
Database module for AR Vocabulary App
Handles SQLite database operations
"""

import sqlite3
from pathlib import Path
from typing import Optional, Dict

DB_PATH = Path("experiment_data.db")


def init_database():
    """Initialize SQLite database with tables for experiment data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Participants table - Demographics and condition assignment
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS participants (
            participant_id INTEGER PRIMARY KEY AUTOINCREMENT,
            age INTEGER,
            gender TEXT,
            language_experience TEXT,
            condition_order TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Translation sessions - When QR code is scanned and word is shown
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS translation_sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            participant_id INTEGER,
            marker_id TEXT,
            object_name TEXT,
            target_word TEXT,
            modality TEXT,
            phase TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (participant_id) REFERENCES participants(participant_id)
        )
    """)
    
    # Recall attempts - Voice recordings submitted by participants
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recall_attempts (
            recall_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            participant_id INTEGER,
            marker_id TEXT,
            target_word TEXT,
            audio_file_path TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES translation_sessions(session_id),
            FOREIGN KEY (participant_id) REFERENCES participants(participant_id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized.")


def register_participant(age: int, gender: str, language_experience: str, 
                        condition_order: str) -> int:
    """Register a new participant and return their ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO participants (age, gender, language_experience, condition_order)
        VALUES (?, ?, ?, ?)
    """, (age, gender, language_experience, condition_order))
    
    participant_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return participant_id


def log_translation_session(participant_id: int, marker_id: str, object_name: str,
                           target_word: str, modality: str, phase: str) -> int:
    """Log a translation session when QR code is scanned"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO translation_sessions 
        (participant_id, marker_id, object_name, target_word, modality, phase)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (participant_id, marker_id, object_name, target_word, modality, phase))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return session_id


def log_recall_attempt(session_id: Optional[int], participant_id: int, marker_id: str,
                       target_word: str, audio_file_path: str) -> int:
    """Log a recall attempt when voice is recorded"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO recall_attempts 
        (session_id, participant_id, marker_id, target_word, audio_file_path)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, participant_id, marker_id, target_word, audio_file_path))
    
    recall_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return recall_id

def export_to_csv():
    """Export all data to CSV files"""
    import pandas as pd
    
    conn = sqlite3.connect(DB_PATH)
    
    # Export participants
    participants_df = pd.read_sql_query("SELECT * FROM participants", conn)
    participants_df.to_csv("export_participants.csv", index=False)
    
    # Export translation sessions
    sessions_df = pd.read_sql_query("SELECT * FROM translation_sessions", conn)
    sessions_df.to_csv("export_translation_sessions.csv", index=False)
    
    # Export recall attempts
    recalls_df = pd.read_sql_query("SELECT * FROM recall_attempts", conn)
    recalls_df.to_csv("export_recall_attempts.csv", index=False)
    
    # Create combined view - FIXED QUERY
    query = """
        SELECT 
            p.participant_id,
            p.age,
            p.gender,
            p.language_experience,
            p.condition_order,
            ts.session_id,
            ts.marker_id,
            ts.object_name,
            ts.target_word,
            ts.modality,
            ts.phase,
            ts.timestamp as word_shown_at,
            ra.recall_id,
            ra.audio_file_path,
            ra.timestamp as voice_recorded_at
        FROM translation_sessions ts
        LEFT JOIN participants p ON ts.participant_id = p.participant_id
        LEFT JOIN recall_attempts ra ON ts.session_id = ra.session_id
        ORDER BY ts.participant_id, ts.timestamp
    """
    combined_df = pd.read_sql_query(query, conn)
    combined_df.to_csv("export_combined_data.csv", index=False)
    
    conn.close()
    
    return {
        "participants": len(participants_df),
        "sessions": len(sessions_df),
        "recordings": len(recalls_df),
        "combined_rows": len(combined_df)
    }