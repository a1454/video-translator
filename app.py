import os
import tempfile
import uuid
from flask import Flask, request, render_template, send_file, jsonify
from werkzeug.utils import secure_filename
import yt_dlp
import whisper
from googletrans import Translator
from gtts import gTTS
import logging

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = 'temp'

# Create temp directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize models
whisper_model = whisper.load_model("base")
translator = Translator()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_video():
    try:
        data = request.json
        youtube_url = data.get('youtube_url')
        target_language = data.get('target_language', 'es')
        
        if not youtube_url:
            return jsonify({'error': 'YouTube URL is required'}), 400
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        os.makedirs(temp_dir, exist_ok=True)
        
        # Step 1: Extract audio from YouTube
        logger.info(f"Extracting audio from: {youtube_url}")
        audio_path = extract_audio_from_youtube(youtube_url, temp_dir)
        
        # Step 2: Convert audio to text using Whisper
        logger.info("Converting audio to text...")
        text = audio_to_text(audio_path)
        
        # Step 3: Translate text
        logger.info(f"Translating to {target_language}...")
        translated_text = translate_text(text, target_language)
        
        # Step 4: Convert translated text to speech
        logger.info("Converting translated text to speech...")
        output_mp3_path = text_to_speech(translated_text, target_language, temp_dir)
        
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

def extract_audio_from_youtube(url, output_dir):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, 'audio.%(ext)s'),
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web']
            }
        }
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    return os.path.join(output_dir, 'audio.wav')

def audio_to_text(audio_path):
    result = whisper_model.transcribe(audio_path)
    return result["text"]

def translate_text(text, target_language):
    # Map language codes for compatibility
    lang_map = {
        'zh': 'zh-cn',  # Chinese simplified
        'pt': 'pt-br',  # Portuguese Brazilian
    }
    dest_lang = lang_map.get(target_language, target_language)
    translated = translator.translate(text, dest=dest_lang)
    return translated.text

def text_to_speech(text, language, output_dir):
    tts = gTTS(text=text, lang=language, slow=False)
    output_path = os.path.join(output_dir, 'output.mp3')
    tts.save(output_path)
    return output_path

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)