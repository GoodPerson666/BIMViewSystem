<template>
  <!-- 固定右侧控制面板 -->
  <aside class="control-card" v-if="!isMobile || showPanel" :class="{ 'mobile-expanded': isMobile && showPanel }">
    <div class="card-header">
      <span class="card-title">BIM模型管理</span>
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

    <!-- 整合TopBar的功能按钮 -->
    <div class="top-bar-actions">
      <el-upload
          class="upload-btn"
          accept=".ifc"
          :show-file-list="false"
          :before-upload="handleBeforeUpload"
      >
        <el-button
            type="primary"
            plain
            icon="Upload"
            class="w-full"
            :class="{ 'hover-active': isUploadHover }"
            @mouseenter="isUploadHover = true"
            @mouseleave="isUploadHover = false"
        >上传 IFC</el-button>
      </el-upload>

      <!-- 只有模型加载后才显示按钮组 -->
      <el-button-group class="button-group" v-if="modelLoaded">
        <el-button
            type="success"
            plain
            icon="Check"
            @click="handleCompliance"
            class="flex-1"
            :class="{ 'hover-active': isComplianceHover }"
            @mouseenter="isComplianceHover = true"
            @mouseleave="isComplianceHover = false"
        >合规</el-button>
        <el-button
            type="danger"
            plain
            icon="Close"
            @click="handleNonCompliance"
            class="flex-1"
            :class="{ 'hover-active': isNonComplianceHover }"
            @mouseenter="isNonComplianceHover = true"
            @mouseleave="isNonComplianceHover = false"
        >不合规</el-button>
        <el-button
            type="info"
            plain
            icon="Help"
            @click="handleNormal"
            class="flex-1"
            :class="{ 'hover-active': isNormalHover }"
            @mouseenter="isNormalHover = true"
            @mouseleave="isNormalHover = false"
        >不适用</el-button>
        <el-button
            type="primary"
            plain
            icon="RefreshLeft"
            @click="handleClearColor"
            class="flex-1"
            :class="{ 'hover-active': isClearHover }"
            @mouseenter="isClearHover = true"
            @mouseleave="isClearHover = false"
        >清空</el-button>
      </el-button-group>
    </div>

    <!-- 原有控制面板内容 -->
    <div class="section-header">
      <el-divider content-position="center" class="custom-divider">所选构件</el-divider>
    </div>
    <el-empty v-if="!localId" description="在场景中点击元素" :image-size="60" class="custom-empty" />
    <div v-else class="selected-element">
      <p class="item-name ellipsis" :title="selectedName || '未命名构件'">{{ selectedName || '未命名构件' }}</p>

      <el-button
          type="primary"
          size="small"
          :disabled="!localId"
          @click="handleLogAttributes"
          class="w-full mb-2"
          :class="{ 'hover-active': isAttrHover }"
          @mouseenter="isAttrHover = true"
          @mouseleave="isAttrHover = false"
      >构件审查结果</el-button>

      <div class="row">
        <el-button
            type="primary"
            size="small"
            :disabled="!localId"
            @click="handleLogPsets"
            class="flex-1"
            :class="{ 'hover-active': isPsetHover }"
            @mouseenter="isPsetHover = true"
            @mouseleave="isPsetHover = false"
        >构件详细信息</el-button>
        <el-checkbox
            :checked="formatPset"
            @change="handleToggleFormatPset"
            class="format-checkbox"
            size="small"
            :class="{ 'hover-active': isFormatHover }"
            @mouseenter="isFormatHover = true"
            @mouseleave="isFormatHover = false"
        >Format</el-checkbox>
      </div>
    </div>

    <div class="section-header">
      <el-divider content-position="center" class="custom-divider">类别</el-divider>
    </div>
    <el-select
        :model-value="currentCategory"
        placeholder="请选择类别"
        style="width: 100%"
        @change="handleChangeCategory"
        class="category-select"
        size="small"
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

    <div class="category-actions">
      <el-button
          size="small"
          @click="handleLogNames"
          class="action-btn"
          :class="{ 'hover-active': isNamesHover }"
          @mouseenter="isNamesHover = true"
          @mouseleave="isNamesHover = false"
      >类别名称</el-button>
      <el-button
          size="small"
          @click="handleLogGeometries"
          class="action-btn"
          :class="{ 'hover-active': isGeoHover }"
          @mouseenter="isGeoHover = true"
          @mouseleave="isGeoHover = false"
      >加载类别</el-button>
      <el-button
          size="small"
          @click="handleDisposeMeshes"
          class="action-btn danger-btn"
          :class="{ 'hover-active': isDisposeHover }"
          @mouseenter="isDisposeHover = true"
          @mouseleave="isDisposeHover = false"
      >清除类别</el-button>
    </div>
  </aside>

  <!-- 手机端浮动按钮 -->
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
import { Setting, Close } from '@element-plus/icons-vue'
import { ref } from 'vue'

