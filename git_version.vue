<template>
  <view class="chat-page">
    <!-- 椤堕儴瀵艰埅鏍?-->
    <view class="nav-header">
      <view class="nav-left" @tap="goBack">
        <text class="back-icon">鈥?/text>
      </view>
      <view class="nav-center">
        <text class="nav-title">{{ currentAgent.name }}</text>
        <view class="agent-tag">
          <text class="tag-dot"></text>
          <text class="tag-text">AI 鍒涗綔鍔╂墜</text>
        </view>
      </view>
      <view class="nav-right">
        <view class="model-chip" @tap="showModelPicker">
          <text class="model-icon">{{ currentModel.icon }}</text>
          <text class="model-text">{{ currentModel.name }}</text>
        </view>
      </view>
    </view>

    <!-- 鑱婂ぉ娑堟伅鍖哄煙 -->
    <scroll-view 
      class="chat-container"
      scroll-y
      :scroll-top="scrollTop"
      :scroll-with-animation="true"
      @scrolltoupper="onScrollToUpper"
    >
      <!-- IP 妗ｆ鍗＄墖 (绯荤粺娑堟伅) -->
      <view class="system-card" v-if="activeProject && ipCardMessage">
        <view class="card-header">
          <view class="card-avatar" :style="{ background: activeProject.avatar_color }">
            <text class="avatar-letter">{{ activeProject.avatar_letter }}</text>
          </view>
          <view class="card-title-group">
            <text class="card-title">{{ activeProject.name }}</text>
            <text class="card-subtitle">IP 妗ｆ 路 AI 宸插氨浣?/text>
          </view>
          <view class="card-status">
            <view class="status-pulse"></view>
            <text class="status-text">鍦ㄧ嚎</text>
          </view>
        </view>
        <view class="card-body">
          <view class="info-row">
            <text class="info-label">馃 褰撳墠鏅鸿兘浣?/text>
            <text class="info-value agent-value">{{ currentAgent.name }}</text>
          </view>
          <view class="info-row" v-if="activeProject.industry">
            <text class="info-label">馃彿锔?琛屼笟棰嗗煙</text>
            <text class="info-value">{{ activeProject.industry }}</text>
          </view>
          <view class="info-row" v-if="currentPersonaSettings.tone">
            <text class="info-label">馃幁 椋庢牸鏍囩</text>
            <text class="info-value">{{ formatStyleTags(currentPersonaSettings.tone) }}</text>
          </view>
          <view class="info-row" v-if="currentPersonaSettings.target_audience">
            <text class="info-label">馃懃 鐩爣鍙椾紬</text>
            <text class="info-value">{{ currentPersonaSettings.target_audience }}</text>
          </view>
        </view>
        <view class="card-footer">
          <text class="footer-hint">馃幆 鍑嗗灏辩华锛岃鍛婅瘔鎴戜綘鎯虫媿浠€涔堬紵</text>
        </view>
      </view>

      <!-- 鏃犻」鐩彁绀哄崱鐗?-->
      <view class="empty-project-card" v-if="!activeProject">
        <text class="empty-icon">馃搵</text>
        <text class="empty-title">灏氭湭閫夋嫨 IP 椤圭洰</text>
        <text class="empty-desc">璇峰厛鍒涘缓鎴栭€夋嫨涓€涓?IP 椤圭洰锛屼互渚?AI 鏇村ソ鍦扮悊瑙ｆ偍鐨勫垱浣滈渶姹?/text>
        <button class="create-btn" @tap="goToProjectList">
          <text>閫夋嫨椤圭洰</text>
        </button>
      </view>

      <!-- 瀵硅瘽娑堟伅鍒楄〃 -->
      <view 
        v-for="(msg, index) in chatHistory" 
        :key="index"
        class="message-wrapper"
        :class="msg.role"
      >
        <!-- 鐢ㄦ埛娑堟伅 -->
        <view v-if="msg.role === 'user'" class="message-bubble user-bubble">
          <text class="bubble-text">{{ msg.content }}</text>
        </view>
        
        <!-- AI 娑堟伅 -->
        <view v-else-if="msg.role === 'assistant'" class="message-row assistant-row">
          <view class="ai-avatar">
            <text class="ai-avatar-icon">{{ currentAgent.icon }}</text>
          </view>
          <view class="message-bubble assistant-bubble">
            <text class="bubble-text">{{ msg.content }}</text>
            <!-- 澶嶅埗鎸夐挳 -->
            <view class="bubble-actions">
              <view class="action-item" @tap="copyMessage(msg.content)">
                <text class="action-icon">馃搵</text>
                <text class="action-label">澶嶅埗</text>
              </view>
            </view>
          </view>
        </view>

        <!-- 绯荤粺鎻愮ず娑堟伅 (鏅鸿兘浣撳垏鎹㈢瓑) -->
        <view v-else-if="msg.role === 'system_hint'" class="system-hint-wrapper">
          <view class="system-hint-bubble">
            <text class="hint-text">{{ msg.content }}</text>
          </view>
        </view>
      </view>

      <!-- 鍔犺浇涓姸鎬?-->
      <view v-if="isGenerating" class="message-wrapper assistant">
        <view class="message-row assistant-row">
          <view class="ai-avatar">
            <text class="ai-avatar-icon">{{ currentAgent.icon }}</text>
          </view>
          <view class="message-bubble assistant-bubble loading-bubble">
            <view class="typing-indicator">
              <view class="typing-dot"></view>
              <view class="typing-dot"></view>
              <view class="typing-dot"></view>
            </view>
            <text class="loading-text">AI 姝ｅ湪鎬濊€?..</text>
          </view>
        </view>
      </view>

      <!-- 搴曢儴鍗犱綅 -->
      <view class="scroll-bottom-spacer"></view>
    </scroll-view>

    <!-- 鏅鸿兘浣撳垏鎹㈡偓娴悆 -->
    <view class="agent-fab" @tap="showAgentPicker">
      <text class="fab-icon">{{ currentAgent.icon }}</text>
    </view>

    <!-- 搴曢儴杈撳叆鏍?-->
    <view class="input-bar">
      <view class="input-container">
        <!-- 娓呯┖瀵硅瘽鎸夐挳 -->
        <view class="clear-btn" @tap="clearChat">
          <text class="clear-icon">馃棏锔?/text>
        </view>
        
        <!-- 杈撳叆妗?-->
        <view class="input-wrapper">
          <textarea
            v-model="inputText"
            class="chat-input"
            :placeholder="inputPlaceholder"
            :maxlength="2000"
            :auto-height="true"
            :show-confirm-bar="false"
            :adjust-position="true"
            :cursor-spacing="20"
            @confirm="sendMessage"
            @linechange="onInputLineChange"
          />
        </view>
        
        <!-- 鍙戦€佹寜閽?-->
        <view 
          class="send-btn"
          :class="{ active: canSend, disabled: !canSend || isGenerating }"
          @tap="sendMessage"
        >
          <text class="send-icon">{{ isGenerating ? '鈴? : '馃殌' }}</text>
        </view>
      </view>
    </view>

    <!-- 鏅鸿兘浣撻€夋嫨寮圭獥 -->
    <view class="agent-modal" v-if="showAgentModal" @tap="showAgentModal = false">
      <view class="modal-content" @tap.stop>
        <view class="modal-header">
          <text class="modal-title">閫夋嫨鏅鸿兘浣?/text>
          <view class="modal-close" @tap="showAgentModal = false">
            <text>鉁?/text>
          </view>
        </view>
        <view class="agent-list">
          <view 
            v-for="(agent, idx) in agentList" 
            :key="idx"
            class="agent-item"
            :class="{ active: currentAgent.id === agent.id }"
            @tap="selectAgent(agent)"
          >
            <view class="agent-icon-wrap">
              <text class="agent-icon">{{ agent.icon }}</text>
            </view>
            <view class="agent-info">
              <text class="agent-name">{{ agent.name }}</text>
              <text class="agent-desc">{{ agent.description }}</text>
            </view>
            <view class="agent-check" v-if="currentAgent.id === agent.id">
              <text>鉁?/text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 妯″瀷閫夋嫨寮圭獥 -->
    <view class="model-modal" v-if="showModelModal" @tap="showModelModal = false">
      <view class="modal-content" @tap.stop>
        <view class="modal-header">
          <text class="modal-title">鍒囨崲 AI 妯″瀷</text>
          <view class="modal-close" @tap="showModelModal = false">
            <text>鉁?/text>
          </view>
        </view>
        <view class="model-list">
          <view 
            v-for="(model, idx) in availableModels" 
            :key="idx"
            class="model-item"
            :class="{ active: currentModel.type === model.type }"
            @tap="selectModel(model)"
          >
            <text class="model-item-icon">{{ model.icon }}</text>
            <view class="model-item-info">
              <text class="model-item-name">{{ model.name }}</text>
              <text class="model-item-desc">{{ model.description }}</text>
            </view>
            <view class="model-check" v-if="currentModel.type === model.type">
              <text>鉁?/text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted, nextTick } from 'vue'
import { useSettingsStore, type ModelConfig } from '@/stores/settings'
import { useAuthStore } from '@/stores/auth'
import { useProjectStore } from '@/stores/project'

// ============== Store ==============
const settingsStore = useSettingsStore()
const authStore = useAuthStore()
const projectStore = useProjectStore()

const currentModel = computed(() => settingsStore.currentModel)
const availableModels = computed(() => settingsStore.availableModels)
const activeProject = computed(() => projectStore.activeProject)
const currentPersonaSettings = computed(() => projectStore.currentPersonaSettings)

// ============== 鏅鸿兘浣撻厤缃?==============
interface Agent {
  id: string
  name: string
  icon: string
  description: string
  systemPrompt: string
}

const agentList = reactive<Agent[]>([
  {
    id: 'copywriter',
    name: '楂樻晥鍙ｆ挱鏂囨鏅鸿兘浣?,
    icon: '馃帣锔?,
    description: '涓撴敞浜庣煭瑙嗛鍙ｆ挱鏂囨锛岃妭濂忔劅寮猴紝閫傚悎 TikTok/鎶栭煶',
    systemPrompt: `浣犳槸涓€浣嶄笓涓氱殑鐭棰戝彛鎾枃妗堝垱浣滀笓瀹躲€備綘鐨勬枃妗堢壒鐐癸細
1. 寮€澶村繀椤绘湁寮虹儓鐨勯挬瀛愶紝3绉掓姄浣忔敞鎰忓姏
2. 鑺傚鎰熷己锛岄€傚悎鏈楄锛屽彞瀛愮畝鐭湁鍔?3. 鍠勭敤鍙嶉棶銆佽闂寮轰簰鍔ㄦ劅
4. 缁撳熬鏈夋槑纭殑琛屽姩鍙峰彫锛圕TA锛?5. 鎺у埗鍦?00瀛椾互鍐咃紝閫傚悎60绉掍互鍐呯殑鐭棰慲
  },
  {
    id: 'xiaohongshu',
    name: '灏忕孩涔︾鑽夌瑪璁版櫤鑳戒綋',
    icon: '馃摃',
    description: '灏忕孩涔︾垎娆剧瑪璁伴鏍硷紝鐪熷疄鎰熷己锛宔moji涓板瘜',
    systemPrompt: `浣犳槸涓€浣嶅皬绾功澶撮儴鍗氫富锛屾搮闀垮啓绉嶈崏绗旇銆備綘鐨勬枃妗堢壒鐐癸細
1. 鏍囬蹇呴』鏈塭moji锛屽惛寮曠偣鍑?2. 寮€澶寸敤涓汉鐪熷疄浣撻獙鍒囧叆锛屽寮哄彲淇″害
3. 鍐呭鍒嗙偣娓呮櫚锛屽杽鐢╡moji鍒嗛殧
4. 璇皵浜插拰鐪熷疄锛屽儚鏈嬪弸鍒嗕韩
5. 閫傚綋浣跨敤缃戠粶鐑瘝鍜屾祦琛屾
6. 缁撳熬璁剧疆浜掑姩璇濋锛屽紩瀵艰瘎璁篳
  },
  {
    id: 'marketing',
    name: '钀ラ攢杞寲鏂囨鏅鸿兘浣?,
    icon: '馃挵',
    description: '楂樿浆鍖栬惀閿€鏂囨锛孉IDA妯″瀷锛屽埡婵€璐拱娆?,
    systemPrompt: `浣犳槸涓€浣嶈祫娣辫惀閿€鏂囨涓撳锛岀簿閫氭秷璐瑰績鐞嗗銆備綘鐨勬枃妗堥伒寰狝IDA妯″瀷锛?1. Attention - 鐢ㄧ棝鐐规垨鍒╃泭鐐规姄浣忔敞鎰忓姏
2. Interest - 灞曠ず浜у搧鐙壒鍗栫偣锛屽紩鍙戝叴瓒?3. Desire - 鎻忕粯浣跨敤鍦烘櫙锛屾縺鍙戣喘涔版鏈?4. Action - 闄愭椂浼樻儬銆佺█缂烘€э紝淇冧娇绔嬪嵆琛屽姩
鍠勭敤鏁板瓧銆佸姣斻€佺ぞ浼氳鍚岀瓑璇存湇鎶€宸
  },
  {
    id: 'story',
    name: '鏁呬簨鍙欒堪鏅鸿兘浣?,
    icon: '馃摉',
    description: '娌夋蹈寮忔晠浜嬪唴瀹癸紝鎯呮劅鍏遍福锛屽紩浜哄叆鑳?,
    systemPrompt: `浣犳槸涓€浣嶅嚭鑹茬殑鏁呬簨璁茶堪鑰咃紝鎿呴暱鍒涗綔寮曚汉鍏ヨ儨鐨勫彊浜嬪唴瀹广€備綘鐨勭壒鐐癸細
1. 鍠勪簬璁剧疆鎮康鍜屽啿绐?2. 浜虹墿鍒荤敾鐢熷姩锛岀粏鑺備赴瀵?3. 鎯呰妭鍙戝睍鏈夎捣浼忥紝鑺傚鎶婃帶绮惧噯
4. 鍠勪簬璋冨姩璇昏€呮儏缁紝寮曞彂鍏遍福
5. 缁撳熬瀵屾湁鍔涢噺鎰熸垨鍚彂鎬
  },
  {
    id: 'knowledge',
    name: '鐭ヨ瘑绉戞櫘鏅鸿兘浣?,
    icon: '馃帗',
    description: '涓撲笟鐭ヨ瘑閫氫織鍖栵紝娣卞叆娴呭嚭锛屾潈濞佸彲淇?,
    systemPrompt: `浣犳槸涓€浣嶇煡璇嗙鏅揪浜猴紝鑳藉皢澶嶆潅涓撲笟鐭ヨ瘑杞寲涓洪€氫織鏄撴噦鐨勫唴瀹广€備綘鐨勭壒鐐癸細
1. 鐢ㄧ敓娲诲寲鐨勬瘮鍠昏В閲婃娊璞℃蹇?2. 閫昏緫娓呮櫚锛屽眰灞傞€掕繘
3. 寮曠敤鏉冨▉鏁版嵁澧炲己鍙俊搴?4. 璁剧疆鐤戦棶寮曞鎬濊€?5. 鐭ヨ瘑鐐归€傚害锛屼笉璐姹傚叏`
  }
])

const currentAgent = ref<Agent>(agentList[0])

// ============== 鐘舵€佸畾涔?==============
interface ChatMessage {
  role: 'user' | 'assistant' | 'system_card' | 'system_hint'
  content: string
  timestamp: number
}

const chatHistory = reactive<ChatMessage[]>([])
const inputText = ref('')
const isGenerating = ref(false)
const scrollTop = ref(0)
const showAgentModal = ref(false)
const showModelModal = ref(false)
const ipCardMessage = ref<ChatMessage | null>(null)

// ============== 璁＄畻灞炴€?==============
const canSend = computed(() => inputText.value.trim().length > 0)

const inputPlaceholder = computed(() => {
  return `鍚?{currentAgent.value.name}鍙戦€佸垱浣滄寚浠?..`
})

// ============== API 閰嶇疆 ==============
const API_BASE_URL = __API_BASE_URL__

// ============== 鏂规硶瀹氫箟 ==============

/**
 * 杩斿洖涓婁竴椤? */
function goBack() {
  uni.navigateBack({
    fail: () => {
      uni.switchTab({ url: '/pages/index/index' })
    }
  })
}

/**
 * 璺宠浆鍒伴」鐩垪琛? */
function goToProjectList() {
  uni.navigateTo({ url: '/pages/project/list' })
}

/**
 * 鏍煎紡鍖栭鏍兼爣绛? */
function formatStyleTags(tone: string): string {
  if (!tone) return ''
  // 濡傛灉宸茬粡鏄暟缁勬牸寮忕殑瀛楃涓诧紝灏濊瘯瑙ｆ瀽
  try {
    const parsed = JSON.parse(tone)
    if (Array.isArray(parsed)) {
      return parsed.join(', ')
    }
  } catch {
    // 涓嶆槸 JSON锛岀洿鎺ヨ繑鍥?  }
  return tone
}

/**
 * 鍒濆鍖?IP 鍗＄墖娑堟伅 (Task 1)
 */
function initIPCard() {
  if (activeProject.value) {
    ipCardMessage.value = {
      role: 'system_card',
      content: `馃 褰撳墠鏅鸿兘浣擄細${currentAgent.value.name}\n馃懁 缁戝畾 IP锛?{activeProject.value.name}\n馃彿锔?椋庢牸鏍囩锛?{formatStyleTags(currentPersonaSettings.value?.tone || '榛樿')}\n馃幆 鍑嗗灏辩华锛岃鍛婅瘔鎴戜綘鎯虫媿浠€涔堬紵`,
      timestamp: Date.now()
    }
  }
}

/**
 * 鏄剧ず鏅鸿兘浣撻€夋嫨鍣? */
function showAgentPicker() {
  showAgentModal.value = true
}

/**
 * 閫夋嫨鏅鸿兘浣?(Task 2)
 */
function selectAgent(agent: Agent) {
  if (currentAgent.value.id === agent.id) {
    showAgentModal.value = false
    return
  }

  const previousAgent = currentAgent.value
  currentAgent.value = agent
  showAgentModal.value = false

  // 鎻掑叆绯荤粺鎻愮ず娑堟伅锛屼笉娓呴櫎鍘嗗彶璁板綍
  chatHistory.push({
    role: 'system_hint',
    content: `宸插垏鎹负 [${agent.name}]锛屾帴涓嬫潵鐨勫唴瀹瑰皢鎸夋椋庢牸鐢熸垚銆俙,
    timestamp: Date.now()
  })

  // 鏇存柊 IP 鍗＄墖涓殑鏅鸿兘浣撲俊鎭?  initIPCard()

  uni.showToast({
    title: `宸插垏鎹㈠埌 ${agent.name}`,
    icon: 'none'
  })

  scrollToBottom()
}

/**
 * 鏄剧ず妯″瀷閫夋嫨鍣? */
function showModelPicker() {
  showModelModal.value = true
}

/**
 * 閫夋嫨妯″瀷
 */
function selectModel(model: ModelConfig) {
  settingsStore.setModelType(model.type)
  showModelModal.value = false
  uni.showToast({
    title: `宸插垏鎹㈠埌 ${model.name}`,
    icon: 'none'
  })
}

/**
 * 娓呯┖瀵硅瘽 (Task 3)
 * 娓呴櫎闄?IP 鍗＄墖"澶栫殑鎵€鏈夊璇? */
function clearChat() {
  if (chatHistory.length === 0) {
    uni.showToast({
      title: '鏆傛棤瀵硅瘽璁板綍',
      icon: 'none'
    })
    return
  }

  uni.showModal({
    title: '娓呯┖瀵硅瘽',
    content: '纭畾瑕佹竻绌哄綋鍓嶅璇濊褰曞悧锛烮P 妗ｆ鍗＄墖灏嗕繚鐣欍€?,
    success: (res) => {
      if (res.confirm) {
        // 娓呯┖鑱婂ぉ鍘嗗彶锛屼絾淇濈暀 IP 鍗＄墖
        chatHistory.splice(0, chatHistory.length)
        uni.showToast({
          title: '瀵硅瘽宸叉竻绌?,
          icon: 'success'
        })
      }
    }
  })
}

/**
 * 婊氬姩鍒板簳閮? */
function scrollToBottom() {
  nextTick(() => {
    // 浣跨敤涓€涓緢澶х殑鏁板€肩‘淇濇粴鍔ㄥ埌搴曢儴
    scrollTop.value = scrollTop.value === 99999 ? 100000 : 99999
  })
}

/**
 * 婊氬姩鍒伴《閮ㄤ簨浠? */
function onScrollToUpper() {
  // 棰勭暀锛氬彲鐢ㄤ簬鍔犺浇鍘嗗彶娑堟伅
}

/**
 * 杈撳叆妗嗚鏁板彉鍖? */
function onInputLineChange() {
  // 杈撳叆妗嗛珮搴﹀彉鍖栨椂鐨勫鐞?}

/**
 * 鍙戦€佹秷鎭?(Task 3)
 */
async function sendMessage() {
  if (!canSend.value || isGenerating.value) return

  // 鐧诲綍妫€鏌?  const loggedIn = await authStore.requireLogin()
  if (!loggedIn) return

  const userMessage = inputText.value.trim()
  inputText.value = ''

  // 娣诲姞鐢ㄦ埛娑堟伅
  chatHistory.push({
    role: 'user',
    content: userMessage,
    timestamp: Date.now()
  })

  scrollToBottom()
  isGenerating.value = true

  try {
    // 鏋勫缓绯荤粺鎻愮ず璇?    let systemPrompt = currentAgent.value.systemPrompt
    
    // 娉ㄥ叆椤圭洰浜鸿涓婁笅鏂?    const personaContext = projectStore.getPersonaSystemPrompt()
    if (personaContext) {
      systemPrompt = `${personaContext}\n\n---\n\n${systemPrompt}`
    }

    // 鏋勫缓瀵硅瘽鍘嗗彶锛堝彧鍖呭惈 user 鍜?assistant 娑堟伅锛?    const messages = chatHistory
      .filter(msg => msg.role === 'user' || msg.role === 'assistant')
      .map(msg => ({
        role: msg.role,
        content: msg.content
      }))

    let modelType = settingsStore.modelType
    if (!modelType || !['deepseek', 'doubao', 'claude'].includes(modelType)) {
      modelType = 'claude'
    }

    const requestData = {
      prompt: userMessage,
      model_type: modelType,
      system_prompt: systemPrompt,
      temperature: 0.7,
      max_tokens: 2048,
      stream: false
    }

    const response = await new Promise<UniApp.RequestSuccessCallbackResult>((resolve, reject) => {
      uni.request({
        url: `${API_BASE_URL}/api/generate`,
        method: 'POST',
        header: { 'Content-Type': 'application/json' },
        timeout: 60000,
        data: requestData,
        success: resolve,
        fail: (err: any) => reject(new Error(err?.errMsg || 'Network request failed'))
      })
    })

    const result = response.data as any

    if (response.statusCode !== 200) {
      const errorMsg = result?.detail || result?.error || `HTTP ${response.statusCode}`
      throw new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg))
    }

    if (result.success && result.content) {
      chatHistory.push({
        role: 'assistant',
        content: result.content,
        timestamp: Date.now()
      })
      scrollToBottom()
    } else {
      throw new Error(result.error || result.detail || '鐢熸垚澶辫触')
    }

  } catch (error: any) {
    console.error('鐢熸垚澶辫触:', error)
    uni.showToast({
      title: error.message || '鐢熸垚澶辫触锛岃绋嶅悗閲嶈瘯',
      icon: 'none',
      duration: 2500
    })
    // 娣诲姞閿欒娑堟伅
    chatHistory.push({
      role: 'assistant',
      content: `鉂?鐢熸垚澶辫触锛?{error.message || '璇风◢鍚庨噸璇?}`,
      timestamp: Date.now()
    })
    scrollToBottom()
  } finally {
    isGenerating.value = false
  }
}

/**
 * 澶嶅埗娑堟伅
 */
function copyMessage(content: string) {
  uni.setClipboardData({
    data: content,
    success: () => {
      uni.showToast({
        title: '宸插鍒跺埌鍓创鏉?,
        icon: 'success'
      })
    }
  })
}

// ============== 鐢熷懡鍛ㄦ湡 ==============
onMounted(() => {
  // Task 1: 鍒濆鍖?IP 鍗＄墖
  initIPCard()
  // 鍒濆鍖栨椂婊氬姩鍒板簳閮?  scrollToBottom()
})

// 鐩戝惉椤圭洰鍙樺寲锛屾洿鏂?IP 鍗＄墖
watch(activeProject, () => {
  initIPCard()
}, { immediate: true })
</script>

<style lang="scss" scoped>
// ============== 鍙橀噺瀹氫箟 ==============
$primary-orange: #FF6B35;
$primary-orange-light: #FF8C5A;
$accent-blue: #4FACFE;
$accent-cyan: #00F2FE;
$bg-dark: #1A1A2E;
$bg-card: rgba(255, 255, 255, 0.95);
$text-primary: #1A1A2E;
$text-secondary: #666;
$text-muted: #999;
$border-light: rgba(0, 0, 0, 0.06);

// ============== 椤甸潰瀹瑰櫒 ==============
.chat-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: linear-gradient(165deg, #F8FAFF 0%, #EEF2FF 50%, #FFF5F0 100%);
}

// ============== 椤堕儴瀵艰埅鏍?==============
.nav-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 24rpx;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px);
  border-bottom: 1rpx solid $border-light;
  position: relative;
  z-index: 100;

  .nav-left {
    width: 72rpx;
    height: 72rpx;
    display: flex;
    align-items: center;
    justify-content: center;

    .back-icon {
      font-size: 56rpx;
      color: $text-primary;
      font-weight: 300;
    }
  }

  .nav-center {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;

    .nav-title {
      font-size: 32rpx;
      font-weight: 600;
      color: $text-primary;
    }

    .agent-tag {
      display: flex;
      align-items: center;
      gap: 8rpx;
      margin-top: 4rpx;

      .tag-dot {
        width: 12rpx;
        height: 12rpx;
        border-radius: 50%;
        background: linear-gradient(135deg, #4CAF50, #8BC34A);
        animation: pulse 2s infinite;
      }

      .tag-text {
        font-size: 22rpx;
        color: $text-muted;
      }
    }
  }

  .nav-right {
    .model-chip {
      display: flex;
      align-items: center;
      gap: 8rpx;
      padding: 12rpx 20rpx;
      background: linear-gradient(135deg, #F0F4FF 0%, #E8EEFF 100%);
      border-radius: 32rpx;
      border: 1rpx solid rgba(79, 172, 254, 0.2);

      .model-icon {
        font-size: 28rpx;
      }

      .model-text {
        font-size: 24rpx;
        color: $accent-blue;
        font-weight: 500;
      }
    }
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(0.9); }
}

// ============== 鑱婂ぉ瀹瑰櫒 ==============
.chat-container {
  flex: 1;
  padding: 24rpx;
  overflow: hidden;
}

// ============== IP 妗ｆ鍗＄墖 ==============
.system-card {
  background: $bg-card;
  border-radius: 28rpx;
  padding: 32rpx;
  margin-bottom: 32rpx;
  border: 2rpx solid transparent;
  background-clip: padding-box;
  position: relative;
  box-shadow: 0 8rpx 32rpx rgba(79, 172, 254, 0.1);

  &::before {
    content: '';
    position: absolute;
    inset: -2rpx;
    border-radius: 30rpx;
    background: linear-gradient(135deg, $accent-blue, $accent-cyan, $primary-orange);
    z-index: -1;
    opacity: 0.6;
  }

  .card-header {
    display: flex;
    align-items: center;
    margin-bottom: 24rpx;
    padding-bottom: 20rpx;
    border-bottom: 1rpx dashed rgba(0, 0, 0, 0.08);

    .card-avatar {
      width: 88rpx;
      height: 88rpx;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.15);

      .avatar-letter {
        font-size: 40rpx;
        font-weight: 700;
        color: #fff;
      }
    }

    .card-title-group {
      flex: 1;
      margin-left: 20rpx;

      .card-title {
        font-size: 36rpx;
        font-weight: 700;
        color: $text-primary;
        display: block;
      }

      .card-subtitle {
        font-size: 24rpx;
        color: $text-muted;
        margin-top: 4rpx;
      }
    }

    .card-status {
      display: flex;
      align-items: center;
      gap: 8rpx;
      padding: 8rpx 16rpx;
      background: rgba(76, 175, 80, 0.1);
      border-radius: 20rpx;

      .status-pulse {
        width: 16rpx;
        height: 16rpx;
        border-radius: 50%;
        background: #4CAF50;
        animation: pulse 2s infinite;
      }

      .status-text {
        font-size: 22rpx;
        color: #4CAF50;
        font-weight: 500;
      }
    }
  }

  .card-body {
    .info-row {
      display: flex;
      align-items: center;
      padding: 16rpx 0;

      .info-label {
        font-size: 26rpx;
        color: $text-secondary;
        width: 180rpx;
      }

      .info-value {
        flex: 1;
        font-size: 26rpx;
        color: $text-primary;
        font-weight: 500;

        &.agent-value {
          color: $primary-orange;
        }
      }
    }
  }

  .card-footer {
    margin-top: 20rpx;
    padding-top: 20rpx;
    border-top: 1rpx dashed rgba(0, 0, 0, 0.08);

    .footer-hint {
      font-size: 24rpx;
      color: $text-muted;
      text-align: center;
      display: block;
    }
  }
}

// ============== 绌洪」鐩崱鐗?==============
.empty-project-card {
  background: $bg-card;
  border-radius: 28rpx;
  padding: 60rpx 40rpx;
  margin-bottom: 32rpx;
  text-align: center;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.06);

  .empty-icon {
    font-size: 80rpx;
    display: block;
    margin-bottom: 24rpx;
  }

  .empty-title {
    font-size: 32rpx;
    font-weight: 600;
    color: $text-primary;
    display: block;
    margin-bottom: 16rpx;
  }

  .empty-desc {
    font-size: 26rpx;
    color: $text-muted;
    display: block;
    margin-bottom: 32rpx;
    line-height: 1.6;
  }

  .create-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 20rpx 48rpx;
    background: linear-gradient(135deg, $primary-orange, $primary-orange-light);
    border-radius: 40rpx;
    border: none;
    color: #fff;
    font-size: 28rpx;
    font-weight: 500;
    box-shadow: 0 8rpx 24rpx rgba(255, 107, 53, 0.3);

    &::after {
      border: none;
    }
  }
}

