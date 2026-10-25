// Claims of the access token issued by auth-service (`JwtService.generateToken`).
export type AccessTokenClaimsDto = {
  // Telegram user id.
  sub: string
  roles: string[]
  // Issued at / expires at, seconds since the epoch.
  iat: number
  exp: number
}
