-- 修复 resume_history 表的字符集问题
-- 解决错误: (1366, "Incorrect string value: '\\xF0\\x9F\\x92\\xA1 A...' for column 'ai_analysis' at row 1")
-- 
-- 请在数据库管理界面执行以下 SQL 语句

-- 1. 修改整个表的字符集为 utf8mb4
ALTER TABLE resume_history CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 2. 确保 ai_analysis 字段使用 utf8mb4（如果上面命令没有生效，单独修改字段）
ALTER TABLE resume_history MODIFY ai_analysis TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 3. 验证修改结果
SHOW CREATE TABLE resume_history;

-- 4. 检查字段字符集
SHOW FULL COLUMNS FROM resume_history WHERE Field = 'ai_analysis';

-- 说明：
-- - utf8mb4 是 MySQL 中支持完整 UTF-8 字符集的字符集，包括 emoji（4 字节字符）
-- - utf8 在 MySQL 中只支持 3 字节的 UTF-8 字符，不支持 emoji
-- - 修改后，表可以正常存储包含 emoji 的文本内容
