# EasyOllama
from openai import OpenAI
# EasyOllamaBeta
import anthropic

# Lastest
class EasyOllama:
    def __init__(self, api_key, model='qwen3-coder', base_url='http://localhost:11434/v1/'):
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
        chat_completion = self.client.chat.completions.create(
            messages=self.messages,
            model=self.model,
        )
        self.messages.append({'role': 'assistant', 'content': chat_completion.choices[0].message.content})
        return chat_completion.choices[0].message.content
    # Powershell 命令的执行删除，因为我们只想为Ollama专用而生，不想搞Anthropic的工具调用。

# Pre-release
class EasyOllamaBeta:
    def __init__(self, api_key):
        print(f"[EasyOllama] Init model qwen3-coder...")
        self.client = anthropic.Anthropic(
            base_url='http://localhost:11434/',
            api_key=api_key,  # required but ignored
        )
        self.messages = [
            {'role': 'system', 'content': '你是一个有帮助的AI智能助手，你回复的内容必须是纯文本格式，因为使用端是Python，不能包含HTML、Markdown、原生Ollama的标签（包括left、right、'+r'\['+'、frac等等）等文本，必须是纯文本格式！。如果用户请求你回答Python等等代码，你必须编辑文件。编辑文件前必须先阅读文件内容（使用read_file这个tools然后用edit_file这个tools进行编辑），不能直接编辑（防止覆盖了重要的信息）。如果用户让你用tools什么的（编辑文件、阅读文件等等等等）你必须要用tools！'},
        ]
    def chat(self, message, role='user'):
        self.messages.append({'role': role, 'content': message})
        chat_completion = self.client.messages.create(
            messages=self.messages,
            model='qwen3-coder',
            max_tokens=1024,
            tools=[
                {
                    'name': 'edit_file',
                    'description': 'Edit a file (UTF-8 encoding)',
                    'input_schema': {
                        'type': 'object',
                        'properties': {
                            'file_path': {
                                'type': 'string',
                                'description': 'The file path to edit'
                            },
                            'content': {
                                'type': 'string',
                                'description': 'The content to write to the file'
                            }
                        },
                        'required': ['file_path', 'content']
                    }
                },
                {
                    'name': 'read_file',
                    'description': 'Read a file (UTF-8 encoding)',
                    'input_schema': {
                        'type': 'object',
                        'properties': {
                            'file_path': {
                                'type': 'string',
                                'description': 'The file path to read'
                            },
                        },
                        'required': ['file_path']
                    }
                },
            ],
        )
        self.output_text = ""
        for block in chat_completion.content:
            if block.type == "tool_use":
                if block.name == "edit_file":
                    self.edit_file(block.input)
                elif block.name == "read_file":
                    self.read_file(block.input)
            elif block.type == "text":
                if block.text:
                    self.output_text += block.text + "\n"
        self.messages.append({'role': 'assistant', 'content': self.output_text})
        return self.output_text
    def read_file(self, input):
        file_path = input['file_path']
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.chat(f'成功读取文件：{file_path}，内容为：{content}', role='system')
            print(f"[Read {file_path}]")
        except Exception as e:
            self.chat(f'读取文件失败：{file_path}，错误信息：{e}', role='system')
            return None
    def edit_file(self, input):
        file_path = input['file_path']
        content = input['content']
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.chat(f'成功编辑文件：{file_path}', role='system')
        print(f"[Edit {file_path}]")
if __name__ == "__main__":
    eob = EasyOllamaBeta(api_key='183c13563a0043d6b5c3e1f780a13b7e.3h_dao1mrZZtQwGtMWUhR-Yo')
    while True:
        message = input("Enter(/bye to exit): ")
        if message == "/bye":
            break
        print(eob.chat(message))