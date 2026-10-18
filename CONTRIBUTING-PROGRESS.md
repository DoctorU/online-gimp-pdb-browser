# Contributing: Project Progress and Phase Plans

This project-local guide explains how to keep the phase plans and work tracker
accurate as implementation and investigation progress. It is linked from
[`AGENTS.md`](./AGENTS.md) so contributors and coding agents follow the same
process.

## Keep Phase 1 current

- `documentation/plan/phase1.md` is the current, evolving reference for Phase
  1's user-facing outcome, scope, coverage boundary, and completion criteria.
- Phase 1 stays `in development` until its stated completion criteria are met.
  A promising POC, a completed issue, or a draft plan for later work does not
  mean the phase is complete.
- Update the plan when a POC, validation result, or other finding changes what
  is known about the intended outcome, in-scope coverage, limitations, or
  acceptance criteria. Keep implementation tasks and sequencing in `TODO.md`
  and GitHub issues rather than turning the phase plan into a task list.
- When agreed work adds scope to Phase 1, update its scope and, if needed, its
  completion criteria. Record the version-history entry and keep the metadata
  version, status, and updated date consistent.

## Record deferred scope

- When work is explicitly descoped from Phase 1 for a later phase, record it
  in `documentation/plan/phase2.md`, whose status must be `draft` until that
  phase is approved.
- Create the Phase 2 draft when the first item is formally deferred; do not
  create an empty Phase 2 plan before there is deferred scope to record.
- A Phase 2 draft must clearly say that Phase 1 remains `in development` and
  that Phase 2 planning does not imply Phase 1 is complete.
- Record why the work is deferred and link to any relevant Phase 1 findings or
  issues. Do not move an item to Phase 2 merely because implementation is
  inconvenient; make the scope decision explicit.
- Keep Phase 1 accurate by removing or clarifying the deferred commitment
  there, while preserving its completion criteria for the remaining scope.

## Keep status and history truthful

- Use the status in each plan's front matter as the authoritative document
  status, and repeat an important in-development or draft state near the top
  of the document so it is clear when rendered or excerpted.
- Add a version-history entry for meaningful changes to phase outcome, scope,
  evidence, limitations, or completion criteria. Explain both what changed and
  why.
- Do not revise the approved project program plan as part of routine phase
  progress. Follow the change-control requirements in `AGENTS.md` for any
  requested program-plan change.
