<template>
  <div class="table-container">
    <!-- 提示加载状态/错误信息 -->
    <div v-if="loading" class="loading-tip">数据加载中...</div>
    <div v-else-if="errorMsg" class="error-tip">{{ errorMsg }}</div>

    <!-- 表格区域 -->
    <div v-else>
      <!-- 第一个表格：规范类型识别 -->
      <div class="table-card">
        <div
            class="table-header"
            @click="toggleTable('RecognizeRulesType')"
        >
          <h4 class="table-title">第一部分：规范类型识别</h4>
          <el-icon class="toggle-icon">
            <ArrowDown v-if="tableExpandStatus.RecognizeRulesType" />
            <ArrowRight v-else />
          </el-icon>
        </div>

        <el-table
            v-show="tableExpandStatus.RecognizeRulesType"
            :data="RecognizeRulesTypeData"
            border
            style="width: 100%; margin-bottom: 20px"
            empty-text="暂无规范类型数据"
            height="400"
        >
          <el-table-column
              prop="规范来源"
              label="规范来源"
              width="100"
          />
          <el-table-column
              prop="规范内容"
              label="规范内容"
              min-width="150"
          />
          <el-table-column
              prop="识别类型"
              label="识别类型"
              min-width="200"
          />
          <el-table-column
              prop="规则序号"
              label="规则序号"
              min-width="250"
          />
        </el-table>
      </div>

      <!-- 第二个表格：规范实体识别 -->
      <div class="table-card">
        <div
            class="table-header"
            @click="toggleTable('RecognizeRulesProperties')"
        >
          <h4 class="table-title">第二部分：规范实体识别</h4>
          <el-icon class="toggle-icon">
            <ArrowDown v-if="tableExpandStatus.RecognizeRulesProperties" />
            <ArrowRight v-else />
          </el-icon>
        </div>

        <el-table
            v-show="tableExpandStatus.RecognizeRulesProperties"
            :data="RecognizeRulesPropertiesData"
            border
            style="width: 100%; margin-bottom: 20px"
            empty-text="暂无规范类型数据"
            height="400"
        >
          <el-table-column
              prop="实体文本"
              label="实体文本"
              width="100"
          />
          <el-table-column
              prop="实体类型"
              label="实体类型"
              min-width="150"
          />
          <el-table-column
              prop="规则序号"
              label="规则序号"
              min-width="200"
          />
        </el-table>
      </div>

      <!-- 第三个表格：Ifc类型识别 -->
      <div class="table-card">
        <div
            class="table-header"
            @click="toggleTable('IfcClass')"
        >
          <h4 class="table-title">第三部分：Ifc类型识别</h4>
          <el-icon class="toggle-icon">
            <ArrowDown v-if="tableExpandStatus.IfcClass" />
            <ArrowRight v-else />
          </el-icon>
        </div>

        <el-table
            v-show="tableExpandStatus.IfcClass"
            :data="IfcClassData"
            border
            style="width: 100%; margin-bottom: 20px"
            empty-text="暂无规范类型数据"
            height="400"
        >
          <el-table-column
              prop="guid"
              label="guid"
              width="100"
          />
          <el-table-column
              prop="ifc_type"
              label="ifc_type"
              min-width="150"
          />
          <el-table-column
              prop="name"
              label="name"
              min-width="200"
          />
        </el-table>
      </div>

      <!-- 第四个表格：IFC实体属性识别 -->
      <div class="table-card">
        <div
            class="table-header"
            @click="toggleTable('PropertiesSet')"
        >
          <h4 class="table-title">第四部分：IFC实体属性识别</h4>
          <el-icon class="toggle-icon">
            <ArrowDown v-if="tableExpandStatus.PropertiesSet" />
            <ArrowRight v-else />
          </el-icon>
        </div>

        <el-table
            v-show="tableExpandStatus.PropertiesSet"
            :data="PropertiesSetData"
            border
            style="width: 100%; margin-bottom: 20px"
            empty-text="暂无规范类型数据"
            height="400"
        >
          <el-table-column
              prop="guid"
              label="guid"
              width="100"
          />
          <el-table-column
              prop="property_set_name"
              label="property_set_name"
              min-width="150"
          />
          <el-table-column
              prop="property_name"
              label="property_name"
              min-width="200"
          />
        </el-table>
      </div>

      <!-- 第五个表格：规范实体与条文对齐 -->
      <div class="table-card">
        <div
            class="table-header"
            @click="toggleTable('EntitiesToRules')"
        >
          <h4 class="table-title">第五部分：规范实体与条文对齐</h4>
          <el-icon class="toggle-icon">
            <ArrowDown v-if="tableExpandStatus.EntitiesToRules" />
            <ArrowRight v-else />
          </el-icon>
        </div>

        <el-table
            v-show="tableExpandStatus.EntitiesToRules"
            :data="EntitiesToRulesData"
            border
            style="width: 100%; margin-bottom: 20px"
            empty-text="暂无规范类型数据"
            height="400"
        >
          <el-table-column
              prop="规范条文"
              label="规范条文"
              width="100"
          />
          <el-table-column
              prop="实体"
              label="实体"
              min-width="150"
          />
        </el-table>
      </div>

      <!-- 第六个表格：entity_strength 数据 -->
      <div class="table-card">
        <div
            class="table-header"
            @click="toggleTable('entityStrength')"
        >
          <h4 class="table-title">第六部分：实体强度数据</h4>
          <el-icon class="toggle-icon">
            <ArrowDown v-if="tableExpandStatus.entityStrength" />
            <ArrowRight v-else />
          </el-icon>
        </div>

        <el-table
            v-show="tableExpandStatus.entityStrength"
            :data="entityStrengthData"
            border
            style="width: 100%; margin-bottom: 20px"
            empty-text="暂无实体强度数据"
            height="400"
        >
          <el-table-column
              prop="ruleNumber"
              label="规则序号"
              width="100"
          />
          <el-table-column
              prop="specEntityText"
              label="规范实体文本"
              align="center"
              min-width="150"
          />
          <el-table-column
              prop="ifcGuid"
              label="ifc_guid"
              align="center"
              min-width="200"
          />
          <el-table-column
              prop="ifcEntityWithType"
              label="ifc_entity_with_type"
              align="center"
              min-width="250"
          />
        </el-table>
      </div>

      <!-- 第七个表格：tuple_set 数据 -->
      <div class="table-card">
        <div
            class="table-header"
            @click="toggleTable('tupleSet')"
        >
          <h4 class="table-title">第七部分：元组集合数据</h4>
          <el-icon class="toggle-icon">
            <ArrowDown v-if="tableExpandStatus.tupleSet" />
            <ArrowRight v-else />
          </el-icon>
        </div>

        <el-table
            v-show="tableExpandStatus.tupleSet"
            :data="tupleSetData"
            border
            style="width: 100%"
            empty-text="暂无元组集合数据"
            height="400"
        >
          <el-table-column
              prop="ruleNumber"
              label="规则序号"
              align="center"
              width="100"
          />
          <el-table-column
              prop="specEntityGroup"
              label="规范实体组"
              align="center"
              min-width="200"
          >
            <!-- 自定义渲染JSON解析后的文本 -->
            <template #default="scope">
              <div class="entity-group">
                <span v-for="(item, idx) in scope.row.specEntityGroupParsed" :key="idx">
                  {{ item.text }}({{ item.type }})
                  <span v-if="idx < scope.row.specEntityGroupParsed.length - 1">、</span>
                </span>
              </div>
            </template>
          </el-table-column>
          <el-table-column
              prop="ifcEntityGroup"
              label="IFC实体组"
              align="center"
              min-width="300"
          >
            <!-- 自定义渲染JSON解析后的IFC实体 -->
            <template #default="scope">
              <div class="ifc-group">
                <span v-for="(item, idx) in scope.row.ifcEntityGroupParsed" :key="idx">
                  {{ item.guid }}({{ item.type }})
                  <span v-if="idx < scope.row.ifcEntityGroupParsed.length - 1">、</span>
                </span>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { ArrowDown, ArrowRight } from "@element-plus/icons-vue";

