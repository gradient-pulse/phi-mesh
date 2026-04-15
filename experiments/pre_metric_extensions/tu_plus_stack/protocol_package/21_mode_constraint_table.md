# T-Protocol — Mode Constraint Table v1

## Purpose

This note provides a compact comparison table for T-Protocol operating modes.

Its purpose is to make mode selection easier for:
- licensees
- reviewers
- technical partners
- deployment planners

It supplements `09_operating_modes.md`.

---

## Mode comparison table

| Dimension | Light | Standard | High-Integrity |
|---|---|---|---|
| Core use | Fast support | Stateful coordination | Higher-risk supervisory use |
| Feedback depth | Shallow | Moderate | Deep and explicit |
| State carry-forward | Basic continuity | Strong continuity | Strongest continuity and recovery relevance |
| Ambiguity retention | Bounded | Important | Critical |
| Mismatch accountability | Basic | Strong | Strict |
| Restart discipline | Minimal but valid | Present and important | Explicit and central |
| Returned-trace discipline | Basic where relevant | Strong where relevant | Strongest where relevant |
| Evaluation strictness | Basic internal checks | Stronger internal checks | Highest internal discipline |
| Latency tolerance | Low | Moderate | Higher acceptable |
| Typical domains | Conversational support, workflow help | Planning, orchestration, enterprise state management | Supervisory autonomy, robotics oversight, anomaly-heavy systems |
| Main risk if underused | Too shallow for continuity-heavy tasks | Usually balanced | May add more overhead than needed |
| Main risk if overused | Too weak for difficult ambiguity/recovery | Usually acceptable | Excess cost/latency for low-risk cases |

---

## Mode selection rule

Select the **lowest mode** that still preserves the continuity, recovery, ambiguity handling, and interpretive discipline required by the application.

Compactly:

> Use as much protocol as the situation needs, but no less.
