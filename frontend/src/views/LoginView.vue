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
              name="login-username"
              autocomplete="username"
            />
          </el-form-item>

          <el-form-item label="密码" prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              show-password
              size="large"
              name="login-password"
              autocomplete="current-password"
            />
          </el-form-item>

          <el-form-item label="角色" prop="role">
            <div class="role-selection">
              <el-radio-group v-model="loginForm.role" size="large">
                <el-radio label="user" class="role-option">
                  <div class="role-item">
                    <div class="role-icon user-icon">
                      <i class="el-icon-user"></i>
                    </div>
                    <span class="role-text">用户</span>
                  </div>
                </el-radio>
                <el-radio label="admin" class="role-option">
                  <div class="role-item">
                    <div class="role-icon admin-icon">
                      <i class="el-icon-s-custom"></i>
                    </div>
                    <span class="role-text">管理员</span>
                  </div>
                </el-radio>
              </el-radio-group>
            </div>
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
        
        <div class="register-link">
          <p>还没有账户？<el-button type="text" @click="goToRegister">立即注册</el-button></p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import axios from 'axios'
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

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true

      try {
        // 准备登录数据
        const loginData = {
          username: loginForm.username,
          password: loginForm.password
        }

        // 调用登录API
        const response = await axios.post('http://localhost:5000/api/login', loginData)
        
        ElMessage.success('登录成功')
        
        // 使用Pinia状态管理
        userStore.login({
          username: response.data.user.username,
          is_admin: response.data.user.is_admin,
          token: response.data.token
        })
        
        // 根据角色跳转到相应页面
        if (response.data.user.is_admin) {
          router.push('/admin')
        } else {
          router.push('/survey')
        }
      } catch (error: any) {
        console.error('登录失败:', error)
        if (error.response && error.response.data && error.response.data.message) {
          ElMessage.error(error.response.data.message)
        } else {
          ElMessage.error('登录失败，请重试')
        }
      } finally {
        loading.value = false
      }
    }
  })
}

const goToRegister = () => {
  router.push('/register')
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

.role-selection {
  display: flex;
  justify-content: center;
  width: 100%;
}

.role-option {
  margin: 0 15px;
}

.role-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
}

.role-icon {
  width: 15px;
  height: 15px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 8px;
  border: 2px solid #dcdfe6;
  transition: all 0.3s ease;
}

.role-icon i {
  font-size: 12px;
}

.user-icon {
  color: #409eff;
}

.admin-icon {
  color: #e6a23c;
}

.role-text {
  font-size: 14px;
  color: #606266;
}

/* 选中状态样式 */
:deep(.el-radio__input.is-checked + .el-radio__label .role-icon) {
  border-color: #409eff;
  background-color: rgba(64, 158, 255, 0.1);
}

:deep(.el-radio__input.is-checked + .el-radio__label .user-icon) {
  border-color: #409eff;
  background-color: rgba(64, 158, 255, 0.1);
}

:deep(.el-radio__input.is-checked + .el-radio__label .admin-icon) {
  border-color: #e6a23c;
  background-color: rgba(230, 162, 60, 0.1);
}

:deep(.el-radio__input.is-checked + .el-radio__label .role-text) {
  color: #409eff;
  font-weight: 500;
}

/* 隐藏默认的radio按钮 */
:deep(.el-radio__input) {
  display: none;
}

.register-link {
  text-align: center;
  margin-top: 20px;
}

.register-link p {
  margin: 0;
  color: #666;
}
</style>