// 响应式数据定义
const loading = ref(true); // 加载状态
const errorMsg = ref(""); // 错误信息
const RecognizeRulesTypeData = ref([]) //第一个表格数据
const RecognizeRulesPropertiesData = ref([]) //第二个表格数据
const IfcClassData = ref([]) //第三个表格数据
const PropertiesSetData = ref([]) //第四个表格数据
const EntitiesToRulesData = ref([]) //第五个表格数据
const entityStrengthData = ref([]); // 第六个表格数据
const tupleSetData = ref([]); // 第七个表格数据

// 表格展开/收起状态，默认全部收起
const tableExpandStatus = ref({

  RecognizeRulesType:false,
  RecognizeRulesProperties:false,
  IfcClass:false,
  PropertiesSet:false,
  entitiesToRules:false,
  entityStrength: false,
  tupleSet: false,
});

// 切换表格展开/收起状态
const toggleTable = (tableKey) => {
  tableExpandStatus.value[tableKey] = !tableExpandStatus.value[tableKey];
};

// 解析后端返回的复杂数据
const parseBackendData = (resData) => {
  if (resData.code !== 200) {
    throw new Error(`接口返回错误：${resData.msg || '未知错误'}`);
  }

  const { outputs } = resData;

  const recognizeRulesType = outputs[0] || [];
  const recognizeRulesProperties = outputs[1] || [];
  const ifcClass = outputs[2] || [];
  const propertiesSet = outputs[3] || [];
  const entitiesToRules = outputs[4] || [];
  const entityRawData = outputs[5] || [];
  const tupleRawData = outputs[6] || [];

  // 解析第一个表格
  RecognizeRulesTypeData.value =recognizeRulesType.map(item =>({
    规范来源:item[0] || "",
    规范内容:item[1] || "",
    识别类型:item[2] || "",
    规则序号:item[3] || "",
  }));

  // 解析第二个表格
  RecognizeRulesPropertiesData.value = recognizeRulesProperties.map(item =>({
    实体文本:item[0] || "",
    实体类型:item[1] || "",
    规则序号:item[2] || ""
  }))

  // 解析第三个表格
  IfcClassData.value = ifcClass.map(item=>({
    guid:item[0] || "",
    ifc_type:item[1] || "",
    name:item[2] || "",
  }))

  // 解析第四个表格
  PropertiesSetData.value =propertiesSet.map(item=>({
    guid:item[0] || "",
    property_set_name:item[1] || "",
    property_name:item[2] || "",
  }))

  // 解析第五个表格
  EntitiesToRulesData.value = entitiesToRules.map(item=>({
    规范条文:item[0] || "",
    实体:item[1] || "",
  }))

  // 解析第六个表格数据
  entityStrengthData.value = entityRawData.map(item => ({
    ruleNumber: item[0] || "", // 规则序号
    specEntityText: item[1] || "", // 规范实体文本
    ifcGuid: item[2] || "", // ifc_guid
    ifcEntityWithType: item[3] || "" // ifc_entity_with_type
  }));

  // 解析第七个表格数据（包含JSON字符串解析）
  tupleSetData.value = tupleRawData.map(item => {
    // 解析规范实体组的JSON字符串
    let specEntityGroupParsed = [];
    try {
      specEntityGroupParsed = JSON.parse(item[1] || "[]");
    } catch (e) {
      console.error("规范实体组JSON解析失败：", e);
      specEntityGroupParsed = [{ text: "解析失败", type: "错误" }];
    }

    // 解析IFC实体组的JSON字符串
    let ifcEntityGroupParsed = [];
    try {
      ifcEntityGroupParsed = JSON.parse(item[2] || "[]");
    } catch (e) {
      console.error("IFC实体组JSON解析失败：", e);
      ifcEntityGroupParsed = [{ guid: "解析失败", type: "错误" }];
    }

    return {
      ruleNumber: item[0] || "", // 规则序号
      specEntityGroup: item[1] || "", // 原始JSON字符串（备用）
      specEntityGroupParsed, // 解析后的数组（用于渲染）
      ifcEntityGroup: item[2] || "", // 原始JSON字符串（备用）
      ifcEntityGroupParsed // 解析后的数组（用于渲染）
    };
  });
};

