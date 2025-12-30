<template>
  <div ref="containerRef" class="viewport"></div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as THREE from 'three'
import * as OBC from '@thatopen/components'
import * as FRAGS from '@thatopen/fragments'

// 定义事件
const emit = defineEmits(['select-entity', 'load-model', 'open-entity-popup'])
const containerRef = ref()

// 内部状态
let components, world, fragments, model
let LOCKED_ID = []
const meshes = []

// 初始化场景
onMounted(async () => {
  await nextTick()
  await initScene()
})

async function initScene() {
  components = new OBC.Components()
  const worlds = components.get(OBC.Worlds)
  world = worlds.create()
  world.scene = new OBC.SimpleScene(components)
  world.scene.setup()
  world.renderer = new OBC.SimpleRenderer(components, containerRef.value)
  world.camera = new OBC.SimpleCamera(components)
  await world.camera.controls.setLookAt(58, 22, -25, 13, 0, 4.2)
  components.init()

  const grids = components.get(OBC.Grids)
  grids.create(world)

  const workerUrl = '/worker.mjs'
  fragments = new FRAGS.FragmentsModels(workerUrl)

  world.camera.controls.addEventListener('rest', () => fragments.update(true))
  fragments.models.list.onItemSet.add(({ value: m }) => {
    m.useCamera(world.camera.three)
    world.scene.three.add(m.object)
    fragments.update(true)
  })
}

// 加载模型
async function loadModel(arrayBuffer) {
  const serializer = new FRAGS.IfcImporter()
  serializer.wasm = {
    absolute: true,
    path: 'https://unpkg.com/web-ifc@latest/'
  }

  const fragmentBytes = await serializer.process({
    bytes: new Uint8Array(arrayBuffer),
    progressCallback: (progress, data) => console.log(progress, data),
  })

  if (model) {
    world.scene.three.remove(model.object)
    await fragments.unload(model)
    model = null
  }

  model = await fragments.load(fragmentBytes, { modelId: 'example' })
  const categories = await model.getCategories()
  emit('load-model', categories)
  setupRaycasting()
}


// 射线拾取
function setupRaycasting() {
  const highlightMaterial = {
    color: new THREE.Color('purple'),
    renderedFaces: FRAGS.RenderedFaces.TWO,
    opacity: 1,
    transparent: false,
  }

  const mouse = new THREE.Vector2()
  let selectedLocalId = null

  // 双击事件 - 打开弹窗
  containerRef.value.addEventListener('dblclick', async (event) => {
    if (!model) return

    const rect = containerRef.value.getBoundingClientRect()
    mouse.x = event.clientX - rect.left
    mouse.y = event.clientY - rect.top

    const result = await model.raycast({
      camera: world.camera.three,
      mouse,
      dom: world.renderer.three.domElement,
    })

    if (result) {
      const localId = result.localId
      const [data] = await model.getItemsData([localId], {
        attributesDefault: false,
        attributes: ['Name']
      })
      const name = data?.Name?.value || '未知构件'

      selectedLocalId = localId
      emit('select-entity', { localId, name })
      emit('open-entity-popup', {
        localId,
        name,
        guid: data?._guid?.value
      })
    }
  })

  // 单击事件 - 保持高亮逻辑
  containerRef.value.addEventListener('click', async (event) => {
    if (!model) return

    const rect = containerRef.value.getBoundingClientRect()
    mouse.x = event.clientX - rect.left
    mouse.y = event.clientY - rect.top

    const result = await model.raycast({
      camera: world.camera.three,
      mouse,
      dom: world.renderer.three.domElement,
    })

    const promises = []

    if (result) {
      if (selectedLocalId !== null && !LOCKED_ID.includes(selectedLocalId)) {
        promises.push(model.resetHighlight([selectedLocalId]))
      }

      const localId = result.localId
      const [data] = await model.getItemsData([localId], {
        attributesDefault: false,
        attributes: ['Name']
      })

      const name = data?.Name?.value || '未知构件'

      if (!LOCKED_ID.includes(localId)) {
        promises.push(model.highlight([localId], highlightMaterial))
      }

      selectedLocalId = localId
      emit('select-entity', { localId, name })

    } else {
      const toReset = selectedLocalId !== null && !LOCKED_ID.includes(selectedLocalId)
          ? [selectedLocalId]
          : []
      if (toReset.length) promises.push(model.resetHighlight(toReset))
      selectedLocalId = null
      emit('select-entity', { localId: null, name: null })
    }

    promises.push(fragments.update(true))
    await Promise.all(promises)
  })
}

