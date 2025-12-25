# -*- coding: utf-8 -*-
"""
维护模式配置
"""
# 需要维护的页面路径列表
# 将需要维护的页面路径添加到列表中，例如：['/login', '/register', '/account']
# 空列表表示所有页面都正常访问
# 路径匹配规则：
#   - 精确匹配：'/login' 只匹配 '/login'
#   - 前缀匹配：'/api' 匹配所有以 '/api' 开头的路径（如 '/api/chat', '/api/login' 等）
MAINTENANCE_PAGES = [
    # 示例：
    # '/login',        # 维护登录页面
    # '/register',     # 维护注册页面
    # '/account',      # 维护账户页面
    # '/feedback',     # 维护反馈页面
    # '/api/chat',     # 维护聊天API
    # '/alert',
]

