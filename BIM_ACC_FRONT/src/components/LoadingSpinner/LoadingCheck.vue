<template>
  <div class="modal-backdrop" :style="{ display: visible ? 'flex' : 'none' }" @click="handleBackdropClick">
    <div class="modal">
      <div class="modal-header">
        <h2>{{ title }}</h2>
        <p class="sub">{{ subTitle }}</p>
        <el-button class="detail-btn" @click="showDetails = true">查看详情</el-button>
        <div class="loader">
          <div class="ring" :class="{ complete, paused }" id="ring"></div>
        </div>
      </div>
      <div class="modal-body">
        <div class="logs" id="logs" aria-live="polite" aria-atomic="true"></div>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <Check_details
        v-if="showDetails"
        :visible="showDetails"
        @close="showDetails = false"
    />

  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import Check_details from "@/components/PopUp/Check_details.vue";
// 导入详情组件

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

// 新增：控制详情弹窗显示状态
const showDetails = ref(false)

// 原有状态管理
const title = ref('正在执行……')
const subTitle = ref('请稍候，审查即将完成')
const complete = ref(false)
const paused = ref(false)
const running = ref(false)
const logsEl = ref(null)
const loading = ref(false)
const error = ref('')

// 审查步骤（不变）
const parts = [
  '正在执行第一部分，规范类型识别......',
  '正在执行第二部分，规范实体识别......',
  '正在执行第三部分，IFC类型识别......',
  '正在执行第四部分，IFC实体属性识别......',
  '正在执行第五部分，规范实体与条文对齐......',
  '正在执行第六部分，规范实体与IFC属性增强对齐......',
  '正在执行第七部分，构建实体对齐元组......',
  '正在执行第八bimlogiqbimlogiqbimlogiqbimlogiq部分，进行合规性审查......',
]

// 从后端获取outputs数据（不变）
const fetchOutputs = async () => {
  try {
    loading.value = true
    error.value = ''
    const response = await fetch('http://localhost:5000/check/rusults', {
      method: 'POST',
    })

    if (!response.ok) {
      throw new Error(`网络错误：${response.status}`)
    }

    const data = await response.json()
    console.log(data)

    if (data.code !== 200) {
      throw new Error(data.msg || '获取审查结果失败')
    }

    return data.outputs
  } catch (err) {
    error.value = err.message
    console.error('获取审查结果失败：', err)
    // 返回默认数据作为降级处理
    return [
      null
    ]
  } finally {
    loading.value = false
  }
}

// 延迟函数（不变）
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// 清空日志（不变）
function clearLogs() {
  if (logsEl.value) {
    logsEl.value.innerHTML = ''
  }
}

// 添加日志项（不变）
function appendLog(text, status = 'running') {
  if (!logsEl.value) return

  const item = document.createElement('div')
  item.className = 'log-item'
  if (status === 'done') item.classList.add('done')
  if (status === 'output') item.classList.add('output')
  if (status === 'error') item.classList.add('error')

  const badge = document.createElement('span')
  badge.className = 'badge'
  badge.textContent = status === 'done' ? '完成' :
      status === 'output' ? '输出' :
          status === 'error' ? '错误' : '执行中'

  const content = document.createElement('span')
  content.className = 'text'
  content.textContent = text

  item.appendChild(badge)
  item.appendChild(content)
  logsEl.value.appendChild(item)
  logsEl.value.scrollTop = logsEl.value.scrollHeight
}

