import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

interface User {
  username: string
  role: 'user' | 'admin'
  token: string
}

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  
  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const isUser = computed(() => user.value?.role === 'user')
  
  function login(userData: User) {
    user.value = userData
    // 保存到本地存储
    localStorage.setItem('user', JSON.stringify(userData))
  }
  
  function logout() {
    user.value = null
    // 清除本地存储
    localStorage.removeItem('user')
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
      }
    }
  }
  
  return { 
    user, 
    isAuthenticated, 
    isAdmin, 
    isUser,
    login, 
    logout,
    initializeUser
  }
})