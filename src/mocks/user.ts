// Mocked current user until the app authenticates against the backend.

export type Role = 'STUDENT' | 'MENTOR' | 'ADMIN'

export type CurrentUser = {
  firstName: string
  lastName: string
  roles: Role[]
}

const knownRoles: Role[] = ['STUDENT', 'MENTOR', 'ADMIN']

export function getCurrentUser(): CurrentUser {
  return {
    firstName: 'Сергей',
    lastName: 'Жуков',
    roles: mockRoles(),
  }
}

function mockRoles(): Role[] {
  const roles = (import.meta.env.VITE_MOCK_ROLES ?? 'STUDENT')
    .split(',')
    .map((role) => role.trim().toUpperCase())
    .filter((role): role is Role => knownRoles.includes(role as Role))
  return roles.length > 0 ? roles : ['STUDENT']
}
