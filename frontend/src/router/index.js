import { createRouter, createWebHistory } from 'vue-router';
import Home from "../views/Home.vue";
import CategoryPage from "../views/CategoryPage.vue";
import StudentLessons from "../views/StudentLessons.vue";
import LessonList from "../views/LessonList.vue";
const routes = [
  { path: '/', component: Home },
  { path: '/:category', component: CategoryPage },
  { path: '/:category/:studentId', component: StudentLessons },
  { path: '/:category/:studentId/lessons',component: LessonList, props: (route) => ({
    studentId: Number(route.params.studentId) || null, // Convert to number, fallback to null
  }),},
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;