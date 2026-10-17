# ADR-0001: Record architecture decisions

- **Status:** Proposed
- **Date:** 2026-10-17
- **Deciders:** Brennan

## Context

Most of the work on engram is done by AI agents opening PRs, with Brennan
reviewing. Decisions made in chat threads are easy to lose, and agents starting
cold need a reliable record of what was decided and why. Brennan wants to own
the direction and be able to explain it later.

## Decision

We record significant decisions as ADRs in `docs/adr/`, one per file, using the
template in this folder. ADRs are reviewed and merged like code. A decision is
significant if it is expensive to reverse or other code will depend on it:
platforms, interfaces between components, middleware, tooling, power design.

## Consequences

- Agents read `docs/adr/` before proposing changes that touch a decision.
- A PR that changes a decision must add or supersede an ADR.
- Small, easily reversed choices stay in PR descriptions.

## Alternatives considered

- **Keep decisions in the plan document only** — it mixes ideas with decisions
  and has no review step.
- **Wiki or chat history** — not versioned with the code; agents can't rely on it.
