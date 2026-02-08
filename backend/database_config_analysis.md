# 数据库配置分析报告 - Render 部署环境变量清单

## 📋 结论摘要

| 项目 | 值 |
|------|-----|
| **数据库类型** | 腾讯云 TDSQL-C (CynosDB MySQL) |
| **连接方式** | pymysql (直接连接) |
| **连接入口文件** | `backend/db_config.py` (第14-22行) |
| **当前配置方式** | 硬编码在 `DB_CONFIG` 字典中 |
| **环境变量使用** | ❌ 未使用（仅 `DEEPSEEK_API_KEY` 使用了环境变量） |
| **需要改造** | ✅ 是（建议改为环境变量） |

---

## 🔍 任务 1：数据库连接代码定位

### 1.1 关键字搜索结果

| 关键字 | 命中文件 | 行号 | 说明 |
|--------|---------|------|------|
| `pymysql` | `backend/db_config.py` | 7, 8, 21, 36 | 导入和使用 pymysql |
| `pymysql` | `backend/requirements.txt` | 3 | 依赖声明 |
| `mysql` | `backend/main.py` | 163 | 注释中的关键词 |
| `tencentcdb` | `backend/db_config.py` | 15 | 腾讯云数据库主机地址 |
| `cynosdb` | `backend/db_config.py` | 15 | 数据库类型标识 |

### 1.2 连接入口文件

**主要文件：`backend/db_config.py`**

```python
# 第14-22行：数据库连接配置（硬编码）
DB_CONFIG = {
    "host": "bj-cynosdbmysql-grp-ovt0aqds.sql.tencentcdb.com",
    "port": 20603,
    "user": "root",
    "password": "AIcareer@helper123",    # ⚠️ 硬编码密码
    "database": "ai_career_helper",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

# 第28-53行：连接函数
def get_db_connection():
    conn = pymysql.connect(**DB_CONFIG)
    return conn
```

**使用位置：**
- `backend/main.py` 第20行：导入 `get_db_connection` 等函数
- 所有数据库操作函数都调用 `get_db_connection()`

### 1.3 连接方式说明

- **连接库**：`pymysql` (纯 Python MySQL 客户端)
- **连接字符串格式**：字典参数形式（非 URL 字符串）
- **连接池**：❌ 未使用（每次操作都创建新连接）
- **SSL**：未显式配置（使用默认）

---

## 🔧 任务 2：环境变量字段提取

### 2.1 当前硬编码字段

从 `backend/db_config.py` 提取的字段：

| 字段名 | 当前值 | 类型 | 说明 |
|--------|--------|------|------|
| `host` | `bj-cynosdbmysql-grp-ovt0aqds.sql.tencentcdb.com` | string | 腾讯云数据库主机地址 |
| `port` | `20603` | int | 数据库端口（外网端口） |
| `user` | `root` | string | 数据库用户名 |
| `password` | `AIcareer@helper123` | string | 数据库密码（硬编码） |
| `database` | `ai_career_helper` | string | 数据库名称 |
| `charset` | `utf8mb4` | string | 字符集（固定值） |
| `cursorclass` | `pymysql.cursors.DictCursor` | class | 游标类型（固定值） |

### 2.2 环境变量改造建议

**当前问题：**
- 密码硬编码在代码中（安全风险）
- 无法在不同环境（本地/生产）使用不同配置
- Render 部署时无法动态配置

**建议改造方案：**

修改 `backend/db_config.py`，将硬编码改为环境变量读取：

```python
# 改造前（当前代码）
DB_CONFIG = {
    "host": "bj-cynosdbmysql-grp-ovt0aqds.sql.tencentcdb.com",
    "port": 20603,
    "user": "root",
    "password": "AIcareer@helper123",
    "database": "ai_career_helper",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

# 改造后（建议）
import os
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "bj-cynosdbmysql-grp-ovt0aqds.sql.tencentcdb.com"),
    "port": int(os.getenv("DB_PORT", "20603")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),  # ⚠️ 必须设置，无默认值
    "database": os.getenv("DB_NAME", "ai_career_helper"),
    "charset": os.getenv("DB_CHARSET", "utf8mb4"),
    "cursorclass": pymysql.cursors.DictCursor
}

# 验证必填字段
if not DB_CONFIG["password"]:
    raise ValueError("DB_PASSWORD 环境变量未设置，请在 Render 中配置")
```

**补丁文件（diff 格式）：**

