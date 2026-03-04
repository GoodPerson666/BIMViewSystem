<template>
  <div class="table-container">
    <div class="header-bar">
      <div class="title-group">
        <h2 class="main-title">合规审查详细报告</h2>
        <span class="sub-subtitle">Compliance Check Detailed Report</span>
      </div>
      <div class="header-actions">
        <el-button
            type="primary"
            plain
            size="small"
            @click="expandAll(true)"
            class="action-btn"
        >全部展开</el-button>
        <el-button
            type="info"
            plain
            size="small"
            @click="expandAll(false)"
            class="action-btn"
        >全部收起</el-button>
        <el-divider direction="vertical" />
        <el-button
            circle
            @click="handleClose"
            class="close-floating-btn"
        >
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
    </div>

    <div v-if="loading" class="state-container">
      <el-skeleton :rows="10" animated />
    </div>
    <div v-else-if="errorMsg" class="state-container">
      <el-result icon="error" title="加载失败" :sub-title="errorMsg">
        <template #extra>
          <el-button type="primary" @click="fetchTableData">重试</el-button>
        </template>
      </el-result>
    </div>

    <div v-else class="content-wrapper">

      <section class="table-card" :class="{ 'is-active': tableExpandStatus.RecognizeRulesType }">
        <div class="table-header" @click="toggleTable('RecognizeRulesType')">
          <div class="title-wrapper">
            <span class="index-badge">01</span>
            <h4 class="table-title">第一部分：规范类型识别</h4>
          </div>
          <el-icon class="toggle-icon" :class="{ 'is-rotate': tableExpandStatus.RecognizeRulesType }">
            <ArrowDown />
          </el-icon>
        </div>
        <el-collapse-transition>
          <div v-show="tableExpandStatus.RecognizeRulesType" class="table-body">
            <el-table :data="RecognizeRulesTypeData" border stripe height="400" style="width: 100%">
              <el-table-column prop="规范来源" label="规范来源" width="250" show-overflow-tooltip />
              <el-table-column prop="规范内容" label="规范内容" min-width="350" />
              <el-table-column prop="识别类型" label="识别类型" width="120" >
                <template #default="{row}">
                  <el-tag size="small" effect="light">{{ row.识别类型 }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="规则序号" label="规则序号" width="100" align="center" />
            </el-table>
          </div>
        </el-collapse-transition>
      </section>

      <section class="table-card" :class="{ 'is-active': tableExpandStatus.RecognizeRulesProperties }">
        <div class="table-header" @click="toggleTable('RecognizeRulesProperties')">
          <div class="title-wrapper">
            <span class="index-badge">02</span>
            <h4 class="table-title">第二部分：规范实体识别</h4>
          </div>
          <el-icon class="toggle-icon" :class="{ 'is-rotate': tableExpandStatus.RecognizeRulesProperties }">
            <ArrowDown />
          </el-icon>
        </div>
        <el-collapse-transition>
          <div v-show="tableExpandStatus.RecognizeRulesProperties" class="table-body">
            <p class="table-subtitle">结果分析Agent语义校验前</p>
            <el-table :data="RecognizeRulesPropertiesFrontData" border stripe height="300" class="mb-4">
              <el-table-column prop="实体文本" label="实体文本" width="300" />
              <el-table-column prop="实体类型" label="实体类型" />
              <el-table-column prop="规则序号" label="规则序号" width="100" align="center" />
            </el-table>
            <p class="table-subtitle">结果分析Agent语义校验前</p>
            <el-table :data="RecognizeRulesPropertiesData" border stripe height="300">
              <el-table-column prop="实体文本" label="实体文本" width="300" />
              <el-table-column prop="实体类型" label="实体类型" />
              <el-table-column prop="规则序号" label="规则序号" width="100" align="center" />
            </el-table>
          </div>
        </el-collapse-transition>
      </section>

      <section class="table-card" :class="{ 'is-active': tableExpandStatus.IfcClass }">
        <div class="table-header" @click="toggleTable('IfcClass')">
          <div class="title-wrapper">
            <span class="index-badge">03</span>
            <h4 class="table-title">第三部分：IFC实体提取及其所有属性抽取</h4>
          </div>
          <el-icon class="toggle-icon" :class="{ 'is-rotate': tableExpandStatus.IfcClass }">
            <ArrowDown />
          </el-icon>
        </div>
        <el-collapse-transition>
          <div v-show="tableExpandStatus.IfcClass" class="table-body">
            <p class="table-subtitle">IFC实体</p>
            <el-table :data="IfcClassData" border stripe height="300" class="mb-4">
              <el-table-column prop="guid" label="GUID" width="300" />
              <el-table-column prop="ifc_type" label="IFC 类型" min-width="150" />
              <el-table-column prop="name" label="名称" min-width="200" />
            </el-table>
            <p class="table-subtitle">IFC属性</p>
            <el-table :data="PropertiesSetData" border stripe height="300">
              <el-table-column prop="guid" label="GUID" width="300" />
              <el-table-column prop="property_set_name" label="属性集名称" min-width="150" />
              <el-table-column prop="property_name" label="属性名称" min-width="200" />
            </el-table>
          </div>
        </el-collapse-transition>
      </section>

      <section class="table-card" :class="{ 'is-active': tableExpandStatus.EntitiesToRules }">
        <div class="table-header" @click="toggleTable('EntitiesToRules')">
          <div class="title-wrapper">
            <span class="index-badge">04</span>
            <h4 class="table-title">第四部分：语义对齐第一阶段：类层级对齐</h4>
          </div>
          <el-icon class="toggle-icon" :class="{ 'is-rotate': tableExpandStatus.EntitiesToRules }">
            <ArrowDown />
          </el-icon>
        </div>
        <el-collapse-transition>
          <div v-show="tableExpandStatus.EntitiesToRules" class="table-body">
            <el-table :data="EntitiesToRulesData" border stripe height="400">
              <el-table-column prop="规范内容" label="规范内容" min-width="400" />
              <el-table-column prop="规范实体" label="规范实体" width="100" />
              <el-table-column prop="规范实体类型" label="规范实体类型" width="100" />
              <el-table-column prop="匹配IFC类型" label="匹配IFC类型" width="100" />
              <el-table-column prop="匹配原因" label="匹配原因" width="400" />
            </el-table>
          </div>
        </el-collapse-transition>
      </section>

      <section class="table-card" :class="{ 'is-active': tableExpandStatus.entityStrength }">
        <div class="table-header" @click="toggleTable('entityStrength')">
          <div class="title-wrapper">
            <span class="index-badge">05</span>
            <h4 class="table-title">第五部分：语义对齐第二阶段：实例层级对齐</h4>
          </div>
          <el-icon class="toggle-icon" :class="{ 'is-rotate': tableExpandStatus.entityStrength }">
            <ArrowDown />
          </el-icon>
        </div>
        <el-collapse-transition>
          <div v-show="tableExpandStatus.entityStrength" class="table-body">
            <p class="table-subtitle">结果分析Agent语义校验前</p>
            <el-table :data="entityStrengthFrontData" border height="300" class="mb-4" size="small">
              <el-table-column prop="ruleNumber" label="序号" width="80" />
              <el-table-column prop="specEntityText" label="规范实体" width="100"/>
              <el-table-column prop="ifcGuid" label="IFC GUID" width="280" />
              <el-table-column prop="ifcEntityWithType" label="实体类型" width="300"/>
              <el-table-column prop="匹配原因" label="匹配原因" width="300"/>
            </el-table>
            <p class="table-subtitle">结果分析Agent语义校验后新增对齐</p>
            <el-table :data="entityStrengthNewData" border height="300" class="mb-4" size="small">
              <el-table-column prop="ruleNumber" label="序号" width="80" />
              <el-table-column prop="specEntityText" label="规范实体" width="100"/>
              <el-table-column prop="ifcGuid" label="IFC GUID" width="280" />
              <el-table-column prop="ifcEntityWithType" label="实体类型" width="300"/>
              <el-table-column prop="匹配原因" label="匹配原因" width="300"/>
            </el-table>
            <p class="table-subtitle">结果分析Agent语义校验后完整对齐结果</p>
            <el-table :data="entityStrengthData" border height="300" size="small">
              <el-table-column prop="ruleNumber" label="序号" width="80" />
              <el-table-column prop="specEntityText" label="规范实体" width="100"/>
              <el-table-column prop="ifcGuid" label="IFC GUID" width="280" />
              <el-table-column prop="ifcEntityWithType" label="实体类型" width="300"/>
              <el-table-column prop="匹配原因" label="匹配原因" width="300"/>
            </el-table>
          </div>
        </el-collapse-transition>
      </section>

      <section class="table-card" :class="{ 'is-active': tableExpandStatus.tupleSet }">
        <div class="table-header" @click="toggleTable('tupleSet')">
          <div class="title-wrapper">
            <span class="index-badge">06</span>
            <h4 class="table-title">第六部分：提取规范实体组——IFC实体组</h4>
          </div>
          <el-icon class="toggle-icon" :class="{ 'is-rotate': tableExpandStatus.tupleSet }">
            <ArrowDown />
          </el-icon>
        </div>
        <el-collapse-transition>
          <div v-show="tableExpandStatus.tupleSet" class="table-body">
            <el-table :data="tupleSetData" border stripe height="400">
              <el-table-column prop="ruleNumber" label="规则序号" width="100" align="center" />
              <el-table-column label="规范实体组" min-width="300">
                <template #default="scope">
                  <div class="tag-group">
                    <el-tag
                        v-for="(item, idx) in scope.row.specEntityGroupParsed"
                        :key="idx"
                        size="small"
                        class="custom-tag"
                    >
                      {{ item.text }} <span class="tag-type">({{ item.type }})</span>
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="IFC实体组" min-width="300">
                <template #default="scope">
                  <div class="tag-group">
                    <el-tag
                        v-for="(item, idx) in scope.row.ifcEntityGroupParsed"
                        :key="idx"
                        type="success"
                        size="small"
                        class="custom-tag"
                    >
                      {{ item.guid }} <span class="tag-type">({{ item.type }})</span>
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-collapse-transition>
      </section>

      <section class="table-card" :class="{ 'is-active': tableExpandStatus.chooseStrategy }">
        <div class="table-header" @click="toggleTable('chooseStrategy')">
          <div class="title-wrapper">
            <span class="index-badge">07</span>
            <h4 class="table-title">第七部分：高相关属性选择及属性值抽取</h4>
          </div>
          <el-icon class="toggle-icon" :class="{ 'is-rotate': tableExpandStatus.chooseStrategy }">
            <ArrowDown />
          </el-icon>
        </div>
        <el-collapse-transition>
          <div v-show="tableExpandStatus.chooseStrategy" class="table-body">
            <p class="table-subtitle">规范属性选择策略</p>
            <el-table :data="chooseStrategyData" border stripe height="300" class="mb-4">
              <el-table-column prop="规则序号" label="序号" width="80" />
              <el-table-column prop="property_set_name" label="Pset名称" />
              <el-table-column prop="property_name" label="属性名" />
              <el-table-column prop="优先级" label="优先级" width="80" />
              <el-table-column prop="策略说明" label="策略说明" min-width="300" />
            </el-table>
            <p class="table-subtitle">相关属性集</p>
            <el-table :data="relateEntitiesData" border stripe height="300">
              <el-table-column prop="规则序号" label="序号" width="80" />
              <el-table-column prop="ifc_guid" label="IFC GUID" width="280" />
              <el-table-column prop="property_set_name" label="Pset名称" />
              <el-table-column prop="property_name" label="属性名" />
              <el-table-column prop="property_value" label="属性值" />
            </el-table>
          </div>
        </el-collapse-transition>
      </section>

      <section class="table-card result-card" :class="{ 'is-active': tableExpandStatus.ComplianceCheck }">
        <div class="table-header" @click="toggleTable('ComplianceCheck')">
          <div class="title-wrapper">
            <span class="index-badge ">08</span>
            <h4 class="table-title">第八部分：合规审查结果</h4>
          </div>
          <el-icon class="toggle-icon" :class="{ 'is-rotate': tableExpandStatus.ComplianceCheck }">
            <ArrowDown />
          </el-icon>
        </div>
        <el-collapse-transition>
          <div v-show="tableExpandStatus.ComplianceCheck" class="table-body">
            <el-table :data="ComplianceCheckData" border highlight-current-row height="400">
              <el-table-column prop="规则序号" label="规则序号" width="100" />
              <el-table-column prop="组序号" label="组号" width="80"  />
              <el-table-column prop="IFC实体组" label="IFC实体组" width="300" />
              <el-table-column prop="原始属性集" label="原始属性集" width="300" />
              <el-table-column prop="analysis_process" label="分析原因" width="300" />
              <el-table-column label="审查结果" width="100">
                <template #default="{row}">
                  <span :class="getStatusClass(row.judgement_result)" class="status-text">
                    {{ row.judgement_result }}
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-collapse-transition>
      </section>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { ArrowDown, Close } from "@element-plus/icons-vue";

const emit = defineEmits(['close']);

// 响应式数据
const loading = ref(true);
const errorMsg = ref("");

// 表格数据
const RecognizeRulesTypeData = ref([]);
const RecognizeRulesPropertiesData = ref([]);
const RecognizeRulesPropertiesFrontData = ref([]);
const IfcClassData = ref([]);
const PropertiesSetData = ref([]);
const EntitiesToRulesData = ref([]);
const entityStrengthFrontData = ref([]);
const entityStrengthNewData = ref([]);
const entityStrengthData = ref([]);
const tupleSetData = ref([]);
const chooseStrategyData = ref([]);
const relateEntitiesData = ref([]);
const ComplianceCheckData = ref([]);

// 状态管理
const tableExpandStatus = ref({
  RecognizeRulesType: false,
  RecognizeRulesProperties: false,
  IfcClass: false,
  EntitiesToRules: false,
  entityStrength: false,
  tupleSet: false,
  chooseStrategy: false,
  ComplianceCheck: false
});

const toggleTable = (key) => {
  tableExpandStatus.value[key] = !tableExpandStatus.value[key];
};

const expandAll = (val) => {
  Object.keys(tableExpandStatus.value).forEach(key => {
    tableExpandStatus.value[key] = val;
  });
};

const handleClose = () => emit('close');

const getStatusClass = (text) => {
  if (text?.includes('不合规')) return 'status-fail';
  if (text?.includes('合规')) return 'status-pass';
  return 'status-warn';
};

const parseBackendData = (resData) => {
  if (resData.code !== 200) throw new Error(resData.msg || '未知错误');
  const { outputs } = resData;

  RecognizeRulesTypeData.value = (outputs[0] || []).map(item => ({
    规范来源: item[0] || "",
    规范内容: item[1] || "",
    识别类型: item[2] || "",
    规则序号: item[3] || "",
  }));

  RecognizeRulesPropertiesFrontData.value = (outputs[1] || []).map(item => ({
    实体文本: item[0], 实体类型: item[1], 规则序号: item[2]
  }));

  RecognizeRulesPropertiesData.value = (outputs[2] || []).map(item => ({
    实体文本: item[0], 实体类型: item[1], 规则序号: item[2]
  }));

  IfcClassData.value = (outputs[3] || []).map(item => ({
    guid: item[0], ifc_type: item[1], name: item[2]
  }));

  PropertiesSetData.value = (outputs[4] || []).map(item => ({
    guid: item[0], property_set_name: item[1], property_name: item[2]
  }));

  EntitiesToRulesData.value = (outputs[5] || []).map(item => ({
    规范内容:item[0],规范实体:item[1],规范实体类型:item[2],匹配IFC类型:item[3],匹配原因:item[4]
  }));

  entityStrengthFrontData.value = (outputs[6] || []).map(item => ({
    ruleNumber: item[0], specEntityText: item[1], ifcGuid: item[2], ifcEntityWithType: item[3],匹配原因:item[4]
  }));

  entityStrengthNewData.value = (outputs[7] || []).map(item => ({
    ruleNumber: item[0], specEntityText: item[1], ifcGuid: item[2], ifcEntityWithType: item[3],匹配原因:item[4]
  }));

  entityStrengthData.value = (outputs[8] || []).map(item => ({
    ruleNumber: item[0], specEntityText: item[1], ifcGuid: item[2], ifcEntityWithType: item[3],匹配原因:item[4]
  }));

  tupleSetData.value = (outputs[9] || []).map(item => {
    let specP = [], ifcP = [];
    try { specP = JSON.parse(item[1] || "[]"); } catch (e) { specP = [{text:'Error'}]; }
    try { ifcP = JSON.parse(item[2] || "[]"); } catch (e) { ifcP = [{guid:'Error'}]; }
    return { ruleNumber: item[0], specEntityGroupParsed: specP, ifcEntityGroupParsed: ifcP };
  });

  chooseStrategyData.value = (outputs[10] || []).map(item => ({
    规则序号: item[0], property_set_name: item[1], property_name: item[2], 优先级: item[3], 策略说明: item[4]
  }));

  relateEntitiesData.value = (outputs[11] || []).map(item => ({
    规则序号: item[0], ifc_guid: item[1], property_set_name: item[2], property_name: item[3], property_value: item[4]
  }));

  ComplianceCheckData.value = (outputs[12] || []).map(item => ({
    规则序号: item[0],组序号:item[1],IFC实体组:item[2],原始属性集:item[3],analysis_process:item[4],judgement_result:item[5]
  }));
};

const fetchTableData = async () => {
  try {
    loading.value = true;
    const res = await axios.post('http://localhost:5000/check/rusults/details', {}, { timeout: 10000 });
    parseBackendData(res.data);
  } catch (err) {
    errorMsg.value = err.message || "数据加载失败";
  } finally {
    loading.value = false;
  }
};

onMounted(fetchTableData);
</script>

<style scoped>
/* 核心容器 */
.table-container {
  width: 50%;
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  background: #f8fafc;
  border-radius: 12px;
  max-height: 94vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

/* 顶部栏 */
.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  margin-bottom: 24px;
  border-bottom: 1px solid #e2e8f0;
}

.main-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.sub-subtitle {
  font-size: 12px;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 卡片布局 */
.table-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  margin-bottom: 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.table-card.is-active {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
  border-color: #3b82f6;
}

/* 列表头部 */
.table-header {
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  background: #ffffff;
}

.table-header:hover {
  background: #f1f5f9;
}

.title-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.index-badge {
  background: #f1f5f9;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 6px;
}

.index-badge.primary {
  background: #dbeafe;
  color: #2563eb;
}

.table-title {
  margin: 0;
  font-size: 16px;
  color: #334155;
  font-weight: 600;
}

.toggle-icon {
  transition: transform 0.3s ease;
  color: #94a3b8;
}

.is-rotate {
  transform: rotate(180deg);
  color: #3b82f6;
}

/* 内容区域 */
.table-body {
  padding: 0 20px 20px;
}

.table-subtitle {
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
  margin: 16px 0 8px;
  display: flex;
  align-items: center;
}

.table-subtitle::before {
  content: "";
  width: 3px;
  height: 14px;
  background: #3b82f6;
  margin-right: 8px;
  border-radius: 4px;
}

/* 标签与文本 */
.tag-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.custom-tag {
  border-radius: 4px;
  padding: 0 8px;
}

.tag-type {
  font-size: 10px;
  opacity: 0.7;
}

.status-text {
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 13px;
}

.status-pass { color: #16a34a; background: #f0fdf4; }
.status-fail { color: #dc2626; background: #fef2f2; }
.status-warn { color: #d97706; background: #fffbeb; }

/* 按钮样式 */
.close-floating-btn {
  border: none;
  background: #f1f5f9;
  color: #64748b;
  transition: all 0.2s;
}

.close-floating-btn:hover {
  background: #fee2e2;
  color: #ef4444;
  transform: scale(1.1);
}

.mb-4 { margin-bottom: 20px; }

/* 深度覆盖 Element Plus */
:deep(.el-table) {
  --el-table-border-color: #f1f5f9;
  --el-table-header-bg-color: #f8fafc;
  border-radius: 8px;
}

:deep(.el-table th.el-table__cell) {
  color: #475569;
  font-weight: 700;
}
</style>