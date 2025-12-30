<template>
  <aside class="control-card">
    <div class="card-header">
      <span class="card-title">规范条文管理</span>
      <div class="card-divider"></div>
    </div>

    <div class="rules-container">
      <!-- 上传按钮 -->
      <el-upload
          class="upload-btn"
          accept=".pdf,.doc,.docx,.txt,.json"
          :show-file-list="true"
          :auto-upload="true"
          :action="uploadUrl"
          :on-error="handleUploadError"
          :on-success="handleUploadSuccess"
      >
        <el-button
            type="success"
            plain
            icon="Upload"
            class="rules-button"
            :class="{ 'hover-active': isUploadHover }"
            @mouseenter="isUploadHover = true"
            @mouseleave="isUploadHover = false"
        >
          上传规范条文
        </el-button>
      </el-upload>

      <!-- 规范条文解析按钮 -->
      <el-button
          type="success"
          plain
          class="analysis-rules rules-button"
          :class="{ 'hover-active': isAnalysisHover }"
          @click="handleAnalyzeRules"
          @mouseenter="isAnalysisHover = true"
          @mouseleave="isAnalysisHover = false"
      >
        解析所有规范条文
      </el-button>

      <!-- 新增：查看条文按钮 -->
      <el-button
          type="info"
          plain
          class="rules-button"
          :class="{ 'hover-active': isDatabaseHover }"
          @click="handleViewDatabases"
          @mouseenter="isDatabaseHover = true"
          @mouseleave="isDatabaseHover = false"
      >
        查看条文
      </el-button>
    </div>
  </aside>
</template>

<script setup>
import { defineEmits, ref } from 'vue'
import { ElMessage, ElLoading } from 'element-plus'

const emit = defineEmits(['find-rules', 'view-databases', 'view-database-info'])

// 上传接口地址
const uploadUrl = ref('http://localhost:5000/rules/uploads')

// hover状态管理
const isUploadHover = ref(false)
const isAnalysisHover = ref(false)
const isDatabaseHover = ref(false)  // 新增按钮的hover状态

// 上传错误处理
function handleUploadError(error) {
  const errorMsg = error.response?.data?.message || '文件上传失败，请重试'
  ElMessage.error(errorMsg)
}

// 上传成功处理
function handleUploadSuccess(response) {
  if (response.success) {
    ElMessage.success('文件上传成功')
  } else {
    ElMessage.error(response.message || '文件上传失败')
  }
}

// 新增：查看数据库列表
function handleViewDatabases() {
  emit('view-databases')
}

// 解析规范条文处理函数
async function handleAnalyzeRules() {
  // 显示加载状态
  const loading = ElLoading.service({
    lock: true,
    text: '正在解析规范条文...',
    background: 'rgba(15, 23, 42, 0.8)'
  })

  try {
    // 发送GET请求到解析接口
    const response = await fetch('http://localhost:5000/rules/analysis')

    if (!response.ok) {
      throw new Error(`HTTP错误，状态码: ${response.status}`)
    }

    const result = await response.json()

    // 根据返回结果显示不同的提示信息
    if (result.status === 'completed') {
      ElMessage.success(`解析完成，共处理 ${result.total_files} 个文件`)
    } else if (result.status === 'warning') {
      ElMessage.warning(result.message)
    } else if (result.status === 'error') {
      ElMessage.error(result.message)
    }
  } catch (error) {
    console.error('解析请求失败:', error)
    ElMessage.error('解析规范条文失败，请稍后重试')
  } finally {
    // 关闭加载状态
    loading.close()
  }
}
</script>

