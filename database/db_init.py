# -*- coding: utf-8 -*-
"""
数据库初始化模块
"""
import sqlite3
import os
from pathlib import Path


# 数据库文件路径
DB_DIR = Path(__file__).parent
DB_FILE = DB_DIR / 'app.db'


def get_db_connection():
    """
    获取数据库连接
    
    Returns:
        sqlite3.Connection: 数据库连接对象
    """
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
    return conn


def init_database():
    """
    初始化数据库，如果数据库不存在则创建并创建表
    """
    # 确保数据库目录存在
    DB_DIR.mkdir(parents=True, exist_ok=True)
    
    # 检查数据库文件是否存在
    db_exists = DB_FILE.exists()
    
    # 连接数据库（如果不存在会自动创建）
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 创建用户画像表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                role INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # 兼容旧库，补齐并规范 role 字段
        cursor.execute("PRAGMA table_info(user_profile)")
        columns = [row["name"] for row in cursor.fetchall()]
        if "role" not in columns:
            cursor.execute("ALTER TABLE user_profile ADD COLUMN role INTEGER NOT NULL DEFAULT 0")
        # 将历史上误写成 9 的角色统一改为 2（管理员）
        cursor.execute("UPDATE user_profile SET role = 2 WHERE role = 9")
        
        # 创建索引以提高查询性能
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_username ON user_profile(username)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_email ON user_profile(email)
        ''')
        
        conn.commit()
        
        if not db_exists:
            print(f"✓ 数据库已创建: {DB_FILE}")
        else:
            print(f"✓ 数据库已加载: {DB_FILE}")
            
    except Exception as e:
        conn.rollback()
        print(f"✗ 数据库初始化失败: {str(e)}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    # 测试数据库初始化
    init_database()
    print("数据库初始化完成！")

