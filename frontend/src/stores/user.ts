import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

interface User {
  id?: number
  username: string
  is_admin: boolean
  token: string
}

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  
  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.is_admin || false)
  const isUser = computed(() => user.value && !user.value.is_admin)
  const token = computed(() => user.value?.token || null)
  
  function login(userData: User) {
    user.value = userData
    // 保存到本地存储
    localStorage.setItem('user', JSON.stringify(userData))
    localStorage.setItem('token', userData.token)
  }
  
  function logout() {
    user.value = null
    // 清除本地存储
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }
  
  function initializeUser() {
    // 从本地存储初始化用户信息
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch (e) {
        console.error('Failed to parse stored user data', e)
        localStorage.removeItem('user')
        localStorage.removeItem('token')
      }
    }
  }
  
  return { 
    user, 
    isAuthenticated, 
    isAdmin, 
    isUser,
    token,
    login, 
    logout,
    initializeUser
  }
})