```diff
--- backend/db_config.py (原文件)
+++ backend/db_config.py (改造后)
@@ -11,9 +11,16 @@
 # ==========================================
 # 数据库连接配置（固定值，仅需修改 password）
 # ==========================================
+import os
 DB_CONFIG = {
-    "host": "bj-cynosdbmysql-grp-ovt0aqds.sql.tencentcdb.com",
-    "port": 20603,
-    "user": "root",
-    "password": "AIcareer@helper123",    # ⚠️ 仅需替换这1个参数
-    "database": "ai_career_helper",
-    "charset": "utf8mb4",
+    "host": os.getenv("DB_HOST", "bj-cynosdbmysql-grp-ovt0aqds.sql.tencentcdb.com"),
+    "port": int(os.getenv("DB_PORT", "20603")),
+    "user": os.getenv("DB_USER", "root"),
+    "password": os.getenv("DB_PASSWORD", ""),  # ⚠️ 必须设置，无默认值
+    "database": os.getenv("DB_NAME", "ai_career_helper"),
+    "charset": os.getenv("DB_CHARSET", "utf8mb4"),
     "cursorclass": pymysql.cursors.DictCursor
 }
+
+# 验证必填字段
+if not DB_CONFIG["password"]:
+    raise ValueError("DB_PASSWORD 环境变量未设置，请在 Render 中配置")
```

---

## 📝 任务 3：Render 环境变量清单

### 3.1 Render 环境变量配置清单

在 Render Dashboard → Your Service → Environment 中添加以下变量：

```bash
# ==========================================
# 腾讯云数据库连接配置（必填）
# ==========================================
DB_HOST=bj-cynosdbmysql-grp-ovt0aqds.sql.tencentcdb.com
DB_PORT=20603
DB_USER=root
DB_PASSWORD=AIcareer@helper123
DB_NAME=ai_career_helper
DB_CHARSET=utf8mb4

# ==========================================
# 其他环境变量（如果使用）
# ==========================================
DEEPSEEK_API_KEY=sk-d3a066f75e744cd58708b9af635d3606
```

### 3.2 字段说明与来源

| 环境变量 | Render 中填什么 | 从哪里获取 | 是否必填 |
|---------|----------------|-----------|---------|
| `DB_HOST` | `bj-cynosdbmysql-grp-ovt0aqds.sql.tencentcdb.com` | 腾讯云控制台 → 数据库实例 → **外网地址** | ✅ 必填 |
| `DB_PORT` | `20603` | 腾讯云控制台 → 数据库实例 → **外网端口** | ✅ 必填 |
| `DB_USER` | `root` | 数据库用户名（通常是 `root`） | ✅ 必填 |
| `DB_PASSWORD` | `你的数据库密码` | 腾讯云控制台 → 数据库实例 → **重置密码** | ✅ 必填 |
| `DB_NAME` | `ai_career_helper` | 数据库名称（在数据库中创建） | ✅ 必填 |
| `DB_CHARSET` | `utf8mb4` | 固定值（建议使用 utf8mb4） | ⚪ 可选（有默认值） |

### 3.3 腾讯云控制台操作指南

