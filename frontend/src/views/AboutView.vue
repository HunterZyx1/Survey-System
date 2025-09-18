<template>
  <div class="about">
    <div v-if="userStore.isAuthenticated" class="user-status">
      <el-alert
        :title="`欢迎，${userStore.user?.username}!`"
        :description="`您当前的身份是：${userStore.isAdmin ? '管理员' : '普通用户'}`"
        type="success"
        show-icon
        style="margin-bottom: 30px; max-width: 800px;"
      />
    </div>
    
    <!-- 管理员用户管理功能 -->
    <div v-if="userStore.isAdmin" class="admin-user-management" style="width: 100%; max-width: 1000px;">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>用户管理</span>
            <el-button type="primary" @click="fetchUsers" size="small">刷新</el-button>
          </div>
        </template>
        
        <el-table :data="users" style="width: 100%" v-loading="loadingUsers">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="username" label="用户名" />
          <el-table-column prop="email" label="邮箱" />
          <el-table-column label="角色" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.is_admin ? 'danger' : 'success'">
                {{ scope.row.is_admin ? '管理员' : '用户' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="注册时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button size="small" @click="editUser(scope.row)">编辑</el-button>
              <el-button 
                size="small" 
                type="danger" 
                @click="deleteUser(scope.row)"
                :disabled="scope.row.id === userStore.user?.id"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 添加用户按钮 -->
        <div style="margin-top: 20px; text-align: right;">
          <el-button type="primary" @click="showAddUserDialog = true">添加用户</el-button>
        </div>
      </el-card>
    </div>
    
    <!-- 普通用户显示欢迎信息 -->
    <div v-else class="user-welcome" style="text-align: center; padding: 50px 20px;">
      <h2>欢迎使用调查系统</h2>
      <p>请登录以访问更多功能</p>
    </div>
    
    <!-- 编辑用户对话框 -->
    <el-dialog v-model="showEditUserDialog" title="编辑用户" width="500px">
      <el-form :model="editingUser" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="editingUser.username" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editingUser.email" type="email" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="editingUser.password" type="password" placeholder="留空则不修改密码" />
        </el-form-item>
        <el-form-item label="角色">
          <el-switch 
            v-model="editingUser.is_admin" 
            active-text="管理员" 
            inactive-text="用户"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditUserDialog = false">取消</el-button>
          <el-button type="primary" @click="saveUserChanges">保存</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 添加用户对话框 -->
    <el-dialog v-model="showAddUserDialog" title="添加用户" width="500px">
      <el-form :model="newUser" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="newUser.username" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="newUser.email" type="email" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="newUser.password" type="password" />
        </el-form-item>
        <el-form-item label="角色">
          <el-switch 
            v-model="newUser.is_admin" 
            active-text="管理员" 
            inactive-text="用户"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddUserDialog = false">取消</el-button>
          <el-button type="primary" @click="addUser">添加</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const userStore = useUserStore()
const users = ref<any[]>([])
const loadingUsers = ref(false)
const showEditUserDialog = ref(false)
const showAddUserDialog = ref(false)
const editingUser = ref({
  id: 0,
  username: '',
  email: '',
  password: '',
  is_admin: false
})
const newUser = ref({
  username: '',
  email: '',
  password: '',
  is_admin: false
})

onMounted(() => {
  if (userStore.isAdmin) {
    fetchUsers()
  }
})

const fetchUsers = async () => {
  try {
    loadingUsers.value = true
    const token = userStore.token || localStorage.getItem('token')
    const response = await axios.get('http://localhost:5000/api/users', {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    users.value = response.data
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loadingUsers.value = false
  }
}

const editUser = (user: any) => {
  editingUser.value = { ...user, password: '' }
  showEditUserDialog.value = true
}

const saveUserChanges = async () => {
  try {
    const token = userStore.token || localStorage.getItem('token')
    const updateData: any = {
      username: editingUser.value.username,
      email: editingUser.value.email,
      is_admin: editingUser.value.is_admin
    }
    
    // 只有在密码不为空时才更新密码
    if (editingUser.value.password) {
      updateData.password = editingUser.value.password
    }
    
    await axios.put(`http://localhost:5000/api/users/${editingUser.value.id}`, updateData, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    
    ElMessage.success('用户信息更新成功')
    showEditUserDialog.value = false
    fetchUsers()
  } catch (error) {
    console.error('更新用户信息失败:', error)
    ElMessage.error('更新用户信息失败')
  }
}

const deleteUser = async (user: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除用户 "${user.username}" 吗？此操作不可撤销。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    const token = userStore.token || localStorage.getItem('token')
    await axios.delete(`http://localhost:5000/api/users/${user.id}`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    
    ElMessage.success('用户删除成功')
    fetchUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
      ElMessage.error('删除用户失败')
    }
  }
}

const addUser = async () => {
  try {
    const token = userStore.token || localStorage.getItem('token')
    await axios.post('http://localhost:5000/api/register', {
      username: newUser.value.username,
      email: newUser.value.email,
      password: newUser.value.password
    })
    
    // 设置用户权限
    const createdUser = users.value.find((u: any) => u.username === newUser.value.username)
    if (createdUser) {
      await axios.put(`http://localhost:5000/api/users/${createdUser.id}`, {
        is_admin: newUser.value.is_admin
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })
    }
    
    ElMessage.success('用户添加成功')
    showAddUserDialog.value = false
    newUser.value = {
      username: '',
      email: '',
      password: '',
      is_admin: false
    }
    fetchUsers()
  } catch (error) {
    console.error('添加用户失败:', error)
    ElMessage.error('添加用户失败')
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN')
}
</script>

<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    padding: 30px 20px;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-welcome h2 {
  color: #333;
  margin-bottom: 10px;
}

.user-welcome p {
  color: #666;
  font-size: 1.1rem;
}
</style>