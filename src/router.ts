import { createRouter, createWebHistory, type RouteLocationNormalizedLoaded } from 'vue-router'
import { projectTypeBySlug } from './roadmap'
import { session, whenAuthenticated } from './session'
import HomeView from './views/HomeView.vue'
import StudentProjectsView from './views/StudentProjectsView.vue'
import StudentImplementationView from './views/StudentImplementationView.vue'
import StudentProjectView from './views/StudentProjectView.vue'
import StudentRepetitionTopicsView from './views/StudentRepetitionTopicsView.vue'
import StudentRepetitionView from './views/StudentRepetitionView.vue'
import StudentRepetitionTopicView from './views/StudentRepetitionTopicView.vue'

declare module 'vue-router' {
  interface RouteMeta {
    // Label of this route in the breadcrumb trail of its descendants; a function for labels that
    // depend on params (undefined: no crumb).
    breadcrumb?: string | ((route: RouteLocationNormalizedLoaded) => string | undefined)
    // false: no app shell on tablet/desktop, for focused screens such as the review session.
    shell?: boolean
    backToHome?: boolean
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
          path: 'repetition',
          meta: { breadcrumb: 'Повторение' },
          children: [
            { path: '', name: 'student-repetition', component: StudentRepetitionView },
            {
              path: 'topics',
              meta: { breadcrumb: 'Все темы' },
              children: [
                { path: '', name: 'student-repetition-topics', component: StudentRepetitionTopicsView },
                { path: ':topicId', name: 'student-repetition-topic', component: StudentRepetitionTopicView },
              ],
            },
            {
              path: 'topics/select', name: 'student-repetition-select',
              component: StudentRepetitionTopicsView, props: { onboarding: true },
              meta: { backToHome: true },
            },
          ],
        },
        {
          // Unnamed parent: its breadcrumb links to the list, its empty-path child.
          path: 'projects',
          meta: { breadcrumb: 'Мои проекты' },
          children: [
            { path: '', name: 'student-projects', component: StudentProjectsView },
            {
              // `:projectType` is the readable slug; an unknown one renders the not-found state.
              path: ':projectType',
              meta: { breadcrumb: (route) => projectTypeBySlug(String(route.params.projectType))?.title },
              children: [
                { path: '', name: 'student-project', component: StudentProjectView },
                {
                  path: 'implementations/:implementationId',
                  name: 'student-implementation',
                  component: StudentImplementationView,
                },
              ],
            },
          ],
        },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: { name: 'home' } },
  ],
})

// Role guards need the authenticated user, so navigation waits for authentication.
router.beforeEach(() => whenAuthenticated)
