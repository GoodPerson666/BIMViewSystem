<template>
  <aside class="control-card" v-if="!isMobile || showPanel" :class="{ 'mobile-expanded': isMobile && showPanel }">

    <div class="card-header">
      <span class="card-title">
        <el-icon class="title-icon"><files /></el-icon> BIM 模型管理
      </span>
      <div class="card-divider"></div>
      <el-button
          v-if="isMobile"
          size="small"
          circle
          @click="handleTogglePanel(false)"
          class="close-btn"
          :class="{ 'hover-active': isCloseHover }"
          @mouseenter="isCloseHover = true"
          @mouseleave="isCloseHover = false"
      >
        <el-icon><Close /></el-icon>
      </el-button>
    </div>

    <div class="control-section">
      <el-upload
          class="upload-block"
          accept=".ifc"
          :show-file-list="false"
          :before-upload="handleBeforeUpload"
      >
        <el-button
            type="primary"
            plain
            icon="Upload"
            class="action-btn full-width main-action"
            :class="{ 'hover-active': isUploadHover }"
            @mouseenter="isUploadHover = true"
            @mouseleave="isUploadHover = false"
        >上传 IFC 文件</el-button>
      </el-upload>

      <transition name="el-fade-in">
        <div class="grid-actions" v-if="modelLoaded">
          <el-button
              type="success"
              plain
              icon="Check"
              @click="handleCompliance"
              class="grid-btn"
              :class="{ 'hover-active': isComplianceHover }"
              @mouseenter="isComplianceHover = true"
              @mouseleave="isComplianceHover = false">合规
          </el-button>

          <el-button
              type="danger"
              plain
              icon="Close"
              @click="handleNonCompliance"
              class="grid-btn"
              :class="{ 'hover-active': isNonComplianceHover }"
              @mouseenter="isNonComplianceHover = true"
              @mouseleave="isNonComplianceHover = false">不合规
          </el-button>

          <el-button
              type="info"
              plain
              icon="Help"
              @click="handleNormal"
              class="grid-btn"
              :class="{ 'hover-active': isNormalHover }"
              @mouseenter="isNormalHover = true"
              @mouseleave="isNormalHover = false">不适用
          </el-button>

          <el-button
              type="warning"
              plain
              icon="RefreshLeft"
              @click="handleClearColor"
              class="grid-btn"
              :class="{ 'hover-active': isClearHover }"
              @mouseenter="isClearHover = true"
              @mouseleave="isClearHover = false">重置颜色
          </el-button>
        </div>
      </transition>
    </div>

    <div class="section-header">
      <span class="section-title">所选构件</span>
    </div>

    <div class="info-panel-container">
      <el-empty v-if="!localId" description="点击模型选取构件" :image-size="40" class="custom-empty" />

      <div v-else class="selected-content">
        <div class="info-card">
          <div class="info-label">构件名称</div>
          <div class="info-value ellipsis" :title="selectedName || '未命名构件'">
            {{ selectedName || '未命名构件' }}
          </div>
        </div>

        <div class="element-actions">
          <el-button
              type="primary"
              size="default"
              :disabled="!localId"
              @click="handleLogAttributes"
              class="action-btn full-width mb-2"
              :class="{ 'hover-active': isAttrHover }"
              @mouseenter="isAttrHover = true"
              @mouseleave="isAttrHover = false"
          >
            <el-icon class="mr-1"><Search /></el-icon> 查看审查结果
          </el-button>

          <div class="flex-row">
            <el-button
                type="primary"
                plain
                size="small"
                :disabled="!localId"
                @click="handleLogPsets"
                class="action-btn flex-1"
                :class="{ 'hover-active': isPsetHover }"
                @mouseenter="isPsetHover = true"
                @mouseleave="isPsetHover = false"
            >详细属性</el-button>

            <div
                class="checkbox-wrapper"
                :class="{ 'hover-active': isFormatHover }"
                @mouseenter="isFormatHover = true"
                @mouseleave="isFormatHover = false"
            >
              <el-checkbox
                  :checked="formatPset"
                  @change="handleToggleFormatPset"
                  class="custom-checkbox"
                  size="small"
              >格式化</el-checkbox>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="section-header mt-4">
      <span class="section-title">类别筛选</span>
    </div>

    <div class="category-panel">
      <el-select
          :model-value="currentCategory"
          placeholder="选择 IFC 类别"
          style="width: 100%"
          @change="handleChangeCategory"
          class="category-select custom-select-dark"
          popper-class="dark-popper"
          :class="{ 'hover-active': isSelectHover }"
          @mouseenter="isSelectHover = true"
          @mouseleave="isSelectHover = false"
      >
        <el-option
            v-for="c in categories"
            :key="c"
            :label="c"
            :value="c"
        />
      </el-select>

      <div class="category-actions-grid">
        <el-button
            size="small"
            @click="handleLogNames"
            icon="List"
            class="action-btn full-span"
            :class="{ 'hover-active': isNamesHover }"
            @mouseenter="isNamesHover = true"
            @mouseleave="isNamesHover = false"
        >输出类别名称列表</el-button>

        <el-button
            size="small"
            type="primary"
            plain
            @click="handleLogGeometries"
            class="action-btn"
            :class="{ 'hover-active': isGeoHover }"
            @mouseenter="isGeoHover = true"
            @mouseleave="isGeoHover = false"
        >加载类别</el-button>

        <el-button
            size="small"
            type="danger"
            plain
            @click="handleDisposeMeshes"
            class="action-btn"
            :class="{ 'hover-active': isDisposeHover }"
            @mouseenter="isDisposeHover = true"
            @mouseleave="isDisposeHover = false"
        >清除类别</el-button>
      </div>
    </div>
  </aside>

  <el-button
      v-if="isMobile && !showPanel"
      class="fab"
      circle
      size="large"
      @click="handleTogglePanel(true)"
      :class="{ 'fab-active': showPanel, 'hover-active': isFabHover }"
      @mouseenter="isFabHover = true"
      @mouseleave="isFabHover = false"
  >
    <el-icon><Setting /></el-icon>
  </el-button>
