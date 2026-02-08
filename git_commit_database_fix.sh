#!/bin/bash
# 数据库连接修复 Git 提交脚本

echo "========================================"
echo "准备提交数据库连接修复代码"
echo "========================================"
echo ""

# 添加修改的文件
echo "1. 添加修改的文件..."
git add backend/db_config.py
git add backend/main.py

echo ""
echo "2. 查看暂存区状态..."
git status

echo ""
echo "3. 提交代码..."
git commit -m "Fix database connection for Render deployment

- Add environment variable support (DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_CHARSET, DB_SSL)
- Add .env file support (python-dotenv)
- Add connection timeout parameters (connect_timeout=10, read_timeout=20, write_timeout=20)
- Add SSL support (controlled by DB_SSL environment variable)
- Improve error classification and logging (DNS/timeout/auth/permission/SSL/Unknown database)
- Enhance /health endpoint with database connection check (db_ok field)"

echo ""
echo "4. 查看提交记录..."
git log --oneline -1

echo ""
echo "========================================"
echo "提交完成！"
echo "========================================"
echo ""
echo "下一步："
echo "  git push  # 推送到远程仓库"
echo ""
