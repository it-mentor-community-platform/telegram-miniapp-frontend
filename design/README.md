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
| `*.dc.html` | One screen (artboard) per file — HTML template + a small logic class |

The `.dc.html` files only render inside the Claude Design canvas editor (they depend on its
runtime). Opening them directly in a browser will not show the design. In this repo they are for
history, review and as a readable spec.

### Base screens and states

Each section has **base screens** that hold the full markup. A base screen takes a `scenario`
(or `start`) prop; **state files** are thin wrappers that render the base screen in one specific
state via `<dc-import>`. Change a base screen and every state of it changes too.

| Base screen | State files (scenario) |
|---|---|
| `Projects.dc.html` (nothing submitted) | `Projects-Java3` (Java 3/6), `Projects-Multi` (Java/Python/Go + C#), `Projects-Java6` (roadmap complete), `Projects-Other` (only C# and Rust) |
| `ProjectType.dc.html` (Hangman, first submission) | `ProjectType-Empty` (Currency Exchange, first submission), `ProjectType-List` (3 implementations), `ProjectType-AddOther` (new implementation, other language "Rust"), `ProjectType-Duplicate` (repository already registered) |
| `Implementation.dc.html` (Currency Exchange, deploy + 2 reviews) | `Impl-Hangman` (no reviews, no deploy section), `Impl-NoDeploy`, `Impl-EditGithub`, `Impl-GithubTaken` (new URL already in use), `Impl-EditDeploy` |
| `Review.dc.html` (question) | `Review-Answer` (answer revealed), `Review-Done` (session summary) |

Every screen has a `dark` prop (light/dark mode).

## Screen map

Suggested routes and the PrimeVue components each mockup maps to.

| Mockup | Route | Main PrimeVue components |
|---|---|---|
| `Main` — home, section launcher | `/` | `Avatar`, `Tag`, `Card`, `ProgressBar` |
| `Repetition` — my topics | `/repetition` | `Breadcrumb`, `Card`, `ProgressBar`, `Button` |
| `Categories` — all topics | `/repetition/topics` | `Breadcrumb`, `IconField` + `InputText`, `SelectButton`, `Button` (toggle) |
| `Topic` — one topic, questions and answers | `/repetition/topics/:id` | `Breadcrumb`, `Tag`, `Button`, `Accordion` |
| `Review` — review session | `/repetition/review` (`?topic=:id` for one topic) | `ProgressBar`, `Tag`, `Button` |
| `Stats` — statistics | `/repetition/stats` | `Breadcrumb`, `MeterGroup`, `Card` |
| `Projects` — my projects | `/projects` | `Breadcrumb`, `Card`, `Tag` |
| `ProjectType` — project page | `/projects/:type` | `Breadcrumb`, `Button`, `SelectButton`, `InputText`, `Message` |
| `Implementation` — implementation page | `/projects/implementations/:id` | `Breadcrumb`, `InputText`, `Button`, `Message`, `Avatar` |

Not covered by PrimeVue (custom components): the 6-segment roadmap progress bar, the 365-day
activity heatmap, and the icon + two-line + chevron list rows (styled router links).

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
- Whether "Повторить всё" / "Сдать проект" become Telegram's MainButton instead of in-page buttons.
- Spec links on the project page currently point to each roadmap's root, not the project's page.