</template>

<script setup>
import { Setting, Close, Search, Files } from '@element-plus/icons-vue'
import { ref } from 'vue'

// 新增模型加载状态
const modelLoaded = ref(false)
// hover状态管理 (保持原逻辑)
const isCloseHover = ref(false)
const isUploadHover = ref(false)
const isComplianceHover = ref(false)
const isNonComplianceHover = ref(false)
const isNormalHover = ref(false)
const isClearHover = ref(false)
const isAttrHover = ref(false)
const isPsetHover = ref(false)
const isFormatHover = ref(false)
const isSelectHover = ref(false)
const isNamesHover = ref(false)
const isGeoHover = ref(false)
const isDisposeHover = ref(false)
const isFabHover = ref(false)

// 接收父组件的参数
defineProps({
  categories: { type: Array, default: () => [] },
  localId: { type: [String, Number, null], default: null },
  selectedName: { type: String, default: null },
  isMobile: { type: Boolean, default: false },
  showPanel: { type: Boolean, default: false },
  currentCategory: { type: String, default: '' },
  formatPset: { type: Boolean, default: true }
})

const emit = defineEmits([
  'toggle-panel', 'change-category', 'toggle-format-pset',
  'log-attributes', 'log-psets', 'log-names', 'log-geometries', 'dispose-meshes',
  'upload-ifc', 'get-compliance', 'get-noncompliance', 'get-normal', 'clear-color', 'find-rules'
])

// 事件处理函数保持不变
function handleBeforeUpload(file) {
  emit('upload-ifc', file)
  modelLoaded.value = true
  return false
}
function handleCompliance() { emit('get-compliance') }
function handleNonCompliance() { emit('get-noncompliance') }
function handleNormal() { emit('get-normal') }
function handleClearColor() { emit('clear-color') }
function handleTogglePanel(show) { emit('toggle-panel', show) }
function handleChangeCategory(value) { emit('change-category', value) }
function handleToggleFormatPset(value) { emit('toggle-format-pset', value) }
function handleLogAttributes() { emit('log-attributes') }
function handleLogPsets() { emit('log-psets') }
function handleLogNames() { emit('log-names') }
function handleLogGeometries() { emit('log-geometries') }
function handleDisposeMeshes() { emit('dispose-meshes') }
</script>

