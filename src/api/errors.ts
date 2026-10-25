import type { ErrorResponseDto } from './dto/error'

// Every failed API call rejects with an ApiError subclass, never with an axios error.
export class ApiError extends Error {
  constructor(message: string, options?: ErrorOptions) {
    super(message, options)
    this.name = new.target.name
  }
}

// No response: backend unreachable, CORS rejection, timeout.
export class NetworkError extends ApiError {}

// The backend responded with a non-2xx status.
export class HttpError extends ApiError {
  readonly status: number
  readonly body?: ErrorResponseDto

  constructor(status: number, body?: ErrorResponseDto, options?: ErrorOptions) {
    super(body?.message || `HTTP ${status}`, options)
    this.status = status
    this.body = body
  }
}

export class BadRequestError extends HttpError {}
export class UnauthorizedError extends HttpError {}
export class ForbiddenError extends HttpError {}
export class NotFoundError extends HttpError {}
export class ServerError extends HttpError {}

// The auth response has no access token, or the token can't be decoded.
export class InvalidTokenError extends ApiError {}
