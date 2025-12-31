#coding=utf-8

'''
requires Python 3.6 or later

pip install asyncio
pip install websockets
pip install python-dotenv

'''

import asyncio
import websockets
import uuid
import json
import gzip
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 消息类型常量
MESSAGE_TYPES = {11: "audio-only server response", 12: "frontend server response", 15: "error message from server"}
MESSAGE_TYPE_SPECIFIC_FLAGS = {0: "no sequence number", 1: "sequence number > 0",
                               2: "last message from server (seq < 0)", 3: "sequence number < 0"}
MESSAGE_SERIALIZATION_METHODS = {0: "no serialization", 1: "JSON", 15: "custom type"}
MESSAGE_COMPRESSIONS = {0: "no compression", 1: "gzip", 15: "custom compression method"}

# 默认请求头: version(4 bits) + header size(4 bits) + message type(4 bits) + flags(4 bits) + serialization(4 bits) + compression(4 bits) + reserved(1 byte)
DEFAULT_HEADER = bytearray(b'\x11\x10\x11\x00')


class TTSConfig:
    """TTS 配置类"""
    def __init__(self):
        self.appid = os.getenv("APPID", "9697584635")
        self.token = os.getenv("TOKEN", "Aexv7EXkY2k4Dktw9km21Po9FX3b3_fP")
        self.cluster = os.getenv("CLUSTER", "volcano_icl")
        self.voice_type = os.getenv("VOICE_TYPE", "S_bl5gb9NO1")
        self.host = os.getenv("HOST", "openspeech.bytedance.com")
        self.user_uid = os.getenv("USER_UID", "388808087185088")
        self.audio_encoding = os.getenv("AUDIO_ENCODING", "mp3")
        self.audio_speed_ratio = float(os.getenv("AUDIO_SPEED_RATIO", "1.0"))
        self.audio_volume_ratio = float(os.getenv("AUDIO_VOLUME_RATIO", "1.0"))
        self.audio_pitch_ratio = float(os.getenv("AUDIO_PITCH_RATIO", "1.0"))
        self.text_type = os.getenv("TEXT_TYPE", "plain")
        self.api_url = f"wss://{self.host}/api/v1/tts/ws_binary"


def build_request(config: TTSConfig, text: str, operation: str) -> dict:
    """构建请求 JSON"""
    return {
        "app": {
            "appid": config.appid,
            "token": "access_token",
            "cluster": config.cluster
        },
        "user": {
            "uid": config.user_uid
        },
        "audio": {
            "voice_type": config.voice_type,
            "encoding": config.audio_encoding,
            "speed_ratio": config.audio_speed_ratio,
            "volume_ratio": config.audio_volume_ratio,
            "pitch_ratio": config.audio_pitch_ratio,
        },
        "request": {
            "reqid": str(uuid.uuid4()),
            "text": text,
            "text_type": config.text_type,
            "operation": operation
        }
    }


def build_request_bytes(request_json: dict) -> bytearray:
    """将请求 JSON 转换为二进制数据"""
    payload_bytes = json.dumps(request_json).encode('utf-8')
    payload_bytes = gzip.compress(payload_bytes)
    request_bytes = bytearray(DEFAULT_HEADER)
    request_bytes.extend(len(payload_bytes).to_bytes(4, 'big'))
    request_bytes.extend(payload_bytes)
    return request_bytes


async def send_request(config: TTSConfig, request_bytes: bytearray, output_file: str, wait_for_complete: bool = True):
    """发送 WebSocket 请求并接收响应"""
    # websockets 14.0+ 使用 additional_headers，13.1及更早版本使用 extra_headers
    headers = [("Authorization", f"Bearer; {config.token}")]
    
    # 检测 websockets 版本并选择正确的参数名
    try:
        # 尝试使用 importlib.metadata（Python 3.8+）
        from importlib.metadata import version
        websockets_version_str = version('websockets')
        websockets_version = tuple(map(int, websockets_version_str.split('.')[:2]))
        use_additional_headers = websockets_version >= (14, 0)
    except (ImportError, ValueError):
        try:
            # 回退到 importlib_metadata（Python 3.7 或需要额外安装）
            from importlib_metadata import version
            websockets_version_str = version('websockets')
            websockets_version = tuple(map(int, websockets_version_str.split('.')[:2]))
            use_additional_headers = websockets_version >= (14, 0)
        except (ImportError, ValueError):
            # 如果无法检测版本，默认使用 extra_headers（更兼容旧版本）
            use_additional_headers = False
    
    with open(output_file, "wb") as file:
        # 根据版本选择正确的参数名
        connect_kwargs = {"ping_interval": None}
        if use_additional_headers:
            connect_kwargs["additional_headers"] = headers
        else:
            connect_kwargs["extra_headers"] = headers
        
        async with websockets.connect(config.api_url, **connect_kwargs) as ws:
            await ws.send(request_bytes)
            
            if wait_for_complete:
                # submit 操作：等待所有音频数据
                while True:
                    res = await ws.recv()
                    if parse_response(res, file):
                        break
            else:
                # query 操作：只接收一次响应
                res = await ws.recv()
                parse_response(res, file)
    
    print("\n连接已关闭...")


