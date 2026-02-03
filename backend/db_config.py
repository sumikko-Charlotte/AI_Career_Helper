# -*- coding: utf-8 -*-
"""
腾讯云 TDSQL-C 数据库配置文件
包含数据库连接配置、连接函数和核心查询函数
"""
import os
import pymysql
from pymysql import OperationalError
from typing import List, Dict, Optional, Tuple

# ==========================================
# 数据库连接配置（固定值，仅需修改 password）
# ==========================================
DB_CONFIG = {
    "host": "bj-cynosdbmysql-grp-ovt0aqds.sql.tencentcdb.com",
    "port": 20603,
    "user": "root",
    "password": "AIcareer@helper123",    # ⚠️ 仅需替换这1个参数
    "database": "ai_career_helper",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}


# ==========================================
# 数据库连接函数
# ==========================================
def get_db_connection():
    """
    获取数据库连接对象
    
    Returns:
        pymysql.Connection: 数据库连接对象，连接失败返回 None
    """
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print("✅ 成功连接到云端数据库 ai_career_helper！")
        return conn
    except OperationalError as e:
        error_msg = str(e)
        if "Access denied" in error_msg or "1045" in error_msg:
            print(f"❌ 数据库连接失败：密码错误，请检查 db_config.py 中的 password 参数")
        elif "Can't connect" in error_msg or "2003" in error_msg:
            print(f"❌ 数据库连接失败：无法连接到服务器，请检查：")
            print(f"   1. 端口号是否正确（当前：{DB_CONFIG['port']}）")
            print(f"   2. 安全组是否开放了该端口")
            print(f"   3. 网络连接是否正常")
        else:
            print(f"❌ 数据库连接失败（OperationalError）：{error_msg}")
        return None
    except Exception as e:
        print(f"❌ 数据库连接失败（未知错误）：{e}")
        return None


# ==========================================
# 核心数据库查询函数
# ==========================================

def get_all_users() -> List[Dict]:
    """
    查询 users 表所有用户数据
    
    Returns:
        List[Dict]: 用户字典列表，无数据返回空列表
    """
    conn = get_db_connection()
    if conn is None:
        return []
    
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users"
            cursor.execute(sql)
            results = cursor.fetchall()
            return list(results) if results else []
    except Exception as e:
        print(f"❌ 查询所有用户失败：{e}")
        return []
    finally:
        conn.close()


def get_user_by_username(username: str) -> Optional[Dict]:
    """
    根据用户名精准查询单个用户
    
    Args:
        username: 用户名字符串
    
    Returns:
        Dict: 单个用户字典，无用户返回 None
    """
    conn = get_db_connection()
    if conn is None:
        return None
    
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            return result if result else None
    except Exception as e:
        print(f"❌ 查询用户失败：{e}")
        return None
    finally:
        conn.close()


def user_login(username: str, password: str) -> Tuple[bool, str]:
    """
    用户登录核心验证
    
    Args:
        username: 用户名字符串
        password: 密码字符串
    
    Returns:
        Tuple[bool, str]: (登录是否成功, 提示信息)
    """
    conn = get_db_connection()
    if conn is None:
        return False, "数据库连接失败"
    
    try:
        with conn.cursor() as cursor:
            # 查询用户是否存在
            sql = "SELECT * FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            user = cursor.fetchone()
            
            if user is None:
                return False, "用户名不存在"
            
            # 验证密码
            if user.get('password') == password:
                return True, "登录成功"
            else:
                return False, "密码错误"
    except Exception as e:
        print(f"❌ 登录验证失败：{e}")
        return False, f"数据库连接失败：{e}"
    finally:
        conn.close()


# ==========================================
# 扩展数据库操作函数（用于项目其他功能）
# ==========================================

def update_user_field(username: str, field: str, value) -> bool:
    """
    更新用户指定字段
    
    Args:
        username: 用户名
        field: 字段名
        value: 字段值
    
    Returns:
        bool: 更新是否成功
    """
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        with conn.cursor() as cursor:
            # 使用参数化查询，避免 SQL 注入
            sql = f"UPDATE users SET {field} = %s WHERE username = %s"
            cursor.execute(sql, (value, username))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"❌ 更新用户字段失败：{e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def update_user_multiple_fields(username: str, fields: Dict) -> bool:
    """
    更新用户多个字段
    
    Args:
        username: 用户名
        fields: 字段字典，如 {'nickname': '新昵称', 'phone': '13800138000'}
    
    Returns:
        bool: 更新是否成功
    """
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        with conn.cursor() as cursor:
            # 构建动态 SQL
            set_clause = ", ".join([f"{k} = %s" for k in fields.keys()])
            sql = f"UPDATE users SET {set_clause} WHERE username = %s"
            values = list(fields.values()) + [username]
            cursor.execute(sql, values)
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"❌ 更新用户多个字段失败：{e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def create_user(username: str, password: str, grade: str, target_role: str) -> Tuple[bool, str]:
    """
    创建新用户（注册）
    
    Args:
        username: 用户名
        password: 密码
        grade: 年级
        target_role: 目标岗位
    
    Returns:
        Tuple[bool, str]: (是否成功, 提示信息)
    """
    conn = get_db_connection()
    if conn is None:
        return False, "数据库连接失败"
    
    try:
        with conn.cursor() as cursor:
            # 检查用户名是否已存在
            check_sql = "SELECT username FROM users WHERE username = %s"
            cursor.execute(check_sql, (username,))
            if cursor.fetchone():
                return False, "该用户名已被注册"
            
            # 插入新用户
            insert_sql = """
                INSERT INTO users (username, password, grade, target_role, createTaskNum, uploadedResumeNum)
                VALUES (%s, %s, %s, %s, 0, 0)
            """
            cursor.execute(insert_sql, (username, password, grade, target_role))
            conn.commit()
            return True, "注册成功"
    except Exception as e:
        print(f"❌ 创建用户失败：{e}")
        conn.rollback()
        return False, f"注册失败：{e}"
    finally:
        conn.close()


def increment_user_field(username: str, field: str, increment: int = 1) -> bool:
    """
    递增用户指定字段的值（如 createTaskNum, uploadedResumeNum）
    
    Args:
        username: 用户名
        field: 字段名
        increment: 递增数量，默认为1
    
    Returns:
        bool: 操作是否成功
    """
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        with conn.cursor() as cursor:
            sql = f"UPDATE users SET {field} = {field} + %s WHERE username = %s"
            cursor.execute(sql, (increment, username))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"❌ 递增用户字段失败：{e}")
        conn.rollback()
        return False
    finally:
        conn.close()


def decrement_user_field(username: str, field: str, decrement: int = 1) -> bool:
    """
    递减用户指定字段的值（如 uploadedResumeNum）
    
    Args:
        username: 用户名
        field: 字段名
        decrement: 递减数量，默认为1
    
    Returns:
        bool: 操作是否成功
    """
    conn = get_db_connection()
    if conn is None:
        return False
    
    try:
        with conn.cursor() as cursor:
            sql = f"UPDATE users SET {field} = GREATEST({field} - %s, 0) WHERE username = %s"
            cursor.execute(sql, (decrement, username))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"❌ 递减用户字段失败：{e}")
        conn.rollback()
        return False
    finally:
        conn.close()
