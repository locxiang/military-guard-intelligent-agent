<template>
  <iframe
    :src="`/docx-preview.html?url=${encodeURIComponent(props.docxUrl)}`"
    class="docx-iframe"
  ></iframe>
</template>

<script setup lang="ts">
const props = defineProps<{
  docxUrl: string
}>()
</script>

<style scoped>
.docx-iframe {
  width: 100%;
  height: 600px;
  border: none;
}
</style>
