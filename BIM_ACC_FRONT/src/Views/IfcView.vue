<template>
  <div class="ifc-view">
    <!-- 加载动画 -->
    <LoadingSpinner
        :visible="isLoading"
        text="模型加载中..."
    />
    <!-- 场景渲染 -->
    <SysTitle />
    <IfcSceneRenderer
        class="IfcSceneRenderer"
        ref="sceneRef"
        @select-entity="handleEntitySelect"
        @load-model="handleModelLoad"
        @open-entity-popup="handleOpenEntityPopup"
    />

    <!-- 控制面板 -->
    <IfcControlPanel
        :categories="categories"
        :local-id="localId"
        :selected-name="selectedName"
        :is-mobile="isMobile"
        :show-panel="showPanel"
        :current-category="currentCategory"
        :format-pset="formatPset"
        @toggle-panel="showPanel = $event"
        @change-category="currentCategory = $event"
        @toggle-format-pset="formatPset = $event"
        @log-attributes="handleLogAttributes"
        @log-psets="handleLogPsets"
        @log-names="handleLogNames"
        @log-geometries="handleLogGeometries"
        @dispose-meshes="handleDisposeMeshes"
        @upload-ifc="handleUploadIfc"
        @get-compliance="handleGetCompliance"
        @get-noncompliance="handleGetNonCompliance"
        @get-normal="handleGetNormal"
        @clear-color="handleClearColor"
    />

    <!--  规范条文面板  -->
    <IfcRules
        @view-databases="handleViewDatabases"
        @view-database-info="handleViewDatabaseInfo"
    />

    <!-- 弹窗组件 -->
    <IfcPopups
        :is-popup-visible="isPopupVisible"
        :is-pop-rules-visible="isPopRulesVisible"
        :is-database-list-visible="isDatabaseListVisible"
        :is-database-info-visible="isDatabaseInfoVisible"
        :databases="databases"
        :database-info="databaseInfo"
        :selected-database="selectedDatabase"
        :ifc-name="ifcName"
        :formatted-rules="formattedRules"
        :rules-content="RulesContent"
        @close-popup="handleClosePopup"
        @fetch-databases="fetchDatabases"
        @fetch-database-info="handleViewDatabaseInfo"
    />

    <LoadingCheck
        :visible="isCheckVisible"
        @close="isCheckVisible = false" />

    <el-button class="CheckBtn"  @click="handleStartCheck">开始审查</el-button>

  </div>
</template>

<script setup>
import {ref, computed} from 'vue'
import IfcSceneRenderer from '@/components/IfcSceneRenderer.vue'
import IfcControlPanel from '@/components/IfcControlPanel.vue'
import IfcPopups from '@/components/IfcPopups.vue'
import SysTitle from "@/components/SysTitle.vue";
import IfcRules from "@/components/IfcRules.vue";
import LoadingSpinner from "@/components/LoadingSpinner/LoadingIfc.vue";
import axios from 'axios'
import {ElMessage} from "element-plus";
import LoadingCheck from "@/components/LoadingSpinner/LoadingCheck.vue";


// 设备判断
const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
)

// 响应式状态
const categories = ref([])
const localId = ref(null)
const selectedName = ref(null)
const formatPset = ref(true)
const currentCategory = ref('')
const showPanel = ref(false)
const ifcName = ref('')
const ifcRule = ref('')
const isPopupVisible = ref(false)
const isPopRulesVisible = ref(false)
const rawRules = ref([])
const sceneRef = ref(null)
const isLoading = ref(false)

// 新增：数据库相关状态
const databases = ref([])
const databaseInfo = ref(null)
const selectedDatabase = ref('')
const isDatabaseListVisible = ref(false)
const isDatabaseInfoVisible = ref(false)

// 添加响应式状态
const isCheckVisible = ref(false)

// 添加处理函数
function handleStartCheck() {
  isCheckVisible.value = true
}

// 计算属性
const formattedRules = computed(() => {
  if (!Array.isArray(ifcRule.value)) return []
  return ifcRule.value.map(item => ({
    content: item?.内容 || '',
    reason:item?.判断原因 || '',
    result: item?.判断结果 || '未知'
  }))
})

const RulesContent = computed(() =>
    rawRules.value.map(row => ({
      rulesId: row[0],
      ruleFrom: row[1],
      itemId: row[2],
      content: row[3]
    }))
)


// 事件处理
function handleEntitySelect({localId: id, name}) {
  localId.value = id
  selectedName.value = name
}

function handleModelLoad(cats) {
  categories.value = cats
}

async function handleUploadIfc(file) {
  try {
    isLoading.value = true
    const arrayBuffer = await file.arrayBuffer()
    await sceneRef.value.loadModel(arrayBuffer)
  } catch (error) {
    console.error('模型加载失败:', error)
  } finally {
    isLoading.value = false
  }
}

async function handleGetCompliance() {
  try {
    const {data} = await axios.post('http://localhost:5000/ifcView/compliance')
    await sceneRef.value.highlightByGuids(data, 'green')
  } catch (e) {
    console.error(e)
  }
}

async function handleGetNonCompliance() {
  try {
    const {data} = await axios.post('http://localhost:5000/ifcView/Noncompliance')
    await sceneRef.value.highlightByGuids(data, 'red')
  } catch (e) {
    console.error(e)
  }
}

