<script setup lang="ts">
import Avatar from 'primevue/avatar'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import ListSection from '../components/ListSection.vue'
import NavListRow from '../components/NavListRow.vue'
import RoadmapProgress from '../components/RoadmapProgress.vue'
import StatTiles from '../components/StatTiles.vue'
import { getHomeData } from '../mocks/home'
import { getMyProjects } from '../mocks/projects'
import { buildRoadmapTracks } from '../roadmap'
import { session, type Role } from '../session'
import DevPanel from './home/DevPanel.vue'
import SectionCard from './home/SectionCard.vue'

// App.vue renders routes only for an authenticated session, so the user is always set here.
const user = session.user!
const home = getHomeData()
const tracks = buildRoadmapTracks(getMyProjects())

const roleTags: Record<Role, { label: string; severity?: 'success' | 'info'; class?: string }> = {
  STUDENT: { label: 'Студент', severity: 'success' },
  MENTOR: { label: 'Ментор', severity: 'info' },
  ADMIN: { label: 'Админ', class: 'tag-violet' },
}

const initials = `${user.firstName.charAt(0)}${user.lastName?.charAt(0) ?? ''}`
const showDevTools = import.meta.env.VITE_SHOW_DEV_TOOLS === 'true'
const isMentor = user.roles.includes('MENTOR')
const isAdmin = user.roles.includes('ADMIN')
</script>

<template>
  <div class="home">
    <header class="home-header">
      <Avatar :label="initials" shape="circle" size="large" class="home-avatar" />
      <div class="home-greeting">
        <h1 class="home-title">Привет, {{ user.firstName }}</h1>
        <div class="home-roles">
          <Tag
            v-for="role in user.roles"
            :key="role"
            :value="roleTags[role].label"
            :severity="roleTags[role].severity"
            :class="roleTags[role].class"
          />
        </div>
      </div>
      <Button
        icon="pi pi-sliders-h"
        text
        rounded
        severity="secondary"
        aria-label="Настройки"
        class="home-settings"
      />
    </header>

    <SectionCard icon="pi-sync" title="Вопросы к собеседованиям" subtitle="Интервальное повторение">
      <StatTiles :items="home.repetitionStats" />
    </SectionCard>

    <SectionCard
      icon="pi-map"
      title="Мои проекты"
      subtitle="Прогресс по роадмапу"
      :to="{ name: 'student-projects' }"
    >
      <div v-if="tracks.length > 0" class="home-tracks">
        <RoadmapProgress
          v-for="track in tracks"
          :key="track.language"
          :label="track.label"
          :steps="track.steps"
          compact
        />
      </div>
    </SectionCard>

    <ListSection title="Разделы">
      <NavListRow
        icon="pi-user"
        title="Профиль"
        subtitle="Достижения, проекты и ревью"
        :badge="`${home.achievementCount} ачивки`"
      />
      <NavListRow icon="pi-comments" title="Ревью" subtitle="Ревью на ваши проекты" divider />
      <NavListRow
        icon="pi-graduation-cap"
        title="Кабинет ментора"
        subtitle="Цены на ревью и услуги"
        :badge="isMentor ? undefined : 'Неактивен'"
        badge-tone="neutral"
        divider
      />
      <NavListRow
        icon="pi-users"
        title="Участники"
        subtitle="Поиск по имени, GitHub, Telegram"
        divider
      />
      <NavListRow
        icon="pi-chart-line"
        title="Рынок труда"
        subtitle="Вакансии и зарплаты на hh.ru"
        divider
      />
      <NavListRow
        v-if="isAdmin"
        icon="pi-shield"
        title="Администрирование"
        subtitle="Роли пользователей"
        divider
      />
    </ListSection>

    <DevPanel v-if="showDevTools" />
  </div>
</template>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.home-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.home-avatar {
  flex-shrink: 0;
  width: 3rem;
  height: 3rem;
  background: var(--p-emerald-50);
  color: var(--p-emerald-700);
  font-size: 1.0625rem;
  font-weight: 600;
}

.app-dark .home-avatar {
  background: color-mix(in srgb, var(--p-emerald-400) 16%, transparent);
  color: var(--p-emerald-300);
}

.home-greeting {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 0.375rem;
  min-width: 0;
}

.home-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  line-height: 1.375rem;
}

.home-roles {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.tag-violet {
  background: var(--p-violet-50);
  color: var(--p-violet-700);
}

.app-dark .tag-violet {
  background: color-mix(in srgb, var(--p-violet-400) 16%, transparent);
  color: var(--p-violet-300);
}

.home-settings {
  flex-shrink: 0;
  width: 2.75rem;
  height: 2.75rem;
}

.home-tracks {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

</style>
