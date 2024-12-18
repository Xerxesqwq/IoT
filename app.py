from flask import Flask, request, jsonify, render_template, redirect, send_file, session
import os
import numpy as np
import soundfile as sf
import tempfile
import deepseek
import AudioProcessor
from utils import DatabaseManager
from utils import Scheduler
from utils import Controller
from utils import Operation
import config

from openai import OpenAI

app = Flask(__name__)
app.secret_key = '998244353'

UPLOAD_FOLDER = 'temp'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

deepseek_client = deepseek.Deepseek()
audio_processor = AudioProcessor.AudioProcessor()
db_manager = DatabaseManager(sync_mode=True)

controller = Controller()
scheduler = Scheduler()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login_page():
    if 'user_id' in session:
        return redirect('/')
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({
            'success': False,
            'message': '请填写用户名和密码'
        })
    
    user_id = db_manager.user_login(username, password)
    
    if user_id > 0:
        session['user_id'] = user_id
        return jsonify({
            'success': True
        })
    else:
        return jsonify({
            'success': False,
            'message': '用户名或密码错误'
        })
        
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')

@app.route('/recognize', methods=['POST'])
def recognize():
    
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': '没有收到音频文件'}), 400
    
    recognized_text = ''
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'success': False, 'error': '文件名为空'}), 400

    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            audio_file.save(temp_file.name)
            recognized_text = audio_processor.process_audio(temp_file.name)
    except:
        return jsonify({
            'success': False,
            'error': '抱歉，无法识别您的语音'
        }), 500
        
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'error': '请先登录'
        })
    
    user_id = session['user_id']
    prompt = config.base_prompt
    prompt = prompt.replace('^^^', str(user_id)).replace('+++', recognized_text)
    print(prompt)
    response = deepseek_client.response(prompt)
    if 'pass' in response:
        return jsonify({
            'success': False,
            'error': '抱歉，无法执行您的请求'
        }), 500
        
    responses = response.split('#')
    for each in responses:
        scheduler.add_raw_command(each)
    return jsonify({
        'success': True,
        'text': '已尝试执行您的请求'
    })
    




if __name__ == '__main__':
    app.run(port=5001)