<style scoped>
/* 核心暗系样式 */
.control-card {
  position: fixed;
  top: 55%;
  left: 1.5rem;
  transform: translateY(-50%);
  width: 290px;
  max-width: 90vw;
  height: 88vh;
  max-height: 750px;
  background: rgba(15, 15, 25, 0.96);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(60, 60, 80, 0.5);
  border-radius: 22px;
  padding: 1.5rem 1rem;
  overflow-y: auto;
  z-index: 999;
  box-shadow: 0 0 30px rgba(0, 0, 0, 0.4),
  inset 0 0 1px rgba(255, 255, 255, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 悬浮放大+霓虹效果 */
.control-card:hover {
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.5),
  0 0 15px rgba(124, 58, 237, 0.15),
  inset 0 0 1px rgba(255, 255, 255, 0.15);
  transform: translateY(-50%) scale(1.01);
}

/* 卡片头部 */
.card-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(60, 60, 80, 0.5);
  position: relative;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: #e0e0ff;
  display: flex;
  align-items: center;
  gap: 8px;
  letter-spacing: 0.5px;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.1);
}

.card-divider {
  width: 50px;
  height: 3px;
  background: linear-gradient(90deg, #7c3aed, #4f46e5, #7c3aed);
  background-size: 200% auto;
  border-radius: 3px;
  margin-top: 8px;
  box-shadow: 0 0 10px rgba(124, 58, 237, 0.5);
  animation: gradientShift 3s ease infinite;
}

/* 按钮容器 - 调整布局和间距 */
.rules-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem; /* 增加按钮间距 */
  padding: 0 1rem; /* 调整左右内边距 */
  position: relative;
  top: 10%; /* 按钮整体向下偏移 */
  transform: translateY(-10%);
}

/* 按钮样式 - 调整大小和比例 */
.rules-button {
  width: 90%; /* 按钮宽度改为90%，居中显示 */
  height: 55px; /* 增加按钮高度 */
  line-height: 55px;
  margin: 0 auto; /* 按钮居中 */
  border-radius: 15px; /* 增大圆角 */
  border: 1px solid rgba(124, 58, 237, 0.2);
  background: rgba(30, 41, 59, 0.6);
  color: #e2e8f0;
  font-size: 1rem; /* 增大字体 */
  font-weight: 500;
  letter-spacing: 0.3px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

/* 按钮hover效果 */
.rules-button.hover-active {
  background: linear-gradient(135deg, rgba(45, 35, 80, 0.8), rgba(35, 25, 70, 0.8)) !important;
  border-color: #9333ea !important;
  color: #f8fafc;
  transform: translateY(-3px); /* 增大上浮距离 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
  width: 92%; /* hover时轻微加宽 */
}

/* 按钮点击波纹效果 */
.rules-button::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(74, 222, 128, 0.2);
  transform: translate(-50%, -50%);
  transition: width 0.6s ease, height 0.6s ease;
}

.rules-button:active::after {
  width: 300px;
  height: 300px;
  opacity: 0;
}

/* 修改element-plus按钮默认样式 */
:deep(.el-button) {
  --el-button-text-color: #e2e8f0;
  --el-button-hover-text-color: #f8fafc;
  --el-button-bg-color: transparent;
  --el-button-hover-bg-color: transparent;
  --el-button-border-color: transparent;
  --el-button-hover-border-color: transparent;
  font-size: 1rem;
}

:deep(.el-button--success) {
  --el-button-text-color: #e2e8f0;
}

:deep(.el-button--info) {
  --el-button-text-color: #e2e8f0;
}

/* 上传组件样式适配 */
:deep(.upload-btn) {
  width: 100%;
  justify-content: center;
}

/* 滚动条美化 */
.control-card::-webkit-scrollbar {
  width: 4px;
}

.control-card::-webkit-scrollbar-track {
  background: rgba(30, 30, 45, 0.5);
  border-radius: 3px;
}

.control-card::-webkit-scrollbar-thumb {
  background: rgba(100, 116, 139, 0.5);
  border-radius: 3px;
  transition: all 0.2s;
}

.control-card::-webkit-scrollbar-thumb:hover {
  background: rgba(124, 58, 237, 0.6);
  width: 8px;
  box-shadow: 0 0 10px rgba(124, 58, 237, 0.4);
}
</style>