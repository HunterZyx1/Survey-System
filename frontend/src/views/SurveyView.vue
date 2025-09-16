<template>
  <div class="survey-page-container">
    <el-card class="survey-card">
      <template #header>
        <div class="card-header">
          <h1 v-if="currentSurvey">{{ currentSurvey.title }}</h1>
          <h1 v-else>Survey</h1>
        </div>
      </template>

      <div v-if="!userStore.isAuthenticated" class="login-required">
        <el-alert
          title="需要登录"
          description="请先登录以参与调查"
          type="warning"
          show-icon
        />
        <el-button type="primary" @click="goToLogin" style="margin-top: 20px;">前往登录</el-button>
      </div>
      
      <div v-else-if="loading" class="loading-state">
        <p>Loading surveys...</p>
      </div>
      
      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
      </div>
      
      <div v-else-if="!currentSurvey && surveys.length > 0" class="survey-selection">
        <h2>请选择要参与的调查</h2>
        <el-row :gutter="20">
          <el-col 
            v-for="survey in surveys" 
            :key="survey.id" 
            :span="24" 
            style="margin-bottom: 15px;"
          >
            <el-card class="survey-item-card" @click="selectSurvey(survey)">
              <h3>{{ survey.title }}</h3>
              <p v-if="survey.description">{{ survey.description }}</p>
              <div class="survey-meta">
                <span>问题数: {{ survey.questions.length }}</span>
                <span>创建时间: {{ formatDate(survey.created_at) }}</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <div v-else-if="currentSurvey" class="survey-form">
        <p v-if="currentSurvey.description" class="survey-description">{{ currentSurvey.description }}</p>
        
        <el-form @submit.prevent="submitSurvey" label-position="top">
          <el-card 
            v-for="(question, index) in currentSurvey.questions" 
            :key="question.id" 
            class="question-card"
          >
            <el-form-item :required="question.required">
              <template #label>
                <h3>{{ index + 1 }}. {{ question.text }}</h3>
              </template>

              <!-- Single choice -->
              <el-radio-group 
                v-if="question.type === 1" 
                v-model="responses[question.id]" 
                class="options-group"
              >
                <el-radio
                  v-for="option in question.options"
                  :key="option.id"
                  :value="option.id"
                  border
                  class="option-item"
                >
                  {{ option.text }}
                </el-radio>
              </el-radio-group>

              <!-- Multiple choice -->
              <el-checkbox-group 
                v-else-if="question.type === 2" 
                v-model="selectedOptions[question.id]" 
                class="options-group"
              >
                <el-checkbox
                  v-for="option in question.options"
                  :key="option.id"
                  :value="option.id"
                  border
                  class="option-item"
                >
                  {{ option.text }}
                </el-checkbox>
              </el-checkbox-group>

              <!-- Text answer -->
              <el-input
                v-else-if="question.type === 3"
                type="textarea"
                :rows="4"
                v-model="responses[question.id]"
                placeholder="请输入您的回答..."
              />
            </el-form-item>
          </el-card>

          <el-form-item class="submit-btn-container">
            <el-button 
              type="primary" 
              @click="submitSurvey" 
              size="large" 
              round
              :loading="submitting"
            >
              提交调查
            </el-button>
            <el-button @click="currentSurvey = null" style="margin-left: 15px;">返回调查列表</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <div v-else class="no-surveys">
        <el-empty description="暂无已发布的调查" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

interface Option {
  id: number
  question_id: number
  text: string
  order: number
}

interface Question {
  id: number
  survey_id: number
  text: string
  type: number
  required: boolean
  order: number
  options: Option[]
}

interface Survey {
  id: number
  title: string
  description: string
  is_published: boolean
  created_at: string
  updated_at: string
  questions: Question[]
}

const userStore = useUserStore()
const router = useRouter()
const surveys = ref<Survey[]>([])
const currentSurvey = ref<Survey | null>(null)
const responses = ref<Record<string, any>>({})
const selectedOptions = ref<Record<number, number[]>>({})
const loading = ref(true)
const error = ref('')
const submitting = ref(false)

