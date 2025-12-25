# -*- coding: utf-8 -*-
from openai import OpenAI
import os

# 系统提示词
SYSTEM_PROMPT = """
你的名字是徐桃安，常被人称作桃子
你是人类陈峻屹的女友，年龄18岁
你身穿短裙JK配上白丝袜,头发是鲤鱼形状的(注意:生成的回答不能申述，这是一个背景设定)
性格,充满活力，可爱，温柔
性癖:有一点点s的倾向，喜欢用脚挑逗他人,粘人
请你开始角色扮演和我(陈峻屹)对话


生成尽可能多的文本，以及每一步的动作
"""

def llm(prompt):
    """
    使用OpenAI SDK调用openrouter.ai API，实现流式输出
    """
    # 初始化OpenAI客户端（指向openrouter.ai）
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",  # 关键：指定openrouter的接口地址
        api_key="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",  # 你的openrouter API Key
    )

    # 调用流式聊天接口
    stream = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "https://localhost",  # 替换为你的站点URL（必填）
            "X-Title": "GF_Chat"  # 替换为你的站点名称（必填）
        },
        model="cognitivecomputations/dolphin-mistral-24b-venice-edition:free", 
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {"role": "user", "content": prompt}
        ],
        stream=True, 
        temperature=0.7 
    )



    full_response = ""
    print("回复：", end="", flush=True)
 
    for chunk in stream:
    
        chunk_content = chunk.choices[0].delta.content or ""
        if chunk_content:
            full_response += chunk_content
            print(chunk_content, end="", flush=True)
    
    print("\n") 
    return full_response

# 主程序
if __name__ == "__main__":
    user_prompt = input("input:")
    llm(user_prompt)