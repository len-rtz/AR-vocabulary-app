# AR Vocabulary Learning App
A mobile application for conducting a HCI experiment on multimodal vocabulary learning using augmented reality.

## Features
- **QR Code Recognition:** Point camera at QR codes to reveal vocabulary
- **Voice Recording:** pronunciation recording after each word
- **Experimental Data Logging in SQL + CSV Export**

## Frontend (Flutter/Dart)
- Cross-platform mobile app (iOS/Android)
- QR code scanning with camera feed
- Text-to-speech for (Romanian) pronunciation
- Audio recording for pronunciation assessment
- feedback display

## Backend (Python/FastAPI)
- RESTful API for vocabulary delivery
- SQLite database for experimental data
- local voice recording storage
- CSV export for data analysis

## Setup Instructions

### Prerequisites
- **Frontend:** Flutter SDK, Xcode (iOS) or Android Studio
- **Backend:** Python 3.8+, pip
- **Network:** Phone and computer on same network

### Backend Setup
1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
   
2. **Start the server:**
   ```bash
   python main.py
   ```

### Frontend Setup

1. **Update configuration in `lib/screens/scanner_screen.dart`:**
   ```dart
   const bool USE_MOCK_DATA = false;
   const String BASE_BACKEND_URL = 'http://YOUR_IP:8000';  // Your IP
   ```

2. **Set participant ID:**
   ```dart
   final int _participantId = 1;  // Change for each participant
   ```

3. **Run the app:**
   ```bash
   flutter run
   r // after changing participant
   ```

## Data Collection Workflow

1. **Register participant:**
   ```bash
   curl -X POST http://YOUR_IP:8000/participant/register \
     -H "Content-Type: application/json" \
     -d '{"age":25,"gender":"female","language_experience":"English native","condition_order":"AR_first"}'
   ```
   or via FastAPI Swagger UI

2. **Run experimental session:**
   - Practice phase (3 items)
   - Condition 1 (3 items)
   - Condition 2 (3 items)

3. **After all participants: Export data:**
   ```bash
   curl http://YOUR_IP:8000/export/csv
   ```
## Repo Structure

```
AR-vocabulary-app/
├── backend/
│   ├── main.py              # FastAPI server
│   ├── database.py          # Database operations
│   ├── vocabulary.py        # QR → word mappings
│   ├── models.py            # API data models
│   ├── requirements.txt     # Python dependencies
│   ├── experiment_data.db   # SQLite database (auto-created)
│   └── voice_recordings/    # Audio files (auto-created)
├── lib/
│   └── screens/
│       └── scanner_screen.dart  # Main app screen
├── assets/
│   └── images/
│       └── placeholder.png      # For TRADITIONAL condition
└── README.md
```
