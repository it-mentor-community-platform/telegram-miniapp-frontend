import { createRouter, createWebHistory } from 'vue-router'
import { session, whenAuthenticated } from './session'
import HomeView from './views/HomeView.vue'
import StudentProjectsView from './views/StudentProjectsView.vue'
import StudentProjectView from './views/StudentProjectView.vue'

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
          // Unnamed parent: its breadcrumb links to the list, its empty-path child.
          path: 'projects',
          meta: { breadcrumb: 'Мои проекты' },
          children: [
            { path: '', name: 'student-projects', component: StudentProjectsView },
            // `:projectType` is the readable slug; an unknown one renders the not-found state.
            { path: ':projectType', name: 'student-project', component: StudentProjectView },
          ],
        },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: { name: 'home' } },
  ],
})

// Role guards need the authenticated user, so navigation waits for authentication.
router.beforeEach(() => whenAuthenticated)
