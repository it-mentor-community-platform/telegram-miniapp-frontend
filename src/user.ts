import type { CurrentUser, Role } from './session'

// Role tags next to the user's name (home header, app shell).
export const roleTags: Record<Role, { label: string; severity?: 'success' | 'info'; class?: string }> = {
  STUDENT: { label: 'Студент', severity: 'success' },
  MENTOR: { label: 'Ментор', severity: 'info' },
  ADMIN: { label: 'Админ', class: 'tint-help' },
}

export function initials(user: CurrentUser) {
  return `${user.firstName.charAt(0)}${user.lastName?.charAt(0) ?? ''}`
}

export function fullName(user: CurrentUser) {
  return [user.firstName, user.lastName].filter(Boolean).join(' ')
}
