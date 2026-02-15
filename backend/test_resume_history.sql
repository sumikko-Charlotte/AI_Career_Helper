-- 测试 resume_history 表结构和插入操作
-- 请在数据库管理界面执行此 SQL

-- 1. 检查表结构
DESCRIBE resume_history;

-- 2. 检查表是否存在
SHOW TABLES LIKE 'resume_history';

-- 3. 如果表不存在，创建表（请根据实际表结构调整）
CREATE TABLE IF NOT EXISTS `resume_history` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `resume_type` VARCHAR(20) NOT NULL COMMENT '简历类型: normal 或 vip',
  `resume_file_url` VARCHAR(500) NOT NULL COMMENT '简历文件URL或标识',
  `ai_analysis` TEXT NOT NULL COMMENT 'AI分析结果（JSON格式）',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX `idx_user_id` (`user_id`),
  INDEX `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='简历历史记录表';

-- 4. 测试插入一条记录（使用用户 alice 的 ID，通常是 1）
INSERT INTO resume_history (user_id, resume_type, resume_file_url, ai_analysis, created_at)
VALUES (
  1,  -- 假设 alice 的 user_id 是 1
  'normal',
  'test_file_url',
  '{"test": "data"}',
  NOW()
);

-- 5. 查询测试记录
SELECT * FROM resume_history WHERE user_id = 1;

-- 6. 删除测试记录（可选）
-- DELETE FROM resume_history WHERE resume_file_url = 'test_file_url';