// 执行审查流程（不变）
async function runExecution() {
  if (running.value || loading.value) return

  running.value = true
  clearLogs()
  title.value = '正在执行……'
  subTitle.value = '请稍候，审查即将完成'
  complete.value = false
  paused.value = false

  try {
    appendLog('正在获取审查配置数据……', 'running')
    const outputs = await fetchOutputs()

    if (error.value) {
      appendLog(`数据加载失败，使用默认配置：${error.value}`, 'error')
      await delay(1000)
    }

    for (let i = 0; i < parts.length; i++) {
      if (paused.value) break

      appendLog(parts[i], 'running')
      await delay(1200)

      const outputText = outputs[i] || `生成内容：第${i+1}部分执行结果（无数据）`
      appendLog(outputText, 'output')
      await delay(600)

      appendLog(`第${i + 1}部分执行完成\n`, 'done')
      await delay(400)
    }

    appendLog('全部执行完成', 'done')
    paused.value = true
    complete.value = true
    title.value = '已完成审查'
    subTitle.value = '审查已结束，点击背景即可退出弹窗'

  } catch (err) {
    console.error('执行审查流程失败：', err)
    appendLog(`执行出错：${err.message}`, 'error')
    title.value = '执行失败'
    subTitle.value = '点击背景关闭弹窗，稍后重试'
    paused.value = true
  } finally {
    running.value = false
    loading.value = false
  }
}

// 点击背景关闭（不变）
function handleBackdropClick(e) {
  if (e.target === e.currentTarget && !running.value) {
    emit('close')
  }
}

// 当组件显示时初始化日志容器（不变）
onMounted(() => {
  nextTick(() => {
    logsEl.value = document.getElementById('logs')
  })
})

// 监听显示状态变化（不变）
watch(() => props.visible, (newVal) => {
  if (newVal && !running.value && !loading.value) {
    error.value = ''
    paused.value = false
    complete.value = false
    runExecution()
  }
})
</script>

<style scoped>
/* 原有样式不变 */
/* 弹窗背景 */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

/* 模态框主体 */
.modal {
  width: 80%;
  max-width: 800px;
  height: 80%;
  max-height: 600px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0;
}

/* 模态框头部 */
.modal-header {
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
  background-color: #f9fafb;
  position: relative;
}

.modal-header h2 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: #111827;
}

.modal-header .sub {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: #6b7280;
  line-height: 1.5;
}

/* 查看详情按钮 */
.detail-btn {
  margin-bottom: 16px;
  background-color: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.detail-btn:hover {
  background-color: #1d4ed8;
}

/* 加载动画容器 */
.loader {
  position: absolute;
  top: 24px;
  right: 24px;
  width: 40px;
  height: 40px;
}

/* 环形加载动画 */
.ring {
  width: 40px;
  height: 40px;
  border: 4px solid #e5e7eb;
  border-top: 4px solid #2563eb;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  transition: all 0.3s ease;
}

/* 完成状态 */
.ring.complete {
  border-top-color: #10b981;
  animation: none;
  transform: rotate(0deg);
}

/* 暂停状态 */
.ring.paused {
  animation-play-state: paused;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 模态框内容区（日志容器） */
.modal-body {
  flex: 1;
  padding: 16px 24px;
  overflow: hidden;
}

/* 日志容器 */
.logs {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  background-color: #f9fafb;
  border-radius: 8px;
  padding: 16px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
  scrollbar-width: thin;
  scrollbar-color: #9ca3af #e5e7eb;
}

/* 日志滚动条样式（webkit） */
.logs::-webkit-scrollbar {
  width: 6px;
}

.logs::-webkit-scrollbar-track {
  background: #e5e7eb;
  border-radius: 3px;
}

.logs::-webkit-scrollbar-thumb {
  background: #9ca3af;
  border-radius: 3px;
}

.logs::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}


/* 执行中状态 */
.log-item .badge {
  background-color: #dbeafe;
  color: #2563eb;
}

/* 完成状态 */
.log-item.done .badge {
  background-color: #d1fae5;
  color: #059669;
}

/* 输出状态 */
.log-item.output .badge {
  background-color: #fef3c7;
  color: #d97706;
}

/* 错误状态 */
.log-item.error .badge {
  background-color: #fee2e2;
  color: #dc2626;
}


/* 不同状态的文本颜色 */
.log-item.done .text {
  color: #065f46;
}

.log-item.output .text {
  color: #92400e;
}

.log-item.error .text {
  color: #b91c1c;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .modal {
    width: 95%;
    height: 90%;
  }

  .modal-header {
    padding: 16px;
  }

  .loader {
    position: static;
    margin-top: 16px;
  }

  .modal-header h2 {
    font-size: 18px;
  }

  .logs {
    padding: 12px;
    font-size: 12px;
  }

}
</style>