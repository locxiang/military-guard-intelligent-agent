<script setup lang="ts">
import { useCounterStore } from '@/stores/counter'

const counter = useCounterStore()
</script>

<template>
  <main class="min-h-screen p-8">
    <!-- Tailwind CSS 示例 -->
    <div class="w-full h-[100px] bg-red-500 flex justify-center items-center mb-6 rounded-lg">
      <span class="text-white text-xl font-bold">Hello Tailwind CSS</span>
    </div>

    <!-- Element Plus 示例 -->
    <div class="mb-6">
      <el-button type="primary">Element Plus 按钮</el-button>
    </div>

    <!-- Pinia Store 示例 -->
    <div class="mb-6">
      <p class="text-lg mb-4">当前计数: {{ counter.count }}</p>
      <p class="text-lg mb-4">双倍计数: {{ counter.doubleCount }}</p>
      <el-button type="success" @click="counter.increment()">增加计数</el-button>
    </div>
  </main>
</template>

