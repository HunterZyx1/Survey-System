<template>
  <div class="admin-page">
    <el-card class="admin-card">
      <template #header>
        <div class="card-header">
          <h2>管理员面板</h2>
        </div>
      </template>
      
      <div class="admin-content">
        <el-alert
          title="欢迎管理员"
          type="success"
          description="您已成功登录管理员账户，可以管理调查系统的所有功能。"
          show-icon
          closable
          style="margin-bottom: 20px;"
        />
        
        <el-tabs v-model="activeTab" type="border-card">
          <el-tab-pane label="仪表板" name="dashboard">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <h3>总调查数</h3>
                    <p class="stat-number">{{ surveys.length }}</p>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="8">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <h3>已发布调查</h3>
                    <p class="stat-number">{{ publishedSurveys.length }}</p>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="8">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <h3>总响应数</h3>
                    <p class="stat-number">{{ totalResponses }}</p>
                  </div>
                </el-card>
              </el-col>
            </el-row>
            
            <div class="admin-actions">
              <h3>管理功能</h3>
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-card class="action-card" shadow="hover">
                    <div class="action-content">
                      <h4>创建新调查</h4>
                      <p>创建新的调查问卷，设置问题和选项</p>
                      <el-button type="primary" style="margin-top: 10px;" @click="activeTab = 'create'">开始创建</el-button>
                    </div>
                  </el-card>
                </el-col>
                
                <el-col :span="8">
                  <el-card class="action-card" shadow="hover">
                    <div class="action-content">
                      <h4>管理调查</h4>
                      <p>查看、编辑和发布调查问卷</p>
                      <el-button type="primary" style="margin-top: 10px;" @click="activeTab = 'manage'; fetchSurveys()">管理调查</el-button>
                    </div>
                  </el-card>
                </el-col>
                
                <el-col :span="8">
                  <el-card class="action-card" shadow="hover">
                    <div class="action-content">
                      <h4>查看调查内容</h4>
                      <p>查看用户填写的调查响应</p>
                      <el-button type="primary" style="margin-top: 10px;" @click="activeTab = 'view-responses'; fetchSurveysForResponseView()">查看响应</el-button>
                    </div>
                  </el-card>
                </el-col>
              </el-row>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="创建调查" name="create">
            <el-card class="create-survey-card">
              <template #header>
                <div class="create-survey-header">
                  <h3>创建新调查</h3>
                </div>
              </template>
              
              <el-form 
                ref="surveyFormRef" 
                :model="surveyForm" 
                label-position="top"
              >
                <el-form-item label="调查标题" prop="title">
                  <el-input 
                    v-model="surveyForm.title" 
                    placeholder="请输入调查标题"
                  />
                </el-form-item>
                
                <el-form-item label="调查描述" prop="description">
                  <el-input 
                    v-model="surveyForm.description" 
                    type="textarea"
                    placeholder="请输入调查描述（可选）"
                    :rows="3"
                  />
                </el-form-item>
                
                <div class="questions-section">
                  <h4>问题列表</h4>
                  
                  <div 
                    v-for="(question, index) in surveyForm.questions" 
                    :key="index" 
                    class="question-item"
                  >
                    <el-card class="question-card">
                      <template #header>
                        <div class="question-header">
                          <span>问题 {{ index + 1 }}</span>
                          <el-button 
                            type="danger" 
                            icon="Delete" 
                            circle 
                            size="small" 
                            @click="removeQuestion(index)"
                          />
                        </div>
                      </template>
                      
                      <el-form-item label="问题文本">
                        <el-input 
                          v-model="question.text" 
                          placeholder="请输入问题文本"
                        />
                      </el-form-item>
                      
                      <el-form-item label="问题类型">
                        <el-select v-model="question.type" placeholder="请选择问题类型">
                          <el-option label="单选题" :value="1" />
                          <el-option label="多选题" :value="2" />
                          <el-option label="文本题" :value="3" />
                        </el-select>
                      </el-form-item>
                      
                      <el-form-item label="是否必填">
                        <el-switch v-model="question.required" />
                      </el-form-item>
                      
                      <div v-if="question.type !== 3" class="options-section">
                        <h5>选项</h5>
                        <div 
                          v-for="(option, optIndex) in question.options" 
                          :key="optIndex" 
                          class="option-item"
                        >
                          <el-input 
                            v-model="option.text" 
                            placeholder="请输入选项文本"
                          />
                          <el-button 
                            type="danger" 
                            icon="Delete" 
                            circle 
                            size="small" 
                            @click="removeOption(index, optIndex)"
                          />
                        </div>
                        <el-button 
                          type="primary" 
                          icon="Plus" 
                          @click="addOption(index)"
                        >
                          添加选项
                        </el-button>
                        <el-button 
                          type="success" 
                          icon="CirclePlus" 
                          @click="addOtherOption(index)"
                          style="margin-left: 10px;"
                        >
                          添加"其他"选项
                        </el-button>
                      </div>
                    </el-card>
                  </div>
                  
                  <el-button 
                    type="success" 
                    icon="Plus" 
                    @click="addQuestion"
                    style="margin-top: 20px;"
                  >
                    添加问题
                  </el-button>
                </div>
                
                <div class="form-actions">
                  <el-button 
                    type="primary" 
                    @click="saveSurvey"
                    :loading="saving"
                  >
                    保存调查
                  </el-button>
                  <el-button @click="resetForm">重置</el-button>
                </div>
              </el-form>
            </el-card>
          </el-tab-pane>
          
          <el-tab-pane label="管理调查" name="manage">
            <el-card class="manage-survey-card">
              <template #header>
                <div class="manage-survey-header">
                  <h3>管理调查</h3>
                  <el-button 
                    type="primary" 
                    @click="fetchSurveys"
                    icon="Refresh"
                  >
                    刷新
                  </el-button>
                </div>
              </template>
              
              <el-table 
                :data="surveys" 
                style="width: 100%" 
                v-loading="loadingSurveys"
              >
                <el-table-column prop="id" label="ID" width="60" />
                <el-table-column prop="title" label="标题" />
                <el-table-column prop="created_at" label="创建时间" width="180">
                  <template #default="scope">
                    {{ formatDate(scope.row.created_at) }}
                  </template>
                </el-table-column>
                <el-table-column label="状态" width="100">
                  <template #default="scope">
                    <el-tag :type="scope.row.is_published ? 'success' : 'info'">
                      {{ scope.row.is_published ? '已发布' : '未发布' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="250">
                  <template #default="scope">
                    <el-button 
                      size="small" 
                      @click="editSurvey(scope.row)"
                    >
                      编辑
                    </el-button>
                    <el-button 
                      size="small" 
                      type="success" 
                      @click="togglePublish(scope.row)"
                      :loading="scope.row.publishing"
                    >
                      {{ scope.row.is_published ? '取消发布' : '发布' }}
                    </el-button>
                    <el-button 
                      size="small" 
                      type="danger" 
                      @click="deleteSurvey(scope.row)"
                    >
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-tab-pane>
          
          <el-tab-pane label="编辑调查" name="edit">
            <el-card class="edit-survey-card">
              <template #header>
                <div class="edit-survey-header">
                  <h3>编辑调查</h3>
                  <div>
                    <el-button @click="cancelEdit">取消</el-button>
                  </div>
                </div>
              </template>
              
              <el-form 
                ref="editSurveyFormRef" 
                :model="editSurveyForm" 
                label-position="top"
              >
                <el-form-item label="调查标题" prop="title">
                  <el-input 
                    v-model="editSurveyForm.title" 
                    placeholder="请输入调查标题"
                  />
                </el-form-item>
                
                <el-form-item label="调查描述" prop="description">
                  <el-input 
                    v-model="editSurveyForm.description" 
                    type="textarea"
                    placeholder="请输入调查描述（可选）"
                    :rows="3"
                  />
                </el-form-item>
                
                <div class="questions-section">
                  <h4>问题列表</h4>
                  
                  <div 
                    v-for="(question, index) in editSurveyForm.questions" 
                    :key="question.id || 'new-' + index" 
                    class="question-item"
                  >
                    <el-card class="question-card">
                      <template #header>
                        <div class="question-header">
                          <span>问题 {{ index + 1 }}</span>
                          <el-button 
                            type="danger" 
                            icon="Delete" 
                            circle 
                            size="small" 
                            @click="removeEditQuestion(index)"
                          />
                        </div>
                      </template>
                      
                      <el-form-item label="问题文本">
                        <el-input 
                          v-model="question.text" 
                          placeholder="请输入问题文本"
                        />
                      </el-form-item>
                      
                      <el-form-item label="问题类型">
                        <el-select v-model="question.type" placeholder="请选择问题类型">
                          <el-option label="单选题" :value="1" />
                          <el-option label="多选题" :value="2" />
                          <el-option label="文本题" :value="3" />
                        </el-select>
                      </el-form-item>
                      
                      <el-form-item label="是否必填">
                        <el-switch v-model="question.required" />
                      </el-form-item>
                      
                      <div v-if="question.type !== 3" class="options-section">
                        <h5>选项</h5>
                        <div 
                          v-for="(option, optIndex) in question.options" 
                          :key="option.id || 'new-opt-' + optIndex" 
                          class="option-item"
                        >
                          <el-input 
                            v-model="option.text" 
                            placeholder="请输入选项文本"
                          />
                          <el-button 
                            type="danger" 
                            icon="Delete" 
                            circle 
                            size="small" 
                            @click="removeEditOption(index, optIndex)"
                          />
                        </div>
                        <el-button 
                          type="primary" 
                          icon="Plus" 
                          @click="addEditOption(index)"
                        >
                          添加选项
                        </el-button>
                        <el-button 
                          type="success" 
                          icon="CirclePlus" 
                          @click="addEditOtherOption(index)"
                          style="margin-left: 10px;"
                        >
                          添加"其他"选项
                        </el-button>
                      </div>
                    </el-card>
                  </div>
                  
                  <el-button 
                    type="success" 
                    icon="Plus" 
                    @click="addEditQuestion"
                    style="margin-top: 20px;"
                  >
                    添加问题
                  </el-button>
                </div>
                
                <div class="form-actions">
                  <el-button 
                    type="primary" 
                    @click="updateSurvey"
                    :loading="updating"
                  >
                    更新调查
                  </el-button>
                  <el-button @click="cancelEdit">取消</el-button>
                </div>
              </el-form>
            </el-card>
          </el-tab-pane>
          
          <el-tab-pane label="查看调查内容" name="view-responses">
            <el-card class="view-responses-card">
              <template #header>
                <div class="view-responses-header">
                  <h3>查看调查响应</h3>
                  <el-button 
                    type="primary" 
                    @click="fetchSurveysForResponseView"
                    icon="Refresh"
                  >
                    刷新
                  </el-button>
                </div>
              </template>
              
              <el-row :gutter="20">
                <el-col :span="8">
                  <el-card class="survey-list-card">
                    <template #header>
                      <h4>调查列表</h4>
                    </template>
                    <el-menu
                      :default-active="selectedSurveyId.toString()"
                      @select="handleSurveySelect"
                      style="border-right: none;"
                    >
                      <el-menu-item 
                        v-for="survey in surveysForResponseView" 
                        :key="survey.id" 
                        :index="survey.id.toString()"
                      >
                        <span>{{ survey.title }}</span>
                        <el-tag 
                          size="small" 
                          style="margin-left: 10px;"
                        >
                          {{ survey.response_count }} 条响应
                        </el-tag>
                      </el-menu-item>
                    </el-menu>
                  </el-card>
                </el-col>
                
                <el-col :span="16">
                  <el-card class="responses-detail-card" v-if="selectedSurveyId">
                    <template #header>
                      <div class="responses-detail-header">
                        <h4>{{ selectedSurvey.title }} - 响应详情</h4>
                        <el-button 
                          @click="fetchSurveyResponses"
                          icon="Refresh"
                        >
                          刷新
                        </el-button>
                      </div>
                    </template>
                    
                    <div v-if="loadingResponses" class="loading-responses">
                      <p>加载响应数据中...</p>
                    </div>
                    
                    <div v-else-if="surveyResponses.length === 0" class="no-responses">
                      <el-empty description="暂无响应数据" />
                    </div>
                    
                    <div v-else>
                      <el-collapse v-model="activeResponsePanel">
                        <el-collapse-item 
                          v-for="(response, index) in surveyResponses" 
                          :key="response.id" 
                          :name="response.id"
                        >
                          <template #title>
                            <div class="response-header">
                              <span>响应 #{{ response.id }}</span>
                              <span class="response-time">{{ formatDate(response.created_at) }}</span>
                            </div>
                          </template>
                          
                          <div class="response-content">
                            <el-descriptions 
                              :column="1" 
                              border
                            >
                              <el-descriptions-item 
                                v-for="questionResponse in response.question_responses" 
                                :key="questionResponse.question_id"
                                :label="questionResponse.question_text"
                              >
                                <div v-if="questionResponse.question_type === 3">
                                  {{ questionResponse.response || '无回答' }}
                                </div>
                                <div v-else>
                                  {{ questionResponse.response || '未选择' }}
                                </div>
                              </el-descriptions-item>
                            </el-descriptions>
                          </div>
                        </el-collapse-item>
                      </el-collapse>
                    </div>
                  </el-card>
                  
                  <el-card class="responses-detail-card" v-else>
                    <el-empty description="请选择一个调查查看响应" />
                  </el-card>
                </el-col>
              </el-row>
            </el-card>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { onMounted, ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import type { FormInstance } from 'element-plus'

interface Option {
  id?: number
  text: string
}

interface Question {
  id?: number
  text: string
  type: number // 1: 单选, 2: 多选, 3: 文本
  required: boolean
  options: Option[]
}

interface SurveyForm {
  title: string
  description: string
  questions: Question[]
}

interface Survey {
  id: number
  title: string
  description: string
  is_published: boolean
  created_at: string
  updated_at: string
  questions: Question[]
  publishing?: boolean
  response_count?: number
}

interface QuestionResponse {
  question_id: number
  question_text: string
  question_type: number
  response: string
  option_id?: number
}

interface SurveyResponse {
  id: number
  survey_id: number
  created_at: string
  question_responses: QuestionResponse[]
}

const userStore = useUserStore()
const router = useRouter()
const surveyFormRef = ref<FormInstance>()
const editSurveyFormRef = ref<FormInstance>()
const activeTab = ref('dashboard')
const saving = ref(false)
const updating = ref(false)
const loadingSurveys = ref(false)
const loadingResponses = ref(false)
const surveys = ref<Survey[]>([])
const publishedSurveys = ref<Survey[]>([])
const surveysForResponseView = ref<Survey[]>([])
const selectedSurveyId = ref<number>(0)
const selectedSurvey = ref<Survey>({
  id: 0,
  title: '',
  description: '',
  is_published: false,
  created_at: '',
  updated_at: '',
  questions: []
})
const surveyResponses = ref<SurveyResponse[]>([])
const activeResponsePanel = ref<number[]>([])
const totalResponseCount = ref<number>(0)

const surveyForm = reactive<SurveyForm>({
  title: '',
  description: '',
  questions: []
})

const editSurveyForm = reactive<SurveyForm>({
  title: '',
  description: '',
  questions: []
})

const totalResponses = computed(() => {
  return totalResponseCount.value
})

let currentEditSurveyId = 0

onMounted(() => {
  // 检查用户是否为管理员
  if (!userStore.isAuthenticated) {
    ElMessage.error('请先登录')
    router.push('/login')
  } else if (!userStore.isAdmin) {
    ElMessage.error('您没有权限访问此页面')
    router.push('/')
  } else {
    // 如果是管理员，加载仪表板数据
    fetchDashboardData()
  }
})

const fetchDashboardData = async () => {
  try {
    // 获取统计信息
    const statsResponse = await axios.get('http://localhost:5000/api/survey-stats')
    // 获取详细的调查列表
    const surveysResponse = await axios.get('http://localhost:5000/api/surveys')
    
    // 更新数据
    surveys.value = surveysResponse.data
    publishedSurveys.value = surveys.value.filter(survey => survey.is_published)
    surveysForResponseView.value = surveysResponse.data
    
    // 更新总响应数
    totalResponseCount.value = statsResponse.data.total_responses
    
    // 为了触发响应式更新，我们需要创建一个新的数组引用
    surveysForResponseView.value = [...surveysResponse.data]
  } catch (error) {
    console.error('获取仪表板数据失败:', error)
    ElMessage.error('获取仪表板数据失败，请重试')
  }
}

const addQuestion = () => {
  surveyForm.questions.push({
    text: '',
    type: 1, // 默认为单选题
    required: false,
    options: [{ text: '' }, { text: '' }] // 默认添加两个选项
  })
}

const removeQuestion = (index: number) => {
  surveyForm.questions.splice(index, 1)
}

const addOption = (questionIndex: number) => {
  surveyForm.questions[questionIndex].options.push({ text: '' })
}

const addOtherOption = (questionIndex: number) => {
  surveyForm.questions[questionIndex].options.push({ text: '其他' })
}

const removeOption = (questionIndex: number, optionIndex: number) => {
  surveyForm.questions[questionIndex].options.splice(optionIndex, 1)
}

const resetForm = () => {
  surveyForm.title = ''
  surveyForm.description = ''
  surveyForm.questions = []
}

const saveSurvey = async () => {
  if (!surveyForm.title) {
    ElMessage.error('请输入调查标题')
    return
  }
  
  // 检查每个问题是否填写完整
  for (let i = 0; i < surveyForm.questions.length; i++) {
    const question = surveyForm.questions[i]
    if (!question.text) {
      ElMessage.error(`请填写第 ${i + 1} 个问题的文本`)
      return
    }
    
    // 对于选择题，检查选项是否填写完整
    if (question.type !== 3) {
      if (question.options.length < 2) {
        ElMessage.error(`第 ${i + 1} 个问题至少需要两个选项`)
        return
      }
      
      for (let j = 0; j < question.options.length; j++) {
        if (!question.options[j].text) {
          ElMessage.error(`第 ${i + 1} 个问题的第 ${j + 1} 个选项不能为空`)
          return
        }
      }
    }
  }
  
  try {
    saving.value = true
    
    // 准备发送到后端的数据
    const surveyData = {
      title: surveyForm.title,
      description: surveyForm.description,
      questions: surveyForm.questions.map((question, index) => ({
        text: question.text,
        type: question.type,
        required: question.required,
        options: question.type !== 3 ? question.options.map(opt => opt.text) : []
      }))
    }
    
    // 发送到后端API
    const response = await axios.post('http://localhost:5000/api/surveys', surveyData)
    
    ElMessage.success('调查创建成功')
    resetForm()
    activeTab.value = 'dashboard'
  } catch (error) {
    console.error('保存调查失败:', error)
    ElMessage.error('保存调查失败，请重试')
  } finally {
    saving.value = false
  }
}

// 调查管理功能
const fetchSurveys = async () => {
  try {
    loadingSurveys.value = true
    const response = await axios.get('http://localhost:5000/api/surveys')
    surveys.value = response.data
    publishedSurveys.value = surveys.value.filter(survey => survey.is_published)
    // 更新用于响应视图的调查列表
    surveysForResponseView.value = response.data
    
    // 更新总响应数
    const statsResponse = await axios.get('http://localhost:5000/api/survey-stats')
    totalResponseCount.value = statsResponse.data.total_responses
  } catch (error) {
    console.error('获取调查列表失败:', error)
    ElMessage.error('获取调查列表失败，请重试')
  } finally {
    loadingSurveys.value = false
  }
}

const fetchSurveysForResponseView = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/surveys')
    surveysForResponseView.value = response.data
    
    // 如果有调查，选择第一个作为默认选中
    if (surveysForResponseView.value.length > 0 && !selectedSurveyId.value) {
      handleSurveySelect(surveysForResponseView.value[0].id.toString())
    }
  } catch (error) {
    console.error('获取调查列表失败:', error)
    ElMessage.error('获取调查列表失败，请重试')
  }
}

const handleSurveySelect = async (surveyId: string) => {
  selectedSurveyId.value = parseInt(surveyId)
  const survey = surveysForResponseView.value.find(s => s.id === selectedSurveyId.value)
  if (survey) {
    selectedSurvey.value = survey
    await fetchSurveyResponses()
  }
}

const fetchSurveyResponses = async () => {
  if (!selectedSurveyId.value) return
  
  try {
    loadingResponses.value = true
    const response = await axios.get(`http://localhost:5000/api/survey-responses/${selectedSurveyId.value}`)
    surveyResponses.value = response.data
    
    // 默认展开所有响应面板
    activeResponsePanel.value = response.data.map((r: SurveyResponse) => r.id)
  } catch (error) {
    console.error('获取调查响应失败:', error)
    ElMessage.error('获取调查响应失败，请重试')
  } finally {
    loadingResponses.value = false
  }
}

const editSurvey = async (survey: Survey) => {
  try {
    // 获取调查的详细信息
    const response = await axios.get(`http://localhost:5000/api/surveys/${survey.id}`)
    const surveyDetail = response.data
    
    // 填充编辑表单
    editSurveyForm.title = surveyDetail.title
    editSurveyForm.description = surveyDetail.description
    editSurveyForm.questions = surveyDetail.questions.map((q: any) => ({
      id: q.id,
      text: q.text,
      type: q.type,
      required: q.required,
      options: q.options.map((opt: any) => ({
        id: opt.id,
        text: opt.text
      }))
    }))
    
    currentEditSurveyId = surveyDetail.id
    activeTab.value = 'edit'
  } catch (error) {
    console.error('获取调查详情失败:', error)
    ElMessage.error('获取调查详情失败，请重试')
  }
}

const cancelEdit = () => {
  activeTab.value = 'manage'
  editSurveyForm.title = ''
  editSurveyForm.description = ''
  editSurveyForm.questions = []
  currentEditSurveyId = 0
}

const addEditQuestion = () => {
  editSurveyForm.questions.push({
    text: '',
    type: 1, // 默认为单选题
    required: false,
    options: [{ text: '' }, { text: '' }] // 默认添加两个选项
  })
}

const removeEditQuestion = (index: number) => {
  editSurveyForm.questions.splice(index, 1)
}

const addEditOption = (questionIndex: number) => {
  editSurveyForm.questions[questionIndex].options.push({ text: '' })
}

const addEditOtherOption = (questionIndex: number) => {
  editSurveyForm.questions[questionIndex].options.push({ text: '其他' })
}

const removeEditOption = (questionIndex: number, optionIndex: number) => {
  editSurveyForm.questions[questionIndex].options.splice(optionIndex, 1)
}

const updateSurvey = async () => {
  if (!editSurveyForm.title) {
    ElMessage.error('请输入调查标题')
    return
  }
  
  // 检查每个问题是否填写完整
  for (let i = 0; i < editSurveyForm.questions.length; i++) {
    const question = editSurveyForm.questions[i]
    if (!question.text) {
      ElMessage.error(`请填写第 ${i + 1} 个问题的文本`)
      return
    }
    
    // 对于选择题，检查选项是否填写完整
    if (question.type !== 3) {
      if (question.options.length < 2) {
        ElMessage.error(`第 ${i + 1} 个问题至少需要两个选项`)
        return
      }
      
      for (let j = 0; j < question.options.length; j++) {
        if (!question.options[j].text) {
          ElMessage.error(`第 ${i + 1} 个问题的第 ${j + 1} 个选项不能为空`)
          return
        }
      }
    }
  }
  
  try {
    updating.value = true
    
    // 准备发送到后端的数据
    const surveyData = {
      title: editSurveyForm.title,
      description: editSurveyForm.description,
      questions: editSurveyForm.questions.map((question) => ({
        text: question.text,
        type: question.type,
        required: question.required,
        options: question.type !== 3 ? question.options.map(opt => opt.text) : []
      }))
    }
    
    // 发送到后端API
    const response = await axios.put(`http://localhost:5000/api/surveys/${currentEditSurveyId}`, surveyData)
    
    ElMessage.success('调查更新成功')
    
    // 更新本地survey列表
    const index = surveys.value.findIndex(s => s.id === currentEditSurveyId)
    if (index !== -1) {
      surveys.value[index] = {
        ...surveys.value[index],
        ...response.data
      }
    }
    
    // 更新已发布调查列表
    const pubIndex = publishedSurveys.value.findIndex(s => s.id === currentEditSurveyId)
    if (pubIndex !== -1 && response.data.is_published) {
      publishedSurveys.value[pubIndex] = {
        ...publishedSurveys.value[pubIndex],
        ...response.data
      }
    } else if (pubIndex !== -1 && !response.data.is_published) {
      // 如果调查被取消发布，从已发布列表中移除
      publishedSurveys.value.splice(pubIndex, 1)
    }
    
    cancelEdit()
  } catch (error) {
    console.error('更新调查失败:', error)
    ElMessage.error('更新调查失败，请重试')
  } finally {
    updating.value = false
  }
}

const deleteSurvey = async (survey: Survey) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除调查 "${survey.title}" 吗？此操作不可撤销。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    await axios.delete(`http://localhost:5000/api/surveys/${survey.id}`)
    ElMessage.success('调查删除成功')
    fetchSurveys() // 刷新列表
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除调查失败:', error)
      ElMessage.error('删除调查失败，请重试')
    }
  }
}