<style scoped>
/* --- 核心卡片容器 --- */
.control-card {
  position: fixed;
  top: 55%;
  right: 1.5rem;
  transform: translateY(-50%);
  width: 300px; /* 稍微加宽一点点以适应Grid */
  max-width: 90vw;
  height: auto;
  max-height: 85vh;
  background: rgba(15, 15, 25, 0.95); /* 加深一点背景 */
  backdrop-filter: blur(24px);
  border: 1px solid rgba(80, 80, 100, 0.4);
  border-radius: 20px;
  padding: 1.5rem 1.25rem;
  overflow-y: auto;
  z-index: 999;
  box-shadow:
      0 20px 50px rgba(0, 0, 0, 0.6),
      inset 0 1px 0 rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* 隐藏滚动条但保留功能 */
.control-card::-webkit-scrollbar {
  width: 4px;
}
.control-card::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.1);
  border-radius: 4px;
}

/* --- 头部区域 --- */
.card-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 0.5rem;
  position: relative;
}
.card-title {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 10px;
  letter-spacing: 1px;
  text-shadow: 0 0 15px rgba(124, 58, 237, 0.5);
}
.title-icon { font-size: 20px; color: #a78bfa; }

/* 动态分割线 */
.card-divider {
  width: 40px;
  height: 3px;
  background: linear-gradient(90deg, #7c3aed, #4f46e5);
  border-radius: 10px;
  margin-top: 12px;
  box-shadow: 0 0 12px rgba(124, 58, 237, 0.6);
}

/* --- 分区标题 --- */
.section-header {
  display: flex;
  align-items: center;
  margin: 8px 0;
}
.section-title {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 1.5px;
  font-weight: 600;
}
.section-header::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
  margin-left: 10px;
}

/* --- 1. 全局操作区布局 --- */
.control-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.upload-block {
  width: 100%;
  display: flex;           /* 启用 Flex 布局 */
  justify-content: center; /* 核心代码：水平居中 */
  margin-bottom: 12px;     /* 保持原有间距 */
}

/* 2. 修改按钮宽度：不再强制全宽，而是设置一个合适的宽度 */
.main-action {
  width: 200px;            /* 设置固定宽度，或者用 80% */
  height: 38px;
  font-weight: 600;
  letter-spacing: 1px;
  /* 移除原本可能存在的 width: 100% 或 flex: 1 */
}

/* 2x2 Grid 布局 */
.grid-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.grid-btn {
  margin: 0 !important; /* 覆盖Element默认margin */
  width: 100%;
  justify-content: center;
  border-style: dashed;
  border-width: 1px;
  background: transparent;
}
.grid-btn:hover {
  border-style: solid;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

/* --- 2. 构件信息面板 --- */
.info-panel-container {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}
.custom-empty {
  padding: 10px 0;
  :deep(.el-empty__description) { color: rgba(255,255,255,0.4); }
}

/* 内部信息卡片 */
.info-card {
  background: rgba(124, 58, 237, 0.1);
  border-left: 3px solid #7c3aed;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 12px;
}
.info-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 2px;
}
.info-value {
  font-size: 14px;
  color: #fff;
  font-weight: 500;
}

/* 按钮组 */
.element-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.full-width { width: 100%; }
.flex-row {
  display: flex;
  gap: 8px;
  align-items: center;
}
.flex-1 { flex: 1; }

.checkbox-wrapper {
  background: rgba(255,255,255,0.05);
  padding: 0 10px;
  height: 24px; /* matching small button height mostly */
  display: flex;
  align-items: center;
  border-radius: 4px;
  border: 1px solid transparent;
  transition: all 0.3s;
}
.checkbox-wrapper:hover {
  border-color: rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.1);
}
:deep(.el-checkbox__label) { color: rgba(255,255,255,0.7); font-size: 12px; }

/* --- 3. 类别区布局 --- */
.category-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.category-actions-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.full-span {
  grid-column: span 2;
  background: rgba(255,255,255,0.03);
  border: none;
  color: rgba(255,255,255,0.7);
}
.full-span:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
}

/* --- 通用样式 --- */
.ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.mr-1 { margin-right: 4px; }
.mb-2 { margin-bottom: 8px; }
.mt-4 { margin-top: 16px; }

/* 按钮悬停动画类 (保留原逻辑增强) */
.hover-active {
  transform: translateY(-1px);
  filter: brightness(1.2);
}

/* 关闭按钮 */
.close-btn {
  position: absolute;
  top: 0;
  right: 0;
  background: transparent;
  border: none;
  color: rgba(255,255,255,0.5);
}
.close-btn:hover { color: #fff; background: rgba(255,255,255,0.1); }

/* 移动端 FAB */
.fab {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  width: 56px;
  height: 56px;
  background: #7c3aed;
  box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4);
  border: none;
  z-index: 990;
  font-size: 24px;
  color: #fff;
}
</style>