// ============== 娑堟伅姘旀场 ==============
.message-wrapper {
  margin-bottom: 28rpx;

  &.user {
    display: flex;
    justify-content: flex-end;
  }

  &.assistant {
    display: flex;
    justify-content: flex-start;
  }
}

.message-row {
  display: flex;
  align-items: flex-start;
  max-width: 85%;

  &.assistant-row {
    .ai-avatar {
      width: 72rpx;
      height: 72rpx;
      border-radius: 50%;
      background: linear-gradient(135deg, #667EEA, #764BA2);
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 16rpx;
      flex-shrink: 0;
      box-shadow: 0 4rpx 12rpx rgba(102, 126, 234, 0.3);

      .ai-avatar-icon {
        font-size: 36rpx;
      }
    }
  }
}

.message-bubble {
  padding: 24rpx 28rpx;
  border-radius: 24rpx;
  position: relative;

  .bubble-text {
    font-size: 28rpx;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-word;
  }
}

.user-bubble {
  background: linear-gradient(135deg, $primary-orange, $primary-orange-light);
  color: #fff;
  border-bottom-right-radius: 8rpx;
  max-width: 85%;
  box-shadow: 0 4rpx 16rpx rgba(255, 107, 53, 0.25);
}

.assistant-bubble {
  background: $bg-card;
  color: $text-primary;
  border-bottom-left-radius: 8rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.06);

  .bubble-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 16rpx;
    padding-top: 12rpx;
    border-top: 1rpx solid $border-light;

    .action-item {
      display: flex;
      align-items: center;
      gap: 6rpx;
      padding: 8rpx 16rpx;
      background: #F5F7FA;
      border-radius: 16rpx;

      .action-icon {
        font-size: 24rpx;
      }

      .action-label {
        font-size: 22rpx;
        color: $text-muted;
      }

      &:active {
        background: #E8ECEF;
      }
    }
  }
}

