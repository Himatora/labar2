<template>
  <div>
    <h1 class="mb-4 text-primary">{{ student?.full_name ? `${student.full_name}` : 'Загрузка...' }}</h1>
    <nav v-if="student" class="navbar navbar-expand-lg navbar-dark mb-4">
      <div class="container-fluid">
        <router-link :to="`/${categorySlug}`" class="navbar-brand">Назад</router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <div class="navbar-nav">
            <router-link :to="`/${categorySlug}/${$route.params.studentId}/lessons`" class="nav-link">Просмотреть уроки</router-link>
            <a class="nav-link active" href="#">Уроки и журнал</a>
          </div>
        </div>
      </div>
    </nav>
    <div v-else class="text-center my-4">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Загрузка...</span>
      </div>
    </div>
  </div>
  <div v-if="student" class="row">
    <div class="col-md-6">
      <LessonManagement :studentId="parseInt($route.params.studentId)" />
    </div>
    <div class="col-md-6">
      <JournalManagement :studentId="parseInt($route.params.studentId)" />
    </div>
  </div>
</template>

<script>
import LessonManagement from '@/components/LessonManagement.vue';
import JournalManagement from '@/components/JournalManagement.vue';
import axios from 'axios';

// Use relative paths - nginx will proxy /api/ to backend over HTTPS
axios.defaults.baseURL = '';

export default {
  name: 'StudentLessons',
  components: { LessonManagement, JournalManagement },
  data() {
    return {
      student: null,
    };
  },
  computed: {
    categorySlug() {
      return this.student?.learning_category?.slug || '';
    },
  },
  async mounted() {
    try {
      const response = await axios.get(`/api/students/${this.$route.params.studentId}/`);
      this.student = response.data;
    } catch (error) {
      console.error('Ошибка загрузки данных ученика:', error.response?.data || error.message);
    }
  },
};
</script>