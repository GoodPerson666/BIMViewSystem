<template>
  <div id="app">
    <IfcView />
  </div>
</template>

<script setup>

// 导入ifc视图组件
import IfcView from './Views/IfcView.vue'
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* 确保页面占满全屏 */
html, body, #app {
  width: 100%;
  height: 100%;
  //overflow: hidden;
}
</style>