<template>
  <view class="copywriting-page">
    <!-- 顶部标题栏 -->
    <view class="page-header">
      <view class="header-left" @tap="goBack">
        <text class="back-icon">←</text>
      </view>
      <view class="header-center">
        <text class="header-title">AI 文案生成</text>
        <!-- 当前项目指示器 -->
        <view class="project-indicator" v-if="activeProject" @tap="goToProjectDashboard">
          <view class="indicator-dot" :style="{ background: activeProject.avatar_color }"></view>
          <text class="indicator-name">{{ activeProject.name }}</text>
        </view>
      </view>
      <view class="header-right">
        <view class="model-badge" @tap="showModelInfo">
          <text class="model-icon">{{ currentModel.icon }}</text>
          <text class="model-name">{{ currentModel.name }}</text>
        </view>
      </view>
    </view>

    <!-- 主体内容区 -->
    <scroll-view class="main-content" scroll-y :scroll-into-view="scrollIntoView">
      <!-- 风格选择 -->
      <view class="style-section">
        <view class="section-title">
          <text class="title-text">选择文案风格</text>
        </view>
        <view class="style-grid">
          <view 
            v-for="(style, index) in styleList" 
            :key="index"
            class="style-item"
            :class="{ active: selectedStyle === style.value }"
            @tap="selectedStyle = style.value"
          >
            <text class="style-icon">{{ style.icon }}</text>
            <text class="style-label">{{ style.label }}</text>
          </view>
        </view>
      </view>

      <!-- 输入区域 -->
      <view class="input-section">
        <view class="section-title">
          <text class="title-text">输入文案主题</text>
          <text class="title-hint">描述越详细，生成效果越好</text>
        </view>
        <view class="input-wrapper">
          <textarea 
            v-model="inputTopic"
            class="topic-input"
            :placeholder="placeholderText"
            :maxlength="500"
            :auto-height="true"
            :show-confirm-bar="false"
          />
          <view class="input-footer">
            <text class="char-count">{{ inputTopic.length }}/500</text>
          </view>
        </view>
      </view>

      <!-- 高级设置 -->
      <view class="advanced-section" v-if="showAdvanced">
        <view class="section-title">
          <text class="title-text">高级设置</text>
        </view>
        <view class="setting-item">
          <text class="setting-label">文案长度</text>
          <view class="setting-options">
            <view 
              v-for="(len, idx) in lengthOptions" 
              :key="idx"
              class="option-tag"
              :class="{ active: maxTokens === len.value }"
              @tap="maxTokens = len.value"
            >
              {{ len.label }}
            </view>
          </view>
        </view>
        <view class="setting-item">
          <text class="setting-label">创意程度</text>
          <slider 
            class="creativity-slider"
            :value="temperature * 100"
            :min="0"
            :max="100"
            :step="10"
            activeColor="#4facfe"
            backgroundColor="#e0e5ec"
            block-size="20"
            @change="onTemperatureChange"
          />
          <text class="slider-value">{{ temperatureLabel }}</text>
        </view>
      </view>

      <!-- 展开/收起高级设置 -->
      <view class="toggle-advanced" @tap="showAdvanced = !showAdvanced">
        <text class="toggle-text">{{ showAdvanced ? '收起高级设置' : '展开高级设置' }}</text>
        <text class="toggle-icon">{{ showAdvanced ? '↑' : '↓' }}</text>
      </view>

      <!-- 生成结果 -->
      <view class="result-section" v-if="generatedContent" id="result-area">
        <view class="section-title">
          <text class="title-text">生成结果</text>
          <view class="result-actions">
            <view class="action-btn" @tap="copyContent">
              <text class="action-icon">📋</text>
              <text class="action-text">复制</text>
            </view>
            <view class="action-btn" @tap="regenerate">
              <text class="action-icon">🔄</text>
              <text class="action-text">重新生成</text>
            </view>
          </view>
        </view>
        <view class="result-card">
          <view class="result-header">
            <text class="result-model">{{ lastUsedModel }}</text>
            <text class="result-time">{{ generateTime }}</text>
          </view>
          <text class="result-content">{{ generatedContent }}</text>
        </view>
      </view>

      <!-- 底部占位 -->
      <view class="bottom-spacer"></view>
    </scroll-view>

    <!-- 底部生成按钮 -->
    <view class="bottom-bar">
      <button 
        class="generate-btn"
        :class="{ disabled: !canGenerate, loading: isGenerating }"
        :disabled="!canGenerate || isGenerating"
        @tap="generateCopywriting"
      >
        <view class="btn-content" v-if="!isGenerating">
          <text class="btn-icon">✨</text>
          <text class="btn-text">生成文案</text>
        </view>
        <view class="btn-content" v-else>
          <view class="loading-spinner"></view>
          <text class="btn-text">AI 思考中...</text>
        </view>
      </button>
    </view>

    <!-- 悬浮球组件 -->
    <ModelSwitcher />
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { useSettingsStore } from '@/stores/settings'
import { useAuthStore } from '@/stores/auth'
import { useProjectStore } from '@/stores/project'
import ModelSwitcher from '@/components/ModelSwitcher.vue'

