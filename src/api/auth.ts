import type { AxiosResponse } from 'axios'
import { jwtDecode } from 'jwt-decode'
import { ACCESS_TOKEN_HEADER, client } from './client'
import type { DummyAuthRequestDto, TelegramAuthRequestDto } from './dto/auth'
import type { AccessTokenClaimsDto } from './dto/token'
import { InvalidTokenError } from './errors'

export type AccessToken = {
  raw: string
  claims: AccessTokenClaimsDto
}

// Exchanges Telegram init data for an access token, which auth-service returns in a header.
// Rejects with BadRequestError when the init data is invalid or expired.
export async function authenticateByTelegram(initData: string): Promise<AccessToken> {
  const response = await client.post<void>('/api/auth/by-telegram', {
    initDataRaw: initData,
  } satisfies TelegramAuthRequestDto)
  return readAccessToken(response)
}

// Test environments only: issues a token for any existing user with the given roles.
// Rejects with NotFoundError for an unknown user id, BadRequestError for unknown roles.
export async function authenticateByDummy(request: DummyAuthRequestDto): Promise<AccessToken> {
  const response = await client.post<void>('/api/auth/by-dummy', request)
  return readAccessToken(response)
}

function readAccessToken(response: AxiosResponse): AccessToken {
  const raw = response.headers[ACCESS_TOKEN_HEADER.toLowerCase()]
  if (typeof raw !== 'string' || raw === '') {
    throw new InvalidTokenError(`Response has no ${ACCESS_TOKEN_HEADER} header`)
  }
  return parseAccessToken(raw)
}

// Also restores a token kept from an earlier session. Rejects with InvalidTokenError if malformed.
export function parseAccessToken(raw: string): AccessToken {
  return { raw, claims: decodeClaims(raw) }
}

// Reads the claims without verifying the signature; the gateway verifies the token.
function decodeClaims(raw: string): AccessTokenClaimsDto {
  try {
    const claims = jwtDecode<Partial<AccessTokenClaimsDto>>(raw)
    return { sub: claims.sub ?? '', roles: claims.roles ?? [], iat: claims.iat ?? 0, exp: claims.exp ?? 0 }
  } catch (error) {
    throw new InvalidTokenError('Access token cannot be decoded', { cause: error })
  }
}