// 新增模型加载状态
const modelLoaded = ref(false)

// hover状态管理
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

// 扩展事件，包含原TopBar的事件
const emit = defineEmits([
  // 原有事件
  'toggle-panel', 'change-category', 'toggle-format-pset',
  'log-attributes', 'log-psets', 'log-names', 'log-geometries', 'dispose-meshes',
  // 新增TopBar相关事件
  'upload-ifc', 'get-compliance', 'get-noncompliance', 'get-normal', 'clear-color', 'find-rules'
])

// TopBar相关事件处理
function handleBeforeUpload(file) {
  emit('upload-ifc', file)
  // 上传文件后标记模型为已加载状态
  modelLoaded.value = true
  return false
}

function handleCompliance() {
  emit('get-compliance')
}

function handleNonCompliance() {
  emit('get-noncompliance')
}

function handleNormal() {
  emit('get-normal')
}

function handleClearColor() {
  emit('clear-color')
}

// 原有控制面板事件处理
function handleTogglePanel(show) {
  emit('toggle-panel', show)
}

function handleChangeCategory(value) {
  emit('change-category', value)
}

function handleToggleFormatPset(value) {
  emit('toggle-format-pset', value)
}

function handleLogAttributes() {
  emit('log-attributes')
}

function handleLogPsets() {
  emit('log-psets')
}

function handleLogNames() {
  emit('log-names')
}

function handleLogGeometries() {
  emit('log-geometries')
}

function handleDisposeMeshes() {
  emit('dispose-meshes')
}
</script>

