# Design — Telegram Mini App mockups

UI mockups for the IT Mentor Community Platform Telegram Mini App. They are the reference for
layout, copy, states and behaviour when implementing screens in this repo.

- **Live canvas:** https://claude.ai/artifact/GVdyfc2VDGd72PA8iAnKbg (Claude Design canvas, private
  to the owner until shared)
- **Specs the mockups are based on:** `meta/business-analytics/functionality/`
  (`interview-questions-interval-repetition.md`, `student-roadmap-completion.md`)

## Files

| File | What it is |
|---|---|
| `canvas.json` | Canvas layout: which screens exist, their position and frame size, titles, section headings |
| `*.dc.html` | One screen, screen state or shared component per file — HTML template + a small logic class |
| `Components.dc.html` | Catalogue of all shared components and their variants |

The `.dc.html` files only render inside the Claude Design canvas editor (they depend on its
runtime). Opening them directly in a browser will not show the design. In this repo they are for
history, review and as a readable spec.

### Base screens and states

Each section has **base screens** that hold the full markup. A base screen takes a `scenario`
(or `start`) prop; **state files** are thin wrappers that render the base screen in one specific
state via `<dc-import>`. Change a base screen and every state of it changes too.

| Base screen | State files (scenario) |
|---|---|
| `Projects.dc.html` (nothing submitted) | `Projects-Java3` (Java 3/6), `Projects-Multi` (Java/Python/Go + C#), `Projects-Java6` (roadmap complete), `Projects-Other` (only C# and Rust), `Projects-Loading` (first load, skeletons), `Projects-Error` (load failed, retry) |
| `ProjectType.dc.html` (Hangman, first submission, nothing filled in → «Сдать проект» disabled) | `ProjectType-Empty` (Currency Exchange, first submission), `ProjectType-List` (3 implementations), `ProjectType-AddOther` (new implementation, other language "Rust"), `ProjectType-Duplicate` (repository already registered), `ProjectType-Loading` (first load: form shown, status and list are skeletons), `ProjectType-LoadError` (implementations failed to load: form stays, retry in place of the list), `ProjectType-Submitting` (request in flight), `ProjectType-SubmitError` (server / network error on submit), `ProjectType-InvalidUrl` (GitHub and deploy URLs fail validation), `ProjectType-Submitted` (first implementation just submitted), `ProjectType-SubmittedMore` (another implementation added to a list of 3), `ProjectType-NotFound` (unknown slug) |
| `Implementation.dc.html` (Currency Exchange, deploy + 2 reviews) | `Impl-Hangman` (no reviews, no deploy section), `Impl-NoDeploy`, `Impl-EditGithub`, `Impl-GithubTaken` (new URL already in use), `Impl-EditDeploy` |
| `Review.dc.html` (question) | `Review-Answer` (answer revealed), `Review-Done` (session summary) |
| `AuthError.dc.html` (opened outside Telegram) | `AuthError-Failed` (Telegram login rejected or backend unavailable), `AuthError-Expired` (session expired) |
| `DevLogin.dc.html` (dummy login, empty form) | `DevLogin-Filled` (valid values, «Войти» enabled), `DevLogin-Loading` (request in flight), `DevLogin-NotFound` (404 on the ID field), `DevLogin-Error` (400 / 500 / network), `DevLogin-Expired` (dummy session ran out) |

Every screen has a `dark` prop (light/dark mode).
`Main` has no state files; its `projects` prop («Загружено» / «Загрузка» / «Ошибка») switches the «Мои проекты» card between loaded, skeleton and error.

## Screen map

Routes (see [Routes](#routes)) and the PrimeVue components each mockup maps to.

| Mockup | Route | Main PrimeVue components |
|---|---|---|
| `Main` — home, section launcher | `/` | `Avatar`, `Tag`, `Card`, `ProgressBar`; «Мои проекты» card: `Skeleton` while loading, muted text line on error |
| `Repetition` — my topics | `/student/repetition` | `Breadcrumb`, `Card`, `ProgressBar`, `Button` |
| `Categories` — all topics | `/student/repetition/topics` | `Breadcrumb`, `IconField` + `InputText`, `SelectButton`, `ToggleButton` |
| `Topic` — one topic, questions and answers | `/student/repetition/topics/:topicId` | `Breadcrumb`, `Tag`, `Button`, `Accordion` |
| `Review` — review session | `/student/repetition/review` | `ProgressBar`, `Tag`, `Button` |
| `Stats` — statistics | `/student/repetition/stats` | `Breadcrumb`, `MeterGroup`, `Card` |
| `Projects` — my projects | `/student/projects` | `Breadcrumb`, `Card`, `Tag`; `Skeleton` (loading), `Message` `severity="error"` + `Button` «Попробовать снова» (load failed) |
| `ProjectType` — project page | `/student/projects/:projectType` | `Breadcrumb`, `Button`, `SelectButton`, `InputText`, `Message`; `Skeleton` (loading); `Message` `severity="error"` + `Button` «Попробовать снова» (load failed); `Button` `:loading` + `:disabled` (submit); `Message` `severity="error"` above the button (submit failed); `Message` `severity="error"` `variant="simple"` `size="small"` under a field (validation, duplicate) + `invalid` on `InputText`; `Message` `severity="success"` `closable` (submitted) |
| `Implementation` — implementation page | `/student/projects/:projectType/implementations/:implementationId` | `Breadcrumb`, `InputText`, `Button`, `Message`, `Avatar` |
| `DevLogin` — dummy login (test env, browser) | — (auth screen, replaces any route) | `Card`, `Tag` (`severity="warn"`, «Тестовое окружение»), `InputNumber` (`:min="1"`, `:useGrouping="false"`), `InputGroup` + `InputGroupAddon` («@») + `InputText`, `SelectButton` (`multiple`) for roles, `Button` (`:loading`), `Message` |

Blocks PrimeVue does not cover are shared components — see [Components](#components).

### Project progress data

`Projects` and `Main`'s «Мои проекты» card read `GET /api/project/projects/my/summary` (students
only; for other roles the card stays as it is). Loaded once per screen visit.

- **Loading** — only on the very first load; later visits show the last data while it refreshes.
  `Projects-Loading`: breadcrumbs and title render normally; a skeleton progress card (two
  RoadmapProgress-shaped bars + the note) and the real «Проекты роадмапа» list — icons and titles
  are known up front, only each row's «Сдан / Не сдан» line is a `Skeleton` (`ProjectRow`
  `status="loading"`), so nothing jumps when data arrives. `Main` (`projects="Загрузка"`): two
  skeleton rows in place of the compact RoadmapProgress bars.
- **Failed** (any error except 401, which shows `AuthError-Expired`) — `Projects-Error`: error
  `Message` with «Не удалось загрузить проекты. Проверьте соединение и попробуйте ещё раз.» and
  «Попробовать снова» in place of the progress card; the project list stays (titles and grey icons,
  no status line — `ProjectRow` `status="unknown"`) so project pages remain reachable. `Main`
  (`projects="Ошибка"`): one muted line «Не удалось загрузить прогресс» with an «Открыть» hint —
  the whole card is the link to `Projects`, where the retry lives.
- project-service also returns `WEATHER_VIEWER` and `OTHER`; they are not part of the six-project
  roadmap and are ignored (not listed, not counted).

### Project page data

`ProjectType` reads the student's implementations of that project type and submits new ones
(`POST`, body: language, GitHub URL, optional deploy URL).

> **Not implemented yet:** project-service doesn't store deploy URLs. Until it does, the app
> sends only language and GitHub URL, has no «Ссылка на деплой» field and shows no deploy line in
> «Мои реализации». The mockups keep them as the target design.

- **Loading** — first load only. `ProjectType-Loading`: only the implementations list and the
  status derived from it need the request; everything else is known from the route and renders
  normally — breadcrumbs, title, «Проект N из 6», spec links and the submit form, open. The «Сдан
  на …» status is a `Skeleton`, and a two-row skeleton «Мои реализации» list sits where the list
  goes. When the list arrives and is non-empty, the form collapses to «Добавить реализацию» — unless
  the user has already started filling it in.
- **Load failed** (any error except 401 → `AuthError-Expired`) — `ProjectType-LoadError`: only
  the implementations list depends on the request, so everything else renders: breadcrumbs, title,
  «Проект N из 6» (without the «Сдан на …» status, which comes from the list), spec links and the
  submit form, open. An error `Message` «Не удалось загрузить реализации. Проверьте соединение и
  попробуйте ещё раз.» + «Попробовать снова» takes the place of «Мои реализации» (same block as
  `Projects-Error`). Submitting still works — the backend rejects a duplicate repository (409) as usual.
- **Submit disabled** — «Сдать проект» is disabled until a language is picked (and named, for
  «Другой») and the GitHub URL is not empty; a muted hint under it says what is missing
  («Выберите язык и укажите ссылку на репозиторий»). Format is checked on submit, not while typing.
- **Validation** (client-side, on submit) — `ProjectType-InvalidUrl`: GitHub URL must match
  `https://github.com/<owner>/<repo>` (allow a trailing `/` or `.git`) → «Укажите ссылку вида
  https://github.com/username/repo»; deploy URL, if filled, must start with `https://` → «Укажите
  ссылку, начинающуюся с https://». Inline error under the field (same style as the duplicate
  error), red border, `aria-invalid`. Errors clear when the field is edited.
- **Submitting** — `ProjectType-Submitting`: «Сдать проект» shows a spinner (`Button :loading`),
  all inputs, the language picker and «Отмена» are disabled.
- **Submit failed** — duplicate repository (409) → inline error on the GitHub field
  (`ProjectType-Duplicate`). Any other error (500 / network) → `ProjectType-SubmitError`: error
  `Message` «Не удалось сдать проект. Попробуйте ещё раз.» above the button; entered values stay;
  pressing the button again retries.
- **Submitted** — the form closes; a closable success `Message` appears in its place (inline rather
  than a `Toast`: it stays until dismissed or the page is left, doesn't overlap Telegram's header,
  and sits where the user was looking). Text: «Проект сдан» (first implementation) or «Реализация
  добавлена», plus «Реализация на Go засчитана в прогресс Go Backend.» (for languages outside the
  roadmap: «…В прогресс роадмапов она не попадает.»). The new implementation is inserted at the top
  of «Мои реализации» with a light-green background that fades out after ~2 s; the header status
  updates (`ProjectType-Submitted`: «Ещё не сдан» → «Сдан на Java»; `ProjectType-SubmittedMore`:
  → «Сдан на Java, Python и Go»). Use the response body, no refetch. Invalidate the cached
  `my/summary` so `Projects` / `Main` show the new progress.

### Developer panel (home, test environments only)

The bottom of `Main` has a collapsible **"Для разработчиков"** panel carried over from the starter
`App.vue`: Telegram/browser status tag, read-only init data, and a copy-to-clipboard button with
"Скопировано" feedback (button disabled when there is no init data). Render it only in test environments (e.g. behind a
`VITE_SHOW_DEV_TOOLS` flag) — never in production. `Main`'s `devPanel` prop shows it hidden /
collapsed / expanded; `inTelegram` switches the status. PrimeVue: `Panel` (toggleable) or a
`Button` + `Textarea` (readonly), `Tag`, `Button`.

## Authentication screens

Shown by the app shell **instead of any route** when the user can't be authenticated; the URL is
left unchanged so the target page opens once the problem is fixed. Not a route of its own.

| Case | When | Screen |
|---|---|---|
| Opened outside Telegram | `window.Telegram.WebApp.initData` is empty (regular browser, link opened outside the Mini App) | `AuthError` — explains the app only works inside Telegram; primary "Открыть в Telegram", secondary "Нет Telegram? Установить" |
| Login failed | Backend rejects the init data (invalid / expired) or the auth request fails | `AuthError-Failed` — "Попробовать снова" retries the auth request; secondary link to the community chat |
| Session expired | Any API call returns 401 after a successful login (token older than 30 min) | `AuthError-Expired` — asks to close and reopen the app; primary «Закрыть приложение», secondary link to the community chat |
| Dummy login (test env, browser) | init data is empty **and** the environment is local stack or staging | `DevLogin` — replaces `AuthError`. Form: user ID, Telegram username, roles → `POST /api/auth/by-dummy` `{ user_id, roles, telegram_username }`. States: `DevLogin-Filled`, `-Loading`, `-NotFound` (404 → «Пользователь с ID 42 не найден» on the ID field), `-Error` (400 / 500 / network → server text or «Сервер недоступен. Попробуйте ещё раз.» above the button), `-Expired` (a dummy session hit 401 → back to this form with «Сессия истекла — войдите снова»). |

- "Открыть в Telegram" links to the bot's main Mini App (`https://t.me/<bot>?startapp`). The bot is
  per environment (`VITE_TELEGRAM_BOT_USERNAME`). Planned: a `startapp` code for the current path
  (see [Telegram deep links](#telegram-deep-links)), so the user lands on the same page.
- **Production** always shows `AuthError` outside Telegram; `DevLogin` must not exist in prod
  builds. **Inside Telegram** nothing changes in any environment: init data is present, so the
  normal Telegram login runs and `DevLogin` never appears.
- `DevLogin` details: «Telegram username» has a fixed «@» prefix and is sent without it (a pasted
  leading «@» is stripped). Roles are a multi-select (at least one); the session gets exactly these
  roles, regardless of the user's real roles. «Войти» stays disabled until ID ≥ 1, username and at
  least one role are set. Secondary «Открыть в Telegram» is the normal way in. On desktop browsers
  the screen is a centred 390 px column.
- The old `AuthError` `devHint` prop (dashed developer hint) is superseded by `DevLogin` — don't
  implement it.
- PrimeVue: `Button`, `Message` is not needed — this is a full-screen state.

## Routes

### Structure

- `/` — home, shared by all roles.
- `/student/...` — student functionality (everything designed so far). Mentor and admin
  functionality will get their own prefixes (`/mentor/...`, `/admin/...`) — reserve them.
- Nesting mirrors the breadcrumbs: each route's parent is its breadcrumb parent, so breadcrumbs are
  generated from the matched route records (`meta.breadcrumb`), never hand-written per page. Role
  prefixes are not breadcrumb levels — the trail always starts with the home icon.

| Route | Name | Screen | Breadcrumb trail |
|---|---|---|---|
| `/` | `home` | Главная | — |
| `/student/repetition` | `student-repetition` | Повторение | 🏠 |
| `/student/repetition/topics` | `student-repetition-topics` | Все темы | 🏠 › Повторение |
| `/student/repetition/topics/:topicId` | `student-repetition-topic` | Тема | 🏠 › Повторение › Все темы |
| `/student/repetition/review` | `student-repetition-review` | Review session (`?topic=:topicId` = one topic; none = all) | none (close button only) |
| `/student/repetition/stats` | `student-repetition-stats` | Статистика | 🏠 › Повторение |
| `/student/projects` | `student-projects` | Мои проекты | 🏠 |
| `/student/projects/:projectType` | `student-project` | Project page | 🏠 › Мои проекты |
| `/student/projects/:projectType/implementations/:implementationId` | `student-implementation` | Implementation page | 🏠 › Мои проекты › {project name} |

Use route **names** in code (`{ name: 'student-project', params: { projectType } }`), not
hard-coded paths, so prefixes can change without touching screens. A `/student` route record
without its own page (redirect to `/`) groups the children and is the natural place for a role
guard.

### Parameters

- `:projectType` — fixed readable slugs (the six project types are a fixed list):
  `hangman`, `simulation`, `currency-exchange`, `tennis-scoreboard`, `cloud-storage`,
  `task-scheduler`. Unknown slug → not-found screen (`ProjectType-NotFound`): resolved
  client-side from the fixed list, before any request; breadcrumbs (Главная › Мои проекты), a
  «Проект не найден» message and a «К моим проектам» button. The URL stays as typed (no redirect),
  so Telegram's back button still works. Reuse the same layout for an unknown `:implementationId`
  (backend 404).
- `:topicId`, `:implementationId` — backend IDs.
- An implementation whose `:projectType` does not match its actual type → redirect to the canonical URL.

### Telegram deep links

Bot messages open screens via `https://t.me/<bot>/<app>?startapp=<param>`. Telegram allows only
`A–Z a–z 0–9 _ -` and ≤ 512 characters in `startapp`, so it is a short code mapped to a route on
startup (read from the launch params, then `router.replace`):

| `startapp` | Opens |
|---|---|
| *(empty)* | `/` |
| `review` | `/student/repetition/review` (all topics) |
| `review_<topicId>` | `/student/repetition/review?topic=<topicId>` |
| `topic_<topicId>` | `/student/repetition/topics/<topicId>` |
| `projects` | `/student/projects` |
| `project_<projectType>` | `/student/projects/<projectType>` |
| `impl_<implementationId>` | the implementation page (type resolved from the API) |
| anything unknown | `/` |

### Router mode

Use HTML5 history mode (`createWebHistory`), not hash mode: Telegram passes its launch data in the
URL fragment (`#tgWebAppData=…`), which conflicts with hash routing. Read the launch params (init
data, `startapp`) before the router starts. nginx must fall back to `index.html` for all app paths.

## Components

Shared blocks that PrimeVue does not provide. In the design each is its own file, imported by the
screens with `<dc-import>`; `Components.dc.html` is a catalogue showing every variant. In the app
each becomes **one Vue component** in `src/components/`, built from PrimeVue components where
possible and styled with theme tokens and Tailwind utilities (see `CLAUDE.md` → Styling), so it
follows Aura and dark mode. Props below are the design's props — keep the same names in Vue.

| Component | Props | Behaviour / notes | Used on |
|---|---|---|---|
| `RoadmapProgress` | `label: string`, `steps: boolean[6]`, `compact?: boolean` | One segment per project type, filled when that type has ≥1 implementation in the track's language. Shows "N из 6 проектов" (`compact`: "N из 6"). Parent hides tracks with 0/6. Screen readers: "Java Backend: сдано 3 из 6 проектов". | Main, Projects |
| `StatTiles` | `items: { value, label, tone: 'warn' \| 'info' \| 'success' \| 'neutral' }[]` (3 items) | Three equal tiles. `warn` = due for review, `info` = new, `success` = learned, `neutral` = plain count. | Main, Repetition, Topic |
| `NavListRow` | `icon`, `title`, `subtitle`, `badge?`, `badgeTone?: 'success' \| 'neutral'`, `href`, `divider?` | Whole row is a link (router-link), ≥64 px tall. `divider` draws the top border between rows. Badge renders a PrimeVue `Tag`. | Main |
| `ProjectRow` | `icon: 'hangman' \| 'simulation' \| 'exchange' \| 'tennis' \| 'cloud' \| 'planner'`, `title: string`, `langs: { name, counted }[]`, `href`, `divider?`, `status?: 'loaded' \| 'loading' \| 'unknown'` | One roadmap project in the "Мои проекты" list. Whole row is a link to the project page. Each project type has its own icon (gallows, sprout, swap arrows, tennis ball, cloud, calendar-check); the icon tile is filled when the project has ≥1 implementation in any language. Shows "Сдан" + a `LanguageTag` per language, or "Не сдан". In the app: `ProjectIcon`, the mockup SVGs (PrimeIcons has no equivalents). `status="loading"`: status line is a `Skeleton`; `"unknown"` (load failed): no status line, grey icon. | Projects |
| `LanguageTag` | `label: string`, `counted: boolean` | Solid when the language counts toward roadmap progress (Java, Python, Go); dashed outline + aria "не учитывается в прогрессе" otherwise. | Projects |
| `EmptyState` | `title`, `text`, `icon: 'info' \| 'chat' \| 'none'` | Card used for "nothing here yet" and explanatory notices. | Projects, Implementation |
| `Breadcrumbs` | `items: { label, href }[]` | Home icon + items; current page is not repeated (the page title follows). Last item truncates with ellipsis. In the app: wrap PrimeVue `Breadcrumb` and build items from route meta. | Every screen below home except the review session |
| `ActivityHeatmap` | `days: { date, count }[]` | 53 weeks × 7 days, 5 levels (0, 1–9, 10–19, 20–29, 30+). Opens scrolled to the latest weeks; day tooltip shows the count. | Stats |

Suggested dev aid: a dev-only `/dev/components` route that renders each component's variants (same
as `Components.dc.html`) — a quick visual check in PRs without adding Storybook.

## Component decisions

Choices made up front so every screen (and every contributor) builds them the same way.

| Pattern | Decision |
|---|---|
| Language / specialization choice (Java · Python · Go · Другой, Все · Java · …) | PrimeVue `SelectButton` |
| Topic add/remove toggle on "Все темы" | PrimeVue `ToggleButton` (on: "На повторении", off: "Добавить") |
| Questions with expandable answers | PrimeVue `Accordion`, one panel open at a time |
| Inline edit of GitHub / deploy links | Custom view ⇄ edit toggle with `InputText` + `Button`s — **not** `Inplace` (it can't show "current link + draft + error" together) |
| Inline field errors | Field invalid state + small error text under the field (PrimeVue `Message` with `variant="simple"`, `severity="error"`) |
| Notices inside forms (e.g. "won't count toward progress") | Muted helper text with an info icon, not a `Message` box |
| Stacked learned / in progress / new bar | PrimeVue `MeterGroup` |
| Single progress bars (topic learned %, review session) | PrimeVue `ProgressBar` (`:showValue="false"`, thin) |
| Primary actions "Повторить всё", "Сдать проект" | **Open — recommended:** in-page PrimeVue `Button` for now; revisit Telegram `MainButton` once the app shell exists |
| Back navigation | Telegram `BackButton` + `Breadcrumbs` |
| Multi-choice from a short fixed list (dummy-login roles) | PrimeVue `SelectButton` with `multiple` — same look as single-choice `SelectButton`, checkmark on selected items |
| Icons | PrimeIcons only, except project-type icons (`ProjectIcon`) |

## Design conventions

- **Platform:** Telegram Mini App. Frames are 390 px wide (phone). Telegram's own header is not drawn.
  Light/dark follows Telegram's color scheme.
- **Look:** PrimeVue 4 Aura — Inter, emerald primary, slate surfaces (zinc in dark mode), 12 px card
  radius. Primary buttons use a darker emerald than Aura's default (`#047857` in light mode) so white
  text meets WCAG AA contrast; in dark mode `#34d399` with dark text.
- **Copy:** Russian. Example data is illustrative, not real.
- **Navigation:** breadcrumbs on every screen below home (the home icon links to `/`); the review
  session has none — only a close (X) button. Telegram's BackButton is expected alongside.
- **Icons:** the mockups use hand-drawn stroke icons; the app should use the closest PrimeIcons.
  Exception: project-type icons, which have no PrimeIcons equivalent, are ported as SVGs (`ProjectIcon`).
- **Implementation:** build with PrimeVue components and theme tokens — do not port the mockups'
  inline styles.

## Workflow (keeping repo and canvas in sync)

The repo is the source of truth; the canvas is a preview of whatever is checked out. Mapping:
`design/<file>` in the repo = `project/<file>` in the canvas.

- **Design changes requested from Claude:** Claude updates both this folder and the canvas. Review
  the diff and commit.
- **Edits made directly in the canvas editor:** ask Claude to *save canvas to repo* before
  committing or switching branches — otherwise the next sync overwrites them.
- **Files edited by hand, branch switched or changes pulled:** ask Claude to *sync canvas from repo*.
- To compare a branch side by side, Claude can publish it to a separate canvas instead.

The canvas also keeps its own linear version history (no branches), so an overwritten state can be
recovered from there.

## Open questions

- Mapping of the 4 self-rating buttons to SM-2 grades (0–5); intervals shown on the buttons are examples.
- How many successful repetitions make a question "learned" (`[N]` placeholder on `Stats`).
- Whether "Повторить всё" / "Сдать проект" become Telegram's MainButton instead of in-page buttons
  (see Component decisions).
- Spec links on the project page currently point to each roadmap's root, not the project's page.
