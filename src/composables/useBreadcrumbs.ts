import { computed } from 'vue'
import { useRoute, type RouteLocationNormalizedLoaded, type RouteLocationRaw } from 'vue-router'

export type BreadcrumbItem = {
  label: string
  to: RouteLocationRaw
}

// Ancestors of the route that have a breadcrumb label. The current page is not included: its title
// follows the trail. Role prefixes such as /student have no label and are skipped. An unnamed
// parent (a group of pages) links to its empty-path child, e.g. «Мои проекты» to the list.
export function breadcrumbTrail(route: RouteLocationNormalizedLoaded): BreadcrumbItem[] {
  return route.matched.slice(0, -1).flatMap((record) => {
    const name = record.name ?? record.children.find((child) => child.path === '')?.name
    const { breadcrumb } = record.meta
    const label = typeof breadcrumb === 'function' ? breadcrumb(route) : breadcrumb
    // The group's own page (the list itself) gets no crumb pointing at itself.
    if (!label || !name || name === route.name) {
      return []
    }
    // Only the params the ancestor's path uses; Vue Router warns about extra ones.
    const params = Object.fromEntries(
      Object.entries(route.params).filter(([key]) => record.path.includes(`:${key}`)),
    )
    return [{ label, to: { name, params } }]
  })
}

// Where "back" leads from this route: the last breadcrumb, or home.
export function parentLocation(route: RouteLocationNormalizedLoaded): RouteLocationRaw {
  if (route.meta.backToHome) return { name: 'home' }
  return breadcrumbTrail(route).at(-1)?.to ?? { name: 'home' }
}

export function useBreadcrumbs() {
  const route = useRoute()
  return computed(() => breadcrumbTrail(route))
}
