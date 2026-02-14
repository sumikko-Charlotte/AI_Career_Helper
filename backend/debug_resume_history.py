#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试脚本：测试 resume_history 表的插入操作
用于排查历史记录无法保存的问题
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from db_config import (
    get_db_cursor,
    get_user_by_username,
    create_resume_history
)

def test_resume_history():
    """测试历史记录保存功能"""
    print("=" * 60)
    print("🔍 开始测试 resume_history 表操作")
    print("=" * 60)
    
    # 1. 测试数据库连接
    print("\n1️⃣ 测试数据库连接...")
    try:
        conn, cursor = get_db_cursor()
        print("✅ 数据库连接成功")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    
    # 2. 检查表是否存在
    print("\n2️⃣ 检查 resume_history 表是否存在...")
    try:
        conn, cursor = get_db_cursor()
        cursor.execute("SHOW TABLES LIKE 'resume_history'")
        result = cursor.fetchone()
        if result:
            print("✅ resume_history 表存在")
        else:
            print("❌ resume_history 表不存在！请先创建表")
            cursor.close()
            conn.close()
            return False
        
        # 检查表结构
        cursor.execute("DESCRIBE resume_history")
        columns = cursor.fetchall()
        print(f"✅ 表结构: {len(columns)} 个字段")
        for col in columns:
            print(f"   - {col.get('Field', 'N/A')}: {col.get('Type', 'N/A')}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ 检查表失败: {e}")
        return False
    
    # 3. 测试获取用户
    print("\n3️⃣ 测试获取用户 alice...")
    try:
        user = get_user_by_username("alice")
        if user:
            user_id = user.get('id') if isinstance(user, dict) else getattr(user, 'id', None)
            print(f"✅ 获取用户成功，user_id: {user_id}")
        else:
            print("❌ 用户 alice 不存在")
            return False
    except Exception as e:
        print(f"❌ 获取用户失败: {e}")
        return False
    
    # 4. 测试插入历史记录
    print("\n4️⃣ 测试插入历史记录...")
    try:
        test_data = {
            "diagnosis_report": {"score": 85, "summary": "测试数据"},
            "optimized_resume": "测试优化简历",
            "fallback": False
        }
        import json
        ai_analysis_str = json.dumps(test_data, ensure_ascii=False)
        
        success, history_id = create_resume_history(
            user_id=user_id,
            resume_type="normal",
            resume_file_url="test_debug_url",
            ai_analysis=ai_analysis_str
        )
        
        if success:
            print(f"✅ 历史记录插入成功！记录ID: {history_id}")
        else:
            print("❌ 历史记录插入失败（函数返回 False）")
            return False
    except Exception as e:
        print(f"❌ 插入历史记录异常: {e}")
        import traceback
        print(traceback.format_exc())
        return False
    
    # 5. 验证记录是否真的保存了
    print("\n5️⃣ 验证记录是否保存...")
    try:
        conn, cursor = get_db_cursor()
        cursor.execute("SELECT * FROM resume_history WHERE user_id = %s ORDER BY created_at DESC LIMIT 1", (user_id,))
        record = cursor.fetchone()
        if record:
            print(f"✅ 记录验证成功！")
            print(f"   - ID: {record.get('id')}")
            print(f"   - 简历类型: {record.get('resume_type')}")
            print(f"   - 创建时间: {record.get('created_at')}")
        else:
            print("❌ 记录验证失败：查询不到刚插入的记录")
            cursor.close()
            conn.close()
            return False
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ 验证记录失败: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！历史记录功能正常")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_resume_history()
    sys.exit(0 if success else 1)
