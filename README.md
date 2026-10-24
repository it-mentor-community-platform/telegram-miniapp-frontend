# Telegram Mini App Frontend

Vue frontend for the IT Mentor Community Platform Telegram Mini App.

## Technology stack

- Vue 3 and TypeScript
- Vite
- PrimeVue 4 with the Aura theme
- PrimeIcons
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

Start the Vite development server:

```bash
npm run dev
```

Vite prints the local development URL in the terminal. Outside Telegram the app follows the
system light/dark preference, and the "Для разработчиков" panel on the home screen reads init data
from the page's query parameters (for example `/?query_id=…&user=…`).

The home screen uses mocked data (`src/mocks/`) until the backend exposes it. Pick the mocked
user's roles with `VITE_MOCK_ROLES` (comma-separated, default `STUDENT`):

```bash
VITE_MOCK_ROLES=STUDENT,MENTOR,ADMIN npm run dev
```

Project implementations are mocked too (`src/mocks/projects.ts`). Pick a scenario with
`VITE_MOCK_PROJECTS`: `empty`, `java3`, `multi` (default), `java6` or `other`. These match the
states of the `Projects` mockup.

## Validation and production build

Run the TypeScript checks:

```bash
npm run typecheck
```

Create a production build in `dist/`:

```bash
npm run build
```

Preview the production build locally:

```bash
npm run preview
```

## Docker

The Dockerfile builds the Vite application in a Node.js stage and serves the generated `dist/`
directory from nginx.

Build the image:

```bash
docker build -t telegram-miniapp-frontend:local .
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
`--tg-content-safe-area-inset-*`). The home screen's developer panel shows the init data with a
copy-to-clipboard action and does not transmit it. A backend must validate Telegram init data before it
is trusted for authentication or authorization.