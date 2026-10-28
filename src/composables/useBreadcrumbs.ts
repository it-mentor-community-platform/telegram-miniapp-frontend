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
    // The group's own page (the list itself) gets no crumb pointing at itself.
    if (!record.meta.breadcrumb || !name || name === route.name) {
      return []
    }
    // Only the params the ancestor's path uses; Vue Router warns about extra ones.
    const params = Object.fromEntries(
      Object.entries(route.params).filter(([key]) => record.path.includes(`:${key}`)),
    )
    return [{ label: record.meta.breadcrumb, to: { name, params } }]
  })
}

// Where "back" leads from this route: the last breadcrumb, or home.
export function parentLocation(route: RouteLocationNormalizedLoaded): RouteLocationRaw {
  return breadcrumbTrail(route).at(-1)?.to ?? { name: 'home' }
}

export function useBreadcrumbs() {
  const route = useRoute()
  return computed(() => breadcrumbTrail(route))
}
