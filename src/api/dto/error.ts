// Standard error body of the backend services (auth-service `ErrorResponseDto`).
export type ErrorResponseDto = {
  timestamp: string
  status: number
  error: string
  message: string
  path: string
}
