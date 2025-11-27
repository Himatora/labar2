<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="mb-4 text-primary">Система учета занятий</h1>
      <button @click="showAddCategoryModal" class="btn btn-primary">
        <i class="bi bi-plus-lg me-1"></i> Добавить категорию
      </button>
    </div>
    <div v-if="error" class="alert alert-danger mb-4">{{ error }}</div>
    <nav class="navbar navbar-expand-lg navbar-dark mb-4">
      <div class="container-fluid">
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav">
            <li v-for="category in categories" :key="category.id" class="nav-item">
              <router-link class="nav-link" :to="'/' + category.slug">{{ category.name }}</router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>
    <div class="row">
      <div v-for="category in categories" :key="category.id" class="col-md-4">
        <div class="card mb-4">
          <div class="card-body text-center">
            <h3>{{ category.name }}</h3>
            <p>Подготовка к {{ category.name }}</p>
            <router-link :to="'/' + category.slug" class="btn btn-primary">Перейти</router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно для добавления категории -->
    <div class="modal fade" id="categoryModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Новая категория обучения</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="addCategory">
              <div class="mb-3">
                <label class="form-label">Название категории *</label>
                <input v-model="newCategoryName" type="text" class="form-control" placeholder="Например: Подготовка к ОГЭ" required />
              </div>
              <div v-if="modalError" class="alert alert-danger">{{ modalError }}</div>
              <div class="modal-footer">
                <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">Отмена</button>
                <button type="submit" class="btn btn-primary" :disabled="!newCategoryName">Добавить</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Modal } from 'bootstrap';

// Use relative paths - nginx will proxy /api/ to backend over HTTPS
axios.defaults.baseURL = '';

export default {
  name: 'Home',
  data() {
    return {
      categories: [],
      error: null,
      newCategoryName: '',
      modalError: null,
    };
  },
  mounted() {
    this.fetchCategories();
  },
  methods: {
    async fetchCategories() {
      try {
        const response = await axios.get('/api/learning-categories/');
        console.log('Категории с API:', JSON.stringify(response.data, null, 2));
        this.categories = response.data;
        if (!response.data.length) {
          this.error = 'Категории не найдены. Создайте новую категорию.';
        }
      } catch (error) {
        console.error('Ошибка при загрузке категорий:', error.response?.data || error.message);
        this.error = 'Не удалось загрузить категории: ' + (error.response?.data?.detail || error.message);
      }
    },
    showAddCategoryModal() {
      this.newCategoryName = '';
      this.modalError = null;
      const modalEl = document.getElementById('categoryModal');
      const modal = new Modal(modalEl, { backdrop: 'static' });
      modal.show();
    },
    async addCategory() {
      if (!this.newCategoryName) return;
      try {
        this.modalError = null;
        const data = { name: this.newCategoryName };
        console.log('Отправляем данные категории:', data);
        await axios.post('/api/learning-categories/', data, {
          headers: { 'Content-Type': 'application/json' },
        });
        await this.fetchCategories(); // Обновляем список категорий
        this.newCategoryName = '';
        const modalEl = document.getElementById('categoryModal');
        const modal = Modal.getInstance(modalEl);
        modal.hide();
      } catch (error) {
        console.error('Ошибка при добавлении категории:', error.response?.data || error.message);
        this.modalError = 'Не удалось добавить категорию: ' + (error.response?.data?.detail || error.message);
      }
    },
  },
};
</script>

<style scoped>
.card-body {
  padding: 1.5rem;
}
</style>