# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask web application that processes video files through a translation pipeline: Video Upload → Audio Extraction (FFmpeg) → Speech-to-Text (Whisper) → Translation (OpenAI GPT-3.5) → Text-to-Speech (OpenAI TTS) → Download.

## Architecture

**Single-file Flask application** (`app.py`) with modular processing functions:
- Session-based temporary file management using UUIDs
- RESTful API: `/` (UI), `/process` (main processing), `/download/<session_id>`
- Configurable Whisper mode: local model vs OpenAI API

**Key Processing Functions:**
- `extract_audio_from_video()`: FFmpeg-based audio extraction
- `audio_to_text()`: Whisper transcription (local or API)
- `translate_text()`: OpenAI GPT-3.5 translation
- `text_to_speech()`: OpenAI TTS synthesis

## Development Commands

**Setup:**
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
pip install -r requirements.txt
```

**Run Development Server:**
```bash
python app.py
# Runs on http://localhost:5000 with debug enabled
```

**Docker:**
```bash
docker build -t video-translator .
docker run -p 5000:5000 --env-file .env video-translator
```

## Configuration

**Required Environment Variables:**
- `OPENAI_API_KEY`: OpenAI API key for translation and TTS

**Key Configuration Options:**
- `WHISPER_MODE`: `"local"` (uses local model) or `"api"` (uses OpenAI API)
- `WHISPER_MODEL_SIZE`: Model size for local mode (`tiny`, `base`, `small`, `medium`, `large`)
- `MAX_CONTENT_LENGTH`: Maximum upload size (default: 500MB)

**Whisper Mode Trade-offs:**
- Local: CPU/memory intensive, no API costs, faster for repeated use
- API: Network dependent, incurs costs, less resource intensive

## System Dependencies

**Required:**
- FFmpeg (for video/audio processing)
- Python 3.9+
- OpenAI API key

## File Structure

- `app.py`: Main application with all processing logic
- `templates/index.html`: Single-page frontend with embedded CSS/JS
- `temp/`: Session-based temporary file storage (auto-created)
- `.env`: Configuration (excluded from git)
- `Dockerfile`: Production deployment configuration

## Supported Languages

11 languages with language-specific TTS voice mapping: Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese, Arabic, Hindi.

## Testing Status

No formal testing framework currently implemented. The codebase would benefit from unit tests for processing functions and integration tests for API endpoints.