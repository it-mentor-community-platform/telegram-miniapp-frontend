<script setup lang="ts">
import Avatar from 'primevue/avatar'
import Tag from 'primevue/tag'
import { RouterLink, type RouteLocationRaw } from 'vue-router'
// TODO: replace with a higher-resolution original; the design only embeds a 96×96 JPEG.
import logoUrl from '../assets/logo.jpg'
import { session } from '../session'
import { fullName, initials, roleTags } from '../user'

// App.vue renders the shell only for an authenticated session, so the user is always set here.
const user = session.user!

// `short` is the rail label (tablet). An item without `to` is a section that isn't built yet: shown
// but disabled, like its card on the home page.
const items: { label: string; short: string; icon: string; to?: RouteLocationRaw }[] = [
  { label: 'Главная', short: 'Главная', icon: 'pi-home', to: { name: 'home' } },
  { label: 'Вопросы к собеседованиям', short: 'Вопросы', icon: 'pi-sync', to: user.roles.includes('STUDENT') ? { name: 'student-repetition' } : undefined },
  { label: 'Мои проекты', short: 'Проекты', icon: 'pi-map', to: { name: 'student-projects' } },
]

const itemClass =
  'flex min-h-15 flex-col items-center justify-center gap-1 rounded-lg px-1 py-2 text-center text-[0.6875rem]/3.5 font-semibold ' +
  'lg:min-h-11 lg:flex-row lg:justify-start lg:gap-3 lg:px-3 lg:py-0 lg:text-left lg:text-sm/[1.125rem]'
</script>

<template>
  <!-- Tablet (md): an 88 px rail, icon + short label. Desktop (lg): a 248 px sidebar. -->
  <aside
    class="sticky top-0 hidden h-dvh w-rail shrink-0 flex-col gap-6 border-r border-surface bg-(--p-content-background) px-2 py-5 md:flex lg:w-sidebar lg:px-4"
  >
    <RouterLink
      :to="{ name: 'home' }"
      aria-label="IT Ментор | Платформа сообщества — на главную"
      class="focus-ring flex min-h-10 items-center justify-center gap-2.5 rounded-lg text-color lg:justify-start"
    >
      <img
        :src="logoUrl"
        alt=""
        width="40"
        height="40"
        class="size-10 shrink-0 rounded-full object-cover ring-1 ring-(--p-content-border-color)"
      />
      <span class="hidden min-w-0 flex-col gap-px lg:flex" aria-hidden="true">
        <span class="text-base/5 font-bold">IT Ментор</span>
        <span class="text-note/4 font-medium text-muted-color">Платформа сообщества</span>
      </span>
    </RouterLink>

    <nav aria-label="Разделы приложения" class="flex flex-col gap-1">
      <template v-for="item in items" :key="item.label">
        <RouterLink v-if="item.to" v-slot="{ href, navigate, isActive, isExactActive }" :to="item.to" custom>
          <a
            :href="href"
            :class="[
              itemClass,
              'focus-ring',
              isActive ? 'tint-success' : 'text-(--p-tint-neutral-color) hover:bg-emphasis hover:text-color',
            ]"
            :aria-current="isExactActive ? 'page' : isActive ? 'true' : undefined"
            @click="navigate"
          >
            <i :class="`pi ${item.icon} text-xl`" aria-hidden="true" />
            <span class="lg:hidden">{{ item.short }}</span>
            <span class="hidden lg:inline">{{ item.label }}</span>
          </a>
        </RouterLink>
        <span
          v-else
          :class="[itemClass, 'text-(--p-tint-neutral-color) opacity-(--p-disabled-opacity)']"
          aria-disabled="true"
        >
          <i :class="`pi ${item.icon} text-xl`" aria-hidden="true" />
          <span class="lg:hidden">{{ item.short }}</span>
          <span class="hidden lg:inline">{{ item.label }}</span>
        </span>
      </template>
    </nav>

    <div class="mt-auto flex items-center justify-center gap-2.5 border-t border-surface pt-4 lg:justify-start">
      <Avatar
        :label="initials(user)"
        shape="circle"
        class="tint-success size-9 shrink-0 text-meta font-semibold"
        aria-hidden="true"
      />
      <!-- Visible on desktop; on the tablet rail only the avatar shows, so screen readers get the text. -->
      <div class="sr-only lg:not-sr-only lg:flex lg:min-w-0 lg:flex-1 lg:flex-col lg:gap-1">
        <span class="truncate text-sm/[1.125rem] font-semibold">{{ fullName(user) }}</span>
        <span class="flex flex-wrap gap-1">
          <Tag
            v-for="role in user.roles"
            :key="role"
            :value="roleTags[role].label"
            :severity="roleTags[role].severity"
            class="px-1.5 py-px text-[0.6875rem]/3.5"
            :class="roleTags[role].class"
          />
        </span>
      </div>
    </div>
  </aside>
</template>