// ============== 绯荤粺鎻愮ず娑堟伅 ==============
.system-hint-wrapper {
  display: flex;
  justify-content: center;
  margin: 24rpx 0;
}

.system-hint-bubble {
  background: rgba(0, 0, 0, 0.04);
  padding: 12rpx 24rpx;
  border-radius: 20rpx;

  .hint-text {
    font-size: 24rpx;
    color: $text-muted;
  }
}

.loading-bubble {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 28rpx 32rpx;

  .typing-indicator {
    display: flex;
    gap: 8rpx;

    .typing-dot {
      width: 16rpx;
      height: 16rpx;
      border-radius: 50%;
      background: $accent-blue;
      animation: typingBounce 1.4s infinite both;

      &:nth-child(1) { animation-delay: 0s; }
      &:nth-child(2) { animation-delay: 0.2s; }
      &:nth-child(3) { animation-delay: 0.4s; }
    }
  }

  .loading-text {
    font-size: 26rpx;
    color: $text-muted;
  }
}

@keyframes typingBounce {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.scroll-bottom-spacer {
  height: 200rpx;
}

// ============== 鏅鸿兘浣撴偓娴悆 ==============
.agent-fab {
  position: fixed;
  right: 32rpx;
  bottom: calc(180rpx + env(safe-area-inset-bottom));
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #667EEA, #764BA2);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 32rpx rgba(102, 126, 234, 0.4);
  z-index: 99;
  animation: fabFloat 3s ease-in-out infinite;

  .fab-icon {
    font-size: 48rpx;
  }

  &:active {
    transform: scale(0.95);
  }
}

@keyframes fabFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8rpx); }
}

