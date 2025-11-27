<template>
  <div class="card mb-4">
    <div class="card-body">
      <h2>Список уроков</h2>
      <nav class="navbar navbar-expand-lg navbar-dark mb-4">
        <div class="container-fluid">
          <router-link :to="`/${categorySlug}`" class="navbar-brand">Назад</router-link>
          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse" id="navbarNav">
            <div class="navbar-nav">
              <a class="nav-link active" href="#">Просмотреть уроки</a>
              <router-link :to="`/${categorySlug}/${$route.params.studentId}`" class="nav-link">Уроки и журнал</router-link>
            </div>
          </div>
        </div>
      </nav>
      <div class="filters mb-3 d-flex gap-3">
        <select v-model="typeFilter" class="form-select w-auto">
          <option value="">Все виды</option>
          <option v-for="type in lessonTypes" :value="type.id">{{ type.name }}</option>
        </select>
        <input v-model="dateFilter" type="date" class="form-control w-auto" />
        <button @click="resetFilters" class="btn btn-outline-secondary">Сбросить</button>
        <button @click="generateHomework" class="btn btn-success">Сгенерировать ДЗ</button>
      </div>
      <div v-if="isLoading" class="text-center my-4">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Загрузка...</span>
        </div>
      </div>
      <div v-else-if="error" class="alert alert-danger">
        {{ error }}
      </div>
      <div v-else>
        <div v-for="lesson in filteredLessons" :key="lesson.id" class="lesson-card mb-3 p-3 border rounded">
          <p><strong>Тип:</strong> {{ lesson.lesson_type.name }}</p>
          <p><strong>Тема:</strong> {{ lesson.topic.name }}</p>
          <p><strong>Дата:</strong> {{ formatDate(lesson.date) }}</p>
          <p><strong>Комментарий:</strong> {{ lesson.comment || 'нет' }}</p>
          <button @click="addHomework(lesson)" class="btn btn-primary">Добавить ДЗ</button>
        </div>
        <div v-if="filteredLessons.length === 0" class="text-center text-muted py-3">
          Уроки не найдены. Попробуйте изменить фильтры.
        </div>
      </div>

      <!-- Модальное окно для добавления ДЗ -->
      <div v-if="showAddHomeworkModal" class="modal fade show d-block" tabindex="-1">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h3 class="modal-title">Добавить домашнее задание</h3>
              <button type="button" class="btn-close" @click="closeModal"></button>
            </div>
            <div class="modal-body">
              <div class="form-group mb-3">
                <label>Тема:</label>
                <select v-model="selectedTopic" class="form-select" @change="addTopicResult" :disabled="topics.length === 0">
                  <option value="">Выберите тему</option>
                  <option v-for="topic in topics" :value="topic.id">{{ topic.name }}</option>
                </select>
                <small v-if="topics.length === 0" class="text-muted">Нет доступных тем для этого ученика.</small>
                <button @click="addTopicResult" class="btn btn-primary mt-2" :disabled="!selectedTopic">Добавить тему</button>
              </div>
              <div v-for="(result, index) in newHomework.results" :key="index" class="form-group mb-3 p-3 border rounded">
                <h4>{{ getTopicName(result.topic_id) }}</h4>
                <div v-for="difficulty in ['EASY', 'MEDIUM', 'HARD']" :key="difficulty" class="form-check">
                  <input type="checkbox" v-model="result.difficulties[difficulty].enabled" class="form-check-input">
                  <label class="form-check-label">{{ difficulty === 'EASY' ? 'Легкий' : difficulty === 'MEDIUM' ? 'Средний' : 'Сложный' }}</label>
                  <div v-if="result.difficulties[difficulty].enabled" class="ms-3">
                    <label>Верных:</label>
                    <input v-model.number="result.difficulties[difficulty].correct_count" type="number" min="0" class="form-control w-25 d-inline-block" @input="calculatePercentage(index, difficulty)">
                    <label class="ms-2">Всего:</label>
                    <input v-model.number="result.difficulties[difficulty].total_count" type="number" min="0" class="form-control w-25 d-inline-block" @input="calculatePercentage(index, difficulty)">
                    <span class="ms-2">Процент: {{ result.difficulties[difficulty].percentage.toFixed(2) }}%</span>
                  </div>
                </div>
              </div>
              <div class="form-group mb-3">
                <label>Состояние:</label>
                <select v-model="newHomework.status" class="form-select">
                  <option value="ASSIGNED">Задано</option>
                  <option value="NOT_ASSIGNED">Не задано</option>
                </select>
              </div>
            </div>
            <div class="modal-footer">
              <button @click="saveHomework" class="btn btn-primary">Сохранить ДЗ</button>
              <button @click="closeModal" class="btn btn-outline-secondary">Отмена</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Модальное окно для сгенерированного ДЗ -->
      <div v-if="showGeneratedHomeworkModal" class="modal fade show d-block" tabindex="-1">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h3 class="modal-title">Сгенерированное домашнее задание</h3>
              <button type="button" class="btn-close" @click="closeGeneratedModal"></button>
            </div>
            <div class="modal-body">
              <div v-if="sortedTopics.length" class="mt-3">
                <div class="mb-3">
                  <label class="me-2">Сортировать по проценту:</label>
                  <select v-model="sortOrder" class="form-select w-auto d-inline">
                    <option value="asc">По возрастанию</option>
                    <option value="desc">По убыванию</option>
                  </select>
                </div>
                <p>Рекомендуемые темы для домашнего задания:</p>
                <table class="table table-striped">
                  <thead>
                    <tr>
                      <th>Тема</th>
                      <th>Уровень сложности</th>
                      <th>Процент выполнения</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="item in sortedTopics" :key="`${item.topic.id}-${item.difficulty}`">
                      <td>{{ item.topic.name }}</td>
                      <td>{{ item.difficulty === 'EASY' ? 'Легкий' : item.difficulty === 'MEDIUM' ? 'Средний' : 'Сложный' }}</td>
                      <td>{{ item.percentage.toFixed(2) }}%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-else>
                <p>Нет тем, требующих доработки.</p>
              </div>
            </div>
            <div class="modal-footer">
              <button @click="closeGeneratedModal" class="btn btn-outline-secondary">Закрыть</button>
            </div>
          </div>
        </div>
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
  name: 'LessonList',
  props: {
    studentId: {
      type: Number,
      required: true,
    },
    categorySlug: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const lessons = ref([]);
    const lessonTypes = ref([]);
    const topics = ref([]);
    const typeFilter = ref('');
    const dateFilter = ref('');
    const showAddHomeworkModal = ref(false);
    const selectedLesson = ref(null);
    const selectedTopic = ref('');
    const newHomework = ref({
      lesson: null,
      topics: [],
      status: 'ASSIGNED',
      results: [],
    });
    const isLoading = ref(true);
    const error = ref(null);
    const showGeneratedHomeworkModal = ref(false);
    const generatedTopics = ref([]);
    const sortOrder = ref('asc');

    const fetchLessons = async () => {
      try {
        const response = await axios.get(`/api/lessons/?student=${props.studentId}`);
        lessons.value = response.data;
        if (lessons.value.length === 0) {
          error.value = 'Уроки не найдены для этого ученика.';
        }
      } catch (err) {
        console.error('Error fetching lessons:', err.response?.data || err.message);
        error.value = 'Не удалось загрузить уроки: ' + (err.response?.data?.detail || err.message);
      } finally {
        isLoading.value = false;
      }
    };

    const fetchLessonTypes = async () => {
      try {
        const response = await axios.get('/api/lesson-types/');
        lessonTypes.value = response.data;
      } catch (err) {
        console.error('Ошибка при загрузке видов уроков:', err.response?.data || err.message);
      }
    };

    const fetchTopics = async () => {
      try {
        const response = await axios.get('/api/topics/', {
          params: { students: props.studentId },
        });
        topics.value = response.data;
      } catch (err) {
        console.error('Ошибка при загрузке тем:', err.response?.data || err.message);
        topics.value = [];
      }
    };

    const addHomework = (lesson) => {
      selectedLesson.value = lesson;
      newHomework.value = {
        lesson: lesson.id,
        topics: [],
        status: 'ASSIGNED',
        results: [],
      };
      selectedTopic.value = '';
      showAddHomeworkModal.value = true;
    };

    const addTopicResult = () => {
      if (selectedTopic.value && !newHomework.value.topics.includes(selectedTopic.value)) {
        newHomework.value.topics.push(selectedTopic.value);
        newHomework.value.results.push({
          topic_id: selectedTopic.value,
          difficulties: {
            EASY: { enabled: false, correct_count: 0, total_count: 0, percentage: 0 },
            MEDIUM: { enabled: true, correct_count: 0, total_count: 0, percentage: 0 },
            HARD: { enabled: false, correct_count: 0, total_count: 0, percentage: 0 },
          },
        });
        selectedTopic.value = '';
      }
    };

    const calculatePercentage = (index, difficulty) => {
      const result = newHomework.value.results[index];
      const diff = result.difficulties[difficulty];
      if (diff.total_count > 0) {
        diff.percentage = (diff.correct_count / diff.total_count) * 100;
      } else {
        diff.percentage = 0;
      }
    };

    const updateResult = (index, difficulty) => {
      const result = newHomework.value.results[index];
      if (!result.difficulties[difficulty].enabled) {
        result.difficulties[difficulty].correct_count = 0;
        result.difficulties[difficulty].total_count = 0;
        result.difficulties[difficulty].percentage = 0;
      }
    };

    const getTopicName = (topicId) => {
      const topic = topics.value.find(t => t.id === topicId);
      return topic ? topic.name : 'Неизвестная тема';
    };

    const saveHomework = async () => {
      try {
        const homeworkData = {
          lesson_id: newHomework.value.lesson,
          topic_ids: newHomework.value.topics,
          status: newHomework.value.status,
          results: newHomework.value.results.flatMap(result => {
            return Object.entries(result.difficulties)
              .filter(([_, diff]) => diff.enabled)
              .map(([difficulty, diff]) => ({
                topic_id: result.topic_id,
                difficulty,
                correct_count: diff.correct_count,
                total_count: diff.total_count,
              }));
          }),
        };
        await axios.post('/api/homework/', homeworkData, {
          headers: { 'Content-Type': 'application/json' },
        });
        showAddHomeworkModal.value = false;
        await fetchLessons();
        await fetchTopics();
      } catch (err) {
        console.error('Ошибка при сохранении ДЗ:', err.response?.data || err.message);
        error.value = 'Не удалось сохранить ДЗ: ' + (err.response?.data?.detail || err.message);
      }
    };

    const closeModal = () => {
      showAddHomeworkModal.value = false;
      selectedTopic.value = '';
      newHomework.value = { lesson: null, topics: [], status: 'ASSIGNED', results: [] };
    };

    const generateHomework = async () => {
      try {
        // Получаем все уроки студента
        const lessonsResponse = await axios.get(`/api/lessons/?student=${props.studentId}`);
        const studentLessons = lessonsResponse.data;

        // Собираем ID тем из уроков
        const lessonTopicIds = new Set(studentLessons.map(lesson => lesson.topic.id));

        // Получаем все домашние задания для уроков студента
        const lessonIds = studentLessons.map(lesson => lesson.id);
        const homeworksResponse = await axios.get('/api/homework/', {
          params: { lesson__in: lessonIds.join(',') }
        });
        const homeworks = homeworksResponse.data;

        // Собираем ID тем из домашних заданий
        const homeworkTopicIds = new Set();
        homeworks.forEach(homework => {
          homework.topic_ids.forEach(topicId => homeworkTopicIds.add(topicId));
        });

        // Получаем результаты по темам из домашних заданий
        const resultsResponse = await axios.get('/api/homework-results/', {
          params: { homework__lesson__in: lessonIds.join(',') }
        });
        const results = resultsResponse.data;

        // Формируем список тем, требующих доработки
        const underperformedTopics = [];

        // 1. Темы из уроков, для которых нет ДЗ
        const topicsWithoutHomework = Array.from(lessonTopicIds).filter(
          topicId => !homeworkTopicIds.has(topicId)
        );
        for (const topicId of topicsWithoutHomework) {
          const topic = topics.value.find(t => t.id === topicId);
          if (topic) {
            ['EASY', 'MEDIUM', 'HARD'].forEach(difficulty => {
              underperformedTopics.push({
                topic,
                difficulty,
                percentage: 0,
              });
            });
          }
        }

        // 2. Темы из ДЗ
        for (const topicId of homeworkTopicIds) {
          const topic = topics.value.find(t => t.id === topicId);
          if (!topic) continue;

          const topicResults = results.filter(result => result.topic_id === topicId);

          ['EASY', 'MEDIUM', 'HARD'].forEach(difficulty => {
            const difficultyResults = topicResults.filter(result => result.difficulty === difficulty);

            // Проверяем, есть ли результат 100% для этой сложности
            const hasPerfectScore = difficultyResults.some(result => result.percentage === 100);

            if (!hasPerfectScore) {
              // Если нет результатов, добавляем с 0%
              if (difficultyResults.length === 0) {
                underperformedTopics.push({
                  topic,
                  difficulty,
                  percentage: 0,
                });
              } else {
                // Добавляем последний результат для сложности
                const latestResult = difficultyResults.reduce((latest, current) =>
                  new Date(current.created_at) > new Date(latest.created_at) ? current : latest
                );
                underperformedTopics.push({
                  topic,
                  difficulty,
                  percentage: latestResult.percentage,
                });
              }
            }
          });
        }

        generatedTopics.value = underperformedTopics;
        showGeneratedHomeworkModal.value = true;
      } catch (err) {
        console.error('Ошибка при генерации ДЗ:', err.response?.data || err.message);
        error.value = 'Не удалось сгенерировать ДЗ: ' + (err.response?.data?.detail || err.message);
      }
    };

    const sortedTopics = computed(() => {
      return [...generatedTopics.value].sort((a, b) => {
        if (sortOrder.value === 'asc') {
          return a.percentage - b.percentage;
        } else {
          return b.percentage - a.percentage;
        }
      });
    });

    const closeGeneratedModal = () => {
      showGeneratedHomeworkModal.value = false;
      generatedTopics.value = [];
      sortOrder.value = 'asc';
    };

    const formatDate = (dateString) => {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    };

    const resetFilters = () => {
      typeFilter.value = '';
      dateFilter.value = '';
    };

    const filteredLessons = computed(() => {
      let result = lessons.value;
      if (typeFilter.value) {
        result = result.filter((lesson) => lesson.lesson_type.id == typeFilter.value);
      }
      if (dateFilter.value) {
        const filterDate = new Date(dateFilter.value).toISOString().split('T')[0];
        result = result.filter((lesson) => lesson.date.includes(filterDate));
      }
      return result;
    });

    onMounted(() => {
      fetchLessons();
      fetchLessonTypes();
      fetchTopics();
    });

    return {
      lessons,
      lessonTypes,
      topics,
      typeFilter,
      dateFilter,
      showAddHomeworkModal,
      newHomework,
      selectedTopic,
      isLoading,
      error,
      showGeneratedHomeworkModal,
      generatedTopics,
      sortOrder,
      sortedTopics,
      addHomework,
      addTopicResult,
      saveHomework,
      closeModal,
      generateHomework,
      closeGeneratedModal,
      formatDate,
      filteredLessons,
      resetFilters,
      calculatePercentage,
      updateResult,
      getTopicName,
    };
  },
};
</script>

<style scoped>
.lesson-card {
  border: 1px solid var(--bs-secondary);
  border-radius: 5px;
}
.filters {
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
.form-check {
  margin-bottom: 10px;
}
</style>