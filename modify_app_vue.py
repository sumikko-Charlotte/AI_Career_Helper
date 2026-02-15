# -*- coding: utf-8 -*-
import re

# 读取文件
file_path = r'ai-career-helper-frontend\src\App.vue'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 要插入的代码
new_code = '''    // 【修改点：第1193行之后】检测是否是第二次用户回复（且还在引导环节），如果是则动态生成第三个问题
    if (isGuidingPhase.value && chatHistory.value.filter(m => m.role === 'user').length === 2) {
      // 用户第二次回复（回答第二个问题），提取学历和岗位信息
      let extractedEducation = ''
      let extractedPosition = ''
      
      // 提取学历阶段（大一、大二、大三、大四、研一、研二、研三）
      const educationMatch = userMsg.match(/(大一|大二|大三|大四|研一|研二|研三|研究生|本科生|硕士|博士)/)
      if (educationMatch) {
        extractedEducation = educationMatch[1]
        // 更新 interviewGuide.grade
        if (!interviewGuide.grade) {
          interviewGuide.grade = extractedEducation
        }
      }
      
      // 提取岗位信息（前端、算法、后端、Java、Python、全栈等）
      const positionPatterns = [
        { pattern: /(前端工程师|前端开发|前端)/, name: '前端' },
        { pattern: /(算法工程师|算法|算法开发)/, name: '算法' },
        { pattern: /(后端工程师|后端开发|后端)/, name: '后端' },
        { pattern: /(全栈|全栈开发|全栈工程师)/, name: '全栈' },
        { pattern: /(Java开发|Java工程师|Java)/, name: 'Java开发' },
        { pattern: /(Python开发|Python工程师|Python)/, name: 'Python开发' }
      ]
      
      for (const { pattern, name } of positionPatterns) {
        if (pattern.test(userMsg)) {
          extractedPosition = name
          // 更新 interviewGuide.targetRole
          if (!interviewGuide.targetRole) {
            interviewGuide.targetRole = name + (name.includes('工程师') ? '' : '工程师')
            interviewGuide.templateRole = interviewGuide.targetRole
            interviewGuide.templateStage = interviewGuide.targetRole
          }
          break
        }
      }
      
      // 根据提取的信息动态生成第三个问题
      let thirdQuestion = ''
      let thirdTip = '回答经历类问题时，可以用「一句话概括经历 + 核心做了什么 + 收获了什么」的逻辑，简洁明了哦～'
      
      if (extractedEducation && extractedPosition) {
        // 成功提取学历和岗位，使用模板生成问题
        thirdQuestion = `了解了，${extractedEducation}就开始关注${extractedPosition}岗位，很有规划呀！那你目前在这个方向上有没有接触过一些基础的技术，或者做过什么小练习、小项目呢？`
      } else if (extractedEducation) {
        // 只提取到学历，使用部分模板
        thirdQuestion = `了解了，${extractedEducation}就开始关注这个岗位，很有规划呀！那你目前在这个方向上有没有接触过一些基础的技术，或者做过什么小练习、小项目呢？`
      } else if (extractedPosition) {
        // 只提取到岗位，使用部分模板
        thirdQuestion = `了解了，你关注${extractedPosition}岗位，很有规划呀！那你目前在这个方向上有没有接触过一些基础的技术，或者做过什么小练习、小项目呢？`
      } else {
        // 提取失败，使用兜底问题
        thirdQuestion = '了解了，那你目前在这个方向上有没有接触过一些基础的技术，或者做过什么小练习、小项目呢？'
      }
      
      // 移除加载状态消息（如果存在）
      const loadingIndex = chatHistory.value.findIndex(m => m._isLoading)
      if (loadingIndex !== -1) {
        chatHistory.value.splice(loadingIndex, 1)
      }
      
      // 添加第三个问题到聊天历史
      chatHistory.value.push({
        role: 'ai',
        content: thirdQuestion,
        tip: thirdTip,
        _isGuide: true,
        _isLoading: false,
        _isTemplate: false
      })
      
      // 触发语音播报（不播报tip）
      speakText(thirdQuestion)
      await nextTick()
      scrollChatToBottom()
      
      // 直接返回，不继续处理用户消息的AI回复
      chatSending.value = false
      return
    }
    
'''

# 查找插入位置：在 "return" 和 "// 识别岗位" 之间
pattern = r'(      chatSending\.value = false\s+return\s+\}\s+)\s+// 识别岗位（用于模板匹配）'

# 替换
new_content = re.sub(pattern, r'\1' + new_code + r'    // 识别岗位（用于模板匹配）', content, flags=re.MULTILINE)

# 写回文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("修改完成！")
