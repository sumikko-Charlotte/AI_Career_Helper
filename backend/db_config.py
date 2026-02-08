# -*- coding: utf-8 -*-
"""
腾讯云 TDSQL-C 数据库配置文件
包含数据库连接配置、连接函数和核心查询函数
"""
import os
import pymysql
from pymysql import OperationalError
from typing import List, Dict, Optional, Tuple

# 优先读取环境变量，其次读取 .env 文件
try:
    from dotenv import load_dotenv
    load_dotenv()  # 如果存在 .env 文件则加载，否则忽略
except ImportError:
    pass  # python-dotenv 未安装时跳过

# ==========================================
# 数据库连接配置（从环境变量读取，兼容 .env）
# ==========================================
def validate_db_config():
    """
    验证数据库环境变量是否配置完整
    
    Raises:
        ValueError: 如果缺少必需的环境变量
    """
    required_vars = {
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_NAME": os.getenv("DB_NAME"),
    }
    
    missing_vars = [var for var, value in required_vars.items() if not value]
    
    if missing_vars:
        raise ValueError(
            f"❌ 数据库环境变量配置不完整！缺少以下变量：{', '.join(missing_vars)}\n"
            f"   请在 Render 环境变量或 .env 文件中配置：\n"
            f"   - DB_HOST: 数据库地址\n"
            f"   - DB_PORT: 数据库端口（默认3306）\n"
            f"   - DB_USER: 数据库账号\n"
            f"   - DB_PASSWORD: 数据库密码\n"
            f"   - DB_NAME: 数据库名\n"
            f"   - DB_CHARSET: 字符集（默认utf8mb4）"
        )


def get_db_config():
    """
    获取数据库配置字典
    优先读取环境变量，其次读取 .env 文件
    
    Returns:
        dict: 数据库配置字典
    """
    # 验证必需的环境变量
    validate_db_config()
    
    config = {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
        "charset": os.getenv("DB_CHARSET", "utf8mb4"),
        "cursorclass": pymysql.cursors.DictCursor,
        # 连接超时参数（避免 Render 卡住）
        "connect_timeout": 10,
        "read_timeout": 20,
        "write_timeout": 20,
    }
    
    # SSL 配置
    db_ssl = os.getenv("DB_SSL", "false").lower() in ("true", "1", "yes")
    if db_ssl:
        config["ssl"] = {
            "ca": None,
            "cert": None,
            "key": None,
        }
    
    return config


# ==========================================
# 通用数据库连接和游标获取函数
# ==========================================
def get_db_cursor():
    """
    获取数据库连接对象和游标对象（推荐使用）
    
    功能：
    - 自动检查环境变量是否配置完整
    - 自动处理数据库连接超时/断开的情况，重新建立连接
    - 包含完整的异常捕获和错误信息输出
    
    Returns:
        Tuple[pymysql.Connection, pymysql.cursors.DictCursor]: (连接对象, 游标对象)
    
    Raises:
        ValueError: 环境变量配置不完整
        OperationalError: 数据库连接失败（包含详细的错误分类）
        Exception: 其他未知错误
    """
    max_retries = 2
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            config = get_db_config()
            conn = pymysql.connect(**config)
            cursor = conn.cursor()
            db_name = config.get("database", "unknown")
            print(f"✅ 成功连接到云端数据库 {db_name}！")
            return conn, cursor
        except OperationalError as e:
            error_msg = str(e)
            error_code = e.args[0] if e.args else None
            
            # 失败原因分类
            if error_code == 1045 or "Access denied" in error_msg:
                reason = "认证失败：用户名或密码错误"
                print(f"❌ 数据库连接失败 [认证失败]：用户名或密码错误")
                print(f"   错误代码: {error_code}")
                print(f"   请检查 DB_USER 和 DB_PASSWORD 环境变量")
            elif error_code == 2003 or "Can't connect" in error_msg:
                if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                    reason = "连接超时"
                    print(f"❌ 数据库连接失败 [超时]：连接超时，请检查网络或增加超时时间")
                    if retry_count < max_retries - 1:
                        retry_count += 1
                        print(f"   正在重试连接（{retry_count}/{max_retries}）...")
                        continue
                elif "Name or service not known" in error_msg or "getaddrinfo failed" in error_msg:
                    reason = f"DNS解析失败：无法解析主机名 {config.get('host')}"
                    print(f"❌ 数据库连接失败 [DNS]：无法解析主机名 {config.get('host')}")
                    print(f"   请检查 DB_HOST 环境变量是否正确")
                else:
                    reason = f"网络连接失败：无法连接到 {config.get('host')}:{config.get('port')}"
                    print(f"❌ 数据库连接失败 [网络连接]：无法连接到服务器")
                    print(f"   主机: {config.get('host')}")
                    print(f"   端口: {config.get('port')}")
                    print(f"   请检查：1. 主机地址是否正确 2. 端口是否开放 3. 安全组/防火墙设置 4. 数据库白名单")
                    if retry_count < max_retries - 1:
                        retry_count += 1
                        print(f"   正在重试连接（{retry_count}/{max_retries}）...")
                        continue
            elif error_code == 1049 or "Unknown database" in error_msg:
                reason = f"数据库不存在：{config.get('database')}"
                print(f"❌ 数据库连接失败 [Unknown database]：数据库 {config.get('database')} 不存在")
                print(f"   错误代码: {error_code}")
                print(f"   请检查 DB_NAME 环境变量是否正确")
            elif error_code == 1044 or "access denied" in error_msg.lower():
                reason = f"权限不足：用户 {config.get('user')} 没有访问权限"
                print(f"❌ 数据库连接失败 [权限不足]：用户 {config.get('user')} 没有访问权限")
                print(f"   错误代码: {error_code}")
            elif "ssl" in error_msg.lower() or "tls" in error_msg.lower():
                reason = "SSL/TLS 配置错误"
                print(f"❌ 数据库连接失败 [SSL问题]：SSL/TLS 配置错误")
                print(f"   错误信息: {error_msg}")
                print(f"   提示: 检查 DB_SSL 环境变量设置")
            else:
                reason = f"连接失败（错误代码: {error_code}）"
                print(f"❌ 数据库连接失败 [Unknown]：{error_msg}")
                print(f"   错误代码: {error_code}")
            
            raise OperationalError(f"{reason} (错误代码: {error_code})")
        except ValueError as e:
            # 环境变量配置不完整
            raise
        except Exception as e:
            error_type = type(e).__name__
            print(f"❌ 数据库连接失败 [{error_type}]：{e}")
            raise
    
    # 如果所有重试都失败
    raise OperationalError("数据库连接失败：重试次数已达上限")


