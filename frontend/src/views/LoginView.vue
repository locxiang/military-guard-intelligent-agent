<template>
  <div class="military-login-container">
    <!-- 深邃海军蓝背景 - 多层渐变 -->
    <div class="military-background">
      <div class="military-bg-gradient"></div>
      <div class="military-grid-overlay"></div>
      <div class="military-scan-line"></div>
      <canvas ref="particleCanvas" class="military-particles"></canvas>
    </div>

    <!-- 顶部安全标识栏 -->
    <div class="military-top-bar">
      <div class="military-classification">
        <div class="classification-badge">
          <div class="badge-icon">
            <img :src="logoImage" alt="Logo" class="badge-logo-image" />
          </div>
          <div class="badge-text">
            <span class="classification-level">保卫核心业务智能体平台</span>
            <span class="classification-code">等保二级 · 军事级加密</span>
          </div>
        </div>
      </div>
      <div class="military-system-status">
        <div class="status-indicator active"></div>
        <span class="status-text">系统安全运行中</span>
      </div>
    </div>

    <!-- 政务水印 - 更低调 -->
    <Watermark 
      :text="'军事级保密系统 严禁外泄'"
      :font-size="12"
      :font-color="'#1E40AF'"
      :opacity="0.08"
      :rotate="-45"
      :gap="300"
    />

    <!-- 主内容区 -->
    <div class="military-content-wrapper">
      <div class="military-content-grid">
        
        <!-- 左侧：品牌与安全标识 -->
        <div class="military-brand-section">
          <!-- 品牌标题 -->
          <div class="military-brand-header">
            <div class="military-brand-title">
              <h1 class="brand-main-title">保卫核心业务智能体平台</h1>
              <div class="brand-subtitle-line"></div>
              <p class="brand-subtitle">Military Guard Intelligence System</p>
            </div>
          </div>

          <!-- 主标语 -->
          <div class="military-hero-text">
            <h2 class="hero-title">
              <span class="hero-title-line">数字化案卷管理</span>
              <span class="hero-title-line">智能文档生成平台</span>
            </h2>
            <p class="hero-description">
              基于AI技术的军事级数字案卷管理系统，采用端到端加密传输，
              符合等保二级标准，为军队保卫工作提供全方位智能化支持。
            </p>
          </div>

          <!-- 核心安全特性 - HUD风格 -->
          <div class="military-features-grid">
            <div 
              v-for="(feature, index) in securityFeatures" 
              :key="index"
              class="military-feature-card"
              :style="{ animationDelay: `${index * 100}ms` }"
            >
              <div class="feature-icon-wrapper">
                <div class="feature-icon-glow"></div>
                <component :is="feature.icon" class="feature-icon" />
              </div>
              <div class="feature-content">
                <h3 class="feature-title">{{ feature.title }}</h3>
                <p class="feature-desc">{{ feature.desc }}</p>
              </div>
              <div class="feature-border"></div>
            </div>
          </div>
        </div>

        <!-- 右侧：登录表单 - 高端质感 -->
        <div class="military-form-section">
          <div class="military-form-container">
            <!-- 顶部装饰光带 -->
            <div class="form-top-glow"></div>
            
            <!-- 表单卡片 -->
            <div class="military-form-card">
              <!-- 表单头部 - Logo与标题横排布局 -->
              <div class="military-form-header">
                <div class="form-logo-container">
                  <div class="form-logo-glow"></div>
                  <img :src="logoImage" alt="系统Logo" class="form-logo-image" />
                </div>
                <div class="form-header-text">
                  <h2 class="form-title">安全登录验证</h2>
                  <p class="form-subtitle">请输入您的凭证以访问系统</p>
                </div>
              </div>

              <!-- 登录表单 -->
              <el-form
                ref="loginFormRef"
                :model="loginForm"
                :rules="loginRules"
                label-width="0"
                autocomplete="off"
                @submit.prevent="handleLogin"
                class="military-login-form"
              >
                <!-- 用户名 -->
                <el-form-item prop="username" class="military-form-item">
                  <div class="military-form-label">
                    <span class="label-text">用户名</span>
                    <el-tooltip
                      content="请输入系统管理员分配的用户名。用户名区分大小写，通常为您的工号或专用代码"
                      placement="top"
                      :show-after="200"
                    >
                      <el-icon class="label-help-icon">
                        <InfoFilled />
                      </el-icon>
                    </el-tooltip>
                  </div>
                  <div class="military-input-wrapper">
                    <div class="input-icon">
                      <el-icon :size="20">
                        <User />
                      </el-icon>
                    </div>
                    <el-input
                      v-model="loginForm.username"
                      placeholder="请输入用户名"
                      size="large"
                      class="military-input"
                      clearable
                      autocomplete="off"
                      @keyup.enter="handleLogin"
                      @input="loginError = ''"
                    />
                    <div class="input-focus-border"></div>
                  </div>
                </el-form-item>

                <!-- 密码 -->
                <el-form-item prop="password" class="military-form-item">
                  <div class="military-form-label">
                    <span class="label-text">登录密码</span>
                    <el-tooltip
                      content="密码采用RSA-2048加密传输，请妥善保管。建议定期更换密码并包含大小写字母、数字及特殊字符"
                      placement="top"
                      :show-after="200"
                    >
                      <el-icon class="label-help-icon">
                        <InfoFilled />
                      </el-icon>
                    </el-tooltip>
                  </div>
                  <div class="military-input-wrapper">
                    <div class="input-icon">
                      <el-icon :size="20">
                        <Lock />
                      </el-icon>
                    </div>
                    <el-input
                      v-model="loginForm.password"
                      type="password"
                      placeholder="请输入登录密码"
                      size="large"
                      class="military-input"
                      show-password
                      clearable
                      autocomplete="new-password"
                      @keyup.enter="handleLogin"
                      @input="loginError = ''"
                    />
                    <div class="input-focus-border"></div>
                  </div>
                </el-form-item>

                <!-- 选项 -->
                <el-form-item class="military-form-options">
                  <div class="options-wrapper">
                    <div class="remember-me-wrapper">
                      <el-checkbox v-model="rememberMe" class="military-checkbox">
                        <span class="checkbox-label">记住登录状态</span>
                      </el-checkbox>
                      <el-tooltip
                        content="勾选后将在本设备保存登录状态。建议仅在个人专用设备上使用，公共设备请勿勾选"
                        placement="top"
                        :show-after="200"
                      >
                        <el-icon class="checkbox-help-icon">
                          <InfoFilled />
                        </el-icon>
                      </el-tooltip>
                    </div>
                    <el-link :underline="false" class="forgot-link">
                      忘记密码？
                    </el-link>
                  </div>
                </el-form-item>

                <!-- 错误提示 -->
                <transition name="error-fade">
                  <el-form-item v-if="loginError" class="military-error-item">
                    <div class="military-error-box">
                      <el-icon :size="18" class="error-icon">
                        <Warning />
                      </el-icon>
                      <span class="error-text">{{ loginError }}</span>
                      <el-icon 
                        :size="16" 
                        class="error-close"
                        @click="loginError = ''"
                      >
                        <Close />
                      </el-icon>
                    </div>
                  </el-form-item>
                </transition>

                <!-- 登录按钮 -->
                <el-form-item class="military-button-item">
                  <button
                    type="button"
                    class="military-login-button"
                    :class="{ 'is-loading': loading }"
                    :disabled="loading"
                    @click="handleLogin"
                  >
                    <span v-if="!loading" class="button-content">
                      <svg class="button-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M13.8 12H3"/>
                      </svg>
                      <span class="button-text">确认登录</span>
                    </span>
                    <span v-else class="button-loading">
                      <span class="loading-spinner"></span>
                      <span class="button-text">正在验证身份...</span>
                    </span>
                    <div class="button-glow"></div>
                  </button>
                </el-form-item>
              </el-form>

              <!-- 表单底部 -->
              <div class="military-form-footer">
                <div class="footer-warning">
                  <el-icon :size="16" class="warning-icon">
                    <Lock />
                  </el-icon>
                  <span class="warning-text">系统仅供授权人员使用，所有操作将被记录</span>
                </div>
                <div class="footer-security-badges">
                  <div class="security-badge">
                    <svg class="badge-icon-small" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z"/>
                    </svg>
                    <span>端到端加密</span>
                  </div>
                  <div class="security-badge">
                    <svg class="badge-icon-small" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                    </svg>
                    <span>操作审计</span>
                  </div>
                  <div class="security-badge">
                    <svg class="badge-icon-small" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2z"/>
                    </svg>
                    <span>多因素认证</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部系统信息 -->
    <div class="military-bottom-bar">
      <div class="bottom-info">
        <span class="system-version">版本 v2.1.0</span>
        <span class="system-separator">|</span>
        <span class="system-copyright">© 2026 军事保卫智能系统 · 保留所有权利</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock, Document, Search, Tools, Warning, Close, InfoFilled } from '@element-plus/icons-vue'
