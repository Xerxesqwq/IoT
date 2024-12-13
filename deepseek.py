from openai import OpenAI
import config

class Deepseek:
    def __init__(self):
        self.client = OpenAI(api_key=config.api_key, base_url="https://api.deepseek.com")
    
    
    def response(self, input_text):
        response = self.client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant"},
                            {"role": "user", "content": input_text},
                        ],
                        stream=False
                    )
        return response.choices[0].message.content