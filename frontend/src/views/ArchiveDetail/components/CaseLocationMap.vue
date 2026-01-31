<template>
  <div class="case-location-map military-card">
    <div class="section-header">
      <div class="section-icon">
        <el-icon><Location /></el-icon>
      </div>
      <div class="section-title-area">
        <h3 class="section-title">案发位置</h3>
        <p class="section-subtitle">案件发生地点和相关单位位置示意</p>
      </div>
    </div>

    <!-- 使用 vue-echarts 组件 -->
    <v-chart 
      class="map-container" 
      :option="chartOption" 
      :autoresize="true"
      :theme="'dark'"
    />

    <!-- 位置信息列表 -->
    <div class="location-info-list">
      <!-- 案发单位 -->
      <div class="location-info-item">
        <div class="location-dot unit"></div>
        <div class="location-detail">
          <div class="location-type">案发单位</div>
          <div class="location-name">{{ sourceDepartment }}</div>
        </div>
        <div class="location-region">{{ unitRegion }}</div>
      </div>
      
      <!-- 案发地点 -->
      <div class="location-info-item">
        <div class="location-dot incident"></div>
        <div class="location-detail">
          <div class="location-type">案发地点</div>
          <div class="location-name">{{ incidentPlace }}</div>
        </div>
        <div class="location-region">{{ incidentRegion }}</div>
      </div>

      <!-- 案发时间 -->
      <div class="location-info-item">
        <div class="location-dot time"></div>
        <div class="location-detail">
          <div class="location-type">案发时间</div>
          <div class="location-name">{{ incidentTime }}</div>
        </div>
      </div>
    </div>

    <!-- 地图图例 -->
    <div class="map-legend">
      <div class="legend-item">
        <span class="legend-dot unit"></span>
        <span class="legend-text">案发单位</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot incident"></span>
        <span class="legend-text">案发地点</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Location } from '@element-plus/icons-vue'
import VChart from 'vue-echarts'
import * as echarts from 'echarts'
// 导入真实的中国地图 GeoJSON 数据
import chinaGeoJSON from '@/assets/map/china.json'

// 注册中国地图
echarts.registerMap('china', chinaGeoJSON as any)

// 写死的示例数据
const sourceDepartment = '某部队驻地'
const incidentPlace = '营区东侧训练场'
const incidentTime = '2024-03-15 14:30'
const unitRegion = '陕西省西安市'
const incidentRegion = '陕西省渭南市'

// 地图上的位置坐标（经纬度）
const unitLocation = [108.95, 34.27]      // 西安
const incidentLocation = [109.51, 34.50]  // 渭南

// 使用 computed 定义图表配置
const chartOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'item',
    formatter: (params: any) => {
      if (params.seriesType === 'effectScatter') {
        return `<div style="font-weight:bold">${params.name}</div>`
      }
      if (params.name) {
        return params.name
      }
      return ''
    }
  },
  geo: {
    map: 'china',
    roam: true,
    zoom: 1.2,
    center: [108, 34],
    label: {
      show: false
    },
    itemStyle: {
      areaColor: 'rgba(59, 130, 246, 0.15)',
      borderColor: 'rgba(59, 130, 246, 0.5)',
      borderWidth: 1,
      shadowColor: 'rgba(59, 130, 246, 0.3)',
      shadowBlur: 10
    },
    emphasis: {
      label: {
        show: true,
        color: '#fff',
        fontSize: 12
      },
      itemStyle: {
        areaColor: 'rgba(59, 130, 246, 0.4)'
      }
    },
    select: {
      label: {
        show: true,
        color: '#fff'
      },
      itemStyle: {
        areaColor: 'rgba(59, 130, 246, 0.5)'
      }
    }
  },
  series: [
    {
      name: '案件位置',
      type: 'effectScatter',
      coordinateSystem: 'geo',
      data: [
        {
          name: '案发单位',
          value: [...unitLocation, 80],
          itemStyle: {
            color: '#3B82F6'
          }
        },
        {
          name: '案发地点',
          value: [...incidentLocation, 100],
          itemStyle: {
            color: '#EF4444'
          }
        }
      ],
      symbolSize: function (val: number[]) {
        return val[2] / 5
      },
      showEffectOn: 'render',
      rippleEffect: {
        brushType: 'stroke',
        scale: 3
      },
      label: {
        formatter: '{b}',
        position: 'right',
        show: true,
        color: '#fff',
        fontSize: 12,
        fontWeight: 'bold',
        textShadowColor: 'rgba(0, 0, 0, 0.8)',
        textShadowBlur: 4
      },
      zlevel: 1
    },
    {
      name: '连接线',
      type: 'lines',
      coordinateSystem: 'geo',
      data: [
        {
          coords: [unitLocation, incidentLocation],
          lineStyle: {
            color: 'rgba(255, 255, 255, 0.6)',
            width: 2,
            type: 'dashed'
          }
        }
      ],
      effect: {
        show: true,
        period: 4,
        trailLength: 0.3,
        color: '#fff',
        symbolSize: 4
      },
      zlevel: 2
    }
  ]
}))
</script>

<style scoped>
.case-location-map {
  padding: 20px;
}

.section-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.section-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--military-primary);
  color: #ffffff;
  border-radius: var(--military-radius-md);
  font-size: 20px;
  flex-shrink: 0;
}

.section-title-area {
  flex: 1;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--military-text-primary);
  margin: 0 0 4px 0;
}

.section-subtitle {
  font-size: 12px;
  color: var(--military-text-muted);
  margin: 0;
}

.map-container {
  width: 100%;
  height: 350px;
  background: linear-gradient(135deg, rgba(10, 22, 40, 0.95) 0%, rgba(20, 40, 80, 0.8) 100%);
  border-radius: var(--military-radius-md);
  border: 1px solid var(--military-border);
  margin-bottom: 16px;
}

/* 位置信息列表 */
.location-info-list {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

@media (max-width: 768px) {
  .location-info-list {
    grid-template-columns: 1fr;
  }
}

.location-info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--military-bg-input);
  border-radius: var(--military-radius-sm);
  border: 1px solid var(--military-border);
}

.location-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}

.location-dot.unit {
  background: #3B82F6;
  box-shadow: 0 0 8px rgba(59, 130, 246, 0.5);
}

.location-dot.incident {
  background: #EF4444;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
}

.location-dot.time {
  background: #F59E0B;
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.5);
}

.location-detail {
  flex: 1;
}

.location-type {
  font-size: 11px;
  color: var(--military-text-muted);
  margin-bottom: 2px;
}

.location-name {
  font-size: 14px;
  color: var(--military-text-primary);
  font-weight: 500;
}

.location-region {
  font-size: 12px;
  color: var(--military-text-muted);
  padding: 4px 8px;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 4px;
}

/* 图例 */
.map-legend {
  display: flex;
  gap: 20px;
  padding-top: 12px;
  border-top: 1px solid var(--military-border);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-dot.unit {
  background: #3B82F6;
}

.legend-dot.incident {
  background: #EF4444;
}

.legend-text {
  font-size: 12px;
  color: var(--military-text-muted);
}
</style>
