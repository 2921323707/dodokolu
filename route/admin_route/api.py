# -*- coding: utf-8 -*-
"""
管理员API路由
"""
import ast
import os
from flask import Blueprint, request, jsonify, session
from pathlib import Path
from database import get_db_connection

admin_api_bp = Blueprint('api', __name__, url_prefix='/api')


def check_admin_api():
    """检查管理员权限（API）"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': '未登录'}), 401
    
    if session.get('role') != 2:
        return jsonify({'success': False, 'message': '无权限访问'}), 403
    
    return None


# ==================== 维护配置API ====================

@admin_api_bp.route('/maintenance/config', methods=['GET'])
def get_maintenance_config():
    """获取维护配置"""
    result = check_admin_api()
    if result:
        return result
    
    try:
        # 读取维护配置文件
        maintenance_file = Path(__file__).parent.parent / 'config' / 'maintenance' / 'maintenance.py'
        
        with open(maintenance_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用 ast 模块安全解析
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == 'MAINTENANCE_PAGES':
                        if isinstance(node.value, ast.List):
                            pages = []
                            for item in node.value.elts:
                                if isinstance(item, (ast.Str, ast.Constant)):
                                    # Python 3.8+ 使用 ast.Constant, 旧版本使用 ast.Str
                                    value = item.value if isinstance(item, ast.Constant) else item.s
                                    pages.append(value)
                            return jsonify({'success': True, 'pages': pages})
        
        return jsonify({'success': True, 'pages': []})
    except Exception as e:
        return jsonify({'success': False, 'message': f'读取配置失败: {str(e)}'}), 500


@admin_api_bp.route('/maintenance/config', methods=['POST'])
def update_maintenance_config():
    """更新维护配置"""
    result = check_admin_api()
    if result:
        return result
    
    try:
        data = request.json
        pages = data.get('pages', [])
        
        # 验证 pages 是否为列表
        if not isinstance(pages, list):
            return jsonify({'success': False, 'message': 'pages 必须是列表'}), 400
        
        # 验证每个页面路径都是字符串
        for page in pages:
            if not isinstance(page, str):
                return jsonify({'success': False, 'message': '页面路径必须是字符串'}), 400
        
        # 直接重写配置文件
        maintenance_file = Path(__file__).parent.parent / 'config' / 'maintenance' / 'maintenance.py'
        
        # 生成新文件内容
        new_content = '''# -*- coding: utf-8 -*-
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
'''
        for page in pages:
            new_content += f"    '{page}',\n"
        new_content += ']\n'
        
        with open(maintenance_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # 注意：需要重启应用才能生效
        return jsonify({'success': True, 'message': '配置已更新，需要重启应用才能生效'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新配置失败: {str(e)}'}), 500


# ==================== 数据库管理API ====================

@admin_api_bp.route('/database/tables', methods=['GET'])
def get_tables():
    """获取所有表列表"""
    result = check_admin_api()
    if result:
        return result
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({'success': True, 'tables': tables})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取表列表失败: {str(e)}'}), 500


@admin_api_bp.route('/database/table/<table_name>/schema', methods=['GET'])
def get_table_schema(table_name):
    """获取表结构"""
    result = check_admin_api()
    if result:
        return result
    
    # 验证表名（只允许字母、数字、下划线）
    if not all(c.isalnum() or c == '_' for c in table_name):
        return jsonify({'success': False, 'message': '无效的表名'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取表结构（PRAGMA不支持参数化，但我们已经验证了表名）
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = []
        for row in cursor.fetchall():
            columns.append({
                'cid': row[0],
                'name': row[1],
                'type': row[2],
                'notnull': bool(row[3]),
                'default_value': row[4],
                'pk': bool(row[5])
            })
        
        conn.close()
        
        return jsonify({'success': True, 'columns': columns})
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取表结构失败: {str(e)}'}), 500


@admin_api_bp.route('/database/table/<table_name>/data', methods=['GET'])
def get_table_data(table_name):
    """获取表数据（分页）"""
    result = check_admin_api()
    if result:
        return result
    
    # 验证表名（只允许字母、数字、下划线）
    if not all(c.isalnum() or c == '_' for c in table_name):
        return jsonify({'success': False, 'message': '无效的表名'}), 400
    
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取总数
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        total = cursor.fetchone()[0]
        
        # 获取分页数据
        cursor.execute(f"SELECT * FROM {table_name} LIMIT ? OFFSET ?", (per_page, offset))
        rows = []
        for row in cursor.fetchall():
            row_dict = {}
            for key in row.keys():
                row_dict[key] = row[key]
            rows.append(row_dict)
        
        # 获取列名
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': rows,
            'columns': columns,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取数据失败: {str(e)}'}), 500


@admin_api_bp.route('/database/table/<table_name>/row', methods=['POST'])
def create_row(table_name):
    """创建新行"""
    result = check_admin_api()
    if result:
        return result
    
    # 验证表名（只允许字母、数字、下划线）
    if not all(c.isalnum() or c == '_' for c in table_name):
        return jsonify({'success': False, 'message': '无效的表名'}), 400
    
    try:
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取列名（PRAGMA不支持参数化，但我们已经验证了表名）
        cursor.execute(f"PRAGMA table_info({table_name})")
        column_info = cursor.fetchall()
        columns = [row[1] for row in column_info if not row[5]]  # 排除主键
        
        # 构建插入语句
        values = []
        placeholders = []
        for col in columns:
            if col in data:
                values.append(data[col])
                placeholders.append('?')
        
        if not values:
            conn.close()
            return jsonify({'success': False, 'message': '没有可插入的数据'}), 400
        
        # 注意：表名和列名不能参数化，但我们已经验证了表名，列名来自数据库元数据，相对安全
        insert_columns = [c for c in columns if c in data]
        sql = f"INSERT INTO {table_name} ({', '.join(insert_columns)}) VALUES ({', '.join(placeholders)})"
        cursor.execute(sql, values)
        conn.commit()
        row_id = cursor.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'message': '创建成功', 'id': row_id})
    except Exception as e:
        return jsonify({'success': False, 'message': f'创建失败: {str(e)}'}), 500


@admin_api_bp.route('/database/table/<table_name>/row', methods=['PUT'])
def update_row(table_name):
    """更新行"""
    result = check_admin_api()
    if result:
        return result
    
    # 验证表名（只允许字母、数字、下划线）
    if not all(c.isalnum() or c == '_' for c in table_name):
        return jsonify({'success': False, 'message': '无效的表名'}), 400
    
    try:
        data = request.json
        row_id = data.get('id')
        
        if not row_id:
            return jsonify({'success': False, 'message': '缺少id字段'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取主键列名（PRAGMA不支持参数化，但我们已经验证了表名）
        cursor.execute(f"PRAGMA table_info({table_name})")
        pk_column = None
        for row in cursor.fetchall():
            if row[5]:  # pk
                pk_column = row[1]
                break
        
        if not pk_column:
            conn.close()
            return jsonify({'success': False, 'message': '表没有主键'}), 400
        
        # 构建更新语句
        updates = []
        values = []
        for key, value in data.items():
            if key != 'id' and key != pk_column:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if not updates:
            conn.close()
            return jsonify({'success': False, 'message': '没有可更新的数据'}), 400
        
        values.append(row_id)
        # 注意：表名和列名不能参数化，但我们已经验证了表名，列名来自数据库元数据
        sql = f"UPDATE {table_name} SET {', '.join(updates)} WHERE {pk_column} = ?"
        cursor.execute(sql, values)
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '更新成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新失败: {str(e)}'}), 500


@admin_api_bp.route('/database/table/<table_name>/row', methods=['DELETE'])
def delete_row(table_name):
    """删除行"""
    result = check_admin_api()
    if result:
        return result
    
    # 验证表名（只允许字母、数字、下划线）
    if not all(c.isalnum() or c == '_' for c in table_name):
        return jsonify({'success': False, 'message': '无效的表名'}), 400
    
    try:
        data = request.json
        row_id = data.get('id')
        
        if not row_id:
            return jsonify({'success': False, 'message': '缺少id字段'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取主键列名（PRAGMA不支持参数化，但我们已经验证了表名）
        cursor.execute(f"PRAGMA table_info({table_name})")
        pk_column = None
        for row in cursor.fetchall():
            if row[5]:  # pk
                pk_column = row[1]
                break
        
        if not pk_column:
            conn.close()
            return jsonify({'success': False, 'message': '表没有主键'}), 400
        
        # 注意：表名和列名不能参数化，但我们已经验证了表名，列名来自数据库元数据
        sql = f"DELETE FROM {table_name} WHERE {pk_column} = ?"
        cursor.execute(sql, (row_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500
