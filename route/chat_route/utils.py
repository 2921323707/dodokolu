# -*- coding: utf-8 -*-
"""
聊天路由工具函数
"""
import importlib.util
from pathlib import Path

# 导入 seed1.8.py 模块（文件名包含点号，需要特殊处理）
seed_module_path = Path(__file__).parent.parent.parent / 'config' / 'llm' / 'base' / 'models' / 'multi_content' / 'seed1.8.py'
spec = importlib.util.spec_from_file_location("seed1_8", str(seed_module_path))
seed1_8 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seed1_8)
recognize_image = seed1_8.recognize_image

# 导入 seedream.py 和 seedance.py 模块
seedream_module_path = Path(__file__).parent.parent.parent / 'config' / 'llm' / 'base' / 'models' / 'multi_content' / 'seedream.py'
spec_seedream = importlib.util.spec_from_file_location("seedream", str(seedream_module_path))
seedream = importlib.util.module_from_spec(spec_seedream)
spec_seedream.loader.exec_module(seedream)
generate_image = seedream.generate_image

seedance_module_path = Path(__file__).parent.parent.parent / 'config' / 'llm' / 'base' / 'models' / 'multi_content' / 'seedance.py'
spec_seedance = importlib.util.spec_from_file_location("seedance", str(seedance_module_path))
seedance = importlib.util.module_from_spec(spec_seedance)
spec_seedance.loader.exec_module(seedance)
generate_video = seedance.generate_video

__all__ = ['recognize_image', 'generate_image', 'generate_video']

