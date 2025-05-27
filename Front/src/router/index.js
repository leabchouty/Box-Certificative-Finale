import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/Login.vue';
import HomeStudentView from '../views/HomeStudent.vue';
import HomeTeacher from '../views/HomeTeacher.vue';
import FormView from '../views/Form.vue';
import FormConfig from '../views/FormConfig.vue';
import ResultsView from '../views/Results.vue';

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
  {
    path: '/homeTeacher',
    name: 'HomeTeacher',
    component: HomeTeacher,
  },
  {
    path: '/form-config',
    name: 'FormConfig',
    component: FormConfig,
  },
  {
    path: '/form',
    name: 'StudentForm',
    component: FormView,
  },
  {
    path: '/results',
    name: 'Results',
    component: ResultsView,
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router; 