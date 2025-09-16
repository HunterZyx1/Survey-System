<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { useUserStore } from './stores/user'
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

const isLoggedIn = computed(() => userStore.isAuthenticated)
const isAdmin = computed(() => userStore.isAdmin)
const username = computed(() => userStore.user?.username || '')

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<template>
  <header class="app-header">
    <div class="logo-container">
      <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="40" height="40" />
      <span class="app-title">Survey System</span>
    </div>
    
    <nav v-if="!isLoggedIn">
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/about">About</RouterLink>
    </nav>
    
    <nav v-else>
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/survey">Survey</RouterLink>
      <RouterLink v-if="isAdmin" to="/admin">Admin</RouterLink>
      <RouterLink to="/about">About</RouterLink>
      <div class="user-info">
        <span class="username">{{ username }} ({{ isAdmin ? 'Admin' : 'User' }})</span>
        <button class="logout-btn" @click="handleLogout">Logout</button>
      </div>
    </nav>
  </header>

  <main class="main-content">
    <RouterView />
  </main>
</template>

<style scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: var(--color-background-soft);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.logo-container {
  display: flex;
  align-items: center;
}

.logo {
  margin-right: 1rem;
}

.app-title {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--color-heading);
}

nav {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}

nav a {
  font-size: 1rem;
  text-decoration: none;
  color: var(--color-text);
  padding: 0.5rem 0;
  border-bottom: 2px solid transparent;
  transition: border-color 0.3s, color 0.3s;
}

nav a.router-link-exact-active {
  color: hsla(160, 100%, 37%, 1);
  border-bottom-color: hsla(160, 100%, 37%, 1);
}

nav a:hover {
  color: hsla(160, 100%, 37%, 1);
  background-color: transparent;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-left: 1rem;
  padding-left: 1rem;
  border-left: 1px solid var(--color-border);
}

.username {
  font-weight: 500;
  color: var(--color-heading);
}

.logout-btn {
  background-color: #f56c6c;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background-color: #e45656;
}

.main-content {
  padding: 2rem;
}
</style>
