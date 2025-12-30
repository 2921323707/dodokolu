# -*- coding: utf-8 -*-
"""
高德地图逆地理编码测试
根据经纬度获取地址信息
"""
import sys
from pathlib import Path

# 添加父目录到路径
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from geocode import reverse_geocode, geocode


def test_reverse_geocode():
    """测试逆地理编码：根据经纬度获取地址"""
    print("=" * 60)
    print("测试逆地理编码功能")
    print("=" * 60)
    
    # 测试坐标：北京市天安门广场（示例坐标）
    longitude = 116.807381
    latitude = 36.556355
    
    print(f"\n输入坐标：经度 {longitude}, 纬度 {latitude}")
    print("\n正在查询地址信息...\n")
    
    # 调用逆地理编码API
    result = reverse_geocode(
        longitude=longitude,
        latitude=latitude,
        radius=1000,  # 查询半径1000米
        extensions='all'  # 返回全部信息
    )
    
    # 打印结果
    print(f"状态码: {result.get('status')}")
    print(f"状态信息: {result.get('info')}")
    
    if result.get('status') == '1' and result.get('regeocode'):
        regeocode = result['regeocode']
        address_component = regeocode.get('addressComponent', {})
        
        print("\n" + "-" * 60)
        print("地址信息：")
        print("-" * 60)
        print(f"格式化地址: {regeocode.get('formatted_address', '')}")
        print(f"\n地址组件:")
        print(f"  国家: {address_component.get('country', '')}")
        print(f"  省份: {address_component.get('province', '')}")
        print(f"  城市: {address_component.get('city', '')}")
        print(f"  区县: {address_component.get('district', '')}")
        print(f"  乡镇: {address_component.get('township', '')}")
        print(f"  区域编码: {address_component.get('adcode', '')}")
        
        # 显示周边POI（最多5个）
        pois = regeocode.get('pois', [])
        if pois:
            print(f"\n周边POI（显示前5个）:")
            for i, poi in enumerate(pois[:5], 1):
                print(f"  {i}. {poi.get('name', '')} - {poi.get('type', '')}")
                print(f"     地址: {poi.get('address', '')}")
                print(f"     距离: {poi.get('distance', '')}米")
        
        # 显示道路信息
        roads = regeocode.get('roads', [])
        if roads:
            print(f"\n道路信息:")
            for i, road in enumerate(roads[:3], 1):
                print(f"  {i}. {road.get('name', '')} - {road.get('direction', '')}")
    else:
        print(f"\n查询失败: {result.get('info', '未知错误')}")
        print("\n提示：请确保在.env文件中配置了AMAP_API_KEY")


def test_geocode():
    """测试地理编码：根据地址获取经纬度"""
    print("\n\n" + "=" * 60)
    print("测试地理编码功能")
    print("=" * 60)
    
    # 测试地址
    address = "北京市天安门广场"
    
    print(f"\n输入地址：{address}")
    print("\n正在查询经纬度...\n")
    
    # 调用地理编码API
    result = geocode(address=address, city="北京市")
    
    # 打印结果
    print(f"状态码: {result.get('status')}")
    print(f"状态信息: {result.get('info')}")
    
    if result.get('status') == '1' and result.get('geocodes'):
        geocodes = result['geocodes']
        print(f"\n找到 {len(geocodes)} 个匹配结果：\n")
        
        for i, geocode_item in enumerate(geocodes[:3], 1):
            location = geocode_item.get('location', '').split(',')
            if len(location) == 2:
                longitude, latitude = location
                print(f"{i}. {geocode_item.get('formatted_address', '')}")
                print(f"   经度: {longitude}, 纬度: {latitude}")
                print(f"   级别: {geocode_item.get('level', '')}")
                print()
    else:
        print(f"\n查询失败: {result.get('info', '未知错误')}")


if __name__ == '__main__':
    # 测试逆地理编码
    test_reverse_geocode()
    
    # 测试地理编码
    test_geocode()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

