import pyttsx3, time
op = input("是否使用语音教程？需保证安装了pyttsx3库。（y/n）：")
def s(text, sleep=2):
    global op
    print(text)
    if op.lower() == 'y':
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    else:
        time.sleep(sleep)
s("感谢您使用了EasyOllama！接下来我将为您提供如何使用EasyOllama的教程。", 4)
s("你需要去官网获取API Key。")
s("然后按照以下代码，要保证在同一目录下：", 0)
print("from easyollama import EasyOllama")
print("ollama = EasyOllama('api_key', model='模型选填，默认qwen2.5:1.5b', base_url='http://localhost:11434/v1/')")
print("print(ollama.chat('你好'))")
print("[Tips] 正常默认base_url为http://localhost:11434/v1/")
if op.lower() != 'y':
    time.sleep(5)
s("注意：本模型不支持Anthropic的工具调用！")
input("Press Enter to exit...")