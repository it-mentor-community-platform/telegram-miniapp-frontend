<script setup lang="ts">
import Avatar from 'primevue/avatar'
import Card from 'primevue/card'

defineProps<{
  title: string
  text: string
  icon: 'info' | 'chat' | 'none'
}>()

const icons = { info: 'pi pi-info-circle', chat: 'pi pi-comment' }
</script>

<template>
  <Card>
    <template #content>
      <div class="flex items-start gap-3">
        <Avatar
          v-if="icon !== 'none'"
          :icon="icons[icon]"
          shape="circle"
          class="size-9 shrink-0"
          aria-hidden="true"
        />
        <div class="flex min-w-0 flex-col gap-1">
          <span class="text-md font-semibold">{{ title }}</span>
          <span class="text-sm text-muted-color">{{ text }}</span>
        </div>
      </div>
    </template>
  </Card>
</template>
