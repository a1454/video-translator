# YouTube Audio Translator

A web application that extracts audio from YouTube videos, transcribes it to text, translates it to different languages, and converts the translated text back to speech.

## Features

- Extract audio from YouTube videos using yt-dlp
- Convert speech to text using OpenAI Whisper
- Translate text to multiple languages using OpenAI GPT-3.5 Turbo
- Convert translated text to speech using gTTS
- Download the final translated audio as MP3
- Web interface for easy usage
- Containerized for easy deployment on AWS

## Local Development

### Prerequisites

- Python 3.9+
- FFmpeg (for audio processing)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to `http://localhost:5000`

## Docker Deployment

### Build the Docker image:
```bash
docker build -t youtube-translator .
```

### Run the container:
```bash
docker run -p 5000:5000 youtube-translator
```

## AWS Deployment

1. Build and tag the image for ECR:
   ```bash
   docker build -t youtube-translator .
   docker tag youtube-translator:latest <your-ecr-repo-uri>:latest
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
- `POST /process` - Process YouTube video
- `GET /download/<session_id>` - Download translated audio

## Environment Variables

**Required:**
- `OPENAI_API_KEY` - Your OpenAI API key for GPT-3.5 Turbo translation

**Setup:**
```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

Or create a `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Limitations

- Processing time depends on video length
- Large videos may require significant processing time
- Google Translate API has rate limits
- Requires internet connection for all operations