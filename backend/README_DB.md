# 数据库迁移使用说明

## 📋 概述

项目已从本地 CSV 文件迁移到腾讯云 TDSQL-C 云端数据库，所有用户数据操作现在都通过云端数据库完成。

## 🔧 配置步骤

### 唯一需要修改的地方

打开 `backend/db_config.py` 文件，找到以下配置：

```python
DB_CONFIG = {
    "host": "bj-cynosdbmysql-grp-ovt0aqds.sql.tencentcdb.com",
    "port": 20603,
    "user": "root",
    "password": "【此处替换为用户在腾讯云重置的root密码】",  # ⚠️ 仅需替换这1个参数
    "database": "ai_career_helper",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}
```

**将 `password` 参数的值替换为你在腾讯云重置的 root 密码**（去掉 `【】` 和提示文字，直接填入密码字符串）。

## 🚀 运行方式

1. **激活虚拟环境**（如果使用虚拟环境）：
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **启动后端服务**：
   ```bash
   cd backend
   python main.py
   ```

3. **查看测试结果**：
   - 启动时会自动执行数据库连接测试
   - 如果连接成功，会显示：
     - ✅ 数据库连接成功
     - ✅ 成功获取 X 条用户数据
     - ✅ 登录验证测试结果
   - 如果连接失败，会显示具体错误信息

4. **访问 API**：
   - API 服务地址：http://127.0.0.1:8001
   - API 文档：http://127.0.0.1:8001/docs

## 📝 已迁移的功能

以下功能已从 CSV 迁移到云端数据库：

- ✅ 用户登录验证 (`/api/login`)
- ✅ 用户注册 (`/api/register`)
- ✅ 管理员资料查询 (`/api/admin/profile`)
- ✅ 管理员资料更新 (`/api/admin/profile/update`)
- ✅ 管理员密码修改 (`/api/admin/profile/change-password`)
- ✅ 普通用户密码修改 (`/api/user/change_password`)
- ✅ 用户任务数统计 (`/api/user/addTask`)
- ✅ 简历上传数统计 (`/api/resume/upload`)
- ✅ 简历删除数统计 (`/api/resume/delete`)

## 🔍 数据库表结构

`users` 表包含以下字段：

- `username` (varchar) - 用户名（主键）
- `password` (varchar) - 密码
- `grade` (varchar) - 年级
- `target_role` (varchar) - 目标岗位
- `nickname` (varchar) - 昵称（可选）
- `phone` (varchar) - 手机号（可选）
- `email` (varchar) - 邮箱（可选）
- `department` (varchar) - 部门/职位（可选）
- `createTaskNum` (int) - 创建任务数
- `uploadedResumeNum` (int) - 上传简历数

## ⚠️ 注意事项

1. **密码安全**：当前密码以明文存储，生产环境建议使用加密存储（如 bcrypt）
2. **网络连接**：确保服务器能够访问腾讯云数据库（检查安全组设置）
3. **数据备份**：定期备份云端数据库数据
4. **本地 CSV**：`data/users.csv` 文件已不再使用，但保留作为备份参考

## 🐛 故障排查

### 连接失败

如果看到 "数据库连接失败" 错误：

1. **检查密码**：确认 `db_config.py` 中的 `password` 是否正确
2. **检查端口**：确认端口号 `20603` 是否正确
3. **检查安全组**：确认腾讯云安全组是否开放了端口 `20603`
4. **检查网络**：确认服务器网络连接正常

### 查询失败

如果看到 "查询失败" 错误：

1. **检查表结构**：确认数据库表 `users` 是否存在
2. **检查字段名**：确认字段名与代码中的一致
3. **查看日志**：查看控制台输出的详细错误信息

## 📞 技术支持

如有问题，请检查：
1. 数据库连接配置是否正确
2. 网络连接是否正常
3. 数据库表结构是否匹配
4. 查看控制台输出的详细错误信息