// 高亮处理
async function highlightByGuids(guids, colorName) {
  if (!model || !guids.length) return
  LOCKED_ID = []

  const localIds = await model.getLocalIdsByGuids(guids)
  LOCKED_ID.push(...localIds)

  await model.resetHighlight()
  const colorMap = {
    green: new THREE.Color(0x00c853),
    red: new THREE.Color(0xd50000),
    orange: new THREE.Color(0xff6d00)
  }

  const material = {
    color: colorMap[colorName] || colorMap.orange,
    renderedFaces: FRAGS.RenderedFaces.TWO,
    opacity: 1,
    transparent: false
  }

  model.highlight(localIds, material)
  await fragments.update(true)
}

// 清除高亮
async function clearHighlight() {
  LOCKED_ID = []
  if (model) {
    await model.resetHighlight()
    await fragments.update(true)
  }
}

// 获取实体数据
async function getEntityData(localId) {
  if (!model) return null
  const [data] = await model.getItemsData([localId], { attributesDefault: true })
  return data
}

// 获取实体属性集
async function getEntityPsets(localId, format) {
  if (!model) return
  const [data] = await model.getItemsData([localId], {
    attributesDefault: false,
    attributes: ['Name', 'NominalValue'],
    relations: {
      IsDefinedBy: { attributes: true, relations: true },
      DefinesOcurrence: { attributes: false, relations: false },
    },
  })

  const rawPsets = data.IsDefinedBy || []
  const result = format ? formatItemPsets(rawPsets) : rawPsets
  console.log('PropertySets:', result)
}

// 格式化属性集
function formatItemPsets(rawPsets) {
  const result = {}
  for (const pset of rawPsets) {
    const psetName = pset.Name?.value
    const propsArr = pset.HasProperties
    if (!psetName || !Array.isArray(propsArr)) continue
    const props = {}
    for (const prop of propsArr) {
      const name = prop.Name?.value
      const value = prop.NominalValue?.value
      if (name !== undefined && value !== undefined) props[name] = value
    }
    result[psetName] = props
  }
  return result
}

// 获取类别名称
async function getCategoryNames(category) {
  if (!model) return
  const ids = await model.getItemsOfCategories([new RegExp(`^${category}$`)])
  const localIds = ids[category]
  const data = await model.getItemsData(localIds, {
    attributesDefault: false,
    attributes: ['Name'],
  })

  const names = data
      .map((d) => (d.Name?.value ? String(d.Name.value) : null))
      .filter(Boolean)
  console.log('Names:', names)
}

// 加载类别几何
async function loadCategoryGeometries(category) {
  if (!model) return
  const items = await model.getItemsOfCategories([new RegExp(`^${category}$`)])
  const localIds = Object.values(items).flat()
  const geometries = await model.getItemsGeometry(localIds)

  const mat = new THREE.MeshLambertMaterial({ color: 'purple' })
  geometries.forEach((geoArr) =>
      geoArr.forEach((g) => {
        const mesh = createMesh(g, mat)
        if (mesh) world.scene.three.add(mesh)
      })
  )
  await model.setVisible(localIds, false)
  await fragments.update(true)
}

// 创建网格
function createMesh(data, material) {
  const { positions, indices, normals, transform } = data
  if (!(positions && indices && normals)) return null
  const geo = new THREE.BufferGeometry()
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geo.setAttribute('normal', new THREE.BufferAttribute(normals, 3))
  geo.setIndex(Array.from(indices))
  const mesh = new THREE.Mesh(geo, material)
  mesh.applyMatrix4(transform)
  meshes.push(mesh)
  return mesh
}

// 清除几何
async function disposeGeometries() {
  meshes.forEach((m) => {
    m.removeFromParent()
    m.geometry.dispose()
    const materials = Array.isArray(m.material) ? m.material : [m.material]
    materials.forEach((mat) => mat.dispose())
  })
  meshes.length = 0
  if (model) {
    await model.setVisible(undefined, true)
    await fragments.update(true)
  }
}

defineExpose({
  loadModel,
  highlightByGuids,
  clearHighlight,
  getEntityData,
  getEntityPsets,
  getCategoryNames,
  loadCategoryGeometries,
  disposeGeometries,
})
</script>

<style scoped>
.viewport {
  width: 100%;
  height: 100vh;
  overflow: hidden;
}
</style>