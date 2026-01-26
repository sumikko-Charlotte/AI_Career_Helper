<script setup>
import { ref, reactive } from 'vue'
import { Operation, Check, RefreshLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('resume')

// 模拟 Prompt 数据 (后续可从后端读取)
const prompts = reactive({
  resume: {
    title: '简历医生设定',
    content: `你是一个专业的简历优化专家。请根据用户的简历内容，从“格式规范”、“内容完整性”、“STAR法则应用”三个维度进行打分（满分100）。
并给出具体的修改建议。输出格式必须为 JSON。`
  },
  interview: {
    title: '面试官人设',
    content: `你是一个严厉但公正的技术面试官。请根据用户的求职意向（如Java后端），提出有深度的技术问题。
每次只问一个问题，并在用户回答后进行追问。不要一次性抛出太多问题。`
  },
  career: {
    title: '生涯规划师',
    content: `你是一个资深的大学生职业规划导师。请根据学生的年级和专业，为他规划一条清晰的学习路线图。
请列出具体的学习阶段、推荐书籍和关键项目。`
  }
})

const handleSave = () => {
  // 这里写 axios.post 把 prompts 发给后端保存
  console.log('保存 Prompt:', prompts[activeTab.value].content)
  ElMessage.success('系统提示词已更新，下一次 AI 对话将立即生效！')
}

const handleReset = () => {
  ElMessage.info('已重置为默认设定')
}
</script>

<template>
  <div class="page-container">
    <div class="header">
      <h2><el-icon><Operation /></el-icon> AI 提示词配置 (Prompt Engineering)</h2>
      <p>在此调整 AI 的核心指令，可实时改变 AI 的回答风格与逻辑</p>
    </div>

    <div class="content-layout">
      <div class="left-menu">
        <div 
          class="menu-item" 
          :class="{ active: activeTab === 'resume' }"
          @click="activeTab = 'resume'"
        >
          <div class="dot"></div> 简历医生配置
        </div>
        <div 
          class="menu-item" 
          :class="{ active: activeTab === 'interview' }"
          @click="activeTab = 'interview'"
        >
          <div class="dot"></div> 模拟面试配置
        </div>
        <div 
          class="menu-item" 
          :class="{ active: activeTab === 'career' }"
          @click="activeTab = 'career'"
        >
          <div class="dot"></div> 生涯规划配置
        </div>
      </div>

      <div class="editor-area">
        <div class="editor-header">
          <span class="label">正在编辑：{{ prompts[activeTab].title }}</span>
          <div class="btns">
            <el-button :icon="RefreshLeft" @click="handleReset">重置</el-button>
            <el-button type="primary" color="#101C4D" :icon="Check" @click="handleSave">保存配置</el-button>
          </div>
        </div>
        
        <el-input
          v-model="prompts[activeTab].content"
          type="textarea"
          :rows="15"
          resize="none"
          class="code-editor"
          placeholder="请输入系统提示词 (System Prompt)..."
        />
        
        <div class="tips">
          <el-alert title="提示：修改后立即生效，请谨慎操作核心指令。" type="warning" show-icon :closable="false" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container { padding: 10px; height: calc(100vh - 100px); display: flex; flex-direction: column; }
.header { margin-bottom: 20px; }
.header h2 { color: #101C4D; display: flex; align-items: center; gap: 10px; margin: 0; }
.header p { color: #909399; font-size: 13px; margin: 5px 0 0 32px; }

.content-layout { display: flex; flex: 1; gap: 20px; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }

.left-menu { width: 220px; border-right: 1px solid #f0f2f5; padding-right: 20px; }
.menu-item {
  padding: 15px; margin-bottom: 10px; border-radius: 8px; cursor: pointer;
  display: flex; align-items: center; gap: 10px; color: #606266; font-weight: 500;
  transition: all 0.3s;
}
.menu-item:hover { background: #f5f7fa; }
.menu-item.active { background: #eff4ff; color: #101C4D; font-weight: bold; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: #dcdfe6; }
.menu-item.active .dot { background: #EFE3B2; box-shadow: 0 0 0 2px #101C4D; }

.editor-area { flex: 1; display: flex; flex-direction: column; }
.editor-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.label { font-size: 16px; font-weight: bold; color: #303133; }

.code-editor :deep(.el-textarea__inner) {
  background-color: #f8f9fa;
  font-family: 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  border-color: #e4e7ed;
}
.code-editor :deep(.el-textarea__inner):focus {
  border-color: #101C4D;
  background-color: white;
}

.tips { margin-top: 15px; }
</style>