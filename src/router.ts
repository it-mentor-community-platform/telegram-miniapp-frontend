import { createRouter, createWebHistory } from 'vue-router'
import { session, whenAuthenticated } from './session'
import HomeView from './views/HomeView.vue'
import StudentProjectsView from './views/StudentProjectsView.vue'

declare module 'vue-router' {
  interface RouteMeta {
    // Label of this route in the breadcrumb trail of its descendants.
    breadcrumb?: string
  }
}

// HTML5 history mode: Telegram passes launch data in the URL fragment, which conflicts with hash routing.
export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    {
      path: '/student',
      redirect: { name: 'home' },
      beforeEnter: () => (session.user?.roles.includes('STUDENT') ? true : { name: 'home' }),
      children: [
        {
          path: 'projects',
          name: 'student-projects',
          component: StudentProjectsView,
          meta: { breadcrumb: 'Мои проекты' },
        },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: { name: 'home' } },
  ],
})

// Role guards need the authenticated user, so navigation waits for authentication.
router.beforeEach(() => whenAuthenticated)
