/// <reference types="vite/client" />

interface ImportMetaEnv {
  // Comma-separated roles for the mocked user, e.g. "STUDENT,MENTOR,ADMIN". Defaults to "STUDENT".
  readonly VITE_MOCK_ROLES?: string
  // Mocked project implementations: empty | java3 | multi | java6 | other. Defaults to "multi".
  readonly VITE_MOCK_PROJECTS?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
