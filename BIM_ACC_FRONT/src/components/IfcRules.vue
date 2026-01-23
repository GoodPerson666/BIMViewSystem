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

// 查看数据库列表
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
    loading.close()
  }
}
</script>

<style scoped>
/* 全局盒模型统一，避免边框/内边距影响尺寸 */
* {
  box-sizing: border-box;
}

/* 核心暗系样式 */
.control-card {
  position: fixed;
  top: 55%;
  left: 1.5rem;
  transform: translateY(-50%);
  width: 290px;
  max-width: 90vw;
  height: 60vh;
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

/* ========== 上传按钮样式（完全匹配其他按钮） ========== */
.upload-btn {
  width: 90%;
  margin: 0 auto;
  display: block;
  padding: 0; /* 清除el-upload默认内边距 */
}

/* 覆盖el-upload内部容器样式 */
.upload-btn :deep(.el-upload) {
  width: 100%;
  height: 100%;
  display: block;
  padding: 0;
  margin: 0;
}

/* 强制覆盖el-upload内部按钮样式 */
.upload-btn :deep(.el-button) {
  width: 100% !important;
  height: 55px !important;
  line-height: 55px !important;
  border-radius: 15px !important;
  border: 1px solid rgba(124, 58, 237, 0.2) !important;
  background: rgba(30, 41, 59, 0.6) !important;
  color: #e2e8f0 !important;
  font-size: 1rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.3px !important;
  transition: all 0.3s ease !important;
  position: relative !important;
  overflow: hidden !important;
  padding: 0 !important; /* 清除默认内边距 */
  margin: 0 !important;  /* 清除默认外边距 */
  box-sizing: border-box !important;
  justify-content: center !important;
  align-items: center !important;
}

/* 上传按钮hover效果 */
.upload-btn :deep(.el-button):hover {
  background: linear-gradient(135deg, rgba(45, 35, 80, 0.8), rgba(35, 25, 70, 0.8)) !important;
  border-color: #9333ea !important;
  color: #f8fafc !important;
  transform: translateY(-3px) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
  width: 100% !important;
  height: 55px !important;
}

/* 上传按钮点击波纹效果 */
.upload-btn :deep(.el-button)::after {
  content: '' !important;
  position: absolute !important;
  top: 50% !important;
  left: 50% !important;
  width: 0 !important;
  height: 0 !important;
  border-radius: 50% !important;
  background: rgba(74, 222, 128, 0.2) !important;
  transform: translate(-50%, -50%) !important;
  transition: width 0.6s ease, height 0.6s ease !important;
}

.upload-btn :deep(.el-button):active::after {
  width: 300px !important;
  height: 300px !important;
  opacity: 0 !important;
}

/* ========== 普通按钮样式 ========== */
.rules-button {
  width: 90%;
  height: 55px;
  line-height: 55px;
  margin: 0 auto;
  border-radius: 15px;
  border: 1px solid rgba(124, 58, 237, 0.2);
  background: rgba(30, 41, 59, 0.6);
  color: #e2e8f0;
  font-size: 1rem;
  font-weight: 500;
  letter-spacing: 0.3px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-sizing: border-box;
  padding: 0;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 普通按钮hover效果 */
.rules-button.hover-active {
  background: linear-gradient(135deg, rgba(45, 35, 80, 0.8), rgba(35, 25, 70, 0.8)) !important;
  border-color: #9333ea !important;
  color: #f8fafc !important;
  transform: translateY(-3px) !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
  width: 92% !important;
}

/* 普通按钮点击波纹效果 */
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
  --el-button-text-color: #e2e8f0 !important;
  --el-button-hover-text-color: #f8fafc !important;
  --el-button-bg-color: transparent !important;
  --el-button-hover-bg-color: transparent !important;
  --el-button-border-color: transparent !important;
  --el-button-hover-border-color: transparent !important;
  font-size: 1rem !important;
}

:deep(.el-button--success) {
  --el-button-text-color: #e2e8f0 !important;
}

:deep(.el-button--info) {
  --el-button-text-color: #e2e8f0 !important;
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

/* 渐变动画 */
@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}
</style>