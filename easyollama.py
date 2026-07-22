# EasyOllama
from openai import OpenAI
# EasyOllamaBeta
import anthropic, os
from datetime import datetime
from colorama import Fore

# Lastest
class EasyOllama:
    def __init__(self, api_key, model='qwen2.5:1.5b', base_url='http://localhost:11434/v1/'):
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
            max_tokens=1024,
        )
        self.messages.append({'role': 'assistant', 'content': chat_completion.choices[0].message.content})
        return chat_completion.choices[0].message.content
    # Powershell 命令的执行删除，因为我们只想为Ollama专用而生，不想搞Anthropic的工具调用。

# Pre-release
class EasyOllamaBeta:
    def __init__(self, api_key, model='qwen3.5:0.8b', base_url='http://localhost:11434/', chinese_mode=True, usingterminal=True): # Use qwen3.5:0.8b for best experience.
        self.model = model
        self.chinese_mode = chinese_mode
        self.usingterminal = usingterminal
        self.base_url = base_url
        self.api_key = api_key
        print(f"[EasyOllamaBeta] 初始化模型中：{model}" if self.chinese_mode else f"[EasyOllamaBeta] Init model {model}...")
        self.client = anthropic.Anthropic(
            base_url=base_url,
            api_key=api_key,  # required but ignored
        )
        self.messages = [
            {'role': 'system', 'content': '你是一个有帮助的AI智能助手，你回复的内容必须是纯文本格式，因为使用端是Python，不能包含HTML、Markdown、原生Ollama的标签（包括left、right、'+r'\['+'、frac等等）等文本，必须是纯文本格式！。如果用户请求你回答Python等等代码，你必须编辑文件。编辑文件前必须先阅读文件内容（使用read_file这个tools然后用edit_file这个tools进行编辑），不能直接编辑（防止覆盖了重要的信息）。如果用户让你用tools什么的（编辑文件、阅读文件等等等等）你必须要用tools！'},
        ]
    def chat(self, message, role='user', thinking=True):
        self.messages.append({'role': role, 'content': message})
        chat_completion = self.client.messages.create(
            messages=self.messages,
            model=self.model,
            max_tokens=1024,
            tools=[
                {
                    'name': 'edit_file',
                    'description': '修改文件（UTF-8编码）',
                    'input_schema': {
                        'type': 'object',
                        'properties': {
                            'file_path': {
                                'type': 'string',
                                'description': '修改目标文件的路径'
                            },
                            'content': {
                                'type': 'string',
                                'description': '修改目标文件的内容'
                            }
                        },
                        'required': ['file_path', 'content']
                    }
                },
                {
                    'name': 'read_file',
                    'description': '读取文件（以UTF-8编码）并返回文件内容。',
                    'input_schema': {
                        'type': 'object',
                        'properties': {
                            'file_path': {
                                'type': 'string',
                                'description': '读取目标文件的路径'
                            },
                        },
                        'required': ['file_path']
                    }
                },
                {
                    'name': 'get_time',
                    'description': '获取当前时间',
                    'input_schema': {
                        'type': 'object',
                        'properties': {
                            'format': {
                                'type': 'string',
                                'description': '时间格式（1：YYYY-MM-DD HH:MM:SS，2：YYYY-MM-DD，3：HH:MM:SS）。仅输入1/2/3！'
                            }
                        },
                        'required': ['format']
                    }
                }
            ],
        )
        self.output_text = ""
        for block in chat_completion.content:
            if block.type == "tool_use":
                if block.name == "get_time":
                    self.get_time(block.input, thinking)
                elif block.name == "edit_file":
                    self.edit_file(block.input, thinking)
                elif block.name == "read_file":
                    self.read_file(block.input, thinking)
            elif block.type == "text":
                if block.text:
                    if self.usingterminal:
                        self.output_text += Fore.RESET + block.text + f"\n{Fore.RESET}"
                    else:
                        self.output_text += block.text + f"\n"
            elif block.type == "thinking" and thinking:
                if self.usingterminal:
                    self.output_text += Fore.LIGHTBLACK_EX+block.thinking+f"\n{Fore.RESET}"
                else:
                    self.output_text += "+"+"-"*18+"+\nThinking:\n"+block.thinking+f"\n+"+"-"*18+"+\n"
        self.messages.append({'role': 'assistant', 'content': self.output_text})
        #print(chat_completion.content) # For debug
        return self.output_text
    def read_file(self, input, thinking):
        file_path = input['file_path']
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.aout(f"[读取文件 {file_path}]" if self.chinese_mode else f"[Read {file_path}]")
            self.chat(f'成功读取文件：{file_path}，内容为：{content}', role='system', thinking=thinking)
        except FileNotFoundError:
            self.aout(f"[阅读文件失败因为 {file_path} 这个文件不存在]" if self.chinese_mode else f"[Read failed because {file_path} didn't exist]")
            self.chat(f'文件不存在：{file_path}', role='system', thinking=thinking)
        except Exception as e:
            self.aout(f"[阅读文件失败（未知原因）：{file_path}]" if self.chinese_mode else f"[Read failed(Unknown exception) {file_path}]")
            self.chat(f'读取文件失败：{file_path}，错误信息：{e}', role='system', thinking=thinking)
    def edit_file(self, input, thinking):
        file_path = input['file_path']
        content = input['content']
        try:
            if os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.aout(f"[编辑文件 {file_path}]" if self.chinese_mode else f"[Edit {file_path}]")
                self.chat(f'成功编辑文件：{file_path}', role='system', thinking=thinking)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.aout(f"[创建文件：{file_path}]" if self.chinese_mode else f"[Created {file_path}]")
                self.chat(f'成功创建并编辑文件：{file_path}', role='system', thinking=thinking)
        except Exception as e:
            self.aout(f"[编辑文件失败：{file_path}]" if self.chinese_mode else f"[Edit failed {file_path}]")
            self.chat(f'编辑文件失败：{file_path}，错误信息：{e}', role='system', thinking=thinking)
    def get_time(self, input, thinking):
        if 'format' not in input:
            self.aout("[时间格式错误，未输入时间格式]" if self.chinese_mode else "[Time format error, no format input]")
            self.chat('时间格式错误，未输入时间格式。', role='system', thinking=thinking)
        format = input['format']
        try:
            if format == '1':
                time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.aout(f"[时间获取成功：{time_str}]" if self.chinese_mode else f"[Time get success {time_str}]")
                self.chat(f'成功获取时间：{time_str}', role='system', thinking=thinking)
            elif format == '2':
                time_str = datetime.now().strftime('%Y-%m-%d')
                self.aout(f"[时间获取成功：{time_str}]" if self.chinese_mode else f"[Time get success {time_str}]")
                self.chat(f'成功获取时间：{time_str}', role='system', thinking=thinking)
            elif format == '3':
                time_str = datetime.now().strftime('%H:%M:%S')
                self.aout(f"[时间获取成功：{time_str}]" if self.chinese_mode else f"[Time get success {time_str}]")
                self.chat(f'成功获取时间：{time_str}', role='system', thinking=thinking)
            else:
                self.aout(f"[时间格式错误，输入的格式是{format}]" if self.chinese_mode else f"[Time format error, input format is {format}]")
                self.chat(f'时间格式错误：{format}，请输入1、2、3中的一个。', role='system', thinking=thinking)
        except Exception as e:
            self.aout("[时间获取失败]" if self.chinese_mode else "[Time get failed]")
            self.chat(f'获取时间失败：{format}，错误信息：{e}', role='system', thinking=thinking)
    def aout(self, output):
        if self.usingterminal:
            self.output_text += Fore.RESET + output + f"\n{Fore.RESET}"
        else:
            self.output_text += output + f"\n"
    def set_api_key(self, api_key):
        self.api_key = api_key
        self.reset_cilent()
    def set_base_url(self, base_url="http://localhost:11434/"):
        self.base_url = base_url
        self.reset_cilent()
    def switch_model(self, model="qwen3.5:0.8b"):
        self.model = model
    def reset(self):
        self.messages = []
        # 不用重置self.client，因为不影响。
    def reset_cilent(self):
        self.client = anthropic.Anthropic(
            base_url=self.base_url,
            api_key=self.api_key,  # required but ignored
        )
if __name__ == "__main__":
    eob = EasyOllamaBeta(api_key='') # 官网自取API Key。建议使用qwen3.5:0.8b
    while True:
        message = input(Fore.RESET + "Enter(/bye to exit): ")
        if message == "/bye":
            break
        print(eob.chat(message))