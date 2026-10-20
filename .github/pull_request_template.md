## Scope
<!-- Phase or change this PR closes, in one or two lines. Link the challenge, issue or ADR. -->

## Changes
<!-- Main changes grouped by area, not by commit. Commits stay atomic in the history. -->

## Verification
<!-- CI run link and where the evidence lives (e.g. acceptance criteria in the challenge doc). -->

## Follow-ups
<!-- Deferred work or known limitations. Delete if none. -->

## Definition of Done
All required checks must be green (enforced by the ruleset).

- [ ] Conventional PR title: it becomes the subject of the merge commit.
- [ ] Commits are atomic and conventional, with no `fixup!` or WIP left: all of them reach `main`.
- [ ] The diff has been reviewed (self-review for now; by a reviewer once there are collaborators).
- [ ] New or changed behavior has tests, including failure cases, and I checked they fail without the change.
- [ ] Every new or renamed variable in `EnvSettings` is in `.env.example`.
- [ ] If the PR makes or changes a design decision, there is a new or updated ADR in `docs/adr/`.
- [ ] If installation, configuration or the stack changes, the README is updated.
