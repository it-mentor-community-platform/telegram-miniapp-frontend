import { computed } from 'vue'
import { useRoute, type RouteLocationNormalizedLoaded, type RouteLocationRaw } from 'vue-router'

export type BreadcrumbItem = {
  label: string
  to: RouteLocationRaw
}

// Ancestors of the route that have a breadcrumb label. The current page is not included: its title
// follows the trail. Role prefixes such as /student have no label and are skipped.
export function breadcrumbTrail(route: RouteLocationNormalizedLoaded): BreadcrumbItem[] {
  return route.matched.slice(0, -1).flatMap((record) =>
    record.meta.breadcrumb && record.name
      ? [{ label: record.meta.breadcrumb, to: { name: record.name, params: route.params } }]
      : [],
  )
}

// Where "back" leads from this route: the last breadcrumb, or home.
export function parentLocation(route: RouteLocationNormalizedLoaded): RouteLocationRaw {
  return breadcrumbTrail(route).at(-1)?.to ?? { name: 'home' }
}

export function useBreadcrumbs() {
  const route = useRoute()
  return computed(() => breadcrumbTrail(route))
}