# ==========================================
# 数据库连接函数（保留向后兼容）
# ==========================================
def get_db_connection():
    """
    获取数据库连接对象（向后兼容函数）
    
    注意：推荐使用 get_db_cursor() 函数，它会自动处理游标创建和错误处理
    
    Returns:
        pymysql.Connection: 数据库连接对象，连接失败返回 None
    """
    try:
        conn, _ = get_db_cursor()
        return conn
    except Exception:
        return None


def get_db_connection_with_error():
    """
    获取数据库连接对象，并返回错误信息
    
    Returns:
        Tuple[pymysql.Connection | None, str | None]: (连接对象, 错误信息)
        连接成功返回 (conn, None)
        连接失败返回 (None, 错误原因简述)
    """
    try:
        conn, _ = get_db_cursor()
        return conn, None
    except ValueError as e:
        return None, str(e)
    except OperationalError as e:
        error_msg = str(e)
        # 提取错误原因（去掉错误代码部分）
        if "(" in error_msg and "错误代码:" in error_msg:
            reason = error_msg.split("(")[0].strip()
        else:
            reason = error_msg
        return None, reason
    except Exception as e:
        error_type = type(e).__name__
        return None, f"连接失败：{error_type}"


# ==========================================
# 核心数据库查询函数（已重构为使用 get_db_cursor）
# ==========================================

def get_all_users() -> List[Dict]:
    """
    查询 users 表所有用户数据
    
    Returns:
        List[Dict]: 用户字典列表，无数据返回空列表
    """
    conn = None
    cursor = None
    try:
        conn, cursor = get_db_cursor()
        sql = "SELECT * FROM users"
        cursor.execute(sql)
        results = cursor.fetchall()
        return list(results) if results else []
    except Exception as e:
        print(f"❌ 查询所有用户失败：{e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_user_by_username(username: str) -> Optional[Dict]:
    """
    根据用户名精准查询单个用户
    
    Args:
        username: 用户名字符串
    
    Returns:
        Dict: 单个用户字典，无用户返回 None
    """
    conn = None
    cursor = None
    try:
        conn, cursor = get_db_cursor()
        sql = "SELECT * FROM users WHERE username = %s"
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        return result if result else None
    except Exception as e:
        print(f"❌ 查询用户失败：{e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn:
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
    conn = None
    cursor = None
    try:
        conn, cursor = get_db_cursor()
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
        return False, "数据库连接失败"
    finally:
        if cursor:
            cursor.close()
        if conn:
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
    conn = None
    cursor = None
    try:
        conn, cursor = get_db_cursor()
        # 使用参数化查询，避免 SQL 注入
        sql = f"UPDATE users SET {field} = %s WHERE username = %s"
        cursor.execute(sql, (value, username))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"❌ 更新用户字段失败：{e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
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
    conn = None
    cursor = None
    try:
        conn, cursor = get_db_cursor()
        # 构建动态 SQL
        set_clause = ", ".join([f"{k} = %s" for k in fields.keys()])
        sql = f"UPDATE users SET {set_clause} WHERE username = %s"
        values = list(fields.values()) + [username]
        cursor.execute(sql, values)
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"❌ 更新用户多个字段失败：{e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
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
    conn = None
    cursor = None
    try:
        conn, cursor = get_db_cursor()
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
        if conn:
            conn.rollback()
        return False, f"注册失败：{e}"
    finally:
        if cursor:
            cursor.close()
        if conn:
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
    conn = None
    cursor = None
    try:
        conn, cursor = get_db_cursor()
        sql = f"UPDATE users SET {field} = {field} + %s WHERE username = %s"
        cursor.execute(sql, (increment, username))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"❌ 递增用户字段失败：{e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
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
    conn = None
    cursor = None
    try:
        conn, cursor = get_db_cursor()
        sql = f"UPDATE users SET {field} = GREATEST({field} - %s, 0) WHERE username = %s"
        cursor.execute(sql, (decrement, username))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"❌ 递减用户字段失败：{e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
