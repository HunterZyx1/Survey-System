<script setup lang="ts">
import TheWelcome from '../components/TheWelcome.vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <main>
    <div v-if="!userStore.isAuthenticated" class="login-prompt">
      <el-alert
        title="请先登录"
        description="您需要登录后才能使用调查系统功能"
        type="info"
        show-icon
        style="margin-bottom: 20px;"
      >
        <template #default>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <strong>请先登录</strong>
              <p style="margin: 5px 0 0 0;">您需要登录后才能使用调查系统功能</p>
            </div>
            <el-button type="primary" @click="goToLogin">立即登录</el-button>
          </div>
        </template>
      </el-alert>
    </div>
    <TheWelcome />
  </main>
</template>

<style scoped>
.login-prompt {
  padding: 0 20px;
}
</style>