async function handleGetNormal() {
  try {
    const {data} = await axios.post('http://localhost:5000/ifcView/normal')
    await sceneRef.value.highlightByGuids(data, 'orange')
  } catch (e) {
    console.error(e)
  }
}

async function handleClearColor() {
  await sceneRef.value.clearHighlight()
}


// 新增：处理查看数据库列表
async function handleViewDatabases() {
  isDatabaseListVisible.value = true
  await fetchDatabases()
}

// 新增：获取数据库列表
async function fetchDatabases() {
  try {
    const {data} = await axios.get('http://localhost:5000/rules/databases')
    if (data.status === 'success') {
      databases.value = data.databases
    } else {
      ElMessage.error(data.message || '获取数据库列表失败')
    }
  } catch (error) {
    console.error('获取数据库列表失败:', error)
    ElMessage.error('获取数据库列表失败，请稍后重试')
  }
}

// 新增：处理查看数据库详情
async function handleViewDatabaseInfo(dbName) {
  selectedDatabase.value = dbName
  isDatabaseListVisible.value = false  // 关闭列表弹窗
  await fetchDatabaseInfo(dbName)      // 先获取数据
  isDatabaseInfoVisible.value = true   // 再显示详情弹窗
}

// 新增：获取数据库详情
async function fetchDatabaseInfo(dbName) {
  try {
    const {data} = await axios.get(`http://localhost:5000/rules/database/${dbName}`)
    if (data.status === 'success') {
      databaseInfo.value = data.data
      console.log(data)
    } else {
      ElMessage.error(data.message || '获取数据库信息失败')
    }
  } catch (error) {
    console.error('获取数据库信息失败:', error)
    ElMessage.error('获取数据库信息失败，请稍后重试')
  }
}

// 关闭弹窗
function handleClosePopup() {
  isPopupVisible.value = false
  isPopRulesVisible.value = false
  isDatabaseListVisible.value = false
  isDatabaseInfoVisible.value = false
  databaseInfo.value = null
}

async function handleOpenEntityPopup({localId: id, name, guid}) {
  if (!guid) return

  localId.value = id
  selectedName.value = name
  ifcName.value = name

  try {
    const rules = await axios.get('http://localhost:5000/ifcView/getRules', {
      params: {guid}
    })
    ifcRule.value = rules.data.data
    isPopupVisible.value = true
  } catch (error) {
    console.error('获取规则失败:', error)
  }
}

async function handleLogAttributes() {
  if (!localId.value) return
  const data = await sceneRef.value.getEntityData(localId.value)
  ifcName.value = selectedName.value

  try {
    const rules = await axios.get('http://localhost:5000/ifcView/getRules', {
      params: {guid: data._guid.value}
    })
    ifcRule.value = rules.data.data
    isPopupVisible.value = true
  } catch (error) {
    console.error('获取规则失败:', error)
  }
}

async function handleLogPsets() {
  if (!localId.value) return
  await sceneRef.value.getEntityPsets(localId.value, formatPset.value)
}

async function handleLogNames() {
  if (!currentCategory.value) return
  await sceneRef.value.getCategoryNames(currentCategory.value)
}

async function handleLogGeometries() {
  if (!currentCategory.value) return
  await sceneRef.value.loadCategoryGeometries(currentCategory.value)
}

async function handleDisposeMeshes() {
  await sceneRef.value.disposeGeometries()
}
</script>

<style scoped>
.ifc-view {
  width: 100%;
  height: 100%;
}

.IfcSceneRenderer {
  width: 100%;
  height: 100%;
}

.CheckBtn {
  /* 保留原有位置属性 */
  position: fixed;
  top: 1.5rem;
  right: 1.5rem;
  z-index: 1000;
  padding: 0.5rem 1.2rem;
  font-size: 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;

  /* 暗系炫酷风格重写 */
  background: linear-gradient(135deg, #1e1e2f, #2d2d44);
  color: #00f0ff;
  border: 1px solid rgba(0, 240, 255, 0.3);
  letter-spacing: 0.5px;
  font-weight: 600;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3),
  0 0 8px rgba(0, 240, 255, 0.1);
}

/* 流光效果伪元素 */
.CheckBtn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg,
  transparent,
  rgba(0, 240, 255, 0.15),
  transparent);
  transition: left 0.6s ease;
  pointer-events: none;
}

/* 悬浮态优化 - 保留原有位移效果，增强视觉表现 */
.CheckBtn:hover {
  background: linear-gradient(135deg, #252538, #353550);
  border-color: rgba(0, 240, 255, 0.6);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.4),
  0 0 12px rgba(0, 240, 255, 0.2);
  transform: translateY(-2px); /* 保留原有位移 */
}

.CheckBtn:hover::before {
  left: 100%;
}

/* 点击态 */
.CheckBtn:active {
  transform: translateY(0); /* 点击回位 */
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5),
  0 0 6px rgba(0, 240, 255, 0.15);
  background: linear-gradient(135deg, #1a1a29, #282840);
}

/* 禁用态 */
.CheckBtn:disabled {
  background: linear-gradient(135deg, #1a1a1a, #222222);
  color: #666677;
  border-color: rgba(102, 102, 119, 0.3);
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.CheckBtn:disabled::before {
  display: none;
}



</style>