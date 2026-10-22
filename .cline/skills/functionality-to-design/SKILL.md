---
name: functionality-to-design
description: Turn requirements into an approval-first library-first JSON design proposal and approved specifications for this Telegram Mini App.
---

# Functionality to design

Follow `design/README.md` and `design/USAGE.md`. Business behavior comes from
referenced `../meta/` documents; approved JSON is authoritative; Penpot is
generated.

## Inspect and propose

Read requirements, tokens, `design/libraries/primevue.library.json`, relevant
custom components/pages, Penpot config, and related Penpot objects when
available. Separate user-facing behavior from backend-only concerns.

For each UI concept classify it as:

1. registered PrimeVue `library-component`;
2. page-local composition of library/structural nodes;
3. recurring domain `custom-component`, with a concrete rationale.

Prefer the earlier category. Minor visual differences never justify a custom
wrapper. Present pages/navigation, information hierarchy, actions,
permissions, states, responsive behavior, tokens, component source, custom
rationales, assumptions, and unresolved questions. Wait for explicit approval.

## Implement an approved proposal

Update in order:

1. PrimeVue registry when a new library control is required;
2. tokens;
3. approved custom component contracts;
4. page specifications.

Use `library-component` and `custom-component` explicitly. Put runtime props in
`props`, behavior in `action`, and representative Penpot selection in
`design.appearance`/`design.state`. Custom composition uses library instances
where applicable and must not contain cycles.

Keep pages under `design/pages/<feature>/<screen>.page.json`, include `$schema`,
stable PascalCase names, requirement sources, and approved assumptions.

Run `python3 scripts/validate-design.py`, fix every error, then use
`penpot-design` if synchronization was requested. Report registry entries,
custom rationales, files, validation, Penpot results, and limitations.