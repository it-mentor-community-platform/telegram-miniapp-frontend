// Error body of the backend services. auth-service sends all fields (`ErrorResponseDto`);
// project-service sends only `message`.
export type ErrorResponseDto = {
  timestamp?: string
  status?: number
  error?: string
  message: string
  path?: string
}
