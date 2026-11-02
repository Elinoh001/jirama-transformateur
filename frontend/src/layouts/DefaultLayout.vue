<script setup>
import { ref } from 'vue'

import AppNavbar from '@/components/common/AppNavbar.vue'
import AppSidebar from '@/components/common/AppSidebar.vue'

const sidebarOpen = ref(false)
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-surface">
    <AppSidebar :open="sidebarOpen" @close="sidebarOpen = false" />

    <div class="flex min-w-0 flex-1 flex-col">
      <AppNavbar @toggle-sidebar="sidebarOpen = !sidebarOpen" />
      <main class="flex-1 overflow-y-auto p-4 sm:p-6">
        <div class="mx-auto h-full max-w-[1600px]">
          <RouterView />
        </div>
      </main>
    </div>
  </div>
</template>