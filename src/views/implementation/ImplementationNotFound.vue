<script setup lang="ts">
import NotFoundState from '../../components/NotFoundState.vue'
</script>

<template>
  <!-- An unknown or someone else's implementation (backend 404): the project not-found layout. -->
  <NotFoundState
    title="Реализация не найдена"
    text="Возможно, ссылка устарела или в ней опечатка. Все ваши реализации — на страницах проектов в разделе «Мои проекты»."
    :action="{ label: 'К моим проектам', to: { name: 'student-projects' } }"
  />
</template>
