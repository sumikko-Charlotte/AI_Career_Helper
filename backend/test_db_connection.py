#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接自检脚本
用于测试能否连接到腾讯云数据库
"""
import os
import sys

def test_db_connection():
    """测试数据库连接"""
    print("=" * 60)
    print("数据库连接自检")
    print("=" * 60)
    
    # 从环境变量读取配置
    try:
        from db_config import get_db_cursor, validate_db_config
        
        # 验证环境变量
        print("\n[环境变量检查]")
        try:
            validate_db_config()
            print("✅ 环境变量配置完整")
        except ValueError as e:
            print(f"❌ {e}")
            return False
        
        # 显示配置信息（隐藏密码）
        config = {
            "host": os.getenv("DB_HOST", "N/A"),
            "port": os.getenv("DB_PORT", "3306"),
            "user": os.getenv("DB_USER", "N/A"),
            "database": os.getenv("DB_NAME", "N/A"),
            "charset": os.getenv("DB_CHARSET", "utf8mb4"),
        }
        print(f"\n[配置信息]")
        print(f"  主机: {config['host']}")
        print(f"  端口: {config['port']}")
        print(f"  用户: {config['user']}")
        print(f"  密码: {'*' * 10} (已配置)")
        print(f"  数据库: {config['database']}")
        print(f"  字符集: {config['charset']}")
        
    except ImportError:
        print("❌ 无法导入 db_config.py，请确保在 backend 目录下运行")
        return False
    except Exception as e:
        print(f"❌ 加载配置失败：{e}")
        return False
    
    # 尝试连接
    print(f"\n[连接测试]")
    conn = None
    cursor = None
    try:
        conn, cursor = get_db_cursor()
        print("✅ 数据库连接成功！")
        
        # 测试查询
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✅ MySQL 版本: {version[0] if version else 'N/A'}")
        
        cursor.execute("SELECT DATABASE()")
        db_name = cursor.fetchone()
        print(f"✅ 当前数据库: {db_name[0] if db_name else 'N/A'}")
        
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()
        print(f"✅ users 表记录数: {user_count[0] if user_count else 0}")
        
        print("\n" + "=" * 60)
        print("✅ 自检通过：数据库连接正常")
        print("=" * 60)
        return True
        
    except ValueError as e:
        print(f"❌ 环境变量配置错误：{e}")
        return False
    except Exception as e:
        error_msg = str(e)
        print(f"❌ 数据库连接失败")
        print(f"   错误信息: {error_msg}")
        
        # 常见错误对照
        print(f"\n[常见原因对照]")
        if "认证失败" in error_msg or "Access denied" in error_msg:
            print("   🔴 账号/密码错误")
            print("      → 检查 DB_USER 和 DB_PASSWORD 是否正确")
            print("      → 在腾讯云控制台确认 root 账号密码")
        elif "网络连接失败" in error_msg or "Can't connect" in error_msg:
            print("   🔴 网络连接失败")
            print("      → 检查 DB_HOST 和 DB_PORT 是否正确")
            print("      → 检查服务器网络是否正常")
            print("      → 检查腾讯云安全组是否开放端口")
            print("      → 检查白名单是否包含当前服务器 IP")
        elif "数据库不存在" in error_msg or "Unknown database" in error_msg:
            print("   🔴 数据库不存在")
            print("      → 检查 DB_NAME 是否正确")
            print("      → 在腾讯云控制台创建数据库")
        elif "连接超时" in error_msg or "timeout" in error_msg.lower():
            print("   🔴 连接超时")
            print("      → 检查网络延迟")
            print("      → 检查防火墙设置")
        else:
            print(f"   ⚠️  未知错误")
            print(f"      → 查看完整错误信息: {error_msg}")
        
        print("\n" + "=" * 60)
        print("❌ 自检失败：请根据上述提示排查问题")
        print("=" * 60)
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    success = test_db_connection()
    sys.exit(0 if success else 1)
