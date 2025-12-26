# -*- coding: utf-8 -*-
"""
测试文本生成功能
"""
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# # 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# # 初始化Openai客户端，从环境变量中读取您的API Key
client = OpenAI(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # 从环境变量中获取您的 API Key
    api_key=os.environ.get("ARK_API_KEY"),
)

# Non-streaming:
print("----- 非流式文本生成请求 -----")
completion = client.chat.completions.create(
    # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
    model="doubao-seed-1-6-flash-250828", #doubao-seed-1-6-flash-250828  doubao-seed-1-6-251015
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "请描述这张图片的内容，一句话简短描述输出即可，不要有任何其他内容"},
                {"type": "image_url", "image_url": {"url": "https://pic.nximg.cn/file/20230811/33760392_174457583129_2.jpg"}},
            ],
        }
    ],
    reasoning_effort="minimal" # minimal, low, medium, high
)

if hasattr(completion.choices[0].message, 'reasoning_content'):
    print("\n推理过程:")
    print(completion.choices[0].message.reasoning_content)
print("\n生成内容:")
print(completion.choices[0].message.content)

# # Streaming:
# print("\n----- 流式文本生成请求 -----")
# stream = client.chat.completions.create(
#     # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
#     model="doubao-seed-1-6-251015",
#     messages=[
#         {
#             "role": "user",
#             "content": [
#                 {"type": "text", "text": "请描述这张图片的内容"},
#                 {"type": "image_url", "image_url": {"url": "https://pic.nximg.cn/file/20230811/33760392_174457583129_2.jpg"}},
#             ],
#         }
#     ],
#     # 响应内容是否流式返回
#     stream=True,
#     reasoning_effort="minimal" # minimal, low, medium, high
# )

# reasoning_content = ""
# content = ""
# print("\n流式输出:")
# with stream:
#     for chunk in stream:
#         if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
#             reasoning_content += chunk.choices[0].delta.reasoning_content
#             print(chunk.choices[0].delta.reasoning_content, end="")

#         delta_content = chunk.choices[0].delta.content
#         if delta_content is not None:
#             content += delta_content
#             print(delta_content, end="")

# print("\n\n流式输出完成")
