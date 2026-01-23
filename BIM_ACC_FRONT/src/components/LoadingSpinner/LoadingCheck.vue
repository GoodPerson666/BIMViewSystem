<template>
  <div class="modal-backdrop" :style="{ display: visible ? 'flex' : 'none' }" @click="handleBackdropClick">
    <div class="modal">
      <div class="modal-header">
        <h2>{{ checkState.title }}</h2>
        <p class="sub">{{ checkState.subTitle }}</p>

        <div class="btn-group">
          <div class="main-btn-group">
            <el-button class="detail-btn" @click="toggleDetails" :disabled="running || loading">查看详情</el-button>
            <el-button
                class="next-btn"
                @click="handleNextStep"
                :disabled="running || loading || checkState.complete"
            >下一步</el-button>
          </div>
          <el-button
              class="reset-btn"
              @click="resetCheckProcess"
              type="warning"
              size="small"
              :disabled="running || loading"
          >重新审查</el-button>
        </div>

        <div class="loader">
          <div class="ring" :class="{ complete: checkState.complete, paused: checkState.paused }" id="ring"></div>
        </div>
      </div>
      <div class="modal-body">
        <div class="logs" ref="logsElRef" aria-live="polite" aria-atomic="true"></div>
      </div>
    </div>

    <Check_details
        v-if="showDetails"
        :visible="showDetails"
        @close="showDetails = false"
    />

  </div>
</template>

<script setup>
import { ref, nextTick, watch, reactive } from 'vue'
import Check_details from "@/components/PopUp/Check_details.vue";

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const showDetails = ref(false)
const running = ref(false)
const loading = ref(false)
const logsElRef = ref(null)

const checkState = reactive({
  title: '准备开始审查',
  subTitle: '请点击下一步按钮启动审查流程',
  complete: false,
  paused: false,
  currentStep: -1,
  outputsData: [],
  logContent: '',
  hasInited: false,
  error: ''
})

const parts = [
  '正在执行第一部分，规范类型识别......',
  '正在执行第二部分，规范实体识别......',
  '正在执行第三部分，IFC类型及属性集识别......',
  '正在执行第四部分，规范实体与条文对齐......',
  '正在执行第五部分，实体与IFC类型对齐......',
  '正在执行第六部分，构建实体对齐元组......',
  '正在执行第七部分，规范相关属性选择......',
  '正在执行第八部分，进行合规性审查......',
]

