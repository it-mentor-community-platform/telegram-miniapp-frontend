# Telegram Mini App Frontend

Vue frontend for the IT Mentor Community Platform Telegram Mini App.

## Technology stack

- Vue 3 and TypeScript
- Vite
- PrimeVue 4 with the Aura theme
- PrimeIcons
- Tailwind CSS 4 with `tailwindcss-primeui` (utilities bound to PrimeVue theme tokens)
- nginx
- Docker

PrimeVue is intentionally pinned to the latest MIT-licensed major version. PrimeVue 5 uses a
different license and should only be adopted after its licensing requirements have been reviewed.

## Prerequisites

- Node.js `^20.19.0` or `>=22.12.0`
- npm
- Docker (optional, for the production container)

## Local development

Install dependencies:

```bash
npm install
```

Start the Vite development server (`local-stack` mode, https):

```bash
npm run dev
```

The app authenticates with Telegram init data, so it only gets past the auth screen inside
Telegram. In a regular browser it shows "Откройте приложение в Telegram" (or, in test
environments, the dummy login below). See [Local testing in Telegram](#local-testing-in-telegram).

Project progress (home card and the projects screen) comes from project-service. The rest of home
(repetition stats, achievements) is still mocked in `src/mocks/` until the backend exposes it.

Project pages (`/student/projects/<project>`) list and submit implementations through
project-service. Deploy links are not stored by the backend yet, so the submit form has no deploy
field.

## Environments

Each environment is a Vite mode with its own committed `.env.<mode>` file:

| Mode | `VITE_API_BASE_URL` | `VITE_TELEGRAM_BOT_USERNAME` | Developer tools |
|---|---|---|---|
| `local-stack` | `http://localhost:8080` | `it_mentor_community_local_bot` | yes |
| `staging` | `https://staging.platform.zhukovsd.it` | `it_mentor_community_staging_bot` | yes |
| `prod` | `https://platform.zhukovsd.it` | `it_mentor_community_bot` | no |

Override a value locally in `.env.<mode>.local` (git-ignored).

With developer tools on (local-stack, staging), opening the app in a regular browser shows a dummy
login form instead of "Откройте приложение в Telegram": enter an auth-service user id (`Users.id`,
not the Telegram id), a username and roles, and the app signs in via `POST /api/auth/by-dummy`.
Nothing is remembered: after a reload or when the 30-minute token expires, sign in again. Prod builds
don't contain the form.

`npm run dev` runs in `local-stack` mode over https and proxies `/api` to `VITE_API_BASE_URL`, so the
app calls its own origin. A built `local-stack` image calls `http://localhost:8080` directly, which
needs the gateway to allow the frontend origin via CORS and expose `X-Access-Token`.

## Local testing in Telegram

Test the Mini App from `npm run dev` against the local stack in Telegram Desktop or
[Telegram Web](https://web.telegram.org) on the same machine. The Mini App runs on the device that
runs Telegram, so `https://localhost:5173` reaches the dev server directly. The dev server uses
[vite-plugin-mkcert](https://github.com/liuweiGL/vite-plugin-mkcert): Telegram only opens https
Mini Apps, and its webview rejects untrusted certificates.

1. **Create your own bot.** In `@BotFather`, send `/newbot` (for example `@itmc_local_<name>_bot`)
   and copy the token. Use a bot of your own: a bot has one Mini App URL, and auth-service only
   accepts init data signed for the bot whose token it runs with.
2. **Point its Mini App at the dev server.** In `@BotFather`, open `/mybots` → your bot → Bot Settings
   → Configure Mini App → Enable Mini App, and enter `https://localhost:5173`. If `localhost` is
   rejected, use `https://127.0.0.1:5173`; the certificate covers both.
3. **Give the token to the local stack.** Add `TELEGRAM_BOT_TOKEN=<token>` to `local-stack/.env`
   (git-ignored) and recreate auth-service with `docker compose up -d auth-service`. Never commit
   the token.
4. **Give the bot name to the frontend.** Create `.env.local-stack.local` with
   `VITE_TELEGRAM_BOT_USERNAME=<your bot username>`.
5. **Run.** Start the local stack, then `npm run dev`. The first run installs a local certificate
   authority into the system trust store and asks for your OS password. Restart Telegram afterwards
   so its webview trusts the new authority.
6. **Open** your bot in Telegram and tap "Open". Hot reload works inside the Mini App.
7. **Grant roles.** The first login creates a user without roles. Grant them on auth-service directly
   (the gateway blocks `/internal`), then reopen the Mini App:

   ```bash
   curl -X POST localhost:8081/api/auth/internal/user -H 'Content-Type: application/json' \
     -d '{"telegram_user_id": <your Telegram id>, "roles": ["STUDENT"]}'
   ```

   Your Telegram id is `user.id` in the init data, shown in the "Для разработчиков" panel.

Init data is valid for 30 minutes. After that, reopen the Mini App; "Попробовать снова" won't help.
To debug, enable Settings → Advanced → Experimental → webview inspecting in Telegram Desktop and use
right-click → Inspect, or use the browser devtools in Telegram Web.

## Validation and production build

Run the TypeScript checks:

```bash
npm run typecheck
```

Create a build in `dist/` (`build` is the `prod` mode):

```bash
npm run build
npm run build:staging
npm run build:local-stack
```

Preview the production build locally:

```bash
npm run preview
```

## Docker

The Dockerfile builds the Vite application in a Node.js stage and serves the generated `dist/`
directory from nginx. The `APP_MODE` build argument picks the Vite mode (default `local-stack`).
CI infers it from the pushed branch: `prod` → `prod`, `staging` → `staging`, any other branch →
`local-stack`.

Build the image:

```bash
docker build --build-arg APP_MODE=staging -t telegram-miniapp-frontend:local .
```

Run the container:

```bash
docker run --rm -p 8080:80 telegram-miniapp-frontend:local
```

Open `http://localhost:8080`.

## Telegram Web App integration

The Telegram Web App SDK is loaded from the official Telegram script in `index.html`. At startup,
the application:

1. detects `window.Telegram.WebApp`;
2. reads `initData`;
3. applies Telegram's light or dark color scheme and follows `themeChanged`;
4. hides the BackButton on the home screen;
5. calls `ready()` and requests the expanded viewport.

Content is padded by Telegram's safe-area insets (`--tg-safe-area-inset-*`,
`--tg-content-safe-area-inset-*`). In test environments the home screen's developer panel shows the
init data with a copy-to-clipboard action and does not transmit it.

## Authentication

On startup the app posts the init data to `POST /api/auth/by-telegram` (auth-service via the
gateway). The body is the raw init data string. The response carries the JWT in the
`X-Access-Token` header. The token is kept in memory and sent in the same header on later API calls.
Roles come from the token's `roles` claim. The user's name comes from Telegram's init data, because
the token has none.

Until authentication succeeds, the app shell shows a spinner or an auth error screen instead of the
route. The URL is kept, so the target page opens once a retry succeeds:

- Empty init data (opened outside Telegram): "Откройте приложение в Telegram".
- Init data rejected or backend unreachable: "Не удалось войти", with a retry button.

API code lives in `src/api/`: DTO types, fetch functions, and the `ApiError` subclasses failed calls
reject with.

## Backend API specs

The staging gateway serves the OpenAPI specs behind basic auth:

- auth-service: `https://staging.platform.zhukovsd.it/api/auth/v3/api-docs`
- project-service: `https://staging.platform.zhukovsd.it/api/project/v3/api-docs`

Get the credentials from the team and put them in `.openapi.netrc.local` (git-ignored). Never
commit them:

```
machine staging.platform.zhukovsd.it login <username> password <password>
```

Then fetch a spec:

```bash
curl -sf --netrc-file .openapi.netrc.local https://staging.platform.zhukovsd.it/api/auth/v3/api-docs
```