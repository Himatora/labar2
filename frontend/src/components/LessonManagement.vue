<template>
  <div class="card mb-4">
    <div class="card-body">
      <div class="card mb-3">
        <h2 class="card-body">Добавить урок</h2>
        <div class="form-group m-3">
          <div class="mb-3">
            <label>Вид урока:</label>
            <select v-model="newLesson.lesson_type" class="form-select" required>
              <option value="" disabled>Выберите вид урока</option>
              <option v-for="type in lessonTypes" :key="type.id" :value="type.id">{{ type.name }}</option>
            </select>
          </div>
          <div class="mb-3">
            <label>Тема:</label>
            <div class="input-group mb">
              <select v-model="newLesson.topic" class="form-select" required :disabled="topics.length === 0">
                <option value="" disabled>Выберите тему</option>
                <option v-for="topic in topics" :key="topic.id" :value="topic.id">{{ topic.name }}</option>
              </select>
              <button @click="showAddTopicModal = true" class="btn btn-outline-secondary">+</button>
            </div>
            <small v-if="topics.length === 0" class="text-muted">Нет доступных тем. Добавьте новую тему.</small>
          </div>
          <div class="form-group mb-3">
            <label>Комментарий:</label>
            <textarea v-model="newLesson.comment" class="form-control"></textarea>
          </div>
          <button @click="addLesson" class="btn btn-primary" :disabled="!isLessonValid">Добавить урок</button>
        </div>
      </div>
    </div>

    <div v-if="showAddTopicModal" class="modal fade show d-block" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h3 class="modal-title">Добавить новую тему</h3>
            <button type="button" class="btn-close" @click="showAddTopicModal = false"></button>
          </div>
          <div class="modal-body">
            <input v-model="newTopicName" type="text" class="form-control" placeholder="Название темы" />
          </div>
          <div class="modal-footer">
            <button @click="addTopic" class="btn btn-primary" :disabled="!newTopicName">Добавить</button>
            <button @click="showAddTopicModal = false" class="btn btn-outline-secondary">Отмена</button>
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
  name: 'LessonManagement',
  props: {
    studentId: {
      type: Number,
      required: true,
    },
  },
  setup(props) {
    const lessonTypes = ref([]);
    const topics = ref([]);
    const showAddTopicModal = ref(false);
    const newTopicName = ref('');
    const newLesson = ref({
      student: props.studentId,
      lesson_type: '',
      topic: '',
      comment: '',
    });

    const isLessonValid = computed(() => {
      return newLesson.value.student && newLesson.value.lesson_type && newLesson.value.topic;
    });

    const fetchLessonTypes = async () => {
      try {
        const response = await axios.get('/api/lesson-types/');
        lessonTypes.value = response.data;
        if (lessonTypes.value.length > 0 && !newLesson.value.lesson_type) {
          newLesson.value.lesson_type = lessonTypes.value[0].id;
        }
      } catch (error) {
        console.error('Ошибка при загрузке видов уроков:', error.response?.data || error.message);
      }
    };

    const fetchTopics = async () => {
      try {
        const response = await axios.get('/api/topics/', {
          params: { students: props.studentId },
        });
        topics.value = response.data;
        if (topics.value.length > 0 && !newLesson.value.topic) {
          newLesson.value.topic = topics.value[0].id;
        } else if (topics.value.length === 0) {
          newLesson.value.topic = '';
        }
      } catch (error) {
        console.error('Ошибка при загрузке тем:', error.response?.data || error.message);
        topics.value = [];
        newLesson.value.topic = '';
      }
    };

    const addLesson = async () => {
      if (!isLessonValid.value) {
        console.error('Форма урока не заполнена полностью');
        return;
      }
      try {
        const lessonData = {
          student_id: Number(newLesson.value.student),
          lesson_type_id: Number(newLesson.value.lesson_type),
          topic_id: Number(newLesson.value.topic),
          comment: newLesson.value.comment || "Нет комментария",
        };
        await axios.post('/api/lessons/', lessonData, {
          headers: { 'Content-Type': 'application/json' },
        });
        newLesson.value = {
          student: props.studentId,
          lesson_type: lessonTypes.value.length > 0 ? lessonTypes.value[0].id : '',
          topic: topics.value.length > 0 ? topics.value[0].id : '',
          comment: '',
        };
      } catch (error) {
        console.error('Ошибка при добавлении урока:', error.response?.data || error);
      }
    };

    const addTopic = async () => {
      if (!newTopicName.value) return;
      try {
        const response = await axios.post('/api/topics/', {
          name: newTopicName.value,
          students: [props.studentId],  // Связываем тему с текущим учеником
        }, {
          headers: { 'Content-Type': 'application/json' },
        });
        topics.value.push(response.data);
        newLesson.value.topic = response.data.id;
        newTopicName.value = '';
        showAddTopicModal.value = false;
      } catch (error) {
        console.error('Ошибка при добавлении темы:', error.response?.data || error.message);
      }
    };

    onMounted(() => {
      fetchLessonTypes();
      fetchTopics();
    });

    return {
      lessonTypes,
      topics,
      newLesson,
      newTopicName,
      showAddTopicModal,
      addLesson,
      addTopic,
      isLessonValid,
    };
  },
};
</script>

<style scoped>
.form-section {
  margin-bottom: 30px;
  padding: 15px;
  border: 1px solid var(--bs-secondary);
  border-radius: 5px;
}
.form-group {
  margin-bottom: 15px;
}
.form-group label {
  display: block;
  margin-bottom: 5px;
}
</style>