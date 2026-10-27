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
  ADMIN: { label: 'Админ', class: 'tint-help' },
}

const initials = `${user.firstName.charAt(0)}${user.lastName?.charAt(0) ?? ''}`
const showDevTools = import.meta.env.VITE_SHOW_DEV_TOOLS === 'true'
const isMentor = user.roles.includes('MENTOR')
const isAdmin = user.roles.includes('ADMIN')
</script>

<template>
  <div class="flex flex-col gap-5">
    <header class="flex items-center gap-3">
      <Avatar :label="initials" shape="circle" size="large" class="tint-success shrink-0 text-[1.0625rem] font-semibold" />
      <div class="flex min-w-0 flex-1 flex-col gap-1.5">
        <h1 class="text-lg/[1.375rem] font-semibold">Привет, {{ user.firstName }}</h1>
        <div class="flex flex-wrap gap-1.5">
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
        class="size-11 shrink-0"
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
      <div v-if="tracks.length > 0" class="flex flex-col gap-3">
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
