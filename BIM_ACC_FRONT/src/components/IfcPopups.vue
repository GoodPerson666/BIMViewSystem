<template>
  <!-- 构件弹窗 -->
  <el-dialog
      :model-value="isPopupVisible"
      title="构件详情"
      width="700"
      align-center
      @close="handleClose"
  >
<!--    <p><b>构件名称：</b>{{ ifcName }}</p>-->
<!--    <p><b>规范条文：</b></p>-->

    <el-table
        :data="formattedRules"
        border
        stripe
        style="width: 100%; margin-top: 10px"
        max-height="400"
    >
      <el-table-column prop="content" label="条文内容" width="200"/>
      <el-table-column prop="reason" label="判断原因" width="400" />
      <el-table-column prop="result" label="结果" width="100" />
    </el-table>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
    </template>
  </el-dialog>

  <!-- 数据库列表弹窗 -->
  <el-dialog
      :model-value="isDatabaseListVisible"
      title="规范文件列表"
      width="600"
      @close="handleClose"
  >
    <div v-if="databases.length === 0" class="empty-state">
      暂无规范文件，请先上传并解析规范文件
    </div>
    <div v-else class="database-list">
      <el-card
          v-for="db in databases"
          :key="db"
          class="database-card"
          @click="handleDatabaseClick(db)"
      >
        <div class="database-name">{{ db }}</div>
      </el-card>
    </div>

    <template #footer>
      <el-button @click="handleClose">关闭</el-button>
    </template>
  </el-dialog>

  <!-- 数据库详情弹窗（带动态检索功能） -->
  <el-dialog
      :model-value="isDatabaseInfoVisible"
      :title="`规范文件详情: ${selectedDatabase}`"
      width="1200"
      class="db-details"
      @close="handleClose"
  >
    <!-- 搜索框 -->
    <el-input
        v-model="searchKeyword"
        placeholder="请输入关键词搜索条款内容/章节名称"
        clearable
        class="search-input"
        @input="handleSearchDebounced"
        prefix-icon="el-icon-search"
    >
      <template #suffix>
        <el-button
            v-if="searchKeyword"
            icon="el-icon-refresh"
            @click="resetSearch"
            type="text"
        />
      </template>
    </el-input>

    <!-- 加载状态 -->
    <div v-if="isSearchLoading || isLoading" class="loading-state">
      <el-skeleton :rows="5" animated />
    </div>

    <!-- 搜索结果为空 -->
    <div v-else-if="isSearchEmpty" class="empty-state">
      未找到包含 "{{ searchKeyword }}" 的内容
    </div>

    <!-- 原始数据为空 -->
    <div v-else-if="!databaseInfoList || databaseInfoList.length === 0" class="empty-state">
      该数据库暂无数据
    </div>

    <!-- 数据展示 -->
    <div v-else class="database-info">
      <el-table
          :data="currentPageData"
          border
          stripe
          style="width: 100%; margin-bottom: 15px"
          row-key="item_id"
          max-height="400"
      >

        <el-table-column
            type="selection"
            width="55"
        />

<!--        <el-table-column prop="section_id" label="章节编号" width="100" />-->
<!--        <el-table-column prop="section_name" label="章节名称" width="200" />-->
<!--        <el-table-column prop="item_id" label="条款编号" width="120" />-->
<!--        <el-table-column-->
<!--            prop="content"-->
<!--            label="条款内容"-->
<!--            :show-overflow-tooltip="true"-->
<!--        />-->


        <el-table-column prop="rule_id" label="规则序号" width="100" />
        <el-table-column prop="source" label="规范来源" width="200" />
        <el-table-column prop="clause_id" label="条款编号" width="120" />
        <el-table-column prop="subclause_id" label="条款字句序号" width="120" />
        <el-table-column
            prop="content"
            label="条款内容"
            :show-overflow-tooltip="true"
        />
      </el-table>

      <!-- 分页组件 -->
      <div class="pagination">
        <el-pagination
            :current-page="currentPage"
            :page-size="pageSize"
            :total="totalItems"
            :page-sizes="[5, 10, 20]"
            layout="total, sizes, prev, pager, next, jumper"
            :hide-on-single-page="true"
            @current-change="handlePageChange"
            @size-change="handlePageSizeChange"
        />
      </div>
    </div>

    <template>
      <el-button @click="handleClose">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 定义Props
const props = defineProps({
  isPopupVisible: { type: Boolean, default: false },
  isPopRulesVisible: { type: Boolean, default: false },
  isDatabaseListVisible: { type: Boolean, default: false },
  isDatabaseInfoVisible: { type: Boolean, default: false },
  databases: { type: Array, default: () => [] },
  databaseInfo: { type: Array, default: () => [], required: false },
  selectedDatabase: { type: String, default: '' },
  ifcName: { type: String, default: '' },
  formattedRules: { type: Array, default: () => [] },
  rulesContent: { type: Array, default: () => [] },
  isLoading: { type: Boolean, default: false }
})

// 定义Emits
const emit = defineEmits([
  'close-popup',
  'fetch-databases',
  'fetch-database-info',
  'update:databaseInfo' // 用于更新父组件的数据库信息
])

// -------------------- 搜索相关状态 --------------------
const searchKeyword = ref('') // 搜索关键词
const isSearchLoading = ref(false) // 搜索加载状态
const originalDatabaseInfo = ref([]) // 保存原始数据
const filteredDatabaseInfo = ref([]) // 搜索过滤后的数据
const isSearchEmpty = ref(false) // 搜索结果为空标识

// -------------------- 分页相关状态 --------------------
const currentPage = ref(1)
const pageSize = ref(5)

