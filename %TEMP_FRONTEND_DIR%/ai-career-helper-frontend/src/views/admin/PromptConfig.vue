<script setup>
import { ref, reactive, computed } from 'vue'
import { Operation, Check, RefreshLeft } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('resume')

// 模拟 Prompt 数据 (后续可从后端读取)
// 注意：这些文本也是 User 端的默认兜底内容
const prompts = reactive({
  resume: {
    title: '简历医生设定',
    content: `你是一个专业的简历优化专家。请根据用户的简历内容，从“格式规范”、“内容完整性”、“STAR法则应用”三个维度进行打分（满分100）。\n并给出具体的修改建议。输出格式必须为 JSON。`
  },
  interview: {
    title: '面试官人设',
    content: `你是一个严厉但公正的技术面试官。请根据用户的求职意向（如Java后端），提出有深度的技术问题。\n每次只问一个问题，并在用户回答后进行追问。不要一次性抛出太多问题。`
  },
  career: {
    title: '生涯规划师',
    content: `你是一个资深的大学生职业规划导师。请根据学生的年级和专业，为他规划一条清晰的学习路线图。\n请列出具体的学习阶段、推荐书籍和关键项目。`
  },
  // 新增虚拟职业体验默认 prompt（用于生成体验脚本 / 题目）
  virtual_career: {
    title: '虚拟职业体验（生成体验脚本）',
    content: `你是一个沉浸式体验脚本生成器。根据用户选择的职业（例如“产品经理”），生成一套 15 道情景模拟题目，覆盖真实工作场景，句式简洁明了，便于用户做出选择题回答。每题给出 3 个选项。`
  }
})

// LocalStorage keys（前缀 admin_ai_）
// admin_ai_resume_doctor, admin_ai_interview, admin_ai_virtual_career, admin_ai_career_plan

// 初始化编辑器内容：优先读取 localStorage（管理员曾保存过），否则使用内置默认值
const resumeEditor = ref(localStorage.getItem('admin_ai_resume_doctor') || prompts.resume.content)
const interviewEditor = ref(localStorage.getItem('admin_ai_interview') || prompts.interview.content)
const virtualCareerEditor = ref(localStorage.getItem('admin_ai_virtual_career') || prompts.virtual_career.content)
const careerPlanEditor = ref(localStorage.getItem('admin_ai_career_plan') || prompts.career.content)

// 通用保存函数：保存到 localStorage，更新 prompts，提示用户
const savePrompt = (key, value, label) => {
  if (!value || !String(value).trim()) return ElMessage.warning('提示词不能为空')
  localStorage.setItem(key, value)
  // 将内容同步回 prompts 以便在界面显示一致
  if (key === 'admin_ai_resume_doctor') prompts.resume.content = value
  if (key === 'admin_ai_interview') prompts.interview.content = value
  if (key === 'admin_ai_virtual_career') prompts.virtual_career.content = value
  if (key === 'admin_ai_career_plan') prompts.career.content = value
  ElMessage.success(`${label} 已保存，本地生效（User 端刷新后可读取）`)
}

// 重置为内置默认值并删除 localStorage 中的自定义值（存在则二次确认）
const resetPrompt = async (key, defaultValue, label) => {
  try {
    await ElMessageBox.confirm(`将把 ${label} 重置为默认提示词，是否继续？`, '确认重置', { confirmButtonText: '确认', cancelButtonText: '取消', type: 'warning' })
    localStorage.removeItem(key)
    // 恢复到内置默认
    if (key === 'admin_ai_resume_doctor') resumeEditor.value = defaultValue, prompts.resume.content = defaultValue
    if (key === 'admin_ai_interview') interviewEditor.value = defaultValue, prompts.interview.content = defaultValue
    if (key === 'admin_ai_virtual_career') virtualCareerEditor.value = defaultValue, prompts.virtual_career.content = defaultValue
    if (key === 'admin_ai_career_plan') careerPlanEditor.value = defaultValue, prompts.career.content = defaultValue
    ElMessage.success(`${label} 已重置为默认提示词`) 
  } catch (e) {
    // 用户取消或关闭确认框
  }
}

// editorContent: computed getter/setter to bind single editor textarea for resume/interview tabs
const editorContent = computed({
  get() { return activeTab.value === 'resume' ? resumeEditor.value : interviewEditor.value },
  set(v) { if (activeTab.value === 'resume') resumeEditor.value = v; else interviewEditor.value = v }
})

// 兼容旧的 handleSave/Reset（留作按钮绑定友好提示）
const handleSave = () => { ElMessage.info('请选择要保存的具体提示词并点击对应的保存按钮') }
const handleReset = () => { ElMessage.info('请选择要重置的具体提示词并点击对应的重置按钮') }
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

        <!-- 单个编辑器（简历 / 面试） -->
        <template v-if="activeTab !== 'career'">
          <el-input
            v-model="editorContent"
            type="textarea"
            :rows="15"
            resize="none"
            class="code-editor"
            placeholder="请输入系统提示词 (System Prompt)..."
          />

          <div style="margin-top:12px; display:flex; gap:10px;">
            <el-button @click="savePrompt('admin_ai_' + (activeTab === 'resume' ? 'resume_doctor' : 'interview'), activeTab === 'resume' ? resumeEditor : interviewEditor, activeTab === 'resume' ? '简历医生提示词' : '模拟面试提示词')" type="primary">保存</el-button>
            <el-button @click="resetPrompt(activeTab === 'resume' ? 'admin_ai_resume_doctor' : 'admin_ai_interview', activeTab === 'resume' ? prompts.resume.content : prompts.interview.content, activeTab === 'resume' ? '简历医生提示词' : '模拟面试提示词')">重置</el-button>
          </div>
        </template>

        <!-- 生涯规划 & 虚拟职业体验联动：两个独立编辑框 -->
        <template v-else>
          <div style="display:flex; gap:20px; flex-direction:column;">
            <div>
              <label style="font-weight:700;">虚拟职业体验 AI 提示词（生成体验脚本）</label>
              <el-input v-model="virtualCareerEditor" type="textarea" :rows="8" resize="none" class="code-editor" placeholder="用于生成体验题目/脚本"></el-input>
              <div style="margin-top:8px; display:flex; gap:10px;"><el-button type="primary" @click="savePrompt('admin_ai_virtual_career', virtualCareerEditor, '虚拟职业体验提示词')">保存</el-button><el-button @click="resetPrompt('admin_ai_virtual_career', prompts.virtual_career.content, '虚拟职业体验提示词')">重置</el-button></div>
            </div>

            <div>
              <label style="font-weight:700;">生涯规划 AI 提示词（结合体验报告生成规划）</label>
              <el-input v-model="careerPlanEditor" type="textarea" :rows="8" resize="none" class="code-editor" placeholder="用于生成生涯规划报告"></el-input>
              <div style="margin-top:8px; display:flex; gap:10px;"><el-button type="primary" @click="savePrompt('admin_ai_career_plan', careerPlanEditor, '生涯规划提示词')">保存</el-button><el-button @click="resetPrompt('admin_ai_career_plan', prompts.career.content, '生涯规划提示词')">重置</el-button></div>
            </div>
          </div>
        </template>
        
        <div class="tips">
          <el-alert title="提示：修改后立即生效，请谨慎操作核心指令。" type="warning" show-icon :closable="false" />
        </div>
        
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