async def submit_text(config: TTSConfig, text: str, output_file: str = "output.mp3"):
    """提交文本生成语音"""
    print(f"\n{'='*60}")
    print(f"提交文本生成语音")
    print(f"{'='*60}")
    
    request_json = build_request(config, text, "submit")
    request_bytes = build_request_bytes(request_json)
    
    print(f"请求 JSON: {json.dumps(request_json, ensure_ascii=False, indent=2)}")
    print(f"输出文件: {output_file}")
    
    await send_request(config, request_bytes, output_file, wait_for_complete=True)


async def query_status(config: TTSConfig, reqid: str = None, output_file: str = "query_result.mp3"):
    """查询任务状态"""
    print(f"\n{'='*60}")
    print(f"查询任务状态")
    print(f"{'='*60}")
    
    text = ""  # query 操作不需要文本
    request_json = build_request(config, text, "query")
    if reqid:
        request_json["request"]["reqid"] = reqid
    
    request_bytes = build_request_bytes(request_json)
    
    print(f"请求 JSON: {json.dumps(request_json, ensure_ascii=False, indent=2)}")
    print(f"输出文件: {output_file}")
    
    await send_request(config, request_bytes, output_file, wait_for_complete=False)


def parse_response(res: bytes, file) -> bool:
    """解析服务器响应
    
    Args:
        res: 服务器响应的二进制数据
        file: 输出文件对象
    
    Returns:
        bool: True 表示响应完成，False 表示需要继续接收
    """
    print("\n" + "-" * 60)
    print("服务器响应")
    print("-" * 60)
    
    # 解析响应头
    protocol_version = res[0] >> 4
    header_size = res[0] & 0x0f
    message_type = res[1] >> 4
    message_type_specific_flags = res[1] & 0x0f
    serialization_method = res[2] >> 4
    message_compression = res[2] & 0x0f
    reserved = res[3]
    header_extensions = res[4:header_size*4]
    payload = res[header_size*4:]
    
    print(f"协议版本: {protocol_version:#x} (版本 {protocol_version})")
    print(f"头部大小: {header_size:#x} ({header_size * 4} 字节)")
    print(f"消息类型: {message_type:#x} - {MESSAGE_TYPES.get(message_type, '未知')}")
    print(f"消息标志: {message_type_specific_flags:#x} - {MESSAGE_TYPE_SPECIFIC_FLAGS.get(message_type_specific_flags, '未知')}")
    print(f"序列化方法: {serialization_method:#x} - {MESSAGE_SERIALIZATION_METHODS.get(serialization_method, '未知')}")
    print(f"压缩方式: {message_compression:#x} - {MESSAGE_COMPRESSIONS.get(message_compression, '未知')}")
    print(f"保留字段: {reserved:#04x}")
    
    if header_size != 1:
        print(f"头部扩展: {header_extensions}")
    
    # 处理不同类型的消息
    if message_type == 0xb:  # 音频响应
        if message_type_specific_flags == 0:  # ACK，无序列号
            print("负载大小: 0 (确认消息)")
            return False
        else:
            sequence_number = int.from_bytes(payload[:4], "big", signed=True)
            payload_size = int.from_bytes(payload[4:8], "big", signed=False)
            audio_data = payload[8:]
            print(f"序列号: {sequence_number}")
            print(f"负载大小: {payload_size} 字节")
            file.write(audio_data)
            return sequence_number < 0  # 负数序列号表示最后一条消息
            
    elif message_type == 0xf:  # 错误消息
        code = int.from_bytes(payload[:4], "big", signed=False)
        msg_size = int.from_bytes(payload[4:8], "big", signed=False)
        error_msg = payload[8:]
        
        if message_compression == 1:
            error_msg = gzip.decompress(error_msg)
        error_msg = error_msg.decode("utf-8")
        
        print(f"错误代码: {code}")
        print(f"错误消息大小: {msg_size} 字节")
        print(f"错误消息: {error_msg}")
        return True
        
    elif message_type == 0xc:  # 前端服务器响应
        msg_size = int.from_bytes(payload[:4], "big", signed=False)
        msg_data = payload[4:]
        
        if message_compression == 1:
            msg_data = gzip.decompress(msg_data)
        
        print(f"前端消息大小: {msg_size} 字节")
        print(f"前端消息: {msg_data}")
        return False
    else:
        print(f"未定义的消息类型: {message_type}")
        return True


async def main():
    """主函数"""
    config = TTSConfig()
    
    # 提交文本生成语音
    text = "你好，我是神里凌华，你的专属语音助手。"
    await submit_text(config, text, "test_submit.mp3")
    
    # 查询任务状态（可选）
    # await query_status(config, output_file="test_query.mp3")


if __name__ == '__main__':
    asyncio.run(main())
