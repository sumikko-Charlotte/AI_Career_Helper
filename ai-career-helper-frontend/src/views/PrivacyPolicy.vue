<template>
  <el-container style="min-height: 100vh; padding: 30px 20px; max-width: 1200px; margin: 0 auto; background: #f5f7fa;">
    <el-main>
      <!-- 返回按钮 -->
      <el-button type="link" @click="$router.go(-1)" style="margin-bottom: 20px; color: #165DFF;">
        ← 回到上一页
      </el-button>
      <!-- 隐私政策核心内容 -->
      <h1 id="privacy-intro" style="text-align: center; margin: 20px 0 40px; color: #165DFF; font-size: 28px; font-weight: 600;">隐私政策</h1>
      <p style="text-align: center; line-height: 1.8; font-size: 14px; color: #999; margin: 0 0 30px;">
        <strong>更新日期</strong>：2025年11月1日&nbsp;&nbsp;&nbsp;&nbsp;<strong>生效日期</strong>：2025年11月1日
      </p>

      <h2 style="font-size: 22px; color: #333; font-weight: 600; margin: 30px 0 15px;">一、引言</h2>
      <p style="line-height: 1.8; font-size: 16px; color: #666; margin: 10px 0; text-indent: 2em;">
        「职航—AI辅助的大学生生涯成长平台」（以下简称“本平台”或“我们”）深知个人信息对您的重要性，并会尽全力保护您的个人信息安全与隐私权益。本政策将向您说明我们如何收集、使用、存储和保护您的信息，以及您享有的相关权利。请您在使用本平台前，仔细阅读并理解本政策；若您继续使用本平台，即表示您已同意本政策的全部内容。
      </p>

      <h2 style="font-size: 22px; color: #333; font-weight: 600; margin: 30px 0 15px;">二、我们收集的信息</h2>
      <h3 style="font-size: 18px; color: #333; font-weight: 600; margin: 20px 0 10px; margin-left: 10px;">2.1 您主动提供的信息</h3>
      <ul style="line-height: 1.8; font-size: 16px; color: #666; margin: 10px 0 10px 30px; list-style: disc;">
        <li><strong>账户信息</strong>：您在注册时提供的手机号、邮箱地址和密码，用于账户验证、安全登录和密码找回，是使用本平台基础服务的前提。</li>
        <li><strong>个人资料</strong>：您在完善个人信息时填写的姓名、性别、出生日期、所在院校、专业、年级、求职意向、期望城市等信息，是我们为您提供精准生涯规划、岗位匹配的核心依据。</li>
        <li><strong>上传内容</strong>：您上传的简历、自我介绍视频、面试录音等内容，仅用于本平台AI分析和对应服务提供，不会用于其他任何商业或非商业用途。</li>
        <li><strong>反馈信息</strong>：您通过客服、问卷、留言板等方式向我们提供的反馈、建议或投诉信息，用于帮助我们迭代优化产品功能和服务体验。</li>
      </ul>

      <h3 style="font-size: 18px; color: #333; font-weight: 600; margin: 20px 0 10px; margin-left: 10px;">2.2 我们自动收集的信息</h3>
      <ul style="line-height: 1.8; font-size: 16px; color: #666; margin: 10px 0 10px 30px; list-style: disc;">
        <li><strong>使用行为数据</strong>：您使用本平台时的操作记录，包括访问的页面、使用的功能、停留时间、偏好设置、点击行为等，用于优化产品体验、提升算法准确性和提供个性化内容推荐。</li>
        <li><strong>设备与技术信息</strong>：包括您的IP地址、浏览器类型、操作系统、设备型号、唯一设备标识符、网络状态等，用于保障平台服务器安全、排查技术故障和防范恶意攻击行为。</li>
      </ul>

      <h2 style="font-size: 22px; color: #333; font-weight: 600; margin: 30px 0 15px;">三、我们如何使用您的信息</h2>
      <ul style="line-height: 1.8; font-size: 16px; color: #666; margin: 10px 0 10px 30px; list-style: disc;">
        <li>为您提供、维护和优化生涯规划、简历优化、模拟面试等核心服务，保障平台正常运行；</li>
        <li>基于您的个人资料和使用行为数据，为您提供个性化的职业匹配、成长建议和内容推荐；</li>
        <li>分析用户整体行为和反馈，不断迭代产品功能、优化交互设计，提升整体用户体验；</li>
        <li>防范和打击欺诈、账号滥用、恶意攻击等违规行为，保护您和其他平台用户的合法权益；</li>
        <li>遵守适用的法律法规，向您发送重要通知，如服务版本更新、功能调整、安全风险提醒等。</li>
      </ul>

      <h2 style="font-size: 22px; color: #333; font-weight: 600; margin: 30px 0 15px;">四、信息的共享与披露</h2>
      <p style="line-height: 1.8; font-size: 16px; color: #666; margin: 10px 0; text-indent: 2em;">
        我们非常重视您的隐私，<strong style="color: #e64340;">绝不会向任何第三方出售、出租或交换您的个人信息</strong>。仅在以下有限情况下，我们可能会与第三方共享您的信息：
      </p>
      <ul style="line-height: 1.8; font-size: 16px; color: #666; margin: 10px 0 10px 30px; list-style: disc;">
        <li><strong>经您明确同意</strong>：在您主动授权的情况下，我们可能会与您指定的第三方共享特定信息，例如将您的优化后简历推荐给合作企业；</li>
        <li><strong>法律法规要求</strong>：为遵守适用的法律法规、法院判决、政府命令或其他法定法律程序，我们可能会依法披露您的相关信息；</li>
        <li><strong>合规服务提供商</strong>：我们可能会与协助提供服务的第三方合作（如云服务器提供商、邮件服务商、数据加密服务商），此类服务商仅能在为我们提供服务的范围内使用您的信息，并需遵守严格的保密义务；</li>
        <li><strong>业务合理转让</strong>：如果我们发生合并、收购、资产出售或其他类似合法交易，您的信息可能会作为业务资产的一部分被转让给新的合法所有者，且新所有者将继续遵守本隐私政策。</li>
      </ul>

      <h2 style="font-size: 22px; color: #333; font-weight: 600; margin: 30px 0 15px;">五、信息存储与安全</h2>
      <h3 style="font-size: 18px; color: #333; font-weight: 600; margin: 20px 0 10px; margin-left: 10px;">5.1 存储地点与期限</h3>
      <p style="line-height: 1.8; font-size: 16px; color: #666; margin: 10px 0; text-indent: 2em;">
        您的个人信息将统一存储在中国大陆境内的阿里云合规服务器上，符合中国法律法规对数据存储的地域要求；在您的账户存续期间，我们会持续保存您的信息以提供服务，若您注销账户，我们将在15个工作日内对您的个人信息进行匿名化处理或安全删除，无法再识别到您的个人身份。
      </p>
      <h3 style="font-size: 18px; color: #333; font-weight: 600; margin: 20px 0 10px; margin-left: 10px;">5.2 安全保护措施</h3>
      <p style="line-height: 1.8; font-size: 16px; color: #666; margin: 10px 0; text-indent: 2em;">
        我们采用行业领先的安全技术保障数据安全，包括传输加密、存储加密、访问权限控制、安全审计、漏洞定期扫描等；同时对团队成员进行严格的信息安全培训与管理，建立权限分级制度，确保只有经授权的工作人员才能接触您的个人信息，且接触行为会被全程记录审计。
      </p>

      <h2 style="font-size: 22px; color: #333; font-weight: 600; margin: 30px 0 15px;">六、您的权利</h2>
      <ul style="line-height: 1.8; font-size: 16px; color: #666; margin: 10px 0 10px 30px; list-style: disc;">
        <li><strong>访问与修改权</strong>：您可在平台个人中心随时查看、修改、补充或完善您的所有个人信息；</li>
        <li><strong>信息删除权</strong>：在符合法律法规的前提下，您可向我们申请删除特定的个人信息或上传内容；</li>
        <li><strong>账户注销权</strong>：您可在个人中心自主申请注销账户，账户注销后将按本政策约定处理您的信息；</li>
        <li><strong>数据导出权</strong>：您可申请导出在本平台的个人数据，包括简历、生涯报告、测试结果等；</li>
        <li><strong>撤回同意权</strong>：您可通过关闭功能权限的方式撤回信息收集与使用的同意，若撤回可能会影响您使用平台的部分个性化功能，但不影响基础服务使用。</li>
      </ul>

      <h2 style="font-size: 22px; color: #333; font-weight: 600; margin: 30px 0 15px;">七、未成年人保护</h2>
      <p style="line-height: 1.8; font-size: 16px; color: #666; margin: 10px 0; text-indent: 2em;">
        本平台主要服务对象为年满18周岁的大学生和研究生，若您是未满18周岁的未成年人，需在监护人的指导下阅读本政策并使用本平台服务，我们不会在明知的情况下收集、使用未成年人的个人信息；若监护人发现我们无意收集了未成年人信息，可联系我们申请删除，我们将立即处理。
      </p>

      <h2 style="font-size: 22px; color: #333; font-weight: 600; margin: 30px 0 15px;">八、政策更新</h2>
      <p style="line-height: 1.8; font-size: 16px; color: #666; margin: 10px 0; text-indent: 2em;">
        我们可能会根据产品功能迭代、法律法规更新或用户反馈，不定期优化本隐私政策。更新后的政策将在本平台首页显著位置公示，公示满7日后正式生效；若您在政策更新后继续使用本平台，即表示您已阅读并同意接受更新后的政策内容。
      </p>

      <h2 style="font-size: 22px; color: #333; font-weight: 600; margin: 30px 0 15px;">九、联系方式</h2>
      <p style="line-height: 1.8; font-size: 16px; color: #666; margin: 10px 0;">
        若您对本隐私政策有任何疑问、意见或建议，或需要行使个人信息相关权利，可通过以下方式与我们联系，我们将在7个工作日内回复您的诉求：<br>
        官方邮箱：2025211995@bupt.cn<br>
        商务合作：sumikko@bupt.edu.cn<br>
        联系电话：18671211003
      </p>
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
/* 统一排版样式，和关于我们页面保持一致 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
h1, h2, h3 {
  font-weight: 600;
  letter-spacing: 1px;
}
p {
  text-align: justify;
}
ul li {
  margin: 8px 0;
}
/* 移动端适配 */
@media (max-width: 768px) {
  h1 {
    font-size: 24px !important;
  }
  h2 {
    font-size: 20px !important;
  }
  h3 {
    font-size: 16px !important;
  }
  p, li {
    font-size: 14px !important;
  }
}
</style>