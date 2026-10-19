# UI design workflow

This guide explains how team members turn business-analysis documents into
approved JSON design specifications and generated Penpot layouts.

## Workflow overview

```text
Business-analysis document
          ↓
Design proposal and questions
          ↓
Team review and explicit approval
          ↓
JSON design specifications
          ↓
Penpot synchronization
          ↓
Structural and visual review
```

The workflow deliberately separates discussion from implementation. Cline must
not modify design JSON or Penpot while the proposal is still under discussion.

## Prerequisites

1. Open `it-mentor-community-platform.code-workspace` in VS Code.
2. Ensure `telegram-miniapp-frontend` is the first (primary) workspace folder.
3. Install and configure Cline.
4. Enable the repository skills shown by Cline:
   - `/functionality-to-design`
   - `/penpot-design`
   - `/design-review`
5. Configure and authenticate the Penpot MCP server.
6. Use a vision-capable model when a screenshot is part of the request.

The business requirements are stored in the `meta` workspace folder. Design
specifications are stored in this repository under `design/`.

## Create a design from business requirements

Start the workflow and reference one or more requirement documents:

```text
/functionality-to-design

Use:
@meta/business-analytics/functionality/user-profiles.md

Design the public user profile page for the Telegram Mini App. Start with a
mobile layout. Do not create files or Penpot objects before I approve the
proposal.
```

Cline will inspect the requirement, related documents when necessary, existing
tokens, components, pages, and relevant Penpot objects. It will then propose:

- users and their goals;
- pages and navigation;
- information hierarchy;
- actions and permissions;
- reusable components;
- loading, empty, success, and error states;
- assumptions and unresolved product questions.

Backend-only requirements should be identified but should not automatically
become UI elements.

## Review and revise the proposal

Give concrete feedback before approval. For example:

```text
Move achievements above projects. Show three achievements in the collapsed
state. Use separate tabs for projects and reviews.
```

If feedback materially changes the structure or behavior, Cline should present
the revised proposal and wait for approval again.

## Approve the design

Approval must be explicit. For example:

```text
Approved. Create the JSON specifications under
@telegram-miniapp-frontend/design/ and synchronize the page to Penpot.
```

These are not explicit approvals:

```text
Looks interesting.
Probably fine.
```

After approval, Cline may update tokens, components, and pages, then synchronize
the approved result to Penpot.

## Use screenshots

You can paste or attach an image in Cline. Permanent references should be added
to `design/references/` and committed when licensing and privacy permit it.

Example:

```text
/functionality-to-design

Use:
@meta/business-analytics/functionality/user-profiles.md
@telegram-miniapp-frontend/design/references/public-profile-reference.png

Use the screenshot for visual direction, but reuse our existing tokens and
components. Discuss the design before creating anything.
```

Screenshots are references, not a source of business behavior or approved UI
structure. Cline must not infer hidden functionality from an image.

## Synchronize an existing page

Use the Penpot skill when the JSON is already approved:

```text
/penpot-design

Synchronize
@telegram-miniapp-frontend/design/pages/user-profile.page.json with Penpot.
Update the existing Page/UserProfile frame and do not create duplicates.
```

The same command should be safe to run repeatedly. A second run must update the
same generated objects rather than append copies.

## Review without modifying

Use the review skill for a read-only consistency check:

```text
/design-review

Review:
@meta/business-analytics/functionality/user-profiles.md
@telegram-miniapp-frontend/design/pages/user-profile.page.json

Compare them with Page/UserProfile in Penpot. Do not modify anything.
```

The review should distinguish:

- business requirement coverage;
- approved assumptions;
- JSON validity and reference integrity;
- Penpot structural consistency;
- visual differences that require manual inspection.

## Validate design JSON

Run from the `telegram-miniapp-frontend` repository root:

```bash
python3 scripts/validate-design.py
```

The validator checks JSON syntax, supported structures, duplicate names, token
references, component references, component variants, and requirement source
paths.

## Expected completion report

After implementation or synchronization, Cline should report:

- requirement documents used;
- approved assumptions;
- JSON files created or changed;
- tokens and components created or reused;
- Penpot objects created or modified;
- verification results;
- unsupported operations and remaining differences.

## Team responsibilities

- A business analyst or product owner confirms behavior and assumptions.
- A designer or reviewer confirms information hierarchy and visual direction.
- The workflow operator gives explicit approval and reviews generated output.
- Cline updates JSON first, synchronizes Penpot, and reports limitations.
- Contributors commit design specifications together with relevant frontend
  changes whenever possible.

## Safety rules

- Do not approve unreviewed product assumptions.
- Do not make a generated design change only in Penpot.
- Do not treat a successful MCP request as proof of visual correctness.
- Do not commit Penpot credentials, API tokens, or private screenshots.
- Do not accept duplicate `Page/<Name>` frames or `Component/<Name>` objects.
- Run `/design-review` before merging substantial design changes.

## Troubleshooting

### A skill does not appear as a slash command

Confirm that `telegram-miniapp-frontend` is the primary workspace folder and
that the skill exists under `.cline/skills/<skill-name>/SKILL.md`. Reload the
VS Code window after changing workspace order.

### Project rules are not loaded

In a multi-root workspace, Cline loads project rules only from the primary
workspace folder. Open the supplied workspace file and ensure
`telegram-miniapp-frontend` is first.

### Penpot reports `authentication-required`

Configure credentials for the Penpot MCP server and retry a read-only command,
such as listing teams or projects, before running synchronization.

### A Penpot file or page cannot be found

Check `design/penpot.json`. The target project, generated file, components page,
and naming prefixes must match the actual Penpot objects.

### JSON is valid but Penpot synchronization fails

Keep the JSON changes, report the exact unsupported MCP operation, and do not
claim synchronization succeeded. Retry after fixing authentication or tooling.

### A duplicate generated frame appears

Stop synchronization, identify the canonical stable name, remove only the safe
generated duplicate, and rerun a read-only review. Never delete manually
maintained content without approval.

### Visual comparison is unavailable

The current Penpot MCP integration may support structural reads and writes
without screenshot/export support. In that case, perform manual visual review
in Penpot and record that pixel-level verification was not automated.