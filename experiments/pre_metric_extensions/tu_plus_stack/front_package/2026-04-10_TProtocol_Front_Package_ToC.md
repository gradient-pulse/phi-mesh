# T-Protocol Front Package — Draft Table of Contents

## 1. Executive Overview
A concise explanation of:
- what T-Protocol is
- what problem it solves
- why it matters
- where it fits in an LLM-based system

## 2. One-Page Architecture Note
The clean architecture summary describing:
- triadic roleholding
- bounded information flow
- recursive feedback
- adjustable protocol intensity
- intended gains and best-fit use cases

## 3. Protocol Definition
A precise statement of the protocol as a licensable object:
- what counts as T-Protocol
- what the protocol governs
- what is required for valid implementation
- what is outside scope

## 4. Core Role Specifications
Formal role descriptions for:
- TU
- TU+
- cortexLLM

Each role should include:
- function
- allowed behavior
- forbidden behavior
- handoff logic
- role-boundary constraints

## 5. Bounded Information-Flow Rules
The rules governing:
- what each role receives
- what each role passes onward
- what feedback is retained
- what must remain separated
- how state is updated between cycles

## 6. Operating Modes
Deployment modes such as:
- Light
- Standard
- High-Integrity

Each mode should specify:
- degree of protocol involvement
- latency/overhead expectations
- suitable application classes
- minimum compliance conditions

## 7. Feedback and State Update Logic
The core recursive rule set for:
- treating output as next-state input
- preserving continuity
- handling unresolved signals
- updating bounded state without uncontrolled drift

## 8. Intended Use Cases
A concise list of application domains where T-Protocol is likely to offer value, such as:
- enterprise coordination
- long-horizon decision support
- anomaly-aware supervisory autonomy
- robotics oversight
- edge-case interpretation

## 9. Non-Use / Misuse Boundaries
Clear statements about where T-Protocol is not intended to operate directly, for example:
- raw reflex control
- hard real-time motor loops
- uncontrolled role multiplication
- implementations that violate bounded-flow rules

## 10. Internal Evaluation and Compliance Checklist
A license-facing checklist covering:
- role separation maintained
- bounded-flow rules respected
- feedback loop implemented correctly
- no unauthorized role fusion
- required evaluation discipline present

## 11. Implementation Guidance
Practical guidance for licensees on:
- how to integrate the protocol around an LLM
- how to choose protocol intensity
- how to manage state and feedback
- how to avoid obvious implementation errors

## 12. Licensing Scope
A concise explanation of:
- what the license grants
- what is protected
- what may or may not be modified
- whether sublicensing, internal deployment, or product embedding is allowed

## 13. Support Materials Index
A short index pointing to the substantiation layer, including:
- observations
- laws
- metrics
- failure taxonomy
- protocol assessments

This section should reference supporting material without forcing the reader into it.

## 14. Contact / Discussion Path
A final short section explaining how prospective licensees, partners, or evaluators can proceed to:
- technical review
- pilot discussion
- licensing discussion
- due diligence
