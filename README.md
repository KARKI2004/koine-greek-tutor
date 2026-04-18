# Koine Greek Voice Tutor

A voice-based tutor for Koine Greek pronunciation using the Gemini Live API. Get real-time feedback on pronunciation and English translations.

## Tech Stack

- Python 3.10+
- Gemini 2.5 Flash Live API (native audio)
- PyAudio (microphone I/O)

## Setup

1. Clone and navigate to the project:
   ```bash
   git clone <repo>
   cd koine-greek-tutor
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file with API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage

### Audio File Mode
Process a pre-recorded WAV file (16-bit PCM, mono, 16kHz):
```bash
python tutor.py --audio sample.wav
```

### Microphone Mode
Record from microphone (default 5 seconds):
```bash
python tutor.py --mic
```

Customize recording duration (max 40 seconds):
```bash
python tutor.py --mic --duration 10
```

## Audio Requirements

- Format: WAV (16-bit PCM, mono)
- Sample rate: 16kHz

## How It Works

1. Captures Greek pronunciation (from audio file or microphone)
2. Sends to Gemini Live API for analysis
3. Returns corrected pronunciation, English translation, and feedback
4. Plays spoken response back to user

## Project Files

- `tutor.py` — Main application
- `requirements.txt` — Dependencies
- `.env` — API configuration (create locally)
