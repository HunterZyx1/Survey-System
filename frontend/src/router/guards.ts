import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

// 创建路由守卫
export function setupRouterGuards(router: any) {
  router.beforeEach((to: any, from: any, next: any) => {
    // 获取用户状态
    const userStore = useUserStore()
    
    // 如果没有初始化用户状态，则初始化
    if (userStore.user === null) {
      userStore.initializeUser()
    }
    
    // 不需要登录的页面
    const whiteList = ['/login', '/register', '/about']
    
    // 如果访问的是登录页且已经登录，则重定向到首页
    if (to.path === '/login' && userStore.isAuthenticated) {
      next('/')
      return
    }
    
    // 如果访问的页面不在白名单中，且用户未登录，则重定向到登录页
    if (!whiteList.includes(to.path) && !userStore.isAuthenticated) {
      next('/login')
      return
    }
    
    // 管理员权限检查（示例）
    if (to.path === '/admin' && !userStore.isAdmin) {
      // 如果不是管理员访问管理页面，重定向到首页或提示无权限
      next('/')
      return
    }
    
    // 其他情况正常跳转
    next()
  })
}