# CLAUDE.md

Guidance for Claude Code in this repository.

## Project

Vue 3 + TypeScript frontend for the IT Mentor Community Platform, running as a **Telegram Mini App**.
See `README.md` for the stack, commands and Telegram Web App integration.

- UI library: **PrimeVue 4** with the **Aura** theme (`@primeuix/themes`) and **PrimeIcons**.
  Stay on PrimeVue 4 — PrimeVue 5 has a different license (see `README.md`).
- Platform constraints: phone-width layout; light/dark follows `Telegram.WebApp.colorScheme`;
  respect Telegram safe areas; use Telegram's BackButton for back navigation.
- Auth: send Telegram init data to the backend and use the returned JWT. Outside Telegram, use the
  backend's dummy auth (test environments only).
- Commands: `npm run dev`, `npm run typecheck`, `npm run build`.

## Design reference

UI mockups live in `design/`. Read `design/README.md` first: it explains the file layout, which
mockup is which screen and state, the route map and the PrimeVue component map.

- Treat the mockups as the source of truth for layout, copy (Russian), states and behaviour.
- Implement with PrimeVue components and theme tokens — do not port the mockups' inline styles.
- Use PrimeIcons instead of the mockups' hand-drawn icons.
- Every state listed in `design/README.md` should be reachable and is a test case.
- Routes, route names, project-type slugs, Telegram `startapp` deep-link codes and router mode are
  defined in `design/README.md` → Routes. Student pages live under `/student`; `/mentor` and `/admin`
  are reserved for future roles. Navigate by route name, and build breadcrumbs from route meta.

## Backend API (OpenAPI)

Read the live spec before writing or changing DTOs in `src/api/dto/` or API functions in `src/api/`.
The staging gateway serves them behind basic auth:

- auth-service: `https://staging.platform.zhukovsd.it/api/auth/v3/api-docs`
- project-service: `https://staging.platform.zhukovsd.it/api/project/v3/api-docs`

Fetch with `curl -sf --netrc-file .openapi.netrc.local <url>`. The credentials file is git-ignored
(see `README.md` → Backend API specs); if it is missing, ask the developer for it. Never commit or
echo the credentials.

## Team conventions

Product and system analytics, code style and git flow live in the `meta` repository:
`business-analytics/`, `system-analytics/`, `code-style.md`, `work-and-git-flows.md`.
