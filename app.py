import os
import tempfile
import uuid
from flask import Flask, request, render_template, send_file, jsonify
from werkzeug.utils import secure_filename
import subprocess
import whisper
from openai import OpenAI
# Removed gTTS import - using OpenAI TTS instead
import logging

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = 'temp'

# Create temp directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize models
whisper_model = whisper.load_model("base")
client = OpenAI(api_key="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")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_video():
    try:
        # Check if file was uploaded
        if 'video_file' not in request.files:
            return jsonify({'error': 'No video file uploaded'}), 400
        
        file = request.files['video_file']
        target_language = request.form.get('target_language', 'es')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        os.makedirs(temp_dir, exist_ok=True)
        
        # Step 1: Save uploaded file and extract audio
        logger.info(f"Processing uploaded file: {file.filename}")
        video_path = os.path.join(temp_dir, secure_filename(file.filename))
        file.save(video_path)
        audio_path = extract_audio_from_video(video_path, temp_dir)
        
        # Step 2: Convert audio to text using Whisper
        logger.info("Converting audio to text...")
        text = audio_to_text(audio_path)
        
        # Step 3: Translate text
        logger.info(f"Translating to {target_language}...")
        translated_text = translate_text(text, target_language)
        
        # Step 4: Convert translated text to speech
        logger.info("Converting translated text to speech...")
        text_to_speech(translated_text, target_language, temp_dir)
        
        return jsonify({
            'success': True,
            'original_text': text,
            'translated_text': translated_text,
            'audio_file': f'/download/{session_id}',
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<session_id>')
def download_file(session_id):
    try:
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        output_file = os.path.join(temp_dir, 'output.mp3')
        
        if os.path.exists(output_file):
            return send_file(output_file, as_attachment=True, download_name='translated_audio.mp3')
        else:
            return jsonify({'error': 'File not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_audio_from_video(video_path, output_dir):
    """Extract audio from uploaded video file using FFmpeg"""
    audio_output_path = os.path.join(output_dir, 'audio.wav')
    
    try:
        # Use FFmpeg to extract audio from video
        cmd = [
            'ffmpeg', 
            '-i', video_path,           # Input video file
            '-vn',                      # No video output
            '-acodec', 'pcm_s16le',     # Audio codec: 16-bit PCM
            '-ar', '16000',             # Sample rate: 16kHz (good for Whisper)
            '-ac', '1',                 # Mono audio
            '-y',                       # Overwrite output file
            audio_output_path
        ]
        
        logger.info("Extracting audio from video using FFmpeg...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info("Audio extraction completed successfully")
        
        return audio_output_path
        
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error: {e.stderr}")
        raise Exception(f"Failed to extract audio from video: {e.stderr}")
    except FileNotFoundError:
        raise Exception("FFmpeg not found. Please install FFmpeg to process video files.")
    except Exception as e:
        logger.error(f"Unexpected error during audio extraction: {str(e)}")
        raise Exception(f"Failed to extract audio: {str(e)}")

def audio_to_text(audio_path):
    result = whisper_model.transcribe(audio_path)
    return result["text"]

def translate_text(text, target_language):
    # Map language codes to full language names
    lang_map = {
        'es': 'Spanish',
        'fr': 'French', 
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese',
        'ar': 'Arabic',
        'hi': 'Hindi'
    }
    
    target_lang_name = lang_map.get(target_language, target_language)
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a professional translator. Translate the following text to {target_lang_name}. Only return the translated text, no explanations or additional content."
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            max_tokens=2000,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI translation error: {str(e)}")
        raise e

def text_to_speech(text, language, output_dir):
    """Convert text to speech using OpenAI TTS API"""
    output_path = os.path.join(output_dir, 'output.mp3')
    
    # Map language codes to appropriate voices
    voice_map = {
        'es': 'nova',    # Spanish - female voice
        'fr': 'alloy',   # French - neutral voice
        'de': 'echo',    # German - male voice
        'it': 'fable',   # Italian - female voice
        'pt': 'nova',    # Portuguese - female voice
        'ru': 'onyx',    # Russian - male voice
        'ja': 'shimmer', # Japanese - female voice
        'ko': 'alloy',   # Korean - neutral voice
        'zh': 'nova',    # Chinese - female voice
        'ar': 'fable',   # Arabic - female voice
        'hi': 'echo'     # Hindi - male voice
    }
    
    voice = voice_map.get(language, 'alloy')  # Default to alloy voice
    
    try:
        logger.info(f"Generating speech with OpenAI TTS using voice: {voice}")
        response = client.audio.speech.create(
            model="tts-1",  # Use tts-1 for faster generation, tts-1-hd for higher quality
            voice=voice,
            input=text,
            response_format="mp3"
        )
        
        # Save the audio file
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        logger.info("Speech generation completed successfully")
        return output_path
        
    except Exception as e:
        logger.error(f"OpenAI TTS error: {str(e)}")
        raise Exception(f"Failed to generate speech: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)