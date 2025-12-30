# -*- coding: utf-8 -*-
"""
高德地图地理/逆地理编码API
根据经纬度获取地址信息
"""
import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from pathlib import Path

# 加载环境变量
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

# 高德地图API配置
AMAP_API_KEY = os.getenv('AMAP_API_KEY', '0a252d8417c1a92b319edad941e086bd')
AMAP_BASE_URL = 'https://restapi.amap.com/v3/geocode'


def reverse_geocode(
    longitude: float,
    latitude: float,
    radius: int = 1000,
    extensions: str = 'all',
    roadlevel: Optional[int] = None,
    poitype: Optional[str] = None
) -> Dict[str, Any]:
    """
    逆地理编码：根据经纬度获取地址信息
    
    参数:
        longitude: 经度（必选）
        latitude: 纬度（必选）
        radius: 查询POI的半径范围，单位：米，取值范围：0~3000，默认1000
        extensions: 返回结果控制，可选值：'base'（基本）或 'all'（全部），默认'all'
        roadlevel: 道路级别，可选值：1（仅输出主干道路），默认None
        poitype: POI类型，支持传入POI TYPECODE及名称，多个用"|"分隔，默认None
    
    返回:
        Dict包含以下字段：
        - status: 状态码，1表示成功，0表示失败
        - info: 状态信息
        - regeocode: 逆地理编码结果（当status=1时存在）
        - formatted_address: 格式化地址
        - addressComponent: 地址组件
        - pois: 周边POI列表
        - roads: 道路信息
        - aois: AOI信息
    """
    if not AMAP_API_KEY:
        return {
            'status': '0',
            'info': 'AMAP_API_KEY未配置，请在.env文件中设置AMAP_API_KEY',
            'regeocode': None
        }
    
    # 构建请求参数
    params = {
        'key': AMAP_API_KEY,
        'location': f'{longitude},{latitude}',
        'radius': radius,
        'extensions': extensions,
        'output': 'json'
    }
    
    # 添加可选参数
    if roadlevel is not None:
        params['roadlevel'] = roadlevel
    
    if poitype:
        params['poitype'] = poitype
    
    try:
        # 发送请求
        response = requests.get(f'{AMAP_BASE_URL}/regeo', params=params, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        # 处理返回结果
        if result.get('status') == '1':
            regeocode = result.get('regeocode', {})
            address_component = regeocode.get('addressComponent', {})
            
            return {
                'status': '1',
                'info': result.get('info', 'OK'),
                'regeocode': {
                    'formatted_address': regeocode.get('formatted_address', ''),
                    'addressComponent': {
                        'country': address_component.get('country', ''),
                        'province': address_component.get('province', ''),
                        'city': address_component.get('city', ''),
                        'district': address_component.get('district', ''),
                        'township': address_component.get('township', ''),
                        'neighborhood': address_component.get('neighborhood', {}),
                        'building': address_component.get('building', {}),
                        'adcode': address_component.get('adcode', ''),
                        'streetNumber': address_component.get('streetNumber', {}),
                    },
                    'pois': regeocode.get('pois', []),
                    'roads': regeocode.get('roads', []),
                    'aois': regeocode.get('aois', [])
                }
            }
        else:
            return {
                'status': result.get('status', '0'),
                'info': result.get('info', '请求失败'),
                'regeocode': None
            }
    
    except requests.exceptions.RequestException as e:
        return {
            'status': '0',
            'info': f'请求异常：{str(e)}',
            'regeocode': None
        }
    except Exception as e:
        return {
            'status': '0',
            'info': f'处理异常：{str(e)}',
            'regeocode': None
        }


def geocode(address: str, city: Optional[str] = None) -> Dict[str, Any]:
    """
    地理编码：根据地址获取经纬度
    
    参数:
        address: 地址（必选）
        city: 城市，可选，用于指定查询的城市
    
    返回:
        Dict包含以下字段：
        - status: 状态码，1表示成功，0表示失败
        - info: 状态信息
        - geocodes: 地理编码结果列表（当status=1时存在）
    """
    if not AMAP_API_KEY:
        return {
            'status': '0',
            'info': 'AMAP_API_KEY未配置，请在.env文件中设置AMAP_API_KEY',
            'geocodes': []
        }
    
    # 构建请求参数
    params = {
        'key': AMAP_API_KEY,
        'address': address,
        'output': 'json'
    }
    
    if city:
        params['city'] = city
    
    try:
        # 发送请求
        response = requests.get(f'{AMAP_BASE_URL}/geo', params=params, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        
        # 处理返回结果
        if result.get('status') == '1':
            return {
                'status': '1',
                'info': result.get('info', 'OK'),
                'geocodes': result.get('geocodes', [])
            }
        else:
            return {
                'status': result.get('status', '0'),
                'info': result.get('info', '请求失败'),
                'geocodes': []
            }
    
    except requests.exceptions.RequestException as e:
        return {
            'status': '0',
            'info': f'请求异常：{str(e)}',
            'geocodes': []
        }
    except Exception as e:
        return {
            'status': '0',
            'info': f'处理异常：{str(e)}',
            'geocodes': []
        }

