<template>
  <div class="official-doc-step3">
    <div class="page-header">
      <el-button @click="goBack" :icon="ArrowLeft">返回修改</el-button>
      <h2>标准公文预览</h2>
      <div class="header-actions">
        <el-button @click="reassembleDocx" :loading="assembling" :icon="Refresh">重新生成</el-button>
        <el-button type="primary" @click="downloadDocx" :loading="downloading" :icon="Download">下载 DOCX</el-button>
      </div>
    </div>

    <div class="preview-container">
      <div v-if="loading" class="loading-state">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>正在生成标准公文...</span>
      </div>
      <div v-else-if="error" class="error-state">
        <el-icon class="error-icon"><WarningFilled /></el-icon>
        <span>{{ error }}</span>
        <el-button @click="assembleDocx">重试</el-button>
      </div>
      <div v-else class="docx-preview-wrapper">
        <DocxPreview :docx-url="docxUrl" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Refresh, Download, Loading, WarningFilled } from '@element-plus/icons-vue'
import DocxPreview from '@/components/DocxPreview.vue'
import { docGenerateApi } from '@/api/doc-generate'

const router = useRouter()
const route = useRoute()

const loading = ref(true)
const error = ref('')
const assembling = ref(false)
const downloading = ref(false)
const docxUrl = ref<string>('')
const currentTaskId = ref<string>('')

const getStoredData = () => {
  try {
    const data = sessionStorage.getItem('officialDocData')
    if (!data) {
      throw new Error('未找到公文数据，请先填写表单并生成内容')
    }
    return JSON.parse(data)
  } catch (e) {
    console.error('读取存储数据失败:', e)
    return null
  }
}

const assembleDocx = async () => {
  const data = getStoredData()
  if (!data) {
    error.value = '未找到公文数据，请先填写表单并生成内容'
    loading.value = false
    return
  }

  loading.value = true
  error.value = ''

  try {
    const result: any = await docGenerateApi.assembleOfficialDoc({
      doc_type: data.docType,
      sections: data.sections,
      form_data: data.formData
    })

    if (result.task_id) {
      currentTaskId.value = result.task_id
      await loadDocxPreview(result.task_id)
    } else if (result.data?.task_id) {
      currentTaskId.value = result.data.task_id
      await loadDocxPreview(result.data.task_id)
    } else {
      error.value = result.message || '生成公文失败'
    }
  } catch (e: any) {
    console.error('组装公文失败:', e)
    error.value = e.message || '组装公文时发生错误'
  } finally {
    loading.value = false
  }
}

const loadDocxPreview = async (taskId: string) => {
  try {
    docxUrl.value = '/api/v1/doc-generate/download/' + taskId + '.docx'
    console.log('[Step3View] 设置文档 URL:', docxUrl.value)
  } catch (e: any) {
    console.error('加载文档预览失败:', e)
    error.value = '加载文档预览失败: ' + (e.message || '未知错误')
  }
}

const reassembleDocx = async () => {
  assembling.value = true
  try {
    await assembleDocx()
    ElMessage.success('公文已重新生成')
  } finally {
    assembling.value = false
  }
}

const downloadDocx = async () => {
  if (!currentTaskId.value) {
    ElMessage.warning('请先生成公文')
    return
  }

  downloading.value = true
  try {
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    const url = '/api/v1/doc-generate/download/' + currentTaskId.value + '.docx'

    const response = await fetch(url, {
      headers: {
        'Authorization': 'Bearer ' + token
      }
    })

    if (!response.ok) {
      throw new Error('下载失败: ' + response.status)
    }

    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = '公文_' + Date.now() + '.docx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)
    ElMessage.success('下载开始')
  } catch (e: any) {
    console.error('下载失败:', e)
    ElMessage.error('下载失败: ' + (e.message || '未知错误'))
  } finally {
    downloading.value = false
  }
}

const goBack = () => {
  router.push('/doc-generate/official/step2')
}

onMounted(() => {
  assembleDocx()
})
</script>

<style scoped>
.official-doc-step3 {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
}

.page-header h2 {
  flex: 1;
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.preview-container {
  flex: 1;
  padding: 24px;
  overflow: hidden;
  position: relative;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
  gap: 16px;
  color: #666;
  font-size: 14px;
}

.loading-state .el-icon {
  font-size: 32px;
  color: var(--military-primary, #3b82f6);
}

.error-state .error-icon {
  font-size: 32px;
  color: #f59e0b;
}

.docx-preview-wrapper {
  width: 100%;
  height: 100%;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}
</style>
