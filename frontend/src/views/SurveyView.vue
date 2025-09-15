<template>
  <div class="survey-container">
    <h1>Survey</h1>
    <div v-if="loading">Loading questions...</div>
    <div v-else-if="error">{{ error }}</div>
    <form v-else @submit.prevent="submitSurvey">
      <div v-for="question in questions" :key="question.id" class="question">
        <h3>{{ question.text }}</h3>
        <div v-if="question.type === 1" class="options">
          <!-- Single choice -->
          <div v-for="option in question.options" :key="option.id" class="option radio-option">
            <input 
              type="radio" 
              :id="'q' + question.id + '-o' + option.id" 
              :name="'question-' + question.id" 
              :value="option.id" 
              v-model="responses[question.id]"
              :required="question.required"
            >
            <label :for="'q' + question.id + '-o' + option.id">{{ option.text }}</label>
          </div>
        </div>
        <div v-else-if="question.type === 2" class="options">
          <!-- Multiple choice -->
          <div v-for="option in question.options" :key="option.id" class="option checkbox-option">
            <input 
              type="checkbox" 
              :id="'q' + question.id + '-o' + option.id" 
              :name="'question-' + question.id + '-o' + option.id" 
              :value="option.id" 
              v-model="selectedOptions[question.id]"
            >
            <label :for="'q' + question.id + '-o' + option.id">{{ option.text }}</label>
          </div>
        </div>
        <div v-else-if="question.type === 3" class="text-answer">
          <!-- Text answer -->
          <textarea 
            :id="'q' + question.id" 
            :name="'question-' + question.id" 
            v-model="responses[question.id]" 
            :required="question.required"
            placeholder="Please enter your answer here..."
          ></textarea>
        </div>
      </div>
      <button type="submit" class="submit-btn">Submit Survey</button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

interface Option {
  id: number
  question_id: number
  text: string
  order: number
}

interface Question {
  id: number
  text: string
  type: number
  required: boolean
  options?: Option[]
}

const questions = ref<Question[]>([])
const responses = ref<Record<string, any>>({})
const selectedOptions = ref<Record<number, number[]>>({})
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/questions')
    questions.value = response.data
    loading.value = false
    
    // Initialize selectedOptions for multi-choice questions
    questions.value.forEach(question => {
      if (question.type === 2) {
        selectedOptions.value[question.id] = []
      }
    })
  } catch (err) {
    error.value = 'Failed to load questions'
    loading.value = false
    console.error(err)
  }
})

const submitSurvey = async () => {
  try {
    // Prepare data to send
    const surveyData = {
      responses: responses.value,
      selectedOptions: selectedOptions.value
    }
    
    const response = await axios.post('http://localhost:5000/api/submit', surveyData)
    alert(`Survey submitted successfully! Response ID: ${response.data.survey_response_id}`)
    // Reset form or redirect
  } catch (err) {
    alert('Failed to submit survey')
    console.error(err)
  }
}
</script>

<style scoped>
.survey-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Arial', sans-serif;
}

.survey-container h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

.question {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.question h3 {
  margin-top: 0;
  color: #444;
  font-size: 18px;
}

.options {
  margin-top: 15px;
}

.option {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}

.radio-option input[type="radio"] {
  margin-right: 10px;
  transform: scale(1.2);
}

.checkbox-option input[type="checkbox"] {
  margin-right: 10px;
  transform: scale(1.2);
}

.option label {
  font-size: 16px;
  color: #555;
  cursor: pointer;
}

.text-answer textarea {
  width: 100%;
  min-height: 100px;
  margin-top: 10px;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-sizing: border-box;
  resize: vertical;
}

.text-answer textarea:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 5px rgba(74, 144, 226, 0.3);
}

.submit-btn {
  display: block;
  width: 200px;
  margin: 30px auto;
  padding: 12px 20px;
  font-size: 18px;
  color: white;
  background-color: #4a90e2;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-btn:hover {
  background-color: #357ae8;
}

.submit-btn:active {
  transform: translateY(1px);
}

/* Responsive design */
@media (max-width: 768px) {
  .survey-container {
    padding: 10px;
  }
  
  .question {
    padding: 15px;
  }
  
  .option label {
    font-size: 14px;
  }
}
</style>