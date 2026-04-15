# T-Protocol — Core vs Appendix Note v1

## Purpose

This note clarifies which files in the protocol package are:

- core runtime documents
- validation/compliance documents
- deployment/licensing documents
- clarification/rationale appendices

Its purpose is to prevent package confusion and reading-order drift.

---

## 1. Core runtime documents

These define what must be built for a faithful implementation.

- `01_protocol_overview.md`
- `02_role_definitions.md`
- `03_runtime_order_and_role_handoffs.md`
- `04_data_ontology.md`
- `05_shared_state_schema.md`
- `06_feedback_and_state_update_rules.md`
- `07_transition_grammar.md`
- `08_minimal_invariants.md`
- `09_operating_modes.md`
- `10_faithful_implementation_conditions.md`

These are the core identity documents of the protocol package.

---

## 2. Validation and compliance documents

These define how the implementation is checked and reviewed.

- `11_conformance_test_family_v1.md`
- `12_non_transition_baseline_contract.md`
- `14_compliance_and_review.md`
- `16_protected_review_checklist.md`

These are essential for testing, review, and licensing discipline.

---

## 3. Deployment and licensing documents

These define how the protocol is positioned, deployed, and scoped commercially.

- `13_deployment_guidance.md`
- `15_license_scope_note.md`
- `18_licensee_implementation_checklist.md`
- `21_mode_constraint_table.md`

These are implementation- and business-facing support documents.

---

## 4. Clarification and rationale appendices

These help explain difficult concepts, but are not the first files required to understand the runtime.

- `17_example_cycle_walkthrough.md`
- `19_prediction_replay_and_dynamic_memory_note.md`
- `20_pohccp_note.md`
- `glossary.md`

These are important, but secondary to the core runtime documents.

---

## 5. Visual orientation layer

These help readers grasp the package quickly.

- `00_architecture_diagram.png`
- `README.md`

---

## Closing statement

The core runtime documents define the protocol.
The validation and deployment documents support its use.
The appendices clarify its deeper logic.

Compactly:

> Build from the core, test with the validation layer, deploy with the guidance layer, and understand the deeper logic through the appendices.
