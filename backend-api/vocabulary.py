"""
Vocabulary database, maps QR codes to Romanian words and experimental modalities
"""

from typing import Optional, Dict

# QR Code to Romanian Word Mapping
VOCABULARY_DB = {
    # PRACTICE PHASE (3 items)
    "PRACTICE_PLATE": {
        "target_word": "farfurie",
        "modality": "AR_TEXT_AUDIO",
        "object_name": "plate",
        "phase": "practice"
    },
    "PRACTICE_PEAR": {
        "target_word": "pară",
        "modality": "TRADITIONAL_TEXT_AUDIO",
        "object_name": "pear",
        "phase": "practice"
    },
    "PRACTICE_GLOVES": {
        "target_word": "mânuși",
        "modality": "AR_TEXT_AUDIO",
        "object_name": "gloves",
        "phase": "practice"
    },
    
    # EXPERIMENTAL PHASE (text only, 3 items)
    "CUP_ID_1": {
        "target_word": "cupă",
        "modality": "AR_TEXT_AUDIO",  # Text only
        "object_name": "cup",
        "phase": "experiment"
    },
    "APPLE_ID_2": {
        "target_word": "măr",
        "modality": "TRADITIONAL_TEXT_AUDIO",  # Text only
        "object_name": "apple",
        "phase": "experiment"
    },
    "SHOES_ID_3": {
        "target_word": "pantofi",
        "modality": "TRADITIONAL_TEXT_AUDIO",  # Text only
        "object_name": "shoes",
        "phase": "experiment"
    },
    
    # EXPERIMENTAL PHASE (text + audio, 3 items)
    "SPOON_ID_4": {
        "target_word": "lingură",
        "modality": "AR_TEXT_AUDIO",  # Text + audio
        "object_name": "spoon",
        "phase": "experiment"
    },
    "CUCUMBER_ID_5": {
        "target_word": "castravete",
        "modality": "AR_TEXT_AUDIO",  # Text + audio
        "object_name": "cucumber",
        "phase": "experiment"
    },
    "JACKET_ID_6": {
        "target_word": "jachetă",
        "modality": "AR_TEXT_AUDIO",  # Text + audio
        "object_name": "jacket",
        "phase": "experiment"
    }
}


def get_word_for_marker(marker_id: str) -> Optional[Dict]:
    """
    Get vocabulary data for a given QR marker ID
    
    Args:
        marker_id: QR code content (e.g., "CUP_ID_1")
    
    Returns:
        Dictionary with target_word, modality, object_name, phase
        or None if marker not found
    """
    return VOCABULARY_DB.get(marker_id)


def get_all_marker_ids() -> list:
    """Get list of all valid marker IDs"""
    return list(VOCABULARY_DB.keys())


def get_practice_markers() -> list:
    """Get list of practice phase marker IDs"""
    return [k for k, v in VOCABULARY_DB.items() if v.get("phase") == "practice"]


def get_experimental_markers() -> list:
    """Get list of experimental phase marker IDs"""
    return [k for k, v in VOCABULARY_DB.items() if v.get("phase") == "experiment"]


def get_markers_by_modality(modality: str) -> list:
    """Get marker IDs for a specific modality (AR_TEXT_AUDIO or TRADITIONAL_TEXT_AUDIO)"""
    return [k for k, v in VOCABULARY_DB.items() if v.get("modality") == modality]


def marker_exists(marker_id: str) -> bool:
    """Check if a marker ID exists in the vocabulary database"""
    return marker_id in VOCABULARY_DB