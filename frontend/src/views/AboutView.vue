<template>
  <div class="about">
    <h1>This is an about page</h1>
    <p>Survey System v1.0</p>
    
    <div v-if="userStore.isAuthenticated" class="user-status">
      <el-alert
        :title="`欢迎，${userStore.user?.username}!`"
        :description="`您当前的身份是：${userStore.isAdmin ? '管理员' : '普通用户'}`"
        type="success"
        show-icon
        style="margin-top: 20px;"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user'
const userStore = useUserStore()
</script>

<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
}
</style>