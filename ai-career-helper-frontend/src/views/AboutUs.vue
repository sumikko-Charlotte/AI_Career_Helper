<template>
  <el-container style="min-height: 100vh; padding: 30px 20px; max-width: 1200px; margin: 0 auto; background: #f5f7fa;">
    <el-main>
      <!-- 返回按钮 -->
      <el-button type="link" @click="$router.go(-1)" style="margin-bottom: 20px; color: #165DFF;">
        ← 回到上一页
      </el-button>
      <!-- Slogan 图片 -->
      <div style="text-align: center; margin: 20px 0 30px;">
        <img 
          src="/images/slogan-main_深色.png" 
          alt="职航——AI辅助的大学生生涯成长平台" 
          class="slogan-image"
        >
      </div>
      <!-- 关于我们核心内容 -->
      <h1 style="text-align: center; margin: 20px 0 40px; color: #165DFF; font-size: 28px; font-weight: 600;">关于我们</h1>
      
      <h2 id="product-story" style="font-size: 22px; color: #333; font-weight: 600; margin: 30px 0 15px;">产品故事</h2>
      <p style="line-height: 1.8; font-size: 16px; color: #666; margin: 10px 0; text-indent: 2em;">
        「职航」诞生于一群高校学生的课堂讨论。我们发现身边很多同学在面对“未来做什么”这个问题时，往往只有模糊的方向，却缺乏清晰的路径和专业的工具。市面上的职业规划服务要么价格高昂，要么信息零散，于是我们决定自己动手，用技术打造一款真正属于学生的生涯成长平台。
      </p>

      <h2 style="font-size: 22px; color: #333; font-weight: 600; margin: 30px 0 15px;">产品定位</h2>
      <p style="line-height: 1.8; font-size: 16px; color: #666; margin: 10px 0; text-indent: 2em;">
        「职航—AI辅助的大学生生涯成长平台」是专为中国大学生与研究生打造的<strong>一站式生涯发展智能工具</strong>。我们以“技术赋能，职涯领航”为使命，连接校园与职场，让每一位学生都能通过科学的自我认知、精准的能力匹配和持续的成长训练，找到适合自己的职业方向，并平稳过渡到理想的工作岗位。
      </p>

      <h2 style="font-size: 22px; color: #333; font-weight: 600; margin: 30px 0 15px;">核心功能详解</h2>
      <ul style="line-height: 1.8; font-size: 16px; color: #666; margin: 10px 0 10px 20px; list-style: disc;">
        <li><strong>生涯路径规划</strong>：基于霍兰德职业兴趣测试、MBTI性格分析等专业心理模型，结合专业背景、实习经历、技能证书及目标行业人才需求趋势，生成动态更新的《个人生涯发展路线图》，拆解为大一探索期、大二定位期、大三提升期、大四冲刺期四个阶段，配套阶段任务清单与学习资源。</li>
        <li><strong>AI简历医生</strong>：分析超10万份真实简历与HR筛选标准，精准识别简历岗位匹配度不足、经历描述无量纲成果、格式不规范等问题，提供可直接套用的优化话术与同岗位优秀案例，支持多版本简历保存与对比。</li>
        <li><strong>简历模板库</strong>：覆盖互联网、金融、咨询、制造、教育等20+热门行业，包含校招、实习、保研、留学等多场景模板，所有模板经资深HR与名企入职学长学姐审核，支持一键导出Word/PDF格式。</li>
        <li><strong>模拟面试</strong>：模拟大厂压力面、国企结构化面、外企行为面等不同风格场景，AI面试官随机提问，实时识别回答逻辑、表达流畅度与关键词匹配度，面试后生成详细反馈报告，含逐句分析与提升建议，支持录音回放复盘。</li>
        <li><strong>竞争力沙盘</strong>：将个人能力与目标岗位招聘需求多维度拆解匹配，通过雷达图直观展示优势与短板，针对算法能力、项目经验、框架掌握等维度提供针对性学习资源与实践机会推荐。</li>
        <li><strong>虚拟职业体验</strong>：沉浸式体验产品经理、算法工程师、中学教师、投行分析师等热门职业真实工作流程，完成从用户调研、需求分析到落地执行的完整环节，提前验证职业兴趣与适配度。</li>
      </ul>

      <section class="team-section">
        <h2>我们的团队</h2>
        <p>
          我们是来自北京外国语大学、北京邮电大学、北京科技大学、中央财经大学的9名本科生，经分工协作开发出「职航——AI辅助的大学生生涯成长平台」。我们不仅是技术的开发者，更是产品的深度用户——因为我们自己就是正在生涯探索的学生，更懂同龄人的职业困惑与需求。
        </p>
      </section>

      <section class="contact-section">
        <h2>联系我们</h2>
        <p>官方邮箱：2025211995@bupt.cn</p>
        <p>用户反馈：点击提交你的建议</p>
        <p>商务合作：sumikko@bupt.edu.cn</p>
        <p>办公地址：北京市海淀区西土城路10号北京邮电大学</p>
        <p>联系电话：18671211003</p>
      </section>
    </el-main>
  </el-container>
</template>

<script setup>
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const scrollToHash = () => {
  const h = route.hash
  if (h) {
    const id = h.replace('#', '')
    const el = document.getElementById(id)
    if (el) {
      setTimeout(() => el.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50)
    }
  }
}

onMounted(() => scrollToHash())
watch(() => route.hash, () => scrollToHash())
</script>

<style scoped>
/* 统一排版样式，和项目风格适配 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
h1, h2 {
  font-weight: 600;
  letter-spacing: 1px;
}
p {
  text-align: justify;
}
ul li {
  margin: 8px 0;
}
/* Slogan 图片样式 */
.slogan-image {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 auto;
}

/* 适配小屏幕/移动端 */
@media (max-width: 768px) {
  .slogan-image {
    max-width: 90%;
  }
  h1 {
    font-size: 24px !important;
  }
  h2 {
    font-size: 20px !important;
  }
  p, li {
    font-size: 14px !important;
  }
}
</style>