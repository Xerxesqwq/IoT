import speech_recognition as sr
import os
import tempfile
from pydub import AudioSegment

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
                return text
            
        except sr.UnknownValueError:
            raise Exception("无法识别音频内容")
        except sr.RequestError as e:
            raise Exception(f"识别服务出错: {str(e)}")
        except Exception as e:
            raise Exception(f"处理音频时出错: {str(e)}")
        finally:
            if os.path.exists(temp_wav_path):
                os.remove(temp_wav_path)