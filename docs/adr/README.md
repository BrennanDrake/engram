# Architecture decision records

Key decisions are written down before code depends on them, in the
[MADR](https://adr.github.io/madr/)-style format of [`template.md`](template.md).

## Process

1. Copy `template.md` to `NNNN-short-title.md` with the next free number.
2. Open a PR with status **Proposed**. One ADR per PR.
3. Brennan reviews. Merging the PR accepts the ADR; the merge commit flips
   the status to **Accepted** (the author updates it before merge).
4. ADRs are never edited to change a decision. Write a new ADR that
   supersedes the old one and set the old one's status to
   **Superseded by ADR-NNNN**.