// 设置 store
const settingsStore = useSettingsStore()
const authStore = useAuthStore()
const projectStore = useProjectStore()
const currentModel = computed(() => settingsStore.currentModel)
const activeProject = computed(() => projectStore.activeProject)

// ============== 状态定义 ==============

// 输入主题
const inputTopic = ref('')

// 选中的风格
const selectedStyle = ref('营销')

// 高级设置显示状态
const showAdvanced = ref(false)

// 最大 token 数
const maxTokens = ref(1024)

// 温度参数
const temperature = ref(0.7)

// 生成状态
const isGenerating = ref(false)

// 生成的内容
const generatedContent = ref('')

// 上次使用的模型
const lastUsedModel = ref('')

// 生成时间
const generateTime = ref('')

// 滚动定位
const scrollIntoView = ref('')

// ============== 配置数据 ==============

// 风格列表
const styleList = reactive([
  { label: '营销种草', value: '营销', icon: '🔥' },
  { label: '知识科普', value: '科普', icon: '📚' },
  { label: '故事叙述', value: '故事', icon: '📖' },
  { label: '情感共鸣', value: '情感', icon: '💝' },
  { label: '幽默搞笑', value: '幽默', icon: '😄' },
  { label: '专业正式', value: '专业', icon: '💼' }
])

// 长度选项
const lengthOptions = reactive([
  { label: '短文案', value: 512 },
  { label: '中等', value: 1024 },
  { label: '长文案', value: 2048 }
])

// ============== 计算属性 ==============

// 是否可以生成
const canGenerate = computed(() => {
  return inputTopic.value.trim().length >= 2
})

// 占位文本
const placeholderText = computed(() => {
  const examples: Record<string, string> = {
    '营销': '例如：一款新上市的智能手表，主打健康监测功能...',
    '科普': '例如：为什么天空是蓝色的？适合给小朋友讲解...',
    '故事': '例如：一个关于创业者坚持梦想的励志故事...',
    '情感': '例如：写给异地恋人的温暖文字...',
    '幽默': '例如：程序员的日常生活趣事...',
    '专业': '例如：人工智能在医疗领域的应用前景分析...'
  }
  return examples[selectedStyle.value] || '请输入您想要生成的文案主题...'
})

// 温度标签
const temperatureLabel = computed(() => {
  if (temperature.value < 0.3) return '保守'
  if (temperature.value < 0.6) return '稳定'
  if (temperature.value < 0.8) return '平衡'
  return '创意'
})

// ============== API 配置 ==============

// 后端 API 地址
const API_BASE_URL = __API_BASE_URL__

// ============== 方法定义 ==============

/**
 * 返回上一页
 */
function goBack() {
  uni.navigateBack({
    fail: () => {
      uni.switchTab({ url: '/pages/index/index' })
    }
  })
}

/**
 * 进入项目控制台
 */
function goToProjectDashboard() {
  uni.navigateTo({ url: '/pages/project/dashboard' })
}

/**
 * 显示模型信息
 */
function showModelInfo() {
  uni.showToast({
    title: `当前使用：${currentModel.value.name}`,
    icon: 'none'
  })
}

