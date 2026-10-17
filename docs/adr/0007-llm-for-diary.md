# ADR-0007: LLM provider for the nightly diary

- **Status:** Proposed — needs Brennan's decision
- **Date:** 2026-10-17
- **Deciders:** Brennan

## Context

The MVP's cognition slice ends each night with an LLM summarizing the day's
episodes into a diary entry and rating memories for forgetting. That is one
batch job a night with a few thousand tokens in and out. The inputs are text
summaries of what happened in Brennan's home (not raw camera images). The
desktop GPU model is still an open question, which limits what runs locally.

## Decision (recommended)

Put the LLM behind a **small provider interface** in `cognition/` and start with
a **cloud API** for the MVP, with a **local model on the desktop GPU** as a
drop-in option once the GPU is known.

## Consequences

- Diary quality is high from day one, at a cost of cents per night.
- Home-activity summaries leave the house; the API key lives on the desktop
  host or in CI secrets, never in the repo.
- The diary job needs internet; if the call fails, the job retries the next
  night and episodes are kept until a diary covers them.
- Swapping to a local model later is a config change, not a rewrite.

## Alternatives considered

- **Local model only** (for example via Ollama on the desktop GPU) — private and
  free to run, but quality depends on a GPU we haven't confirmed, and the desktop
  must be on at night.
- **Local on the robot** — the Pi 4 can't run a useful model.
