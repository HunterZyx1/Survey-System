import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

interface User {
  id?: number
  username: string
  is_admin: boolean
  token: string
  rememberMe?: boolean // 添加记住我标志
  expires?: number // 添加过期时间戳
}

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  
  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.is_admin || false)
  const isUser = computed(() => user.value && !user.value.is_admin)
  const token = computed(() => user.value?.token || null)
  
  function login(userData: User, rememberMe: boolean = false) {
    // 设置过期时间（10天）
    const expires = rememberMe ? Date.now() + 10 * 24 * 60 * 60 * 1000 : 0
    
    const userWithRememberMe = {
      ...userData,
      rememberMe,
      expires
    }
    
    user.value = userWithRememberMe
    
    // 保存到本地存储
    if (rememberMe) {
      localStorage.setItem('user', JSON.stringify(userWithRememberMe))
      localStorage.setItem('token', userData.token)
    } else {
      sessionStorage.setItem('user', JSON.stringify(userWithRememberMe))
      sessionStorage.setItem('token', userData.token)
    }
  }
  
  function logout() {
    user.value = null
    // 清除本地存储
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    sessionStorage.removeItem('user')
    sessionStorage.removeItem('token')
  }
  
  function initializeUser() {
    // 检查localStorage中是否有记住我的用户信息
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser)
        // 检查是否过期
        if (parsedUser.rememberMe && parsedUser.expires && parsedUser.expires > Date.now()) {
          user.value = parsedUser
          return
        } else if (parsedUser.rememberMe) {
          // 如果已过期，清除存储
          localStorage.removeItem('user')
          localStorage.removeItem('token')
        }
      } catch (e) {
        console.error('Failed to parse stored user data', e)
        localStorage.removeItem('user')
        localStorage.removeItem('token')
      }
    }
    
    // 检查sessionStorage中的用户信息
    const sessionUser = sessionStorage.getItem('user')
    if (sessionUser) {
      try {
        user.value = JSON.parse(sessionUser)
      } catch (e) {
        console.error('Failed to parse session user data', e)
        sessionStorage.removeItem('user')
        sessionStorage.removeItem('token')
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