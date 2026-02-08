#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接测试脚本（修复版）
用于验证数据库连接是否正常，特别是 encoding 属性访问
"""
import os
import sys

def test_db_connection():
    """测试数据库连接"""
    print("=" * 60)
    print("数据库连接测试（修复版）")
    print("=" * 60)
    
    # 检查环境变量
    print("\n[1] 检查环境变量配置")
    print("-" * 60)
    
    required_vars = {
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_PORT": os.getenv("DB_PORT", "3306"),
        "DB_USER": os.getenv("DB_USER"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD"),
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_CHARSET": os.getenv("DB_CHARSET", "utf8mb4"),
    }
    
    missing_vars = []
    for var, value in required_vars.items():
        if var == "DB_PASSWORD":
            display_value = "***" if value else "❌ 未设置"
        else:
            display_value = value if value else "❌ 未设置"
        
        status = "✅" if value else "❌"
        print(f"  {status} {var}: {display_value}")
        
        if not value and var != "DB_CHARSET":  # DB_CHARSET 有默认值
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ 缺少必需的环境变量：{', '.join(missing_vars)}")
        return False
    
    # 测试导入
    print("\n[2] 测试模块导入")
    print("-" * 60)
    try:
        from db_config import get_db_cursor, get_db_config, validate_db_config
        print("  ✅ 成功导入 db_config 模块")
    except ImportError as e:
        print(f"  ❌ 导入失败：{e}")
        print("  提示：请确保在 backend 目录下运行此脚本")
        return False
    except Exception as e:
        print(f"  ❌ 导入失败：{e}")
        return False
    
    # 测试配置验证
    print("\n[3] 测试配置验证")
    print("-" * 60)
    try:
        validate_db_config()
        print("  ✅ 环境变量配置验证通过")
    except ValueError as e:
        print(f"  ❌ 配置验证失败：{e}")
        return False
    
    # 测试配置获取
    print("\n[4] 测试配置获取")
    print("-" * 60)
    try:
        config = get_db_config()
        print("  ✅ 成功获取数据库配置")
        
        # 检查配置中是否有 None 值
        none_values = [k for k, v in config.items() if v is None and k != "ssl"]
        if none_values:
            print(f"  ⚠️  配置中存在 None 值：{', '.join(none_values)}")
        else:
            print("  ✅ 配置中无 None 值")
    except Exception as e:
        print(f"  ❌ 配置获取失败：{e}")
        return False
    
    # 测试数据库连接
    print("\n[5] 测试数据库连接")
    print("-" * 60)
    conn = None
    cursor = None
    try:
        conn, cursor = get_db_cursor()
        print("  ✅ 数据库连接成功")
        
        # 测试连接对象的 encoding 属性
        try:
            encoding = conn.encoding
            print(f"  ✅ 连接对象 encoding 属性：{encoding}")
        except AttributeError as e:
            print(f"  ❌ 无法访问 encoding 属性：{e}")
            return False
        
        # 测试基本查询
        print("\n[6] 测试数据库查询")
        print("-" * 60)
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"  ✅ MySQL 版本: {version[0] if version else 'N/A'}")
        
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()
        print(f"  ✅ 当前数据库: {db_name[0] if db_name else 'N/A'}")
        
        cursor.execute("SHOW VARIABLES LIKE 'character_set_connection'")
        charset_result = cursor.fetchone()
        if charset_result:
            print(f"  ✅ 字符集: {charset_result[1]}")
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()
        print(f"  ✅ users 表记录数: {user_count[0] if user_count else 0}")
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！数据库连接正常")
        print("=" * 60)
        return True
        
    except ValueError as e:
        print(f"  ❌ 配置错误：{e}")
        print("\n" + "=" * 60)
        print("❌ 测试失败：请检查环境变量配置")
        print("=" * 60)
        return False
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        print(f"  ❌ 连接失败 [{error_type}]：{error_msg}")
        
        # 常见错误提示
        print("\n[常见原因]")
        if "AttributeError" in error_type or "encoding" in error_msg:
            print("  🔴 连接对象为 None 或无效")
            print("     → 检查环境变量是否正确配置")
            print("     → 检查数据库服务是否正常运行")
        elif "认证失败" in error_msg or "Access denied" in error_msg:
            print("  🔴 账号/密码错误")
            print("     → 检查 DB_USER 和 DB_PASSWORD")
        elif "网络连接失败" in error_msg or "Can't connect" in error_msg:
            print("  🔴 网络连接失败")
            print("     → 检查 DB_HOST 和 DB_PORT")
            print("     → 检查数据库白名单和安全组")
        elif "数据库不存在" in error_msg or "Unknown database" in error_msg:
            print("  🔴 数据库不存在")
            print("     → 检查 DB_NAME 是否正确")
        
        print("\n" + "=" * 60)
        print("❌ 测试失败：请根据上述提示排查问题")
        print("=" * 60)
        return False
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass

if __name__ == "__main__":
    success = test_db_connection()
    sys.exit(0 if success else 1)
