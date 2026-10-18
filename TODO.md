---
title: "Project Work Scratchpad"
document_type: work-tracker
version: "0.4.0"
status: active
created: 2026-10-18
updated: 2026-10-18
---

# Project Work Scratchpad

This is the project's general-purpose scratchpad for planning and tracking
current and future work. It may contain ideas, candidate tasks, issue drafts,
dependencies, and links to active work across phases. It is not limited to
Phase 1.

Approved outcomes and scope belong in the relevant program or phase documents,
not here. Existing GitHub issues are the source of truth for their status and
discussion; this file helps plan work that is not yet represented by an issue.
Items marked **proposed** are discussion candidates and are not approved work
or created issues.

## GitHub issue access

GitHub MCP is available in this environment for reading issues, but its
available issue tools do not create or edit issues. The `gh` CLI supports
creating issues and linking them to a parent with `gh issue create --parent`,
but it was not authenticated in this session. Issue creation can therefore be
delegated to the user via copyable `gh` commands when needed.

## Current focus: Phase 1 — built-in C procedure coverage

Outcome baseline: [Phase 1 plan](documentation/plan/phase1.md).

### Existing issues

| Issue | Status | Work and relationship |
|-------|--------|-----------------------|
| [#1: Add additional missing PDB procedures](https://github.com/DoctorU/online-gimp-pdb-browser/issues/1) | Open | Phase 1 parent and user-facing scope. Updated to reflect the production catalog and intended outcome. |
| [#2: Survey GIMP procedure registration patterns](https://github.com/DoctorU/online-gimp-pdb-browser/issues/2) | Complete | Surveyed registration families and extraction gaps. |
| [#3: POC — extract plug-in C procedures](https://github.com/DoctorU/online-gimp-pdb-browser/issues/3) | Open; active | Feasibility POC using `help.c` and `file-png.c`; see the [Issue 3 execution plan](plans/phase3_1.md). Samples are not production coverage. |
| [#4: Modularize the catalog builder](https://github.com/DoctorU/online-gimp-pdb-browser/issues/4) | Open | Preserve existing CLI/output behavior while separating shared code and source-family extractors. |
| [#5: Design procedure browser navigation](https://github.com/DoctorU/online-gimp-pdb-browser/issues/5) | Open | Decide how users browse by procedure, plug-in, and menu location; retain search and detail lookup. |
| [#8: Validate native PDB coverage and choose its extraction path](https://github.com/DoctorU/online-gimp-pdb-browser/issues/8) | Open | Compare native source-based output with an independent reference and decide whether the current extraction path is adequate. |
| [#9: Define catalog schema and measurable coverage validation](https://github.com/DoctorU/online-gimp-pdb-browser/issues/9) | Open | Define the catalog contract, per-family coverage baseline, conditional-registration handling, and publication gates. |
| [#10: Extract and validate built-in C plug-in procedures](https://github.com/DoctorU/online-gimp-pdb-browser/issues/10) | Open | Expand beyond issue #3's POC to the agreed built-in C plug-in coverage. |
| [#11: Integrate validated C plug-in procedures into the browser](https://github.com/DoctorU/online-gimp-pdb-browser/issues/11) | Open | Display validated C plug-in records, coordinating with navigation #5 and modularization #4. |
| [#12: Automate validated catalog updates for latest stable GIMP 3](https://github.com/DoctorU/online-gimp-pdb-browser/issues/12) | Open | Generate, validate, and safely publish only when the stable revision changes. |

### Phase 1 sequence

1. **In progress:** [#3 — C plug-in registration POC](https://github.com/DoctorU/online-gimp-pdb-browser/issues/3).
2. **Run in parallel where useful:** [#8 — native PDB coverage decision](https://github.com/DoctorU/online-gimp-pdb-browser/issues/8) and [#9 — schema and coverage validation](https://github.com/DoctorU/online-gimp-pdb-browser/issues/9).
3. **After the POC and contract are agreed:** [#10 — expand C plug-in extraction](https://github.com/DoctorU/online-gimp-pdb-browser/issues/10).
4. **Coordinate related work:** [#4 — builder modularization](https://github.com/DoctorU/online-gimp-pdb-browser/issues/4) and [#5 — browser navigation](https://github.com/DoctorU/online-gimp-pdb-browser/issues/5), then complete [#11 — browser integration](https://github.com/DoctorU/online-gimp-pdb-browser/issues/11).
5. **After extraction and integration are stable:** [#12 — automated stable-catalog updates](https://github.com/DoctorU/online-gimp-pdb-browser/issues/12).

No new issue drafts are currently pending creation for Phase 1.

## Version history

| Version | Date       | Summary | Reason |
|---------|------------|---------|--------|
| 0.3.0   | 2026-10-18 | Recorded created issues #8–#12 and the Phase 1 sequence | Replace proposed work with the user's confirmed issue links. |
| 0.4.0   | 2026-10-18 | Linked issue #3 to its bounded execution plan | Make the active POC steps and decision gates easy to find. |

## Future phases and general backlog

Add future phase work, cross-phase improvements, and ideas here as they are
identified. Move approved scope into the appropriate phase plan and link
actionable work to existing issues. Keep tentative ideas clearly marked as
proposed until the user approves creating issues.