// ============== 搴曢儴杈撳叆鏍?==============
.input-bar {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  padding: 20rpx 24rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  border-top: 1rpx solid $border-light;
  box-shadow: 0 -4rpx 24rpx rgba(0, 0, 0, 0.05);

  .input-container {
    display: flex;
    align-items: flex-end;
    gap: 16rpx;
  }

  .clear-btn {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    background: #F5F7FA;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;

    .clear-icon {
      font-size: 36rpx;
    }

    &:active {
      background: #E8ECEF;
    }
  }

  .input-wrapper {
    flex: 1;
    background: #F5F7FA;
    border-radius: 40rpx;
    padding: 20rpx 28rpx;
    border: 2rpx solid transparent;
    transition: all 0.3s ease;

    &:focus-within {
      background: #fff;
      border-color: $accent-blue;
      box-shadow: 0 0 0 4rpx rgba(79, 172, 254, 0.1);
    }

    .chat-input {
      width: 100%;
      font-size: 28rpx;
      color: $text-primary;
      line-height: 1.5;
      min-height: 40rpx;
      max-height: 200rpx;
    }
  }

  .send-btn {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    background: #E0E5EC;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    transition: all 0.3s ease;

    .send-icon {
      font-size: 36rpx;
    }

    &.active {
      background: linear-gradient(135deg, $primary-orange, $primary-orange-light);
      box-shadow: 0 4rpx 16rpx rgba(255, 107, 53, 0.35);
    }

    &.disabled {
      opacity: 0.6;
      pointer-events: none;
    }

    &:active:not(.disabled) {
      transform: scale(0.95);
    }
  }
}

