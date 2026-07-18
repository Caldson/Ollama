from openai import OpenAI

class EasyOllama:
    def __init__(self, api_key, model='qwen2.5:1.5b', base_url='http://localhost:11434/v1/', debug=False):
        if debug:
            print(f"[EasyOllama] Init model {model}...")
        self.model = model
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,  # required but ignored
        )
        self.messages = [
            {'role': 'system', 'content': '你是一个有帮助的AI智能助手，你回复的内容必须是纯文本，因为使用端是Python，不能包含HTML、Markdown等标签。如果用户请求你回答Python等等代码，你必须回复\'本模型暂不支持代码。\'。'},
        ]
    def chat(self, message):
        self.messages.append({'role': 'user', 'content': message})
        try:
            chat_completion = self.client.chat.completions.create(
                messages=self.messages,
                model=self.model,
            )
        except Exception as e:
            raise EasyOllamaError(f"[EasyOllama] Error: {e}")
        self.messages.append({'role': 'assistant', 'content': chat_completion.choices[0].message.content})
        return chat_completion.choices[0].message.content
    # Powershell 命令的执行删除，因为我们只想为Ollama专用而生，不想搞Anthropic的工具调用。
    class EasyOllamaError(Exception):
        def __init__(self, message):
            self.message = message
            super().__init__(self.message)