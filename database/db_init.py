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
        
        # 创建相册类别配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS album_category_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_key TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                is_visible INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建相册图片配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS album_image_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_key TEXT NOT NULL,
                image_path TEXT NOT NULL,
                display_name TEXT,
                is_visible INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category_key, image_path)
            )
        ''')
        
        # 创建相册用户权限表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS album_user_permission (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                category_key TEXT NOT NULL,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE,
                UNIQUE(user_id, category_key, image_path)
            )
        ''')
        
        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_album_category_key ON album_category_config(category_key)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_album_image_category ON album_image_config(category_key)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_album_image_path ON album_image_config(image_path)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_album_permission_user ON album_user_permission(user_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_album_permission_category ON album_user_permission(category_key)
        ''')
        
        # 初始化默认类别配置（如果不存在）
        default_categories = [
            ('anime', '动漫', 1),
            ('photo', '照片', 1),
            ('wallpaper', '壁纸', 1),
            ('scene', '场景', 1)
        ]
        
        for category_key, display_name, is_visible in default_categories:
            cursor.execute('''
                INSERT OR IGNORE INTO album_category_config (category_key, display_name, is_visible)
                VALUES (?, ?, ?)
            ''', (category_key, display_name, is_visible))
        
        # 创建相册配置表的索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_album_category_visible ON album_category_config(is_visible)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_album_image_visible ON album_image_config(is_visible)
        ''')
        
        # 创建项目点赞表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                like_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
            )
        ''')
        
        # 创建点赞表的索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_project_likes_user ON project_likes(user_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_project_likes_date ON project_likes(like_date)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_project_likes_user_date ON project_likes(user_id, like_date)
        ''')
        
        # 创建打卡清单表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS check_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                app_name TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE
            )
        ''')
        
        # 创建打卡记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS check_record (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                check_list_id INTEGER NOT NULL,
                check_date DATE NOT NULL,
                check_status TEXT NOT NULL DEFAULT 'pending',
                app_name TEXT,
                check_in_date TEXT,
                details TEXT,
                confidence TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_profile(id) ON DELETE CASCADE,
                FOREIGN KEY (check_list_id) REFERENCES check_list(id) ON DELETE CASCADE,
                UNIQUE(user_id, check_list_id, check_date)
            )
        ''')
        
        # 创建打卡相关索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_check_list_user ON check_list(user_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_check_list_active ON check_list(is_active)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_check_record_user ON check_record(user_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_check_record_list ON check_record(check_list_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_check_record_date ON check_record(check_date)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_check_record_user_date ON check_record(user_id, check_date)
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