// 异步请求后端数据
const fetchTableData = async () => {
  try {
    loading.value = true;
    const response = await axios.post(
        'http://localhost:5000/check/rusults/details',
        {},
        {
          headers: { 'Content-Type': 'application/json' },
          timeout: 10000
        }
    );
    // 解析数据并绑定到表格
    parseBackendData(response.data);
    errorMsg.value = "";
  } catch (err) {
    console.error("数据请求失败：", err);
    errorMsg.value = err.message || "数据加载失败，请刷新重试";
    // 清空表格数据
    RecognizeRulesTypeData.value = []
    entityStrengthData.value = [];
    tupleSetData.value = [];
  } finally {
    loading.value = false;
  }
};

// 组件挂载时请求数据
onMounted(() => {
  fetchTableData();
});
</script>

<style scoped>
.table-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.table-card {
  margin-bottom: 30px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  background-color: #fff;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background-color: #f5f7fa;
  cursor: pointer;
  transition: background-color 0.2s;
}

.table-header:hover {
  background-color: #eef0f4;
}

.table-title {
  margin: 0;
  font-size: 16px;
  color: #303133;
  font-weight: 500;
}

.toggle-icon {
  font-size: 16px;
  color: #606266;
  transition: transform 0.2s;
}

.loading-tip {
  padding: 20px;
  text-align: center;
  color: #606266;
}

.error-tip {
  padding: 20px;
  text-align: center;
  color: #f56c6c;
}

/* 自定义实体组渲染样式 */
.entity-group, .ifc-group {
  word-break: break-all;
  line-height: 1.5;
}

/* 表格样式优化 */
:deep(.el-table) {
  --el-table-header-text-color: #303133;
  --el-table-row-hover-bg-color: #f8f9fa;
  --el-table-border-color: #e5e7eb;
  border-top: none;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
}

/* 表格容器样式 */
:deep(.el-table__inner-wrapper) {
  border-radius: 0 0 8px 8px;
}
</style>