const goToLogin = () => {
  router.push('/login')
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

onMounted(async () => {
  // 检查用户是否已登录
  if (!userStore.isAuthenticated) {
    loading.value = false
    return
  }
  
  await fetchPublishedSurveys()
})

const fetchPublishedSurveys = async () => {
  try {
    loading.value = true
    const response = await axios.get('http://localhost:5000/api/published-surveys')
    surveys.value = response.data
  } catch (err) {
    error.value = '获取调查列表失败'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const selectSurvey = (survey: Survey) => {
  currentSurvey.value = survey
  // 初始化响应数据
  responses.value = {}
  selectedOptions.value = {}
  
  // 为多选题初始化selectedOptions
  survey.questions.forEach(question => {
    if (question.type === 2) {
      selectedOptions.value[question.id] = []
    }
  })
}

const submitSurvey = async () => {
  if (!userStore.isAuthenticated) {
    ElMessage({
      message: '请先登录后再提交调查',
      type: 'warning',
    })
    router.push('/login')
    return
  }
  
  if (!currentSurvey.value) {
    ElMessage({
      message: '未选择调查',
      type: 'warning',
    })
    return
  }
  
  // 验证必填问题
  for (const question of currentSurvey.value.questions) {
    if (question.required) {
      if (question.type === 2) {
        // 多选题
        if (!selectedOptions.value[question.id] || selectedOptions.value[question.id].length === 0) {
          ElMessage({
            message: `问题 "${question.text}" 是必填项`,
            type: 'warning',
          })
          return
        }
      } else {
        // 单选题和文本题
        if (responses.value[question.id] === undefined || responses.value[question.id] === '') {
          ElMessage({
            message: `问题 "${question.text}" 是必填项`,
            type: 'warning',
          })
          return
        }
      }
    }
  }
  
  try {
    submitting.value = true
    
    const surveyData = {
      survey_id: currentSurvey.value.id,
      responses: responses.value,
      selectedOptions: selectedOptions.value
    }

    const response = await axios.post('http://localhost:5000/api/submit', surveyData)
    ElMessage({
      message: `调查提交成功! 响应ID: ${response.data.survey_response_id}`,
      type: 'success',
    })
    
    // 重置表单并返回调查列表
    responses.value = {}
    selectedOptions.value = {}
    currentSurvey.value = null
  } catch (err) {
    ElMessage({
      message: '提交调查失败，请重试',
      type: 'error',
    })
    console.error(err)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.survey-page-container {
  display: flex;
  justify-content: center;
  padding: 20px 0;
}

.survey-card {
  max-width: 800px;
  width: 100%;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.card-header h1 {
  text-align: center;
  color: #333;
  margin: 0;
  font-size: 2rem;
  font-weight: 600;
}

.loading-state, .error-state {
  text-align: center;
  padding: 40px;
  font-size: 1.2rem;
  color: #666;
}

.survey-selection h2 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.survey-item-card {
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #e0e0e0;
}

.survey-item-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.survey-item-card h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 1.2rem;
  font-weight: 600;
}

.survey-item-card p {
  margin: 0 0 15px 0;
  color: #666;
  font-size: 0.9rem;
}

.survey-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #999;
}

.survey-description {
  color: #666;
  font-size: 1rem;
  margin-bottom: 25px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.question-card {
  margin-bottom: 25px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  background-color: #fafafa;
}

.question-card h3 {
  margin-top: 0;
  color: #444;
  font-size: 1.1rem;
  font-weight: 500;
  margin-bottom: 10px;
}

.options-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.option-item {
  margin-right: 0 !important; /* Override Element Plus default margin */
  width: 100%;
  box-sizing: border-box;
}

.submit-btn-container {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}

.el-button {
  min-width: 200px;
  font-size: 1rem;
}

.no-surveys {
  text-align: center;
  padding: 40px 0;
}
</style>
