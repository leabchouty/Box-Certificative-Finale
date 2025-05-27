import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/Login.vue';
import HomeStudentView from '../views/HomeStudent.vue';

const routes = [
  {
    path: '/',
    redirect: '/login',
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
  },
  {
    path: '/homeStudent',
    name: 'HomeStudent',
    component: HomeStudentView,
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router; 