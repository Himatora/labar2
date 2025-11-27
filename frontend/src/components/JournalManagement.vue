<template>
  <div class="card">
    <div class="card-body">
      <h2>Журнал успеваемости</h2>
      <div class="controls mb-3">
        <button @click="generateJournal" class="btn btn-primary">Сформировать журнал</button>
      </div>
      <div v-if="selectedStudent" class="student-info mb-3 p-3">
        <h3>{{ selectedStudent.full_name }}</h3>
        <p>Класс: {{ selectedStudent.grade }}</p>
        <p>Цель: {{ selectedStudent.learning_goal.name }}</p>
        <p>Категория: {{ selectedStudent.learning_category.name }}</p>
        <p>Преподаватель: {{ selectedStudent.teacher.full_name }}</p>
        <div class="journal-form p-3" v-if="showJournalForm">
          <div class="form-group mb-3">
            <label>Количество уроков для анализа:</label>
            <select v-model="lessonsCount" class="form-select">
              <option value="3">3</option>
              <option value="5">5</option>
              <option value="10">10</option>
            </select>
          </div>
          <button @click="createJournalEntry" class="btn btn-primary">Создать запись в журнале</button>
        </div>
      </div>
      <div v-if="error" class="alert alert-danger mb-3">
        {{ error }}
      </div>
      <div v-if="latestJournalEntry" class="journal-entry mb-3 p-3">
        <h3>Запись от {{ formatDate(latestJournalEntry.created_at) }}</h3>
        <div class="section">
          <h4>Результаты:</h4>
          <p>{{ latestJournalEntry.good_results }}</p>
        </div>
        <div class="section">
          <h4>Пройденные темы:</h4>
          <p>{{ latestJournalEntry.covered_topics }}</p>
        </div>
        <div class="section">
          <h4>Работаем над:</h4>
          <p>{{ latestJournalEntry.working_on }}</p>
        </div>
        <div class="section">
          <h4>Рекомендуемый объем занятий:</h4>
          <p>{{ latestJournalEntry.recommendation_reason }}</p>
        </div>
      </div>
      <div v-else-if="!error" class="text-muted">
        Записи в журнале отсутствуют.
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

// Use relative paths - nginx will proxy /api/ to backend over HTTPS
axios.defaults.baseURL = '';

export default {
  name: 'JournalManagement',
  props: {
    studentId: {
      type: Number,
      required: true,
    },
  },
  setup(props) {
    const journalEntries = ref([]);
    const students = ref([]);
    const selectedStudent = ref(null);
    const showJournalForm = ref(false);
    const lessonsCount = ref(5);
    const error = ref(null);

    const fetchJournalEntries = async () => {
      try {
        const response = await axios.get(`/api/journal/?student=${props.studentId}`);
        journalEntries.value = response.data;
      } catch (err) {
        console.error('Ошибка при загрузке журнала:', err.response?.data || err.message);
        error.value = 'Не удалось загрузить записи журнала.';
      }
    };

    const fetchStudents = async () => {
      try {
        const response = await axios.get(`/api/students/${props.studentId}/`);
        students.value = [response.data];
        selectedStudent.value = response.data;
      } catch (err) {
        console.error('Ошибка при загрузке учеников:', err.response?.data || err.message);
        error.value = 'Не удалось загрузить данные ученика.';
      }
    };

    const generateJournal = () => {
      showJournalForm.value = true;
      error.value = null;
    };

    const createJournalEntry = async () => {
      try {
        const data = {
          student_id: Number(props.studentId),
          lessons_count: Number(lessonsCount.value),
        };
        console.log('Отправляемые данные для журнала:', data);
        const response = await axios.post('/api/journal/generate/', data, {
          headers: { 'Content-Type': 'application/json' },
        });
        console.log('Ответ от сервера:', response.data);
        await fetchJournalEntries();
        showJournalForm.value = false;
        error.value = null;
      } catch (err) {
        console.error('Ошибка при создании записи в журнале:', err.response?.data || err);
        error.value = 'Не удалось создать запись в журнале: ' + (err.response?.data?.detail || err.message);
      }
    };

    const formatDate = (dateString) => {
      const date = new Date(dateString);
      return date.toLocaleDateString('ru-RU');
    };

    const latestJournalEntry = computed(() => {
      if (journalEntries.value.length === 0) return null;
      return journalEntries.value.reduce((latest, entry) =>
        new Date(entry.created_at) > new Date(latest.created_at) ? entry : latest
      );
    });

    onMounted(() => {
      fetchJournalEntries();
      fetchStudents();
    });

    return {
      journalEntries,
      students,
      selectedStudent,
      showJournalForm,
      lessonsCount,
      error,
      generateJournal,
      createJournalEntry,
      formatDate,
      latestJournalEntry,
    };
  },
};
</script>

<style scoped>
.controls {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}
.form-group {
  margin-bottom: 15px;
}
.form-group label {
  display: block;
  margin-bottom: 5px;
}
.section {
  margin-bottom: 15px;
}
.section h4 {
  margin-bottom: 5px;
  color: #444;
}
</style>