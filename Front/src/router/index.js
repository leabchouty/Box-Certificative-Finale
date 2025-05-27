import { createRouter, createWebHistory } from 'vue-router';
import { supabase } from '../supabase';

import LoginView from '../views/Login.vue';
import HomeStudentView from '../views/HomeStudent.vue';
import HomeTeacher from '../views/HomeTeacher.vue';
import FormView from '../views/Form.vue';
import FormConfig from '../views/FormConfig.vue';
import ResultsView from '../views/Results.vue';
import GenerateResults from '../views/GenerateResults.vue';
import UnauthorizedView from '../views/Unauthorized.vue'; // Page shown when access is denied

const routes = [
  { path: '/', redirect: '/login' },

  { path: '/login', name: 'Login', component: LoginView },

  {
    path: '/homeStudent',
    name: 'HomeStudent',
    component: HomeStudentView,
    meta: { requiresAuth: true, role: 'student' } // Only students can access
  },
  {
    path: '/form',
    name: 'StudentForm',
    component: FormView,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/results',
    name: 'Results',
    component: ResultsView,
    meta: { requiresAuth: true, role: ['student', 'professor'] } // Both roles can access
  },
  {
    path: '/homeTeacher',
    name: 'HomeTeacher',
    component: HomeTeacher,
    meta: { requiresAuth: true, role: 'professor' }
  },
  {
    path: '/form-config',
    name: 'FormConfig',
    component: FormConfig,
    meta: { requiresAuth: true, role: 'professor' }
  },
  {
    path: '/generate-results',
    name: 'GenerateResults',
    component: GenerateResults,
    meta: { requiresAuth: true, role: 'professor' }
  },
  {
    path: '/unauthorized',
    name: 'Unauthorized',
    component: UnauthorizedView // Shown when user role is not allowed
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

// 🔍 Role detection from Supabase tables
async function detectUserRole(userId) {
  const { data: student } = await supabase
    .from('students')
    .select('id')
    .eq('id', userId)
    .single();

  if (student) return 'student';

  const { data: professor } = await supabase
    .from('professors')
    .select('id')
    .eq('id', userId)
    .single();

  if (professor) return 'professor';

  return null; // Unknown or unauthorized user
}

// 🔐 Global navigation guard
router.beforeEach(async (to, from, next) => {
  const { data: sessionData } = await supabase.auth.getSession();
  const user = sessionData?.session?.user;

  // Route requires authentication but no user is logged in
  if (to.meta.requiresAuth && !user) {
    return next('/login');
  }

  // Route requires a specific role
  if (to.meta.role && user) {
    const role = await detectUserRole(user.id);

    const allowedRoles = Array.isArray(to.meta.role)
      ? to.meta.role
      : [to.meta.role];

    if (!allowedRoles.includes(role)) {
      return next('/unauthorized');
    }
  }

  next(); // Allow access
});

export default router;
