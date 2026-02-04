# Targets Schema

This schema defines the outreach target list for academic acquisition of RGPxScientist.

## Fields
- `org`: University or institution name.
- `lab`: Lab or center name.
- `person`: Primary contact (PI, postdoc, research lead).
- `role`: Role of contact (PI, Professor, Postdoc, Lab Manager, etc.).
- `domain`: Research domain (e.g., systems neuroscience, quantum materials, NLP).
- `pain`: Stated or inferred pain point that RGPxScientist can address.
- `relevance_score(0-5)`: Fit score (0=no fit, 5=perfect fit).
- `source_link`: Public URL supporting the lead (lab page, paper, grant).
- `last_contact`: Date of last outreach (YYYY-MM-DD).
- `next_followup`: Date for next follow-up (YYYY-MM-DD).
- `status`: Pipeline stage (e.g., new, contacted, replied, first_win_delivered, not_interested).
- `notes`: Free-text notes and context.

## File
- CSV lives at `outreach_operator/targets.csv`.
