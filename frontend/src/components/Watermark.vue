<template>
  <div 
    ref="containerRef"
    class="watermark-container"
    :style="watermarkStyle"
  >
    <div
      v-for="(item, index) in watermarkList"
      :key="index"
      class="watermark-item"
      :style="getItemStyle(item)"
    >
      {{ text }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'

interface Props {
  /** 水印文字 */
  text?: string
  /** 字体大小 */
  fontSize?: number
  /** 字体颜色 */
  fontColor?: string
  /** 透明度 */
  opacity?: number
  /** 旋转角度 */
  rotate?: number
  /** 水印间距 */
  gap?: number
  /** 字体家族 */
  fontFamily?: string
}

const props = withDefaults(defineProps<Props>(), {
  text: '保卫核心业务智能体平台 内部机密 请勿外传',
  fontSize: 14,
  fontColor: '#CCCCCC',
  opacity: 0.2,
  rotate: -45,
  gap: 200,
  fontFamily: 'var(--font-body)'
})

const containerRef = ref<HTMLElement | null>(null)
const watermarkList = ref<Array<{ x: number; y: number }>>([])

const watermarkStyle = computed(() => {
  return {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    pointerEvents: 'none',
    overflow: 'hidden',
    zIndex: 9999
  }
})

const getItemStyle = (item: { x: number; y: number }) => {
  return {
    position: 'absolute',
    left: `${item.x}px`,
    top: `${item.y}px`,
    fontSize: `${props.fontSize}px`,
    color: props.fontColor,
    opacity: props.opacity,
    transform: `rotate(${props.rotate}deg)`,
    transformOrigin: 'center',
    whiteSpace: 'nowrap',
    userSelect: 'none',
    fontFamily: props.fontFamily,
    fontWeight: 400
  }
}

const createWatermark = () => {
  if (!containerRef.value) return

  const container = containerRef.value.parentElement || document.body
  const { clientWidth, clientHeight } = container

  // 清空之前的水印
  watermarkList.value = []

  // 计算需要多少个水印
  const cols = Math.ceil(clientWidth / props.gap) + 1
  const rows = Math.ceil(clientHeight / props.gap) + 1

  // 生成水印位置
  for (let i = 0; i < rows; i++) {
    for (let j = 0; j < cols; j++) {
      const x = j * props.gap
      const y = i * props.gap
      watermarkList.value.push({ x, y })
    }
  }
}

onMounted(() => {
  createWatermark()
  
  // 监听窗口大小变化
  window.addEventListener('resize', createWatermark)
  
  // 使用 ResizeObserver 监听容器大小变化
  if (containerRef.value?.parentElement) {
    const resizeObserver = new ResizeObserver(() => {
      createWatermark()
    })
    resizeObserver.observe(containerRef.value.parentElement)
    
    onUnmounted(() => {
      resizeObserver.disconnect()
    })
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', createWatermark)
})
</script>

<style scoped>
.watermark-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
  z-index: 9999;
}

.watermark-item {
  position: absolute;
  white-space: nowrap;
  user-select: none;
  pointer-events: none;
}
</style>
