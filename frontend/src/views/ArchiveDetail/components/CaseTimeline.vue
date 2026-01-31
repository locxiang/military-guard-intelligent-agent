<template>
  <div class="sidebar-card military-card" v-if="timeline && timeline.length > 0">
    <div class="sidebar-header">
      <el-icon class="sidebar-icon"><Clock /></el-icon>
      <h3 class="sidebar-title">案件时间线</h3>
    </div>
    <div class="sidebar-body">
      <div class="compact-timeline">
        <div
          v-for="(item, index) in timeline"
          :key="index"
          class="compact-timeline-item"
          :class="`timeline-type-${item.type}`"
        >
          <div class="compact-timeline-dot" :class="`dot-type-${item.type}`">
            <el-icon class="compact-timeline-icon">
              <component :is="getTimelineIcon(item.type)" />
            </el-icon>
          </div>
          <div class="compact-timeline-content">
            <div class="compact-timeline-time">{{ formatDateTime(item.time) }}</div>
            <div class="compact-timeline-event">{{ item.event }}</div>
            <div class="compact-timeline-desc" v-if="item.description">{{ item.description }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Clock, Warning, Search, Flag, CircleCheck, EditPen } from '@element-plus/icons-vue'
import { formatDateTime } from '../utils'

const props = defineProps<{
  timeline?: Array<{
    time: string
    event: string
    type: 'incident' | 'investigation' | 'filing' | 'judgment' | 'system'
    typeLabel: string
    description?: string
    timestamp: number
  }>
}>()

const getTimelineIcon = (type: string) => {
  const iconMap: Record<string, any> = {
    incident: Warning,
    investigation: Search,
    filing: Flag,
    judgment: CircleCheck,
    system: EditPen
  }
  return iconMap[type] || Clock
}
</script>

<style scoped>
.sidebar-card {
  padding: 20px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--military-border);
}

.sidebar-icon {
  font-size: 20px;
  color: var(--military-primary);
}

.sidebar-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--military-text-primary);
  margin: 0;
  flex: 1;
}

.sidebar-body {
  padding-top: 8px;
}

.compact-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.compact-timeline-item {
  display: flex;
  gap: 12px;
  position: relative;
  padding-left: 8px;
}

.compact-timeline-item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 19px;
  top: 32px;
  width: 2px;
  height: calc(100% + 16px);
  background: var(--military-border);
}

.compact-timeline-dot {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 2px solid var(--military-bg-card);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.compact-timeline-icon {
  font-size: 16px;
  color: #ffffff;
}

.compact-timeline-content {
  flex: 1;
  padding-top: 2px;
}

.compact-timeline-time {
  font-size: 12px;
  color: var(--military-primary);
  font-weight: 600;
  font-family: 'Courier New', monospace;
  margin-bottom: 4px;
}

.compact-timeline-event {
  font-size: 14px;
  font-weight: 600;
  color: var(--military-text-primary);
  margin-bottom: 4px;
}

.compact-timeline-desc {
  font-size: 12px;
  color: var(--military-text-muted);
  line-height: 1.5;
}

.dot-type-incident {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.dot-type-investigation {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.dot-type-filing {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
}

.dot-type-judgment {
  background: linear-gradient(135deg, #10b981, #059669);
}

.dot-type-system {
  background: linear-gradient(135deg, #6b7280, #4b5563);
}
</style>
