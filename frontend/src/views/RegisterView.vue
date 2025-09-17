<template>
  <div class="register-page">
    <div class="register-container">
      <el-card class="register-card">
        <template #header>
          <div class="card-header">
            <h2>用户注册</h2>
          </div>
        </template>
        
        <el-form 
          ref="registerFormRef" 
          :model="registerForm" 
          :rules="registerRules" 
          label-position="top" 
          @submit.prevent="handleRegister"
          autocomplete="off"
        >
          <el-form-item label="用户名" prop="username">
            <el-input 
              v-model="registerForm.username" 
              placeholder="请输入用户名" 
              clearable
              size="large"
              name="register-username"
              autocomplete="username"
            />
          </el-form-item>
          
          <el-form-item label="邮箱" prop="email">
            <el-input 
              v-model="registerForm.email" 
              type="email" 
              placeholder="请输入邮箱" 
              clearable
              size="large"
              name="register-email"
              autocomplete="email"
            />
          </el-form-item>
          
          <el-form-item label="密码" prop="password">
            <el-input 
              v-model="registerForm.password" 
              type="password" 
              placeholder="请输入密码" 
              show-password
              size="large"
              name="register-password"
              autocomplete="new-password"
            />
          </el-form-item>
          
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input 
              v-model="registerForm.confirmPassword" 
              type="password" 
              placeholder="请再次输入密码" 
              show-password
              size="large"
              name="register-confirm-password"
              autocomplete="new-password"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              size="large" 
              native-type="submit" 
              :loading="loading"
              style="width: 100%"
            >
              注册
            </el-button>
          </el-form-item>
        </el-form>
        
        <div class="login-link">
          <p>已有账户？<el-button type="text" @click="goToLogin">立即登录</el-button></p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import type { FormInstance, FormRules } from 'element-plus'

interface RegisterForm {
  username: string
  email: string
  password: string
  confirmPassword: string
}

const router = useRouter()
const registerFormRef = ref<FormInstance>()
const loading = ref(false)

const registerForm = reactive<RegisterForm>({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const registerRules = reactive<FormRules>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
})

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate((valid) => {
    if (valid) {
      // 注册过程
      loading.value = true
      
      // 准备注册数据
      const registerData = {
        username: registerForm.username,
        email: registerForm.email,
        password: registerForm.password
      }
      
      // 调用注册API
      axios.post('http://localhost:5000/api/register', registerData)
        .then(response => {
          ElMessage.success('注册成功！')
          // 注册成功后跳转到登录页面
          router.push('/login')
        })
        .catch(error => {
          console.error('注册失败:', error)
          if (error.response && error.response.data && error.response.data.message) {
            ElMessage.error(error.response.data.message)
          } else {
            ElMessage.error('注册失败，请重试')
          }
        })
        .finally(() => {
          loading.value = false
        })
    }
  })
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px;
}

.register-container {
  width: 100%;
  max-width: 400px;
}

.register-card {
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

.login-link {
  text-align: center;
  margin-top: 20px;
}

.login-link p {
  margin: 0;
  color: #666;
}
</style>