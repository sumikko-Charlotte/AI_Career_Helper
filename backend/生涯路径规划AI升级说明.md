# 生涯路径规划 AI 嵌入升级说明

## 📋 升级概述

本次升级将「生涯路径规划」功能从固定模板生成升级为基于 Deepseek API 的动态 AI 生成，实现真正的个性化规划。

## ✅ 已完成的升级

### 1. AI 生成核心逻辑

**文件：`backend/main.py`**

**函数：`_generate_roadmap_with_ai(current_grade, target_role)`**

- ✅ 使用项目统一的 Deepseek API 调用方式（`_deepseek_json`）
- ✅ 复用相同的 API 调用逻辑、鉴权方式和错误处理机制
- ✅ 生成结构化的 JSON 数据，直接映射到前端时间轴组件

### 2. 优化的 AI Prompt

**系统提示词（System Prompt）包含：**

- ✅ **详细的规划原则**：针对大一到大四每个阶段的具体要求
  - 大一：基础学习与入门竞赛
  - 大二：竞赛进阶与项目实践
  - 大三：实习积累与技术深度
  - 大四：校招冲刺与入职准备

- ✅ **结构化输出要求**：确保生成的数据格式与前端完全一致
  - `grade`: 年级（大一/大二/大三/大四）
  - `title`: 阶段标题
  - `content`: 详细内容（150-200字）
  - `resources`: 推荐资源列表（3-5个）
  - `certificates`: 目标证书/荣誉列表（2-4个）
  - `recommended_companies`: 推荐企业列表（仅大四）

- ✅ **企业推荐要求**：大四阶段推荐3-6家适配企业，贴合职业方向

### 3. 数据验证与错误处理

**增强的数据验证：**

- ✅ 验证 AI 返回数据的完整性（必须包含4个年级）
- ✅ 自动填充缺失字段，确保数据结构完整
- ✅ 降级处理：如果 AI 生成失败，自动使用备选模板
- ✅ 详细的错误日志，便于排查问题

### 4. 保持前端代码不变

**前端代码无需修改：**

- ✅ 数据结构完全兼容，前端可直接使用
- ✅ UI 渲染和交互逻辑保持不变
- ✅ 时间轴组件自动适配 AI 生成的数据

## 🔧 技术实现细节

### API 调用方式

```python
# 使用项目统一的 Deepseek API 调用函数
ai_response = _deepseek_json(system_prompt, user_prompt)
```

### 数据格式

**AI 返回的 JSON 结构：**
```json
{
  "stages": [
    {
      "grade": "大一",
      "title": "阶段标题",
      "content": "详细内容（150-200字）",
      "resources": ["资源1", "资源2", "资源3"],
      "certificates": ["证书1", "证书2"],
      "recommended_companies": []
    },
    // ... 大二、大三、大四
  ],
  "ai_comment": "AI 导师洞察（80-120字）"
}
```

**后端转换后的数据结构（与前端完全一致）：**
```json
{
  "time": "大一",
  "title": "阶段标题",
  "content": "详细内容",
  "status": "done|process|wait",
  "color": "#67C23A|#409EFF|#909399",
  "icon": "CircleCheck|Loading|",
  "resources": ["资源1", "资源2"],
  "certificates": ["证书1", "证书2"],
  "recommended_companies": ["企业1", "企业2"],  // 仅大四
  "timestamp": "大一年级"
}
```

### 状态判断逻辑

根据用户当前年级自动判断各阶段状态：
- **已完成**（done）：当前年级之前的阶段，绿色，CircleCheck 图标
- **进行中**（process）：当前年级，蓝色，Loading 图标
- **待开始**（wait）：当前年级之后的阶段，灰色，无图标

## 📊 功能特点

### 1. 个性化生成

- ✅ 根据用户输入的「当前年级」和「意向职业」动态生成
- ✅ 每个阶段的规划内容贴合职业方向
- ✅ 推荐资源、证书、企业都具有针对性

### 2. 内容详细度

- ✅ 每个阶段包含 150-200 字的详细说明
- ✅ 具体的学习重点、比赛推荐、实习安排
- ✅ 明确的目标荣誉和证书
- ✅ 大四阶段包含企业推荐和匹配理由

### 3. 降级处理

- ✅ AI 生成失败时自动使用备选模板
- ✅ 确保功能始终可用
- ✅ 详细的错误日志便于排查

## 🚀 使用方式

### 前端调用（无需修改）

```javascript
// 前端代码保持不变
const res = await axios.post(`${API_BASE}/api/generate_roadmap`, {
  current_grade: roadmapGrade.value,  // 如：'大一'
  target_role: roadmapRole.value      // 如：'算法工程师'
})

// 数据结构完全兼容
roadmapData.value = res.data.roadmap
roadmapComment.value = res.data.ai_comment
```

### 后端接口

**接口路径：** `POST /api/generate_roadmap`

**请求参数：**
```json
{
  "current_grade": "大一|大二|大三|大四",
  "target_role": "算法工程师|前端工程师|..."
}
```

**返回数据：**
```json
{
  "radar_chart": {
    "indicators": [...],
    "values": [...]
  },
  "ai_comment": "AI 导师洞察",
  "roadmap": [
    {
      "time": "大一",
      "title": "...",
      "content": "...",
      "status": "done|process|wait",
      "color": "...",
      "icon": "...",
      "resources": [...],
      "certificates": [...],
      "recommended_companies": [...]
    },
    // ... 其他阶段
  ]
}
```

## 🔍 代码位置

### 核心函数

1. **`_generate_roadmap_with_ai`** (第 380-496 行)
   - AI 生成核心逻辑
   - Prompt 构建
   - 数据解析和验证

2. **`generate_roadmap`** (第 498-614 行)
   - API 接口处理
   - 调用 AI 生成函数
   - 降级处理逻辑

3. **`_deepseek_json`** (第 67-82 行)
   - Deepseek API 调用封装
   - 统一的错误处理

## ⚙️ 配置说明

### Deepseek API Key

API Key 通过环境变量配置：
```python
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-d3a066f75e744cd58708b9af635d3606")
```

**设置方式：**
1. 在系统环境变量中设置 `DEEPSEEK_API_KEY`
2. 或在代码中直接修改默认值（不推荐，仅用于开发测试）

## 📝 注意事项

1. **API 调用限制**：Deepseek API 有调用频率限制，建议添加缓存机制（可选）

2. **生成时间**：AI 生成需要一定时间（通常 2-5 秒），前端已显示 loading 状态

3. **数据格式**：确保 AI 返回的数据格式正确，代码已包含验证和降级处理

4. **错误处理**：如果 AI 生成失败，会自动使用备选模板，确保功能可用

## 🎯 升级效果

### 升级前
- ❌ 固定模板，内容千篇一律
- ❌ 无法根据职业方向个性化调整
- ❌ 企业推荐固定，不够灵活

### 升级后
- ✅ AI 动态生成，内容个性化
- ✅ 根据职业方向智能调整规划
- ✅ 企业推荐贴合职业方向
- ✅ 内容详细具体，可执行性强
- ✅ 保持原有 UI 和交互不变

## 🔄 后续优化建议（可选）

1. **缓存机制**：对相同输入（年级+职业）的规划结果进行缓存，减少 API 调用
2. **用户反馈**：允许用户对生成的规划进行评分和反馈，优化 prompt
3. **多轮对话**：支持用户对规划内容进行追问和细化
4. **历史记录**：保存用户生成的规划历史，方便查看和对比

---

**升级完成时间：** 2025年2月
**技术栈：** FastAPI + Deepseek API + Vue3
**兼容性：** 完全向后兼容，前端代码无需修改
