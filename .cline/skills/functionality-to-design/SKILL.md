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

For slot-bearing compositions, assess native rendering feasibility before
promising synchronization. Compare the required tree with live source mains
when available; method existence does not establish operation support. Never
plan to append/insert children into a component copy or its inherited containers,
or reparent inherited descendants out of a copy. New mains need their complete
supported composition assembled before registration and copying; nested copies
remain structurally immutable. If live evidence is unavailable, report feasibility
as unverified, not supported. An incompatible tree requires explicit approval
for a template change, justified domain component, or structural-shell exception;
API restrictions alone do not justify a generic custom wrapper. Follow the native
composition capability gate in `penpot-design` and `design/CONFORMANCE.md` before
any artwork writes. No detached controls or sibling-overlay fallback is implied.

Design Penpot mockups as reference-quality implementation guides rather than
pixel-perfect browser specifications. Make hierarchy, grouping, reading order,
responsive/mobile composition, and relative proportions clear while avoiding
unnecessary exact geometry. Content must remain readable and controls must look
sensible for their context.

When a visual reference is provided, inspect it before proposing the layout,
identify the important hierarchy and proportion cues, and state which cues the
proposal follows. Treat exact pixels and cosmetic browser details as
non-authoritative unless the requirement explicitly says otherwise.

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