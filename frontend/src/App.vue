<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div id="app" class="military-theme">
    <RouterView />
  </div>
</template>

<style>
#app {
  min-height: 100vh;
  color: var(--military-text-primary);
}
</style>
