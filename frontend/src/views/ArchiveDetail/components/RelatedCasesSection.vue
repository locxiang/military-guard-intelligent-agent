<template>
  <div class="related-cases-section military-card" v-if="relatedCases.length > 0">
    <div class="related-cases-header">
      <div class="related-cases-header-left">
        <el-icon class="related-cases-icon"><Connection /></el-icon>
        <h3 class="related-cases-title">关联案卷</h3>
        <span class="related-cases-count">（{{ filteredRelatedCases.length }} 个）</span>
      </div>
      <div class="related-cases-filters">
        <button 
          class="filter-btn" 
          :class="{ active: relationFilter === 'person' }"
          @click="relationFilter = 'person'"
        >
          按人员
        </button>
        <button 
          class="filter-btn" 
          :class="{ active: relationFilter === 'department' }"
          @click="relationFilter = 'department'"
        >
          按部门
        </button>
        <button 
          class="filter-btn" 
          :class="{ active: relationFilter === 'type' }"
          @click="relationFilter = 'type'"
        >
          按罪名
        </button>
        <button 
          class="filter-btn" 
          :class="{ active: relationFilter === 'time' }"
          @click="relationFilter = 'time'"
        >
          按时间
        </button>
      </div>
    </div>
    <div class="related-cases-grid">
      <div
        v-for="item in filteredRelatedCases"
        :key="item.id"
        class="related-case-card"
        @click="$emit('view-case', item.id)"
      >
        <div class="related-case-card-header">
          <span class="related-case-card-number">{{ item.caseNo }}</span>
          <el-tag size="small" :type="getStatusType(item.status)">
            {{ getStatusText(item.status) }}
          </el-tag>
        </div>
        <div class="related-case-card-title">{{ item.title || item.caseName }}</div>
        <div class="related-case-card-info">
          <div class="info-row" v-if="item.personName">
            <span class="info-label">人员</span>
            <span class="info-value">{{ item.personName }}</span>
          </div>
          <div class="info-row" v-if="item.sourceDepartment">
            <span class="info-label">部门</span>
            <span class="info-value">{{ item.sourceDepartment }}</span>
          </div>
          <div class="info-row" v-if="item.incidentTime">
            <span class="info-label">时间</span>
            <span class="info-value">{{ formatDate(item.incidentTime) }}</span>
          </div>
        </div>
        <div class="related-case-card-reason">
          <el-tag size="small" type="info">{{ item.relationReason }}</el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Connection } from '@element-plus/icons-vue'
import { getStatusType, getStatusText, formatDate } from '../utils'

const props = defineProps<{
  relatedCases: any[]
}>()

const emit = defineEmits<{
  'view-case': [id: number]
}>()

const relationFilter = ref<'person' | 'department' | 'type' | 'time'>('person')

const filteredRelatedCases = computed(() => {
  return props.relatedCases.filter(item => {
    if (relationFilter.value === 'person') {
      return item.relationReason?.includes('人员')
    } else if (relationFilter.value === 'department') {
      return item.relationReason?.includes('部门')
    } else if (relationFilter.value === 'type') {
      return item.relationReason?.includes('罪名')
    } else if (relationFilter.value === 'time') {
      return item.relationReason?.includes('时间')
    }
    return true
  })
})
</script>

<style scoped>
.related-cases-section {
  padding: 24px;
  margin-top: 20px;
}

.related-cases-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--military-border);
  flex-wrap: wrap;
  gap: 16px;
}

.related-cases-header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.related-cases-icon {
  font-size: 24px;
  color: var(--military-primary);
}

.related-cases-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--military-text-primary);
  margin: 0;
}

.related-cases-count {
  font-size: 14px;
  color: var(--military-text-muted);
}

.related-cases-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 6px 14px;
  background: var(--military-bg-input);
  border: 1px solid var(--military-border);
  border-radius: var(--military-radius-md);
  color: var(--military-text-primary);
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: var(--military-primary);
}

.filter-btn.active {
  background: var(--military-primary);
  color: #ffffff;
  border-color: var(--military-primary);
}

.related-cases-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.related-case-card {
  padding: 16px;
  background: var(--military-bg-input);
  border: 1px solid var(--military-border);
  border-radius: var(--military-radius-md);
  cursor: pointer;
  transition: all 0.2s;
}

.related-case-card:hover {
  border-color: var(--military-primary);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
  transform: translateY(-2px);
}

.related-case-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.related-case-card-number {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  font-weight: 600;
  color: var(--military-primary);
}

.related-case-card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--military-text-primary);
  margin-bottom: 12px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.related-case-card-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.info-label {
  color: var(--military-text-muted);
  font-weight: 500;
  min-width: 50px;
}

.info-value {
  color: var(--military-text-primary);
  font-weight: 600;
}

.related-case-card-reason {
  padding-top: 12px;
  border-top: 1px solid var(--military-border);
}

@media (max-width: 1024px) {
  .related-cases-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .related-cases-grid {
    grid-template-columns: 1fr;
  }
  
  .related-cases-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .related-cases-filters {
    width: 100%;
  }
  
  .filter-btn {
    flex: 1;
  }
}
</style>