const togglePublish = async (survey: Survey) => {
  try {
    survey.publishing = true
    const endpoint = survey.is_published 
      ? `http://localhost:5000/api/surveys/${survey.id}/unpublish`
      : `http://localhost:5000/api/surveys/${survey.id}/publish`
    
    const response = await axios.post(endpoint)
    ElMessage.success(response.data.message)
    
    // 更新本地状态
    survey.is_published = !survey.is_published
    survey.updated_at = response.data.survey.updated_at
    
    // 更新已发布调查列表
    if (survey.is_published) {
      publishedSurveys.value.push({...survey})
    } else {
      const index = publishedSurveys.value.findIndex(s => s.id === survey.id)
      if (index !== -1) {
        publishedSurveys.value.splice(index, 1)
      }
    }
  } catch (error) {
    console.error('发布/取消发布调查失败:', error)
    ElMessage.error('操作失败，请重试')
  } finally {
    survey.publishing = false
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN') + ' ' + date.toLocaleTimeString('zh-CN')
}
</script>

<style scoped>
.admin-page {
  padding: 20px;
}

.admin-card {
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.card-header h2 {
  margin: 0;
  color: #333;
  font-weight: 600;
  text-align: center;
}

.stat-card {
  text-align: center;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.stat-content h3 {
  margin: 0 0 10px 0;
  color: #495057;
  font-size: 1rem;
  font-weight: 500;
}

.stat-number {
  margin: 0;
  font-size: 2rem;
  font-weight: 700;
  color: #007bff;
}

.admin-actions {
  margin-top: 30px;
}

.admin-actions h3 {
  margin-bottom: 20px;
  color: #333;
  font-weight: 600;
}

.action-card {
  border-radius: 8px;
  border: 1px solid #e9ecef;
  height: 100%;
}

.action-content h4 {
  margin: 0 0 10px 0;
  color: #495057;
  font-weight: 600;
}

.action-content p {
  margin: 0 0 15px 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.create-survey-card, .manage-survey-card, .edit-survey-card, .view-responses-card {
  border-radius: 8px;
}

.create-survey-header, .manage-survey-header, .edit-survey-header, .view-responses-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.create-survey-header h3, .manage-survey-header h3, .edit-survey-header h3, .view-responses-header h3 {
  margin: 0;
  color: #333;
  font-weight: 600;
}

.questions-section h4 {
  margin: 20px 0 15px 0;
  color: #495057;
  font-weight: 600;
}

.question-item {
  margin-bottom: 20px;
}

.question-card {
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.options-section h5 {
  margin: 15px 0 10px 0;
  color: #495057;
  font-weight: 500;
}

.option-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}

.option-item .el-input {
  flex: 1;
}

.form-actions {
  margin-top: 30px;
  display: flex;
  gap: 15px;
  justify-content: center;
}

/* View Responses Styles */
.survey-list-card {
  height: calc(100vh - 200px);
  overflow-y: auto;
}

.survey-list-card .el-menu {
  border-right: none;
}

.survey-list-card .el-menu-item {
  height: auto;
  line-height: 1.5;
  padding: 10px 15px;
}

.responses-detail-card {
  height: calc(100vh - 200px);
  overflow-y: auto;
}

.responses-detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.response-header {
  display: flex;
  justify-content: space-between;
  width: 100%;
}

.response-time {
  color: #999;
  font-size: 0.9rem;
}

.response-content {
  padding: 10px 0;
}

.loading-responses, .no-responses {
  text-align: center;
  padding: 40px 0;
  color: #666;
}
</style>