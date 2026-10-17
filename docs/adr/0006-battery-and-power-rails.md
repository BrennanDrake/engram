# ADR-0006: Battery voltage and power rails

- **Status:** Proposed — needs Brennan's decision
- **Date:** 2026-10-17
- **Deciders:** Brennan

## Context

The stock TurtleBot3 runs from 3S (12.6 V full). The XL430 wheels are rated
6.5–12.0 V (11.1 V recommended), so a full 3S pack already runs them slightly
over spec, and their speed sags as the pack drains. The MVP adds a Pi 4 with SSD,
a screen, a RealSense and later the SO-101 arm and a pan-tilt head. The
analysis in the project's `purchasing/screen-and-battery.md` compares options.

## Decision (recommended)

A **4S3P 21700 Li-ion pack** with a smart balancing BMS (UART), and:

- a **regulated 12 V buck for the OpenCR**, so the wheels see a steady 12 V at any charge;
- **separate bucks** for the Pi (5 V) and the servo rail;
- a **16.4 V CC/CV dock charger** (4.1 V/cell to extend pack life).

## Consequences

- Wheels stay in spec and don't slow as the pack drains.
- About 150 Wh usable (194 Wh rated), roughly 5.5 h at 27 W, and low ballast that helps stability with the arm out.
- More parts: the OpenCR buck must handle about 3 A stall current with margin,
  and the BMS must be configured for 4S.
- Below about 13.3 V the 12 V buck drops out of regulation; the
  return-to-dock threshold must trigger before that.

## Alternatives considered

- **4S2P** — same design, about 3.7 h; fallback if space or weight is tight.
- **Stay 3S2P**, charged to 12.3 V — cheapest and simplest, stock wiring, but
  wheels see 10.5–12.3 V and the extra electronics run from an unregulated rail.