#### 步骤 1：获取外网地址和端口
1. 登录 [腾讯云控制台](https://console.cloud.tencent.com/)
2. 进入 **云数据库 MySQL** → **实例列表**
3. 找到你的数据库实例（ID: `ovt0aqds`）
4. 点击实例名称进入详情页
5. 在 **连接信息** 或 **基本信息** 中找到：
   - **外网地址**：`bj-cynosdbmysql-grp-ovt0aqds.sql.tencentcdb.com`
   - **外网端口**：`20603`（注意：外网端口通常与内网端口不同）

#### 步骤 2：确认/重置密码
1. 在数据库实例详情页，找到 **账号管理** 或 **数据库管理**
2. 查看 `root` 账号的密码（如果忘记，可以重置）
3. 复制密码到 `DB_PASSWORD` 环境变量

#### 步骤 3：确认数据库名称
1. 在数据库实例详情页，进入 **数据库管理**
2. 确认数据库 `ai_career_helper` 是否存在
3. 如果不存在，需要创建该数据库

### 3.4 白名单配置（重要！）

**问题：** Render 的出站 IP 不固定，腾讯云数据库默认只允许白名单 IP 访问。

**解决方案：**

#### 方案 A：开放所有 IP（仅用于测试，不推荐生产环境）
1. 腾讯云控制台 → 数据库实例 → **安全组** 或 **访问控制**
2. 添加白名单规则：`0.0.0.0/0`（允许所有 IP）
3. ⚠️ **安全风险**：任何 IP 都可以尝试连接（虽然需要密码）

#### 方案 B：使用 Render 固定 IP（推荐，但需要付费）
1. Render 提供 **Static Outbound IPs**（静态出站 IP）功能（需要付费计划）
2. 获取 Render 的静态 IP 地址
3. 在腾讯云数据库白名单中添加该 IP

#### 方案 C：定期更新白名单（不推荐）
1. 每次 Render 服务重启时，查看 Render 日志获取当前 IP
2. 手动添加到腾讯云白名单
3. ⚠️ **不实用**：IP 会变化，需要频繁更新

#### 方案 D：使用腾讯云私有网络 VPC（最佳方案，但需要架构调整）
1. 将 Render 服务部署到腾讯云 CVM
2. 使用内网地址连接（不需要外网端口和白名单）
3. ⚠️ **需要迁移**：需要将服务从 Render 迁移到腾讯云

**当前建议：**
- **开发/测试环境**：使用方案 A（开放 `0.0.0.0/0`，但设置强密码）
- **生产环境**：使用方案 B（Render 静态 IP）或方案 D（迁移到腾讯云）

---

## 🧪 任务 4：快速自检脚本

### 4.1 自检脚本

创建文件：`backend/test_db_connection.py`

```python
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
```

### 4.2 使用方法

```bash
# 在 backend 目录下运行
cd backend
python test_db_connection.py
```

### 4.3 常见错误对照表

| 错误代码 | 错误信息关键词 | 可能原因 | 解决方案 |
|---------|--------------|---------|---------|
| `1045` | `Access denied` | 账号/密码错误 | 检查 `DB_USER` 和 `DB_PASSWORD` |
| `2003` | `Can't connect` | 网络连接失败 | 检查主机/端口、安全组、白名单 |
| `1049` | `Unknown database` | 数据库不存在 | 在腾讯云控制台创建数据库 |
| `2013` | `Lost connection` | 连接中断 | 检查网络稳定性、防火墙 |
| `-1` | `timeout` | 连接超时 | 检查网络延迟、防火墙规则 |

---

## 📊 证据列表

### 文件路径与关键代码

1. **`backend/db_config.py`** (第14-22行)
   ```python
   DB_CONFIG = {
       "host": "bj-cynosdbmysql-grp-ovt0aqds.sql.tencentcdb.com",
       "port": 20603,
       "user": "root",
       "password": "AIcareer@helper123",
       "database": "ai_career_helper",
       "charset": "utf8mb4",
       "cursorclass": pymysql.cursors.DictCursor
   }
   ```

2. **`backend/db_config.py`** (第28-53行)
   ```python
   def get_db_connection():
       conn = pymysql.connect(**DB_CONFIG)
       return conn
   ```

3. **`backend/main.py`** (第20-30行)
   ```python
   from db_config import (
       get_db_connection, 
       get_all_users, 
       get_user_by_username, 
       user_login,
       ...
   )
   ```

4. **`backend/requirements.txt`** (第3行)
   ```
   pymysql
   ```

---

## ✅ 下一步操作清单

### 在 Render 中配置环境变量

1. ✅ 登录 Render Dashboard
2. ✅ 进入你的服务（Web Service）
3. ✅ 点击 **Environment** 标签
4. ✅ 添加以下环境变量：
   - `DB_HOST` = `bj-cynosdbmysql-grp-ovt0aqds.sql.tencentcdb.com`
   - `DB_PORT` = `20603`
   - `DB_USER` = `root`
   - `DB_PASSWORD` = `你的数据库密码`
   - `DB_NAME` = `ai_career_helper`
   - `DB_CHARSET` = `utf8mb4`（可选）

### 在腾讯云控制台操作

1. ✅ 确认外网地址和端口（连接信息页面）
2. ✅ 确认/重置 root 密码（账号管理页面）
3. ✅ 确认数据库 `ai_career_helper` 存在（数据库管理页面）
4. ✅ **配置白名单**（安全组/访问控制页面）：
   - 添加 `0.0.0.0/0`（测试环境）
   - 或添加 Render 静态 IP（生产环境）

### 代码改造（可选但推荐）

1. ✅ 应用环境变量改造补丁（见任务 2.2）
2. ✅ 测试本地连接（使用 `test_db_connection.py`）
3. ✅ 提交代码到 Git
4. ✅ 在 Render 中重新部署

---

## 📞 技术支持

如有问题，请检查：
1. 环境变量是否正确配置
2. 腾讯云数据库白名单是否包含 Render IP
3. 数据库密码是否正确
4. 网络连接是否正常
5. 运行自检脚本查看详细错误信息

---

**报告生成时间：** 2026-01-30  
**分析工具：** AI 项目排查助手
