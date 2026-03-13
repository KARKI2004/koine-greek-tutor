# Koine Greek Voice Tutor

-------------------------------------

## Overview

This project is a voice-based Koine Greek tutor built using the Gemini Live API.

The tutor accepts spoken input and responds with spoken output.  
It helps practice pronunciation and provides English translations.

The system currently supports two input modes:

1. Audio file mode (for development and testing)
2. Microphone mode (for live spoken input)

Both modes use the same Gemini Live session and native audio model.

-------------------------------------

## Requirements

Python 3.10+

Install dependencies:

pip install -r requirements.txt

-------------------------------------

## Environment Setup

Create a `.env` file in the project root:

GEMINI_API_KEY=your_api_key_here

-------------------------------------

## Running the Tutor

### Audio File Mode

Provide a 16-bit PCM mono 16kHz WAV file:

python tutor.py --audio your_audio.wav

-------------------------------------

### Microphone Mode

Run microphone input mode:

python tutor.py --mic

Note: Microphone access depends on the device being used.

-------------------------------------

## Project Structure

tutor.py  
Main application file containing:

- Gemini Live API connection
- audio streaming logic
- microphone and file input modes
- audio playback

requirements.txt  
Project dependencies

-------------------------------------

## Notes

Audio files must be:

- mono
- 16-bit PCM
- 16kHz sample rate

The application currently records a short microphone segment for testing.  
Future versions will support continuous streaming conversations.

-------------------------------------

## Development Status

Current capabilities:

- Audio file input
- Microphone capture
- Gemini Live audio response
- Spoken tutor feedback

Planned improvements:

- continuous voice streaming
- conversation loop
- web interface for browser use