<style scoped>
/* 基础卡片样式 - 暗系炫酷风格增强版 */
.control-card {
  position: fixed;
  top: 55%;
  right: 1.5rem;
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
/* 卡片悬浮效果 */
.control-card:hover {
  box-shadow: 0 0 40px rgba(0, 0, 0, 0.5),
  0 0 15px rgba(124, 58, 237, 0.15),
  inset 0 0 1px rgba(255, 255, 255, 0.15);
  transform: translateY(-50%) scale(1.01);
}
/* 手机端展开样式 */
.mobile-expanded {
  width: 92vw;
  height: 92vh;
  max-height: 92vh;
  right: 50%;
  transform: translate(50%, -50%) !important;
  box-shadow: 0 0 50px rgba(0, 0, 0, 0.55),
  0 0 20px rgba(124, 58, 237, 0.2);
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
/* 渐变分隔线 - 增强视觉冲击力 */
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
@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
/* 关闭按钮（手机端） */
.close-btn {
  position: absolute;
  top: 1.5rem;
  right: 1rem;
  color: #94a3b8;
  background: rgba(60, 60, 80, 0.3) !important;
  border-radius: 50%;
  width: 34px !important;
  height: 34px !important;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.25s ease;
}
.close-btn:hover, .hover-active.close-btn {
  color: #c4b5fd;
  background: rgba(124, 58, 237, 0.3) !important;
  transform: scale(1.1);
  box-shadow: 0 0 12px rgba(124, 58, 237, 0.4) !important;
}
/* 顶部操作区 */
.top-bar-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(60, 60, 80, 0.5);
}
.upload-btn {
  width: 100%;
}
/* 按钮组样式 */
.button-group {
  width: 100%;
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

/* 空状态样式 */
.custom-empty {
  margin: 2rem 0;
  --el-empty-description-color: #94a3b8;
  --el-empty-image-size: 60px;
}
/* 选中元素样式 */
.selected-element {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: rgba(60, 60, 80, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(60, 60, 80, 0.3);
}
.item-name {
  font-weight: 500;
  color: #e2e8f0;
  margin: 0.75rem 0;
  line-height: 1.5;
  font-size: 14px;
  text-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
}
.ellipsis {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
/* 行布局 */
.row {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin: 0.8rem 0;
}
/* 类别选择器 */
.category-select {
  margin-bottom: 1.2rem;
  --el-select-input-height: 36px;
  --el-select-border-radius: 8px;
  --el-select-input-bg-color: rgba(30, 30, 45, 0.8);
  --el-select-input-text-color: #e2e8f0;
  --el-select-border-color: rgba(60, 60, 80, 0.5);
  --el-select-hover-border-color: #7c3aed;
  --el-select-dropdown-bg-color: rgba(15, 15, 25, 0.95);
  --el-select-dropdown-border-color: rgba(60, 60, 80, 0.5);
  --el-select-option-hover-bg-color: rgba(124, 58, 237, 0.1);
  transition: all 0.25s ease;
}
.category-select.hover-active {
  border-color: #7c3aed;
  box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.2);
}
/* 类别操作按钮组 */
.category-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  margin-top: 0.8rem;
}
.action-btn {
  flex: 1;
  min-width: 85px;
  transition: all 0.25s ease;
  border-radius: 8px !important;
  background: linear-gradient(135deg, rgba(35, 30, 60, 0.8), rgba(25, 20, 50, 0.8)) !important;
  border-color: rgba(100, 80, 160, 0.3) !important;
}
.action-btn:hover, .hover-active.action-btn {
  background: linear-gradient(135deg, rgba(45, 35, 80, 0.8), rgba(35, 25, 70, 0.8)) !important;
  border-color: #9333ea !important;
  color: #ddd6fe !important;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
}
/* 清除类别按钮（危险按钮） */
.danger-btn {
  color: #fca5a5;
  border-color: rgba(75, 50, 105, 0.5);
  background: linear-gradient(135deg, rgba(65, 25, 25, 0.8), rgba(55, 15, 15, 0.8)) !important;
  border-color: rgba(160, 40, 40, 0.3) !important;
}
.danger-btn:hover, .hover-active.danger-btn {
  background: linear-gradient(135deg, rgba(85, 30, 30, 0.8), rgba(75, 20, 20, 0.8)) !important;
  border-color: #ef4444 !important;
  color: #fecaca !important;
  transform: translateY(-2px);
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.3) !important;
}
/* 浮动按钮 */
.fab {
  position: fixed;
  bottom: 2.5rem;
  right: 2.5rem;
  z-index: 1000;
  width: 64px !important;
  height: 64px !important;
  background: linear-gradient(135deg, #9333ea, #6366f1) !important;
  color: white;
  box-shadow: 0 8px 25px rgba(124, 58, 237, 0.5), 0 0 15px rgba(124, 58, 237, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.15) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 50% !important;
  border: none !important;
}
.fab:hover, .hover-active.fab {
  background: linear-gradient(135deg, #a855f7, #7c3aed) !important;
  transform: translateY(-4px) scale(1.1) !important;
  box-shadow: 0 10px 30px rgba(124, 58, 237, 0.6), 0 0 20px rgba(124, 58, 237, 0.4) !important;
}
.fab-active {
  transform: rotate(90deg) scale(1.05);
}
/* 格式复选框 */
.format-checkbox {
  --el-checkbox-text-color: #94a3b8;
  --el-checkbox-checked-text-color: #c4b5fd;
  --el-checkbox-border-radius: 6px;
  --el-checkbox-border-color: rgba(60, 60, 80, 0.5);
  --el-checkbox-checked-border-color: #7c3aed;
  --el-checkbox-checked-bg-color: #7c3aed;
  margin-left: auto;
  transition: all 0.2s ease;
}
.format-checkbox.hover-active {
  --el-checkbox-text-color: #c4b5fd;
}
/* ########## 按钮样式统一优化 ########## */
/* 基础按钮样式重置 - 统一暗系炫酷风格 */
.el-button--plain {
  background: linear-gradient(135deg, rgba(40, 35, 70, 0.9), rgba(30, 25, 55, 0.9)) !important;
  border: 1px solid rgba(124, 58, 237, 0.3) !important;
  border-radius: 10px !important;
  color: #e2e8f0 !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  padding: 8px 16px !important;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.08) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  position: relative;
  overflow: hidden;
}
/* 按钮点击波纹效果 */
.el-button--plain::after {
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  width: 120%;
  height: 120%;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  transform: translate(-50%, -50%) scale(0);
  transition: transform 0.6s ease-out;
  pointer-events: none;
}
.el-button--plain:active::after {
  transform: translate(-50%, -50%) scale(1);
}
/* 通用hover效果 */
.el-button--plain:hover, .hover-active.el-button--plain {
  transform: translateY(-3px) scale(1.02) !important;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.4), 0 0 10px rgba(124, 58, 237, 0.3) !important;
  border-color: rgba(124, 58, 237, 0.6) !important;
}
/* 禁用状态样式 */
.el-button--plain.is-disabled {
  background: linear-gradient(135deg, rgba(30, 30, 45, 0.5), rgba(20, 20, 35, 0.5)) !important;
  border-color: rgba(60, 60, 80, 0.3) !important;
  color: #94a3b8 !important;
  box-shadow: none !important;
  transform: none !important;
  cursor: not-allowed;
}
/* 主按钮（上传IFC、构件审查结果等）- 紫色系 */
.hover-active.el-button--primary.is-plain {
  background: linear-gradient(135deg, rgba(70, 45, 130, 0.4), rgba(55, 35, 105, 0.4)) !important;
  border-color: #8b5cf6 !important;
  color: #c4b5fd !important;
  box-shadow: 0 0 15px rgba(124, 58, 237, 0.4) !important;
}
/* 合规按钮 - 绿色系 */
.hover-active.el-button--success.is-plain {
  background: linear-gradient(135deg, rgba(30, 65, 55, 0.4), rgba(20, 55, 45, 0.4)) !important;
  border-color: #8b5cf6 !important;
  color: #c4b5fd !important;
  box-shadow: 0 0 15px rgba(124, 58, 237, 0.4) !important;
}
/* 不合规按钮 - 红色系 */
.hover-active.el-button--danger.is-plain {
  background: linear-gradient(135deg, rgba(75, 35, 35, 0.4), rgba(65, 25, 25, 0.4)) !important;
  border-color: #f87171 !important;
  color: #fee2e2 !important;
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.4) !important;
}
/* 不适用按钮 - 青色系 */
.hover-active.el-button--info.is-plain {
  background: linear-gradient(135deg, rgba(30, 65, 75, 0.4), rgba(20, 55, 65, 0.4)) !important;
  border-color: #22d3ee !important;
  color: #bff8fd !important;
  box-shadow: 0 0 15px rgba(6, 182, 212, 0.4) !important;
}
/* 清空按钮 - 橙色系 */
.el-button--plain.icon-RefreshLeft.hover-active {
  background: linear-gradient(135deg, rgba(75, 55, 35, 0.4), rgba(65, 45, 25, 0.4)) !important;
  border-color: #fb923c !important;
  color: #fed7aa !important;
  box-shadow: 0 0 15px rgba(249, 115, 22, 0.4) !important;
}
/* 按钮图标样式优化 */
.el-button .el-icon {
  font-size: 18px !important;
  margin-right: 8px !important;
  text-shadow: 0 0 8px rgba(0, 0, 0, 0.4) !important;
}
/* 小尺寸按钮适配 */
.el-button--small {
  --el-button-size: 36px !important;
  padding: 0 12px !important;
  font-size: 13px !important;
}
/* 上传按钮专属样式 */
.upload-btn .el-button--plain {
  padding: 10px 0 !important;
  font-size: 15px !important;
  letter-spacing: 0.5px;
}
.upload-btn .el-icon {
  font-size: 19px !important;
}
/* ########## 按钮样式结束 ########## */
/* 滚动条样式优化 */
.control-card::-webkit-scrollbar {
  width: 6px;
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
/* 响应式调整 */
@media (max-width: 768px) {
  .control-card {
    width: 92vw;
    right: 50%;
    transform: translate(50%, -50%);
    height: 85vh;
    padding: 1.2rem 0.8rem;
  }
  .button-group {
    gap: 0.4rem;
  }
  .category-actions {
    gap: 0.4rem;
  }
  .action-btn {
    min-width: 75px;
    font-size: 13px !important;
    padding: 0 8px !important;
  }
  .fab {
    width: 54px !important;
    height: 54px !important;
    bottom: 1.8rem;
    right: 1.8rem;
  }
  .card-title {
    font-size: 17px;
  }
  .item-name {
    font-size: 13px;
  }
}
@media (max-height: 600px) {
  .control-card {
    height: 80vh;
    padding: 1rem 0.8rem;
  }
  .top-bar-actions {
    gap: 0.8rem;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
  }
  .custom-empty {
    margin: 1.2rem 0;
    --el-empty-image-size: 50px;
  }
}

</style>