/**
 * 温度滑块变化
 */
function onTemperatureChange(e: any) {
  temperature.value = e.detail.value / 100
}

/**
 * 生成文案
 */
async function generateCopywriting() {
  if (!canGenerate.value || isGenerating.value) return
  
  // 登录检查
  const loggedIn = await authStore.requireLogin()
  if (!loggedIn) return
  
  isGenerating.value = true
  generatedContent.value = ''
  
  try {
    // 获取当前选中的模型类型，确保有默认值
    let modelType = settingsStore.modelType
    
    // 验证 modelType，如果无效则使用默认值
    if (!modelType || typeof modelType !== 'string' || !['deepseek', 'doubao'].includes(modelType)) {
      modelType = 'deepseek'
    }
    
    const requestData = {
      prompt: `请为以下主题创作一段${selectedStyle.value}风格的文案：\n\n主题：${inputTopic.value}`,
      model_type: modelType,
      system_prompt: getSystemPrompt(),
      temperature: temperature.value,
      max_tokens: maxTokens.value,
      stream: false
    }
    
    const response = await new Promise<UniApp.RequestSuccessCallbackResult>((resolve, reject) => {
      uni.request({
        url: `${API_BASE_URL}/api/generate`,
        method: 'POST',
        header: {
          'Content-Type': 'application/json'
        },
        timeout: 60000, // 60秒超时
        data: requestData,
        success: (res) => {
          resolve(res)
        },
        fail: (err: any) => {
          reject(new Error(err?.errMsg || 'Network request failed'))
        }
      })
    })
    
    const result = response.data as any
    
    // 检查 HTTP 状态码
    if (response.statusCode !== 200) {
      const errorMsg = result?.detail || result?.error || result?.body_received || `HTTP ${response.statusCode}`
      throw new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg))
    }
    
    if (result.success && result.content) {
      generatedContent.value = result.content
      lastUsedModel.value = `${currentModel.value.icon} ${currentModel.value.name}`
      generateTime.value = formatTime(new Date())
      
      // 滚动到结果区域
      setTimeout(() => {
        scrollIntoView.value = 'result-area'
      }, 100)
    } else {
      throw new Error(result.error || result.detail || '生成失败')
    }
    
  } catch (error: any) {
    console.error('生成失败:', error)
    uni.showToast({
      title: error.message || '生成失败，请稍后重试',
      icon: 'none',
      duration: 2500
    })
  } finally {
    isGenerating.value = false
  }
}

/**
 * 获取系统提示词
 * 结合选中的风格和当前项目的人设配置
 */
function getSystemPrompt(): string {
  const stylePrompts: Record<string, string> = {
    '营销': `你是一位专业的营销文案创作专家，擅长创作具有吸引力和转化力的种草文案。
要求：
1. 内容要有吸引力，能引发用户兴趣
2. 突出产品/服务的核心卖点和价值
3. 适当使用情感化表达，建立共鸣
4. 包含清晰的行动号召（CTA）
5. 适合在社交媒体传播`,
    
    '科普': `你是一位善于知识科普的内容创作者，能将复杂知识转化为通俗易懂的内容。
要求：
1. 语言通俗易懂，避免过多专业术语
2. 逻辑清晰，层层递进
3. 举例生动形象
4. 信息准确可靠
5. 能激发读者的求知欲`,
    
    '故事': `你是一位出色的故事讲述者，擅长创作引人入胜的叙事内容。
要求：
1. 故事要有吸引人的开头
2. 情节发展要有起伏
3. 人物形象要鲜明
4. 细节描写要生动
5. 结尾要有力量感或启发性`,
    
    '情感': `你是一位善于表达情感的文字创作者，文字温暖而有力量。
要求：
1. 情感真挚，能引起共鸣
2. 文字优美，有诗意
3. 触动内心，引发思考
4. 传递正能量和温暖
5. 避免过于煽情或空洞`,
    
    '幽默': `你是一位幽默风趣的内容创作者，善于用轻松的方式表达观点。
要求：
1. 风格轻松有趣
2. 幽默而不低俗
3. 包含巧妙的梗或反转
4. 观点鲜明但不尖锐
5. 让人会心一笑`,
    
    '专业': `你是一位严谨的专业内容创作者，擅长撰写高质量的专业文章。
要求：
1. 内容专业、准确
2. 结构清晰、逻辑严密
3. 论据充分、有说服力
4. 语言正式、精炼
5. 体现专业深度和洞察`
  }
  
  let basePrompt = stylePrompts[selectedStyle.value] || stylePrompts['营销']
  
  // 注入项目人设上下文
  const personaContext = projectStore.getPersonaSystemPrompt()
  if (personaContext) {
    basePrompt = `${personaContext}\n\n---\n\n${basePrompt}`
  }
  
  return basePrompt
}

