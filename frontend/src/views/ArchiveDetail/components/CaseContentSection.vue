<template>
  <div class="content-section-card military-card" v-if="show">
    <div class="content-section-header">
      <div class="section-header-left">
        <div class="section-number">{{ number }}</div>
        <div>
          <h3 class="section-title">{{ title }}</h3>
          <p class="section-subtitle">{{ subtitle }}</p>
        </div>
      </div>
      <slot name="action"></slot>
    </div>
    <div class="content-section-body">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  number: number | string
  title: string
  subtitle: string
  show?: boolean
}>()
</script>

<style scoped>
.content-section-card {
  padding: 24px;
}

.content-section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--military-border);
}

.section-header-left {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  flex: 1;
}

.section-number {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--military-primary);
  color: #ffffff;
  border-radius: 50%;
  font-size: 16px;
  font-weight: 700;
  flex-shrink: 0;
}

.section-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--military-text-primary);
  margin: 0 0 4px 0;
}

.section-subtitle {
  font-size: 13px;
  color: var(--military-text-muted);
  margin: 0;
}

.content-section-body {
  padding-top: 8px;
}

.person-card {
  padding: 20px;
  background: var(--military-bg-input);
  border-radius: var(--military-radius-md);
  border: 1px solid var(--military-border);
}

.person-name-large {
  font-size: 24px;
  font-weight: 700;
  color: var(--military-primary);
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid var(--military-border);
}

.person-info-detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.person-detail-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.detail-label {
  font-size: 14px;
  color: var(--military-text-muted);
  font-weight: 500;
  min-width: 80px;
}

.detail-value {
  font-size: 15px;
  color: var(--military-text-primary);
  font-weight: 600;
}

.text-content-card {
  font-size: 15px;
  line-height: 1.8;
  color: var(--military-text-primary);
  white-space: pre-wrap;
  word-wrap: break-word;
  padding: 20px;
  background: var(--military-bg-input);
  border-radius: var(--military-radius-md);
  border: 1px solid var(--military-border);
}

.text-content-card.warning {
  border-left: 4px solid #f59e0b;
  background: rgba(245, 158, 11, 0.05);
}

:deep(.highlight-mark) {
  background: #fef08a;
  color: #854d0e;
  padding: 2px 4px;
  border-radius: 3px;
  font-weight: 600;
}
</style>
