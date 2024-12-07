from flask import Flask, request, jsonify, render_template
import os
import wave
import numpy as np
import soundfile as sf
import librosa
from pydub import AudioSegment
import speech_recognition as sr
import tempfile
from openai import OpenAI
import config

app = Flask(__name__)

UPLOAD_FOLDER = 'temp'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#You need to replace the api_key with your own, format: "sk-xxxxxx"
client = OpenAI(api_key=config.api_key, base_url="https://api.deepseek.com")

class AudioProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.sample_rate = 16000
        self.channels = 1

    def process_audio(self, audio_file):
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            temp_wav_path = temp_wav.name

        try:
            audio = AudioSegment.from_file(audio_file)
            audio = audio.set_frame_rate(self.sample_rate)
            audio = audio.set_channels(self.channels)
            
            audio.export(temp_wav_path, format='wav')
    
            with sr.AudioFile(temp_wav_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data, language='zh-CN')
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant"},
                        {"role": "user", "content": text},
                    ],
                    stream=False
                )
                print(response.choices[0].message.content)
                return response.choices[0].message.content
                #return text

        except sr.UnknownValueError:
            raise Exception("无法识别音频内容")
        except sr.RequestError as e:
            raise Exception(f"识别服务出错: {str(e)}")
        except Exception as e:
            raise Exception(f"处理音频时出错: {str(e)}")
        finally:
            if os.path.exists(temp_wav_path):
                os.remove(temp_wav_path)

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
            processor = AudioProcessor()
            text = processor.process_audio(temp_file.name)
            
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
    app.run(debug=True)