/**
 * 复制内容
 */
function copyContent() {
  if (!generatedContent.value) return
  
  uni.setClipboardData({
    data: generatedContent.value,
    success: () => {
      uni.showToast({
        title: '已复制到剪贴板',
        icon: 'success'
      })
    }
  })
}

/**
 * 重新生成
 */
function regenerate() {
  generateCopywriting()
}

/**
 * 格式化时间
 */
function formatTime(date: Date): string {
  const hours = date.getHours().toString().padStart(2, '0')
  const minutes = date.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}
</script>

<style lang="scss" scoped>
.copywriting-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #f0f4ff 0%, #ffffff 100%);
  display: flex;
  flex-direction: column;
}

// 顶部标题栏
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx 32rpx;
  background: #ffffff;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
  position: sticky;
  top: 0;
  z-index: 100;
  
  .header-left {
    width: 80rpx;
    display: flex;
    align-items: center;
    
    .back-icon {
      font-size: 40rpx;
      color: #333;
      font-weight: 500;
    }
  }
  
  .header-center {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4rpx;
  }
  
  .header-title {
    font-size: 34rpx;
    font-weight: 600;
    color: #1a1a2e;
  }
  
  .project-indicator {
    display: flex;
    align-items: center;
    gap: 8rpx;
    padding: 4rpx 12rpx;
    background: #f8faff;
    border-radius: 16rpx;
    
    .indicator-dot {
      width: 12rpx;
      height: 12rpx;
      border-radius: 50%;
    }
    
    .indicator-name {
      font-size: 20rpx;
      color: #666;
      max-width: 120rpx;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
  
  .header-right {
    width: auto;
    
    .model-badge {
      display: flex;
      align-items: center;
      gap: 8rpx;
      padding: 8rpx 20rpx;
      background: linear-gradient(135deg, #f0f4ff 0%, #e8f0ff 100%);
      border-radius: 30rpx;
      
      .model-icon {
        font-size: 28rpx;
      }
      
      .model-name {
        font-size: 22rpx;
        color: #4facfe;
        font-weight: 500;
      }
    }
  }
}

// 主体内容
.main-content {
  flex: 1;
  padding: 24rpx;
}

// 通用 section 样式
.section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
  
  .title-text {
    font-size: 30rpx;
    font-weight: 600;
    color: #1a1a2e;
  }
  
  .title-hint {
    font-size: 22rpx;
    color: #999;
  }
}

// 风格选择区
.style-section {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
  
  .style-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16rpx;
  }
  
  .style-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8rpx;
    padding: 20rpx 12rpx;
    background: #f8faff;
    border-radius: 16rpx;
    border: 2rpx solid transparent;
    transition: all 0.3s ease;
    
    &.active {
      background: linear-gradient(135deg, #e8f4ff 0%, #dbeeff 100%);
      border-color: #4facfe;
      
      .style-label {
        color: #4facfe;
        font-weight: 600;
      }
    }
    
    &:active {
      transform: scale(0.96);
    }
    
    .style-icon {
      font-size: 40rpx;
    }
    
    .style-label {
      font-size: 24rpx;
      color: #666;
    }
  }
}