import { authApi } from '@/api/auth'
import { encryptPassword } from '@/utils/rsa'
import { RSA_PUBLIC_KEY } from '@/config/rsaPublicKey'
import Watermark from '@/components/Watermark.vue'
import logoImage from '@/assets/logo.png'

const router = useRouter()

// 表单引用
const loginFormRef = ref<FormInstance>()
const particleCanvas = ref<HTMLCanvasElement>()

// 表单数据
const loginForm = reactive({
  username: '',
  password: ''
})

// 记住我
const rememberMe = ref(false)

// 加载状态
const loading = ref(false)

// 登录错误
const loginError = ref('')

// 记住用户名的 localStorage key
const REMEMBERED_USERNAME_KEY = 'remembered_username'

// 安全特性
const securityFeatures = [
  {
    title: '智能归档',
    desc: 'AI驱动的案卷管理',
    icon: Document
  },
  {
    title: '全文检索',
    desc: '毫秒级快速搜索',
    icon: Search
  },
  {
    title: '自动生成',
    desc: '智能文档生成引擎',
    icon: Tools
  },
  {
    title: '安全防护',
    desc: '军事级加密保护',
    icon: Lock
  }
]

// 表单验证规则
const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为 3 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 100, message: '密码长度为 6 到 100 个字符', trigger: 'blur' }
  ]
}

