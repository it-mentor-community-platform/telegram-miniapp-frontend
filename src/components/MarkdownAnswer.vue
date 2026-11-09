<script setup lang="ts">
import { computed } from 'vue'
import { renderAnswerMarkdown } from '../markdown'

const props = defineProps<{ text: string; specialization?: string }>()
const html = computed(() => renderAnswerMarkdown(props.text, props.specialization))

function onImageError(event: Event) {
  const image = event.target
  if (!(image instanceof HTMLImageElement)) return
  const fallback = document.createElement('span')
  fallback.className = 'markdown-image-error'
  fallback.textContent = `Не удалось загрузить изображение: ${image.alt || 'иллюстрация к ответу'}`
  image.replaceWith(fallback)
}
</script>

<template>
  <!-- Only renderAnswerMarkdown generates this HTML; raw HTML from answers is disabled. -->
  <div class="markdown-answer" @error.capture="onImageError" v-html="html" />
</template>

<style>
/* v-html descendants have no Vue scope attributes. All selectors are confined to this component's
   root; native Markdown elements need semantic styling rather than PrimeVue component overrides. */
.markdown-answer {
  min-width: 0;
  max-width: 100%;
  overflow-wrap: anywhere;
  font-size: var(--text-md);
  line-height: 1.6;
  color: var(--p-text-color);
}
.markdown-answer :where(p, ul, ol, blockquote, pre, table, figure, hr, h3, h4, h5, h6) { margin-block: 0.85em; }
.markdown-answer > :first-child { margin-top: 0; }
.markdown-answer > :last-child { margin-bottom: 0; }
.markdown-answer :where(h3, h4, h5, h6) { font-weight: 700; line-height: 1.35; margin-top: 1.25em; }
.markdown-answer h3 { font-size: 1.2em; }
.markdown-answer h4 { font-size: 1.1em; }
.markdown-answer :where(h5, h6) { font-size: 1em; }
.markdown-answer ul { list-style-type: disc; padding-left: 1.5em; }
.markdown-answer ol { list-style-type: decimal; padding-left: 1.5em; }
.markdown-answer li + li { margin-top: 0.3em; }
.markdown-answer li :where(ul, ol, p) { margin-block: 0.35em; }
.markdown-answer strong { font-weight: 700; }
.markdown-answer em { font-style: italic; }
.markdown-answer s { text-decoration: line-through; }
.markdown-answer a { color: var(--p-primary-color); text-decoration: underline; text-underline-offset: 0.15em; }
.markdown-answer :where(a, pre, .markdown-table):focus-visible { outline: 2px solid var(--p-primary-color); outline-offset: 2px; }
.markdown-answer code { font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 0.9em; }
.markdown-answer :not(pre) > code { background: var(--p-content-hover-background); border-radius: 0.25rem; padding: 0.1em 0.3em; }
.markdown-answer pre { max-width: 100%; overflow-x: auto; white-space: pre; overflow-wrap: normal; padding: 1rem; border: 1px solid var(--p-content-border-color); border-radius: 0.5rem; background: var(--p-content-hover-background); }
.markdown-answer pre code { white-space: inherit; background: transparent; padding: 0; }
.markdown-answer blockquote { padding-left: 1rem; border-left: 3px solid var(--p-content-border-color); color: var(--p-text-muted-color); }
.markdown-answer hr { border: 0; border-top: 1px solid var(--p-content-border-color); }
.markdown-answer .markdown-table { max-width: 100%; overflow-x: auto; }
.markdown-answer table { border-collapse: collapse; font-size: 0.9em; width: 100%; }
.markdown-answer :where(th, td) { border: 1px solid var(--p-content-border-color); padding: 0.5rem 0.75rem; text-align: left; min-width: 7rem; }
.markdown-answer th { font-weight: 600; background: var(--p-content-hover-background); }
.markdown-answer img { display: block; max-width: 100%; height: auto; border-radius: 0.5rem; margin-block: 0.75rem; }
.markdown-answer .markdown-inline-figure { display: inline-block; max-width: 100%; }
.markdown-answer :where(figcaption, .markdown-caption, .markdown-image-error) { display: block; color: var(--p-text-muted-color); font-size: 0.85em; }
</style>