// 输入区域
.input-section {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
  
  .input-wrapper {
    background: #f8faff;
    border-radius: 16rpx;
    padding: 20rpx;
    border: 2rpx solid #e8f0ff;
    
    &:focus-within {
      border-color: #4facfe;
      background: #ffffff;
    }
  }
  
  .topic-input {
    width: 100%;
    min-height: 160rpx;
    font-size: 28rpx;
    color: #333;
    line-height: 1.6;
  }
  
  .input-footer {
    display: flex;
    justify-content: flex-end;
    margin-top: 12rpx;
    
    .char-count {
      font-size: 22rpx;
      color: #999;
    }
  }
}

// 高级设置
.advanced-section {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
  
  .setting-item {
    display: flex;
    align-items: center;
    margin-bottom: 24rpx;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    .setting-label {
      width: 140rpx;
      font-size: 26rpx;
      color: #666;
    }
    
    .setting-options {
      display: flex;
      gap: 16rpx;
      flex: 1;
    }
    
    .option-tag {
      padding: 12rpx 24rpx;
      background: #f8faff;
      border-radius: 30rpx;
      font-size: 24rpx;
      color: #666;
      border: 2rpx solid transparent;
      
      &.active {
        background: linear-gradient(135deg, #e8f4ff 0%, #dbeeff 100%);
        border-color: #4facfe;
        color: #4facfe;
        font-weight: 500;
      }
    }
    
    .creativity-slider {
      flex: 1;
      margin: 0 20rpx;
    }
    
    .slider-value {
      width: 60rpx;
      font-size: 24rpx;
      color: #4facfe;
      text-align: right;
    }
  }
}

// 展开/收起高级设置
.toggle-advanced {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
  padding: 20rpx;
  margin-bottom: 24rpx;
  
  .toggle-text {
    font-size: 24rpx;
    color: #999;
  }
  
  .toggle-icon {
    font-size: 24rpx;
    color: #999;
  }
}

// 结果区域
.result-section {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 28rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.04);
  
  .result-actions {
    display: flex;
    gap: 20rpx;
    
    .action-btn {
      display: flex;
      align-items: center;
      gap: 6rpx;
      padding: 8rpx 16rpx;
      background: #f8faff;
      border-radius: 20rpx;
      
      &:active {
        background: #e8f0ff;
      }
      
      .action-icon {
        font-size: 24rpx;
      }
      
      .action-text {
        font-size: 22rpx;
        color: #666;
      }
    }
  }
  
  .result-card {
    background: linear-gradient(135deg, #f8faff 0%, #f0f4ff 100%);
    border-radius: 16rpx;
    padding: 24rpx;
    border: 1rpx solid #e8f0ff;
    
    .result-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 16rpx;
      padding-bottom: 16rpx;
      border-bottom: 1rpx dashed #e0e5ec;
      
      .result-model {
        font-size: 22rpx;
        color: #4facfe;
      }
      
      .result-time {
        font-size: 22rpx;
        color: #999;
      }
    }
    
    .result-content {
      font-size: 28rpx;
      color: #333;
      line-height: 1.8;
      white-space: pre-wrap;
    }
  }
}

// 底部占位
.bottom-spacer {
  height: 160rpx;
}

// 底部生成按钮
.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20rpx 32rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,1) 30%);
  
  .generate-btn {
    width: 100%;
    height: 96rpx;
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    border-radius: 48rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8rpx 24rpx rgba(79, 172, 254, 0.35);
    border: none;
    
    &::after {
      border: none;
    }
    
    &.disabled {
      background: #e0e5ec;
      box-shadow: none;
      
      .btn-text {
        color: #999;
      }
    }
    
    &.loading {
      background: linear-gradient(135deg, #a0c8f0 0%, #90e0f0 100%);
    }
    
    &:active:not(.disabled):not(.loading) {
      transform: scale(0.98);
      box-shadow: 0 4rpx 16rpx rgba(79, 172, 254, 0.25);
    }
    
    .btn-content {
      display: flex;
      align-items: center;
      gap: 12rpx;
      
      .btn-icon {
        font-size: 36rpx;
      }
      
      .btn-text {
        font-size: 32rpx;
        font-weight: 600;
        color: #ffffff;
      }
      
      .loading-spinner {
        width: 32rpx;
        height: 32rpx;
        border: 4rpx solid rgba(255, 255, 255, 0.3);
        border-top-color: #ffffff;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
      }
    }
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>

