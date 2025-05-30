# Video Audio Translator

A web application that extracts audio from uploaded video files, transcribes it to text, translates it to different languages, and converts the translated text back to speech.

## Features

- Extract audio from uploaded video files using FFmpeg
- Convert speech to text using OpenAI Whisper (local model or API)
- Translate text to multiple languages using OpenAI GPT-3.5 Turbo
- Convert translated text to speech using OpenAI TTS
- Download the final translated audio as MP3
- Web interface for easy usage
- Configurable Whisper mode (local vs API)
- Environment-based configuration
- Containerized for easy deployment

## Local Development

### Prerequisites

- Python 3.9+
- FFmpeg (for audio processing)

### Installation

1. Clone the repository
2. Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key and preferred settings
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to `http://localhost:5000`

## Docker Deployment

### Build the Docker image:
```bash
docker build -t video-translator .
```

### Run the container:
```bash
# Copy environment file first
cp .env.example .env
# Edit .env with your configuration
docker run -p 5000:5000 --env-file .env video-translator
```

## AWS Deployment

1. Build and tag the image for ECR:
   ```bash
   docker build -t video-translator .
   docker tag video-translator:latest <your-ecr-repo-uri>:latest
   ```

2. Push to ECR:
   ```bash
   docker push <your-ecr-repo-uri>:latest
   ```

3. Deploy using ECS, EKS, or App Runner

## Supported Languages

- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
- Korean (ko)
- Chinese (zh)
- Arabic (ar)
- Hindi (hi)

## API Endpoints

- `GET /` - Web interface
- `POST /process` - Process uploaded video file
- `GET /download/<session_id>` - Download translated audio

## Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and configure:

**Required:**
- `OPENAI_API_KEY` - Your OpenAI API key

**Optional:**
- `WHISPER_MODE` - "local" (default) or "api" for OpenAI Whisper API
- `WHISPER_MODEL_SIZE` - "tiny", "base" (default), "small", "medium", "large"
- `MAX_CONTENT_LENGTH` - Maximum file size in bytes (default: 500MB)
- `FLASK_ENV` - "development" or "production"
- `FLASK_DEBUG` - "True" or "False"

**Whisper Modes:**
- `local`: Uses local Whisper model (faster, no API costs, requires more CPU/memory)
- `api`: Uses OpenAI Whisper API (slower, costs per request, less resource intensive)

## Limitations

- Processing time depends on video length and Whisper mode
- Large videos may require significant processing time
- Local Whisper models require substantial CPU/memory resources
- OpenAI API usage incurs costs
- Maximum file size is configurable (default: 500MB)