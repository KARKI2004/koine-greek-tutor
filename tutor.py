import argparse
import asyncio
import os
import wave
from pathlib import Path

import pyaudio
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MODEL = "gemini-2.5-flash-native-audio-preview-12-2025"
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHANNELS = 1
SAMPLE_WIDTH_BYTES = 2
CHUNK_SAMPLES = 1600  # 100ms at 16kHz
MIC_DURATION_SECONDS = 5  # change to adjust recording length


MIC_SYSTEM_INSTRUCTION = """
You are a Koine Greek tutor.

For every user utterance, always respond in this exact order:
1. Say the Greek sentence again with correct Erasmian pronunciation.
2. Give the English translation.
3. If the user's pronunciation had mistakes, briefly correct them.

Rules:
- Always include all applicable parts.
- Keep the response short.
- Do not add unrelated commentary.f
- Speak slowly and clearly for learners.
"""


FILE_SYSTEM_INSTRUCTION = """
You are a Koine Greek language assistant.

For every audio recording, always respond in this exact order:
1. Give a short English summary of the whole recording.
2. Give the English translation of the Greek content.
3. Repeat the key Greek phrase or sentence with Erasmian pronunciation if Greek speech is present.

Rules:
- Always include the summary first.
- Do not skip the translation.
- Keep the response short and clear.
- Do not add unrelated commentary.
"""


MIC_CONFIG = {
    "response_modalities": ["AUDIO"],
    "system_instruction": MIC_SYSTEM_INSTRUCTION,
}


FILE_CONFIG = {
    "response_modalities": ["AUDIO"],
    "system_instruction": FILE_SYSTEM_INSTRUCTION,
}


def resolve_audio_path(requested_path: str) -> str:
    candidate = Path(requested_path)
    if candidate.exists():
        return str(candidate)

    wav_files = sorted(Path(".").glob("*.wav"))
    if requested_path == "sample_audio.wav" and wav_files:
        chosen = wav_files[0]
        print(f"[info] '{requested_path}' not found. Using '{chosen.name}' instead.")
        return str(chosen)

    available = ", ".join(f.name for f in wav_files) if wav_files else "none"
    raise FileNotFoundError(
        f"Audio file not found: '{requested_path}'. Available .wav files: {available}"
    )


def validate_wav(path: str) -> None:
    with wave.open(path, "rb") as wf:
        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        if channels != CHANNELS or sampwidth != SAMPLE_WIDTH_BYTES or framerate != SEND_SAMPLE_RATE:
            raise ValueError(
                f"{path} must be mono, 16-bit PCM, 16kHz. "
                f"Found channels={channels}, sample_width={sampwidth * 8}-bit, rate={framerate}."
            )


async def stream_wav_audio(session, path: str) -> None:
    frames_per_chunk = CHUNK_SAMPLES
    with wave.open(path, "rb") as wf:
        while True:
            chunk = wf.readframes(frames_per_chunk)
            if not chunk:
                break
            await session.send_realtime_input(
                audio=types.Blob(data=chunk, mime_type=f"audio/pcm;rate={SEND_SAMPLE_RATE}")
            )
    await session.send_realtime_input(audio_stream_end=True)


async def play_response_audio(session) -> None:
    pya = pyaudio.PyAudio()
    stream = pya.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=RECEIVE_SAMPLE_RATE,
        output=True,
    )
    try:
        async for response in session.receive():
            server_content = response.server_content
            if server_content and server_content.model_turn:
                for part in server_content.model_turn.parts:
                    if part.inline_data and isinstance(part.inline_data.data, bytes):
                        stream.write(part.inline_data.data)
            if server_content and getattr(server_content, "turn_complete", False):
                break
    finally:
        stream.stop_stream()
        stream.close()
        pya.terminate()


async def run_audio_file(audio_path: str) -> None:
    audio_path = resolve_audio_path(audio_path)
    validate_wav(audio_path)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY in .env")

    client = genai.Client(api_key=api_key)
    async with client.aio.live.connect(model=MODEL, config=FILE_CONFIG) as session:
        await stream_wav_audio(session, audio_path)
        await play_response_audio(session)


async def run_microphone(duration: int = MIC_DURATION_SECONDS) -> None:
    pya = pyaudio.PyAudio()
    stream = pya.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SEND_SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SAMPLES,
    )

    chunks = []
    total_chunks = int((SEND_SAMPLE_RATE * duration) / CHUNK_SAMPLES)

    print("Listening...")
    try:
        for _ in range(total_chunks):
            chunks.append(
                stream.read(CHUNK_SAMPLES, exception_on_overflow=False)
            )
    finally:
        if stream.is_active():
            stream.stop_stream()
        stream.close()
        pya.terminate()

    print("Processing...")
    captured_audio = b"".join(chunks)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing GEMINI_API_KEY in .env")

    client = genai.Client(api_key=api_key)

    async with client.aio.live.connect(model=MODEL, config=MIC_CONFIG) as session:
        await session.send_realtime_input(
            audio=types.Blob(data=captured_audio, mime_type="audio/pcm;rate=16000")
        )
        await session.send_realtime_input(audio_stream_end=True)
        print("Speaking...")
        await play_response_audio(session)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Koine Greek voice tutor.")
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--audio",
        help="Path to 16-bit PCM 16kHz mono WAV file.",
    )
    mode_group.add_argument(
        "--mic",
        action="store_true",
        help="Use microphone input mode.",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=MIC_DURATION_SECONDS,
        help="Recording duration in seconds (mic mode only).",
    )

    args = parser.parse_args()

    if args.duration > 40:
        parser.error("Duration cannot exceed 40 seconds.")

    if args.audio:
        asyncio.run(run_audio_file(args.audio))
    elif args.mic:
        asyncio.run(run_microphone(duration=args.duration))