// -------------------- 防抖处理 --------------------
let searchTimer = null
const handleSearchDebounced = () => {
  // 清除之前的定时器
  if (searchTimer) clearTimeout(searchTimer)

  // 防抖：300ms后执行搜索
  searchTimer = setTimeout(() => {
    handleSearch()
  }, 300)
}


// 原始数据库信息列表（空值保护）
const databaseInfoList = computed(() => {
  return props.databaseInfo || []
})

// 当前展示的数据（搜索结果或原始数据）
const displayData = computed(() => {
  return searchKeyword.value ? filteredDatabaseInfo.value : databaseInfoList.value
})

// 当前页数据
const currentPageData = computed(() => {
  if (!Array.isArray(displayData.value) || displayData.value.length === 0) {
    return []
  }
  const startIndex = (currentPage.value - 1) * pageSize.value
  return displayData.value.slice(startIndex, startIndex + pageSize.value)
})

// 总数据条数
const totalItems = computed(() => {
  return Array.isArray(displayData.value) ? displayData.value.length : 0
})

// -------------------- 方法定义 --------------------
/**
 * 处理搜索逻辑
 */
const handleSearch = async () => {
  // 清空关键词时重置
  if (!searchKeyword.value.trim()) {
    resetSearch()
    return
  }

  // 显示加载状态
  isSearchLoading.value = true
  isSearchEmpty.value = false

  try {
    // 调用后端搜索接口
    const { data } = await axios.get(
        `http://localhost:5000/rules/database/${props.selectedDatabase}/search`,
        { params: { keyword: searchKeyword.value.trim() } }
    )

    if (data.status === 'success') {
      filteredDatabaseInfo.value = data.data || []
      isSearchEmpty.value = filteredDatabaseInfo.value.length === 0

      // 通知父组件更新数据（可选）
      emit('update:databaseInfo', filteredDatabaseInfo.value)

      // 重置分页
      currentPage.value = 1
    } else {
      ElMessage.error(data.message || '搜索失败')
    }
  } catch (error) {
    console.error('搜索接口调用失败:', error)
    ElMessage.error('搜索失败，请检查网络或后端服务')
    isSearchEmpty.value = true
  } finally {
    isSearchLoading.value = false
  }
}

/**
 * 重置搜索状态
 */
const resetSearch = () => {
  searchKeyword.value = ''
  filteredDatabaseInfo.value = []
  isSearchEmpty.value = false
  currentPage.value = 1

  // 恢复原始数据
  if (originalDatabaseInfo.value.length > 0) {
    emit('update:databaseInfo', originalDatabaseInfo.value)
  }
}

/**
 * 分页页码变化
 */
const handlePageChange = (page) => {
  currentPage.value = page
  // 滚动到表格顶部
  const container = document.querySelector('.database-info')
  if (container) {
    container.scrollTop = 0
  }
}

/**
 * 分页大小变化
 */
const handlePageSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1 // 重置页码
}

/**
 * 点击数据库名称查看详情
 */
const handleDatabaseClick = (dbName) => {
  // 关闭数据库列表弹窗
  emit('close-popup')

  // 延迟获取数据库信息
  setTimeout(() => {
    emit('fetch-database-info', dbName)
  }, 300)
}

/**
 * 关闭弹窗
 */
const handleClose = () => {
  // 重置所有状态
  currentPage.value = 1
  pageSize.value = 5
  searchKeyword.value = ''
  filteredDatabaseInfo.value = []
  isSearchEmpty.value = false

  // 通知父组件关闭弹窗
  emit('close-popup')
}

// -------------------- 监听事件 --------------------
// 监听原始数据库信息变化，保存原始数据
watch(
    () => props.databaseInfo,
    (newVal) => {
      if (newVal && newVal.length > 0) {
        originalDatabaseInfo.value = [...newVal]
      }
      currentPage.value = 1 // 数据变化时重置分页
    },
    { immediate: true, deep: true }
)

// 监听数据库详情弹窗显示状态
watch(
    () => props.isDatabaseInfoVisible,
    (visible) => {
      if (visible) {
        // 弹窗打开时重置状态
        currentPage.value = 1
        searchKeyword.value = ''
        isSearchEmpty.value = false
      }
    }
)

// 清理定时器
onMounted(() => {
  return () => {
    if (searchTimer) clearTimeout(searchTimer)
  }
})
</script>

<style scoped>
/* 搜索框样式 */
.search-input {
  margin-bottom: 15px;
  width: 100%;
}

/* 分页样式 */
.pagination {
  margin-top: 15px;
  text-align: right;
}

/* 数据库列表样式 */
.database-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  max-height: 400px;
  overflow-y: auto;
  padding: 10px 0;
}

.database-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e4e7ed;
}

.database-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.database-name {
  font-size: 16px;
  padding: 15px;
  text-align: center;
  color: #303133;
}

/* 空状态/加载状态样式 */
.empty-state, .loading-state {
  text-align: center;
  padding: 50px 0;
  color: #666;
}

.empty-state {
  font-size: 14px;
}

/* 数据库详情容器 */
.database-info {
  max-height: 500px;
  overflow-y: auto;
  padding-bottom: 15px;
}

/* 表格样式优化 */
:deep(.el-table) {
  --el-table-header-text-color: #333;
  --el-table-row-hover-bg-color: #f5f7fa;
  --el-table-header-text-color: #606266;
}

/* 分页组件样式优化 */
:deep(.el-pagination) {
  --el-pagination-button-hover-color: #409eff;
  --el-pagination-current-page-bg-color: #409eff;
}

/* 骨架屏样式 */
:deep(.el-skeleton) {
  --el-skeleton-row-height: 40px;
}


/*数据库弹窗样式 */

</style>