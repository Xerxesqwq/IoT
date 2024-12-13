from flask import Flask, request, jsonify, render_template
import os
import numpy as np
import soundfile as sf
import tempfile
import deepseek
import AudioProcessor


from openai import OpenAI

app = Flask(__name__)

UPLOAD_FOLDER = 'temp'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

deepseek_client = deepseek.Deepseek()
audio_processor = AudioProcessor.AudioProcessor()

@app.route('/')
def index():
    # templates/index.html
    return render_template('index.html')

@app.route('/recognize', methods=['POST'])
def recognize():
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': '没有收到音频文件'}), 400
    
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'success': False, 'error': '文件名为空'}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            audio_file.save(temp_file.name)
            text = audio_processor.process_audio(temp_file.name)
            
            return jsonify({
                'success': True,
                'text': text
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
    finally:
        if 'temp_file' in locals() and os.path.exists(temp_file.name):
            os.remove(temp_file.name)

if __name__ == '__main__':
    app.run(port=5001)