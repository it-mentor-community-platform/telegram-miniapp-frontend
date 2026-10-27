// Backend API: DTO types, fetch functions and the errors they reject with.
export { setAccessTokenProvider, setUnauthorizedHandler } from './client'
export { authenticateByDummy, authenticateByTelegram, type AccessToken } from './auth'
export type { DummyAuthRequestDto } from './dto/auth'
export type { AccessTokenClaimsDto } from './dto/token'
export type { ErrorResponseDto } from './dto/error'
export {
  ApiError,
  BadRequestError,
  ForbiddenError,
  HttpError,
  InvalidTokenError,
  NetworkError,
  NotFoundError,
  ServerError,
  UnauthorizedError,
} from './errors'
