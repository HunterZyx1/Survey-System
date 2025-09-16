<template>
  <div class="login-page">
    <div class="login-container">
      <el-card class="login-card">
        <template #header>
          <div class="card-header">
            <h2>用户登录</h2>
          </div>
        </template>
        
        <el-form 
          ref="loginFormRef" 
          :model="loginForm" 
          :rules="loginRules" 
          label-position="top" 
          @submit.prevent="handleLogin"
        >
          <el-form-item label="用户名" prop="username">
            <el-input 
              v-model="loginForm.username" 
              placeholder="请输入用户名" 
              clearable
              size="large"
            />
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input 
              v-model="loginForm.password" 
              type="password" 
              placeholder="请输入密码" 
              show-password
              size="large"
            />
          </el-form-item>
          
          <el-form-item label="角色" prop="role">
            <el-radio-group v-model="loginForm.role" size="large">
              <el-radio-button label="user">用户</el-radio-button>
              <el-radio-button label="admin">管理员</el-radio-button>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              size="large" 
              native-type="submit" 
              :loading="loading"
              style="width: 100%"
            >
              登录
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import type { FormInstance, FormRules } from 'element-plus'

interface LoginForm {
  username: string
  password: string
  role: string
}

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive<LoginForm>({
  username: '',
  password: '',
  role: 'user' // 默认为普通用户
})

const loginRules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
})

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate((valid) => {
    if (valid) {
      // 模拟登录过程
      loading.value = true
      
      // 模拟API调用延迟
      setTimeout(() => {
        loading.value = false
        
        // 简单的模拟验证（实际项目中应该调用后端API）
        if (loginForm.username === 'admin' && loginForm.password === 'admin123' && loginForm.role === 'admin') {
          // 管理员登录成功
          ElMessage.success('管理员登录成功')
          // 使用Pinia状态管理
          userStore.login({
            username: loginForm.username,
            role: 'admin',
            token: 'admin-token-' + Date.now()
          })
          // 跳转到管理员页面（这里暂时跳转到首页）
          router.push('/')
        } else if (loginForm.username === 'user' && loginForm.password === 'user123' && loginForm.role === 'user') {
          // 用户登录成功
          ElMessage.success('用户登录成功')
          // 使用Pinia状态管理
          userStore.login({
            username: loginForm.username,
            role: 'user',
            token: 'user-token-' + Date.now()
          })
          // 跳转到用户页面（这里暂时跳转到调查页面）
          router.push('/survey')
        } else {
          // 登录失败
          ElMessage.error('用户名或密码错误')
        }
      }, 1000)
    }
  })
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 400px;
}

.login-card {
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.card-header {
  text-align: center;
}

.card-header h2 {
  margin: 0;
  color: #333;
  font-weight: 600;
}

.el-form-item {
  margin-bottom: 24px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #555;
}
</style>