// 粒子动画
let animationFrameId: number | null = null

const initParticles = () => {
  const canvas = particleCanvas.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  canvas.width = window.innerWidth
  canvas.height = window.innerHeight

  const particles: Array<{
    x: number
    y: number
    size: number
    speedX: number
    speedY: number
    opacity: number
  }> = []

  // 创建粒子
  for (let i = 0; i < 80; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      size: Math.random() * 2 + 0.5,
      speedX: (Math.random() - 0.5) * 0.3,
      speedY: (Math.random() - 0.5) * 0.3,
      opacity: Math.random() * 0.5 + 0.2
    })
  }

  const animate = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    particles.forEach((particle, i) => {
      // 更新位置
      particle.x += particle.speedX
      particle.y += particle.speedY

      // 边界检测
      if (particle.x < 0 || particle.x > canvas.width) particle.speedX *= -1
      if (particle.y < 0 || particle.y > canvas.height) particle.speedY *= -1

      // 绘制粒子
      ctx.beginPath()
      ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(59, 130, 246, ${particle.opacity})`
      ctx.fill()

      // 连接附近的粒子
      particles.forEach((otherParticle, j) => {
        if (i === j) return
        const dx = particle.x - otherParticle.x
        const dy = particle.y - otherParticle.y
        const distance = Math.sqrt(dx * dx + dy * dy)

        if (distance < 120) {
          ctx.beginPath()
          ctx.moveTo(particle.x, particle.y)
          ctx.lineTo(otherParticle.x, otherParticle.y)
          ctx.strokeStyle = `rgba(59, 130, 246, ${0.15 * (1 - distance / 120)})`
          ctx.lineWidth = 0.5
          ctx.stroke()
        }
      })
    })

    animationFrameId = requestAnimationFrame(animate)
  }

  animate()
}

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return

  loginError.value = ''

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const encryptedPassword = encryptPassword(loginForm.password, RSA_PUBLIC_KEY)
        
        const response = await authApi.login({
          username: loginForm.username,
          password: encryptedPassword,
          encrypted: true
        })
        
        // 保存用户信息
        const userInfo = {
          id: response.user.id,
          username: response.user.username,
          realName: response.user.realName,
          role: response.user.role
        }
        
        if (rememberMe.value) {
          localStorage.setItem('token', response.token)
          localStorage.setItem('userInfo', JSON.stringify(userInfo))
          localStorage.setItem(REMEMBERED_USERNAME_KEY, loginForm.username)
        } else {
          sessionStorage.setItem('token', response.token)
          sessionStorage.setItem('userInfo', JSON.stringify(userInfo))
          localStorage.removeItem(REMEMBERED_USERNAME_KEY)
        }

        ElMessage.success('登录成功')
        router.push('/dashboard')
      } catch (error: any) {
        let errorMessage = '登录失败，请检查用户名和密码'
        
        if (error?.response) {
          const responseData = error.response.data
          if (responseData?.message) {
            errorMessage = responseData.message
          } else if (responseData?.detail) {
            errorMessage = typeof responseData.detail === 'string' 
              ? responseData.detail 
              : responseData.detail.message || errorMessage
          } else if (error?.message) {
            errorMessage = error.message
          }
        } else if (error?.message) {
          errorMessage = error.message
        }
        
        loginError.value = errorMessage
        ElMessage.error(errorMessage)
      } finally {
        loading.value = false
      }
    }
  })
}

onMounted(() => {
  const rememberedUsername = localStorage.getItem(REMEMBERED_USERNAME_KEY)
  if (rememberedUsername) {
    loginForm.username = rememberedUsername
    rememberMe.value = true
  }

  initParticles()

  window.addEventListener('resize', () => {
    if (particleCanvas.value) {
      particleCanvas.value.width = window.innerWidth
      particleCanvas.value.height = window.innerHeight
    }
  })
})

onUnmounted(() => {
  if (animationFrameId !== null) {
    cancelAnimationFrame(animationFrameId)
  }
})
</script>

<style scoped>
/* ==================== 基础样式 ==================== */
.military-login-container {
  position: relative;
  min-height: 100vh;
  width: 100%;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}

/* ==================== 背景系统 ==================== */
.military-background {
  position: fixed;
  inset: 0;
  z-index: 0;
}

.military-bg-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #0A1628 0%, #1E3A8A 50%, #0F172A 100%);
}

.military-grid-overlay {
  position: absolute;
  inset: 0;
  background-image: 
    linear-gradient(rgba(59, 130, 246, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59, 130, 246, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  background-position: -1px -1px;
}

.military-scan-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent 0%, 
    rgba(59, 130, 246, 0.4) 25%,
    rgba(59, 130, 246, 0.8) 50%,
    rgba(59, 130, 246, 0.4) 75%,
    transparent 100%
  );
  animation: scan 8s linear infinite;
}

@keyframes scan {
  0% { transform: translateY(0); opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { transform: translateY(100vh); opacity: 0; }
}

.military-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

/* ==================== 顶部栏 ==================== */
.military-top-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: rgba(10, 22, 40, 0.7);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(59, 130, 246, 0.2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  z-index: 100;
}

.classification-badge {
  display: flex;
  align-items: center;
  gap: 12px;
}

.badge-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.badge-logo-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 2px 4px rgba(59, 130, 246, 0.3));
}

.badge-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.classification-level {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 1px;
}

.classification-code {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 0.5px;
}

.military-system-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10B981;
  box-shadow: 0 0 12px rgba(16, 185, 129, 0.8);
  animation: pulse-status 2s ease-in-out infinite;
}

@keyframes pulse-status {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.status-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

/* ==================== 主内容区 ==================== */
.military-content-wrapper {
  position: relative;
  z-index: 10;
  min-height: 100vh;
  display: flex;
  align-items: center;
  padding: 80px 32px 80px;
}

.military-content-grid {
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
  align-items: center;
}

/* ==================== 左侧品牌区 ==================== */
.military-brand-section {
  display: flex;
  flex-direction: column;
  gap: 48px;
}

/* 品牌标题区 */
.military-brand-header {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.military-brand-title {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.brand-main-title {
  font-size: 28px;
  font-weight: 800;
  color: #fff;
  line-height: 1.3;
  letter-spacing: 1px;
  margin: 0;
}

.brand-subtitle-line {
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #3B82F6, transparent);
}

.brand-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 2px;
  text-transform: uppercase;
  font-weight: 600;
  margin: 0;
}

/* Hero文本 */
.military-hero-text {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.hero-title {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin: 0;
}

.hero-title-line {
  font-size: 36px;
  font-weight: 800;
  background: linear-gradient(135deg, #fff 0%, rgba(255, 255, 255, 0.7) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.2;
}

.hero-description {
  font-size: 15px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

/* 特性网格 */
.military-features-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.military-feature-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(30, 58, 138, 0.2);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  animation: feature-fade-in 0.6s ease-out backwards;
}

@keyframes feature-fade-in {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.military-feature-card:hover {
  background: rgba(30, 58, 138, 0.3);
  border-color: rgba(59, 130, 246, 0.5);
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(59, 130, 246, 0.2);
}

.feature-icon-wrapper {
  position: relative;
  width: 48px;
  height: 48px;
  flex-shrink: 0;
}

.feature-icon-glow {
  position: absolute;
  inset: -4px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.4) 0%, transparent 70%);
  filter: blur(8px);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.military-feature-card:hover .feature-icon-glow {
  opacity: 1;
}

.feature-icon {
  position: relative;
  width: 48px;
  height: 48px;
  padding: 12px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 10px;
  color: #3B82F6;
}

.feature-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.feature-title {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.feature-desc {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.feature-border {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #3B82F6, transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.military-feature-card:hover .feature-border {
  opacity: 1;
}


/* ==================== 右侧表单区 ==================== */
.military-form-section {
  display: flex;
  justify-content: center;
}

.military-form-container {
  position: relative;
  width: 100%;
  max-width: 540px;
}

.form-top-glow {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #3B82F6, transparent);
  filter: blur(4px);
}

.military-form-card {
  position: relative;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 24px;
  padding: 48px 32px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

/* 表单头部 - 横排居中布局 */
.military-form-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(59, 130, 246, 0.15);
}

.form-header-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: left;
}

/* 表单Logo容器 - 横排布局 */
.form-logo-container {
  position: relative;
  width: 72px;
  height: 72px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-logo-glow {
  position: absolute;
  inset: -16px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.25) 0%, transparent 70%);
  filter: blur(12px);
  animation: logo-pulse 3s ease-in-out infinite;
}

@keyframes logo-pulse {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.05); }
}

.form-logo-image {
  position: relative;
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 4px 12px rgba(59, 130, 246, 0.5));
  z-index: 2;
  transition: transform 0.3s ease;
}

.form-logo-container:hover .form-logo-image {
  transform: scale(1.05);
}

.form-title {
  font-size: 22px;
  font-weight: 800;
  color: #fff;
  margin: 0;
  letter-spacing: 0.5px;
  line-height: 1.3;
}

.form-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}

/* 表单样式 */
.military-login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.military-form-item {
  margin: 0;
  width: 100%;
}

.military-form-item :deep(.el-form-item__content) {
  width: 100%;
}

.military-form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.label-text {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  letter-spacing: 0.3px;
}

.label-help-icon {
  font-size: 15px;
  color: rgba(59, 130, 246, 0.5);
  cursor: help;
  transition: all 0.2s ease;
}

.label-help-icon:hover {
  color: #3B82F6;
  transform: scale(1.1);
}

/* 输入框 */
.military-input-wrapper {
  position: relative;
  width: 100%;
}

.input-icon {
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  color: rgba(255, 255, 255, 0.4);
  pointer-events: none;
  transition: color 0.3s ease;
}

.military-input {
  width: 100%;
}

.military-input :deep(.el-input__wrapper) {
  width: 100%;
  height: 52px;
  padding-left: 52px;
  padding-right: 16px;
  background: rgba(30, 58, 138, 0.15);
  border: 2px solid rgba(59, 130, 246, 0.2);
  border-radius: 12px;
  box-shadow: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.military-input :deep(.el-input__wrapper:hover) {
  background: rgba(30, 58, 138, 0.25);
  border-color: rgba(59, 130, 246, 0.4);
}

.military-input :deep(.el-input__wrapper.is-focus) {
  background: rgba(30, 58, 138, 0.3);
  border-color: #3B82F6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
}

.military-input :deep(.el-input__wrapper.is-focus) ~ .input-icon {
  color: #3B82F6;
}

.military-input :deep(.el-input__inner) {
  color: #fff;
  font-size: 15px;
  font-weight: 500;
}

.military-input :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.3);
  font-size: 14px;
}

.input-focus-border {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #3B82F6, transparent);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.military-input :deep(.el-input__wrapper.is-focus) + .input-focus-border {
  transform: scaleX(1);
}

/* 选项 */
.military-form-options {
  margin: 0;
}

.options-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.remember-me-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
}

.military-checkbox :deep(.el-checkbox__label) {
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  font-weight: 500;
}

.checkbox-label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  font-weight: 500;
}

.military-checkbox :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background: #3B82F6;
  border-color: #3B82F6;
}

.military-checkbox :deep(.el-checkbox__inner) {
  border-color: rgba(59, 130, 246, 0.4);
  border-width: 2px;
}

.checkbox-help-icon {
  font-size: 14px;
  color: rgba(59, 130, 246, 0.5);
  cursor: help;
  transition: all 0.2s ease;
}

.checkbox-help-icon:hover {
  color: #3B82F6;
  transform: scale(1.1);
}

.forgot-link {
  font-size: 13px;
  color: #3B82F6;
  font-weight: 600;
  transition: color 0.2s ease;
}

.forgot-link:hover {
  color: #60A5FA;
}

/* 错误提示 */
.military-error-item {
  margin: 0;
}

.military-error-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: rgba(220, 38, 38, 0.1);
  border: 1px solid rgba(220, 38, 38, 0.3);
  border-radius: 10px;
  backdrop-filter: blur(8px);
}

.error-icon {
  color: #EF4444;
  flex-shrink: 0;
}

.error-text {
  flex: 1;
  font-size: 13px;
  color: #FCA5A5;
  font-weight: 500;
}

.error-close {
  color: #FCA5A5;
  cursor: pointer;
  transition: color 0.2s ease;
  flex-shrink: 0;
}

.error-close:hover {
  color: #EF4444;
}

.error-fade-enter-active,
.error-fade-leave-active {
  transition: all 0.3s ease;
}

.error-fade-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.error-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 登录按钮 */
.military-button-item {
  margin: 8px 0 0 0;
}

.military-login-button {
  position: relative;
  width: 100%;
  height: 56px;
  background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%);
  border: 2px solid transparent;
  border-radius: 12px;
  color: #fff;
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
}

.military-login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(59, 130, 246, 0.4);
}

.military-login-button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.3);
}

.military-login-button:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.button-content,
.button-loading {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.button-icon {
  width: 20px;
  height: 20px;
}

.button-text {
  font-size: 16px;
  font-weight: 700;
}

.button-glow {
  position: absolute;
  inset: -2px;
  background: linear-gradient(135deg, #60A5FA, #3B82F6);
  filter: blur(16px);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.military-login-button:hover:not(:disabled) .button-glow {
  opacity: 0.6;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 表单底部 */
.military-form-footer {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(59, 130, 246, 0.15);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.footer-warning {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 500;
}

.warning-icon {
  color: #3B82F6;
}

.footer-security-badges {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.security-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 600;
}

.badge-icon-small {
  width: 14px;
  height: 14px;
  color: #3B82F6;
}

/* ==================== 底部栏 ==================== */
.military-bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 50px;
  background: rgba(10, 22, 40, 0.7);
  backdrop-filter: blur(12px);
  border-top: 1px solid rgba(59, 130, 246, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.bottom-info {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.system-separator {
  color: rgba(255, 255, 255, 0.2);
}

/* ==================== 响应式设计 ==================== */
@media (max-width: 1200px) {
  .military-content-grid {
    gap: 60px;
  }
  
  .hero-title-line {
    font-size: 32px;
  }
}

@media (max-width: 1024px) {
  .military-content-grid {
    grid-template-columns: 1fr;
    gap: 48px;
    padding: 40px 0;
  }
  
  .military-brand-section {
    text-align: center;
    align-items: center;
  }
  
  .military-logo-container {
    margin: 0 auto;
  }
  
  .military-features-grid {
    max-width: 600px;
  }
}

@media (max-width: 768px) {
  .military-top-bar {
    padding: 0 20px;
  }
  
  .classification-level {
    font-size: 12px;
  }
  
  .classification-code {
    font-size: 10px;
  }
  
  .military-content-wrapper {
    padding: 80px 20px;
  }
  
  .military-features-grid {
    grid-template-columns: 1fr;
  }
  
  .military-form-card {
    padding: 36px 24px;
  }
  
  .hero-title-line {
    font-size: 28px;
  }
}

@media (max-width: 640px) {
  .badge-text {
    display: none;
  }
  
  .military-form-card {
    padding: 32px 20px;
  }
  
  .form-logo-container {
    width: 60px;
    height: 60px;
  }
  
  .form-title {
    font-size: 18px;
  }
  
  .form-subtitle {
    font-size: 12px;
  }
}

/* ==================== 无障碍与性能 ==================== */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* 浏览器自动填充样式覆盖 */
.military-input :deep(input:-webkit-autofill),
.military-input :deep(input:-webkit-autofill:hover),
.military-input :deep(input:-webkit-autofill:focus) {
  -webkit-box-shadow: 0 0 0 1000px rgba(30, 58, 138, 0.3) inset !important;
  -webkit-text-fill-color: #fff !important;
  caret-color: #fff !important;
}
</style>
