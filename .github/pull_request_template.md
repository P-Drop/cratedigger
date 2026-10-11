## Why
<!-- Problem or goal. Link the related issue or ADR, if any. -->

## What changed
<!-- Main changes, briefly. -->

## How to verify
<!-- Commands, CI run links or screenshots that prove it works. -->

## Definition of Done
All required checks must be green (enforced by the ruleset).

- [ ] Conventional PR title; the PR does one thing and the description explains why.
- [ ] The diff has been reviewed (self-review for now; by a reviewer once there are collaborators).
- [ ] New or changed behavior has tests, including failure cases, and I checked they fail without the change.
- [ ] Every new or renamed variable in `EnvSettings` is in `.env.example`.
- [ ] If the PR makes or changes a design decision, there is a new or updated ADR in `docs/adr/`.
- [ ] If installation, configuration or the stack changes, the README is updated.
