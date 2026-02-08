#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接自检脚本
用于测试能否连接到腾讯云数据库
"""
import os
import sys
import pymysql
from pymysql import OperationalError

def test_db_connection():
    """测试数据库连接"""
    print("=" * 60)
    print("数据库连接自检")
    print("=" * 60)
    
    # 从环境变量或配置文件读取
    try:
        from db_config import DB_CONFIG
        print(f"✅ 成功加载 db_config.py")
    except ImportError:
        print("❌ 无法导入 db_config.py，请确保在 backend 目录下运行")
        return False
    except Exception as e:
        print(f"❌ 加载配置失败：{e}")
        return False
    
    # 显示配置信息（隐藏密码）
    print(f"\n[配置信息]")
    print(f"  主机: {DB_CONFIG.get('host', 'N/A')}")
    print(f"  端口: {DB_CONFIG.get('port', 'N/A')}")
    print(f"  用户: {DB_CONFIG.get('user', 'N/A')}")
    print(f"  密码: {'*' * len(str(DB_CONFIG.get('password', '')))}")
    print(f"  数据库: {DB_CONFIG.get('database', 'N/A')}")
    print(f"  字符集: {DB_CONFIG.get('charset', 'N/A')}")
    
    # 尝试连接
    print(f"\n[连接测试]")
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print("✅ 数据库连接成功！")
        
        # 测试查询
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✅ MySQL 版本: {version[0] if version else 'N/A'}")
            
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()
            print(f"✅ 当前数据库: {db_name[0] if db_name else 'N/A'}")
            
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()
            print(f"✅ users 表记录数: {user_count[0] if user_count else 0}")
        
        conn.close()
        print("\n" + "=" * 60)
        print("✅ 自检通过：数据库连接正常")
        print("=" * 60)
        return True
        
    except OperationalError as e:
        error_msg = str(e)
        error_code = e.args[0] if e.args else None
        
        print(f"❌ 数据库连接失败（OperationalError）")
        print(f"   错误代码: {error_code}")
        print(f"   错误信息: {error_msg}")
        
        # 常见错误对照
        print(f"\n[常见原因对照]")
        if error_code == 1045 or "Access denied" in error_msg:
            print("   🔴 账号/密码错误")
            print("      → 检查 DB_USER 和 DB_PASSWORD 是否正确")
            print("      → 在腾讯云控制台确认 root 账号密码")
        elif error_code == 2003 or "Can't connect" in error_msg:
            print("   🔴 网络连接失败")
            print("      → 检查 DB_HOST 和 DB_PORT 是否正确")
            print("      → 检查服务器网络是否正常")
            print("      → 检查腾讯云安全组是否开放端口")
            print("      → 检查白名单是否包含当前服务器 IP")
        elif error_code == 1049 or "Unknown database" in error_msg:
            print("   🔴 数据库不存在")
            print("      → 检查 DB_NAME 是否正确")
            print("      → 在腾讯云控制台创建数据库")
        elif "timeout" in error_msg.lower():
            print("   🔴 连接超时")
            print("      → 检查网络延迟")
            print("      → 检查防火墙设置")
        else:
            print(f"   ⚠️  未知错误（代码: {error_code}）")
            print(f"      → 查看完整错误信息: {error_msg}")
        
        print("\n" + "=" * 60)
        print("❌ 自检失败：请根据上述提示排查问题")
        print("=" * 60)
        return False
        
    except Exception as e:
        print(f"❌ 数据库连接失败（未知错误）")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误信息: {e}")
        print("\n" + "=" * 60)
        print("❌ 自检失败：请检查配置和网络")
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = test_db_connection()
    sys.exit(0 if success else 1)