// ============== 妯℃€佹閫氱敤鏍峰紡 ==============
.agent-modal,
.model-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 200;
  animation: fadeIn 0.2s ease;

  .modal-content {
    width: 100%;
    max-height: 80vh;
    background: #fff;
    border-radius: 32rpx 32rpx 0 0;
    animation: slideUp 0.3s ease;
    overflow: hidden;
  }

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 32rpx;
    border-bottom: 1rpx solid $border-light;

    .modal-title {
      font-size: 34rpx;
      font-weight: 600;
      color: $text-primary;
    }

    .modal-close {
      width: 56rpx;
      height: 56rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #F5F7FA;
      border-radius: 50%;
      font-size: 28rpx;
      color: $text-muted;
    }
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(100%); }
  to { transform: translateY(0); }
}

// ============== 鏅鸿兘浣撳垪琛?==============
.agent-list {
  padding: 16rpx 24rpx;
  max-height: 60vh;
  overflow-y: auto;

  .agent-item {
    display: flex;
    align-items: center;
    padding: 24rpx;
    border-radius: 20rpx;
    margin-bottom: 16rpx;
    background: #F8FAFF;
    border: 2rpx solid transparent;
    transition: all 0.2s ease;

    &.active {
      background: linear-gradient(135deg, rgba(79, 172, 254, 0.1), rgba(0, 242, 254, 0.1));
      border-color: $accent-blue;
    }

    &:active {
      transform: scale(0.98);
    }

    .agent-icon-wrap {
      width: 80rpx;
      height: 80rpx;
      border-radius: 50%;
      background: linear-gradient(135deg, #667EEA, #764BA2);
      display: flex;
      align-items: center;
      justify-content: center;

      .agent-icon {
        font-size: 40rpx;
      }
    }

    .agent-info {
      flex: 1;
      margin-left: 20rpx;

      .agent-name {
        font-size: 30rpx;
        font-weight: 600;
        color: $text-primary;
        display: block;
      }

      .agent-desc {
        font-size: 24rpx;
        color: $text-muted;
        margin-top: 6rpx;
        display: block;
      }
    }

    .agent-check {
      width: 48rpx;
      height: 48rpx;
      border-radius: 50%;
      background: $accent-blue;
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 28rpx;
      font-weight: 600;
    }
  }
}

// ============== 妯″瀷鍒楄〃 ==============
.model-list {
  padding: 16rpx 24rpx;

  .model-item {
    display: flex;
    align-items: center;
    padding: 28rpx 24rpx;
    border-radius: 20rpx;
    margin-bottom: 16rpx;
    background: #F8FAFF;
    border: 2rpx solid transparent;
    transition: all 0.2s ease;

    &.active {
      background: linear-gradient(135deg, rgba(79, 172, 254, 0.1), rgba(0, 242, 254, 0.1));
      border-color: $accent-blue;
    }

    &:active {
      transform: scale(0.98);
    }

    .model-item-icon {
      font-size: 48rpx;
      margin-right: 20rpx;
    }

    .model-item-info {
      flex: 1;

      .model-item-name {
        font-size: 30rpx;
        font-weight: 600;
        color: $text-primary;
        display: block;
      }

      .model-item-desc {
        font-size: 24rpx;
        color: $text-muted;
        margin-top: 4rpx;
        display: block;
      }
    }

    .model-check {
      width: 48rpx;
      height: 48rpx;
      border-radius: 50%;
      background: $accent-blue;
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 28rpx;
      font-weight: 600;
    }
  }
}
</style>