const fetchOutputs = async () => {
  try {
    loading.value = true
    checkState.error = ''
    const response = await fetch('http://localhost:5000/check/rusults', {
      method: 'POST',
    })
    if (!response.ok) throw new Error(`网络错误：${response.status}`)
    const data = await response.json()
    if (data.code !== 200) throw new Error(data.msg || '获取审查结果失败')
    return data.outputs
  } catch (err) {
    checkState.error = err.message
    return Array(parts.length).fill(null)
  } finally {
    loading.value = false
  }
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

function clearLogs() {
  if (logsElRef.value) {
    logsElRef.value.innerHTML = ''
    checkState.logContent = ''
  }
}

// 修改后的日志生成函数
function appendLog(text, status = 'running') {
  if (!logsElRef.value) return

  const item = document.createElement('div')
  item.className = 'log-item'
  if (status === 'done') item.classList.add('done')
  if (status === 'output') item.classList.add('output')
  if (status === 'error') item.classList.add('error')

  const badge = document.createElement('span')
  badge.className = 'badge'
  badge.textContent = status === 'done' ? '完成' :
      status === 'output' ? '输出' :
          status === 'error' ? '错误' : '执行'

  const content = document.createElement('span')
  content.className = 'text'
  content.textContent = text

  item.appendChild(badge)
  item.appendChild(content)
  logsElRef.value.appendChild(item)

  // 自动滚动
  logsElRef.value.scrollTop = logsElRef.value.scrollHeight
  checkState.logContent = logsElRef.value.innerHTML
}

function restoreLogs() {
  if (logsElRef.value && checkState.logContent) {
    logsElRef.value.innerHTML = checkState.logContent
    logsElRef.value.scrollTop = logsElRef.value.scrollHeight
  }
}

const toggleDetails = () => {
  showDetails.value = !showDetails.value
}

async function initExecution() {
  if (running.value || loading.value) return
  running.value = true
  clearLogs()
  checkState.title = '正在执行……'
  checkState.subTitle = '请稍候，审查即将完成'
  checkState.complete = false
  checkState.paused = false

  try {
    appendLog('正在获取审查配置数据……', 'running')
    checkState.outputsData = await fetchOutputs()
    if (checkState.error) {
      appendLog(`数据加载失败：${checkState.error}`, 'error')
    }
    appendLog('数据加载完成，请点击下一步执行第1部分', 'done')
    checkState.hasInited = true
  } catch (err) {
    appendLog(`执行出错：${err.message}`, 'error')
    checkState.paused = true
  } finally {
    running.value = false
  }
}

async function executeSingleStep(stepIndex) {
  if (running.value || loading.value || stepIndex >= parts.length) return
  running.value = true
  try {
    appendLog(parts[stepIndex], 'running')
    await delay(1200)
    const outputText = checkState.outputsData[stepIndex] || `生成内容：第${stepIndex+1}部分执行结果`
    appendLog(outputText, 'output')
    await delay(600)
    appendLog(`第${stepIndex + 1}部分执行完成`, 'done')

    if (stepIndex === parts.length - 1) {
      checkState.complete = true
      checkState.paused = true
      checkState.title = '已完成审查'
      checkState.subTitle = '审查已结束，点击背景即可退出弹窗'
    }
  } finally {
    running.value = false
  }
}

async function handleNextStep() {
  if (checkState.currentStep === -1) {
    await initExecution()
    checkState.currentStep = 0
    return
  }
  if (checkState.currentStep < parts.length) {
    await executeSingleStep(checkState.currentStep)
    checkState.currentStep += 1
  }
}

function handleBackdropClick(e) {
  if (e.target === e.currentTarget && !running.value) {
    emit('close')
  }
}

function resetCheckProcess() {
  checkState.title = '准备开始审查'
  checkState.subTitle = '请点击下一步按钮启动审查流程'
  checkState.complete = false
  checkState.paused = false
  checkState.currentStep = -1
  checkState.outputsData = []
  checkState.logContent = ''
  checkState.hasInited = false
  clearLogs()
  running.value = false
}

watch(() => props.visible, (newVal) => {
  if (newVal) {
    nextTick(() => {
      checkState.hasInited ? restoreLogs() : clearLogs()
    })
  }
})
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex; justify-content: center; align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal {
  width: 80%; max-width: 800px;
  height: 80%; max-height: 700px;
  background-color: #ffffff;
  border-radius: 16px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
  display: flex; flex-direction: column;
  overflow: hidden;
}

.modal-header {
  padding: 24px;
  background-color: #ffffff;
  border-bottom: 1px solid #f0f0f0;
  position: relative;
}

.modal-header h2 { margin: 0 0 8px 0; font-size: 22px; color: #1a1a1a; }
.modal-header .sub { margin: 0 0 20px 0; color: #666; font-size: 14px; }

.btn-group { display: flex; align-items: center; gap: 12px; margin-bottom: 4px; }
.main-btn-group { display: flex; gap: 10px; }

/* 按钮通用样式微调 */
.detail-btn, .next-btn, .reset-btn {
  height: 38px; border-radius: 8px; font-weight: 500; transition: all 0.2s;
}

.modal-body {
  flex: 1;
  padding: 20px;
  background-color: #f8f9fb; /* 浅灰色背景衬托白色卡片 */
  overflow: hidden;
}

/* 日志容器：隐藏原生滚动条，美化 UI */
.logs {
  width: 100%; height: 100%;
  overflow-y: auto;
  padding-right: 8px;
  display: flex;
  flex-direction: column;
  gap: 12px; /* 卡片之间的间距 */
}

/* 核心：日志卡片样式 */
:deep(.log-item) {
  background: #ffffff;
  border: 1px solid #eef0f2;
  border-left: 4px solid #3b82f6; /* 默认蓝色执行条 */
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  align-items: flex-start;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 徽章样式 */
:deep(.badge) {
  flex-shrink: 0;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: bold;
  margin-right: 12px;
  background: #eff6ff;
  color: #3b82f6;
  text-transform: uppercase;
}

:deep(.text) {
  font-family: "PingFang SC", "Microsoft YaHei", monospace;
  font-size: 13.5px;
  color: #334155;
  line-height: 1.6;
  word-break: break-all;
}

/* 不同状态的卡片色 */
:deep(.log-item.done) {
  border-left-color: #10b981;
  background-color: #f0fdf4;
}
:deep(.log-item.done .badge) { background: #dcfce7; color: #10b981; }

:deep(.log-item.output) {
  border-left-color: #f59e0b;
  background-color: #fffbeb;
}
:deep(.log-item.output .badge) { background: #fef3c7; color: #d97706; }

:deep(.log-item.error) {
  border-left-color: #ef4444;
  background-color: #fef2f2;
}
:deep(.log-item.error .badge) { background: #fee2e2; color: #ef4444; }

/* 加载动画 */
.loader { position: absolute; top: 30px; right: 30px; }
.ring {
  width: 45px; height: 45px;
  border: 4px solid #f3f3f3; border-top: 4px solid #3b82f6;
  border-radius: 50%; animation: spin 1s linear infinite;
}
.ring.complete { border-top-color: #10b981; animation: none; }
@keyframes spin { 100% { transform: rotate(360deg); } }

/* 滚动条美化 */
.logs::-webkit-scrollbar { width: 6px; }
.logs::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>