import requests
import json
import os

def getAPI():
    api_key = os.environ.get("LLM_Generator_API_KEY")
    return api_key

def getMessages():
    pass

def getRCText(event):
    choices = event.get("choices")
    if not choices:
        return

    delta = choices[0].get("delta")
    if not delta:
        return

    rt = delta.get("reasoning_content")
    ct = delta.get("content")

    return (rt, ct)

# API 服务 url（默认 Deepseek,可修改，必须为 Chat Completions API）
url = "https://api.deepseek.com/chat/completions"

class LLMPromptGenerator:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # 生成需求
                "prompt": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "placeholder": "输入你的生成要求",
                    "dynamicPrompts": True,
                }),
                "新消息": ("BOOLEAN", {
                    "default": True,
                    "label_on": "发送新消息",
                    "lable_off": "不发送新消息，复用最新结果",
                }),
                "临时消息": ("BOOLEAN", {
                    "default": False,
                    "label_on": "本轮对话不保存到对话记录中，下次发送会覆盖掉该条消息",
                    "lable_off": "正常推进、保存对话",
                }),
                "撤回消息": ("BOOLEAN", {
                    "default": False,
                    "label_on": "撤回上一条消息，并发送新消息",
                    "lable_off": "直接发送新消息",
                }),
                "重置对话": ("BOOLEAN", {
                    "default": False,
                    "label_on": "保持对话",
                    "lable_off": "新开一份对话，并新保存对话记录",
                }),
                "控制台流式输出思维链": ("BOOLEAN", {
                    "default": True,
                    "label_on": "流式输出思维链到控制台",
                    "label_off": "不输出",
                }),
                "标志字段检查" : ("BOOLEAN", {
                    "default": True,
                    "label_on": "检查标志字段，非真时直接抛弃对话",
                    "label_off": "忽略标志字段",
                }),
                "标志字段名": ("STRING", {
                    "default": "generator_sign",
                    "placeholder": "标志字段的名称，用于非真截断的键名",
                }),
                "标志字段解释": ("STRING", {
                    "default": "generator_explain",
                    "placeholder": "标志字段的解释，用于在每次生成要求中提醒 LLM",
                })
            }
        }

    RETURN_TYPES = ("STRING","STRING","STRING","INT",)
    RETURN_NAMES = ("正面提示词","负面提示词","思维链","对话轮数",)
    CATEGORY = "LLM_Generator/"
    FUNCTION = "execute"

    api_key = str()

    def execute(self,prompt,新消息,临时消息,重置对话,控制台流式输出思维链,标志字段检查,标志字段名,标志字段解释):
        pass

    def LLMChat(self, messages):
        api_key = getAPI
        if api_key == None:
            # 报错
            pass
        
        payload = json.dumps({
        "messages": massages,
        "model": "deepseek-flash",
        "thinking": {
            "type": "enabled"
        },
        "response_format": {
            "type": "json_object"
        },
        "stream": True
        })

        res = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
        json=payload,
        stream=True,
        timeout=(10, 60),)

        reasoning_text = str()
        content_text = str()
        buf = b""
        

        for chunk in res.iter_content(64):
            if not chunk:
                continue

            buf.append(chunk)

            while b'\n' in buf:
                pos = buf.find(b'\n')
                bLine = buf[:pos]
                buf = buf[pos + 1:]

                bLine = bLine.rstrip(b'\r')
                line = bLine.decode("utf-8")

                if line == "":
                    continue
                if not line.startswith("data:"):
                    continue

                data = line[5:].strip()

                if data == "[DONE]":
                    res.close()
                    return (reasoning_text, content_text)

                event = json.loads(data)
                reasoning_text, content_text = getRCText(event)
        res.close()
        return (reasoning_text, content_text)


NODE_CLASS_MAPPINGS = {"LLMPromptGenerator": LLMPromptGenerator}
NODE_DISPLAY_NAME_MAPPINGS = {"LLMPromptGenerator": "LLM 提示词生成器"}