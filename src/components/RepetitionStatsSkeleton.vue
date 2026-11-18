<script setup lang="ts">
import Skeleton from 'primevue/skeleton'
</script>

<template>
  <div class="grid grid-cols-3 gap-2" aria-hidden="true">
    <Skeleton v-for="item in 3" :key="item" height="4rem" border-radius="10px" />
  </div>
</template>
