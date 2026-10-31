import axios, { isAxiosError } from 'axios'
import type { ErrorResponseDto } from './dto/error'
import {
  BadRequestError,
  ConflictError,
  ForbiddenError,
  HttpError,
  NetworkError,
  NotFoundError,
  ServerError,
  UnauthorizedError,
} from './errors'

// The gateway reads the access token from this header, without a "Bearer" prefix.
export const ACCESS_TOKEN_HEADER = 'X-Access-Token'

let accessTokenProvider: () => string | undefined = () => undefined
let unauthorizedHandler: () => void = () => {}

// The app tells the client where to take the token from, so this package holds no session state.
export function setAccessTokenProvider(provider: () => string | undefined) {
  accessTokenProvider = provider
}

// Called when a request that carried an access token gets 401, i.e. the token has expired.
export function setUnauthorizedHandler(handler: () => void) {
  unauthorizedHandler = handler
}

export const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 15_000,
})

client.interceptors.request.use((config) => {
  const token = accessTokenProvider()
  if (token) {
    config.headers.set(ACCESS_TOKEN_HEADER, token)
  }
  return config
})

client.interceptors.response.use(undefined, (error: unknown) => {
  // A 401 without a token (the auth request itself) is a failed login, not an expired session.
  if (
    isAxiosError(error) &&
    error.response?.status === 401 &&
    error.config?.headers.has(ACCESS_TOKEN_HEADER)
  ) {
    unauthorizedHandler()
  }
  return Promise.reject(toApiError(error))
})

function toApiError(error: unknown) {
  if (!isAxiosError(error)) {
    return error
  }
  if (!error.response) {
    return new NetworkError(error.message, { cause: error })
  }

  const { status, data } = error.response
  const body = isErrorResponse(data) ? data : undefined
  const options = { cause: error }
  if (status === 400) return new BadRequestError(status, body, options)
  if (status === 401) return new UnauthorizedError(status, body, options)
  if (status === 403) return new ForbiddenError(status, body, options)
  if (status === 404) return new NotFoundError(status, body, options)
  if (status === 409) return new ConflictError(status, body, options)
  if (status >= 500) return new ServerError(status, body, options)
  return new HttpError(status, body, options)
}

function isErrorResponse(data: unknown): data is ErrorResponseDto {
  return typeof data === 'object' && data !== null && 'message' in data
}
