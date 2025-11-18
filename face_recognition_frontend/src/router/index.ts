import { createRouter, createWebHistory } from 'vue-router'
import AuthLayout from '../components/Auth/AuthLayout.vue'
import MainLayout from '../components/MainLayout.vue'
import HomePage from '../views/Home/HomePage.vue'
import CourseManagement from '../views/dashboard/CourseManagement.vue'
import ClassManagement from '../views/dashboard/ClassManagement.vue'
import StudentAccountManagement from '../views/dashboard/account/StudentAccountManagement.vue'
import TeacherAccountManagement from '../views/dashboard/account/TeacherAccountManagement.vue'
import AttendanceManagement from '../views/dashboard/AttendanceManagement.vue'
import StudentAttendanceManagement from '../views/dashboard/StudentAttendanceManagement.vue'
import LeaveManagement from '@/views/dashboard/LeaveManagement.vue'
import FaceManagement from '@/views/dashboard/FaceManagement.vue'
import ProfileCenter from '@/views/Profile/ProfileCenter.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'Login',
      component: AuthLayout,
      meta: { requiresAuth: false }
    },
    {
      path: '/profile',
      name: 'ProfileCenter',
      component: MainLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          component: ProfileCenter
        }
      ]
    },
    {
      path: '/dashboard',
      name: 'DashboardLayout',
      component: MainLayout,
      redirect: '/dashboard/home',
      meta: { requiresAuth: true },
      children: [
        {
          path: 'home',
          name: 'Home',
          component: HomePage
        },
        {
          path: 'course',
          name: 'CourseManagement',
          component: CourseManagement
        },
        {
          path: 'class',
          name: 'ClassManagement',
          component: ClassManagement
        },
        {
          path: 'account/student',
          name: 'StudentAccountManagement',
          component: StudentAccountManagement
        },
        {
          path: 'account/teacher',
          name: 'TeacherAccountManagement',
          component: TeacherAccountManagement
        },
        {
          path: 'attendance',
          name: 'AttendanceManagement',
          component: AttendanceManagement
        },
        {
          path: 'student-attendance',
          name: 'StudentAttendanceManagement',
          component: StudentAttendanceManagement
        },
        {
          path:'leave',
          name:'LeaveManagement',
          component: LeaveManagement
        },
        {
          path:'face-import',
          name: 'FaceManagement',
          component: FaceManagement
        },
        {
          path:'attendance-check',
          name: 'AttendanceCheck',
          component: () => import('../views/dashboard/AttendanceCheck.vue')
        }
      ]
    },
  ],
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token');
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  if (requiresAuth && !isAuthenticated) {
    next('/login');
  } else if (to.path === '/login' && isAuthenticated) {
    next('/dashboard/home');
  } else {
    next();
  }
});

export default router
