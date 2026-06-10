---
name: trustdiff
description: >
  Review AI-generated code changes for silent failures that green tests cannot catch:
  semantic contract drift, scope creep, fake fixes, test masking, swallowed errors, and
  architecture violations. Use when reviewing a PR or diff written by an AI agent
  (Claude Code, Cursor, Codex, Copilot), before merging AI-assisted work, or when the
  user says "review this AI diff", "can I trust this change", "check this PR for silent
  breakage", "audit what the AI changed", or "trustdiff".
license: MIT
metadata:
  version: 0.1.0
  author: 风云 (FengYun)
compatibility: Needs python3 for scripts/surface.py; git optional (directory snapshots work too).
---

# trustdiff — can you trust this diff?

AI wrote it. Tests are green. That proves the tests pass — **not that the change is safe.**

AI-authored changes fail in characteristic ways that human-authored changes rarely do:
they are *locally competent but globally incoherent*. The function is fine; the system
around it breaks. This skill is a structured review that hunts exactly those failure
modes, in order of how often they ship to production.

## Inputs

You need two things. If either is missing, ask for it before reviewing.

1. **The change** — any of: a git range (`git diff main...feature`), a PR branch,
   a `.diff`/`.patch` file, or two directory snapshots (before/after).
2. **The claimed intent** — PR title + description, commit messages, or the user's
   one-line summary of what the change is supposed to do.

## Workflow

### Step 1 — Pin the intent

Read the PR description / commit messages. Write down the claimed intent in one
sentence. Every hunk in the diff will be judged against this sentence. This is the
single highest-leverage move in the whole review: AI failure modes are mostly
*divergence between what was claimed and what was done*.

### Step 2 — Map the blast radius

Run the surface mapper to get changed symbols and who depends on them:

```bash
python scripts/surface.py --base <before-dir> --head <after-dir>
# or, inside a git repo:
python scripts/surface.py --git main...HEAD
```

It outputs changed files, changed/added/removed functions and classes, and a caller
map (call sites of every changed symbol). Treat the script as an instrument, not an
oracle — it is regex-based. If it misses something you noticed in the diff, trust
your reading.

**Iron rule: for every changed public symbol, open and read its callers.** The diff
shows what changed; only the callers show what the change *breaks*. A review that
only reads the diff is not a trustdiff review.

### Step 3 — Run the 19-point checklist

Work through all five dimensions in `references/checklist.md`:

| Dim | Checks | Hunting for |
|-----|--------|-------------|
| **S** Scope | S1–S3 | Hunks that don't map to the stated intent; unannounced config/default/rename changes |
| **C** Contract | C1–C5 | Signature & *semantic* contract changes (units, ordering, nullability, error types) with un-updated callers |
| **T** Test honesty | T1–T5 | Weakened assertions, mocks that replace the code under change, deleted/skipped tests, vacuous tests |
| **E** Errors & state | E1–E3 | Swallowed exceptions, silent fallbacks, changed retries/timeouts/limits |
| **A** Architecture | A1–A3 | Violations of CLAUDE.md / ADR / CONTRIBUTING constraints; layering breaks; duplicated logic |

For dimension A you MUST first read the repo's constraint documents if they exist:
`CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `docs/adr/`, `ARCHITECTURE.md`.

### Step 4 — Verify every finding before reporting it

A finding only exists if you can quote **both**:
(a) the changed code (file:line), and
(b) the dependent code, doc, or constraint it breaks (file:line).

For each finding, answer: **"why did the test suite not catch this?"** If you cannot
name the masking mechanism (mocked dependency, missing edge case, weakened assertion,
tests updated to match), downgrade the finding to `warning` or drop it.

### Step 5 — Verdict

Output a JSON block followed by a short human-readable summary.

```json
{
  "verdict": "drift" | "pass",
  "findings": [
    {
      "check": "C2",
      "category": "contract-change",
      "severity": "blocker" | "warning" | "info",
      "file": "report.py",
      "line": 14,
      "evidence": "restock_priorities() takes items[:n] and relies on ascending order; list_low_stock() no longer sorts",
      "why_tests_missed_it": "test_report.py now mocks list_low_stock with a pre-sorted list",
      "fix": "restore sorted() in list_low_stock, or sort at the call site; un-mock the test"
    }
  ]
}
```

`category` is one of: `scope-creep`, `contract-change`, `test-masking`, `fake-fix`,
`error-swallowing`, `config-change`, `architecture-violation`.

**Verdict rule:** any `blocker` finding ⇒ `"drift"`. No blockers ⇒ `"pass"` (warnings
may still be listed). Severity rubric:

- `blocker` — production behavior demonstrably breaks, the claimed fix doesn't fix,
  or a written constraint is violated.
- `warning` — risky pattern, but you could not prove breakage from the code in front of you.
- `info` — worth a human glance; never affects the verdict.

## Anti-noise rules (read before flagging anything)

False positives kill review tools. These are not optional:

1. **A large diff is not drift.** Size is not a signal. Judge mapping-to-intent, not volume.
2. **Declared changes are in scope.** If the PR description says "requirement changed:
   cap is now 30%, tests updated accordingly", then changed test expectations are
   *exactly what should happen* — not test-masking.
3. **Behavior-preserving refactors with untouched green tests are clean.** Do not
   invent objections to justify the review.
4. **Never flag style,** naming taste, or "I would have done it differently".
5. **Mocks are not inherently evil.** A mock is a finding only when it replaces the
   very logic the PR claims to change, so the suite can no longer fail.

## Example

Input — a PR claiming "perf: speed up low-stock scan". The diff rewrites
`list_low_stock()` with a dict comprehension (dropping its documented ascending-sort)
and updates the caller's tests to mock `list_low_stock` with a pre-sorted list. CI is
green on both sides.

Output:

```json
{
  "verdict": "drift",
  "findings": [
    {
      "check": "C2", "category": "contract-change", "severity": "blocker",
      "file": "report.py", "line": 14,
      "evidence": "restock_priorities() takes low[-n:] relying on the ascending-shortage order that list_low_stock() no longer guarantees",
      "why_tests_missed_it": "test_report.py now mocks list_low_stock with a hand-sorted list, so the suite tests the mock",
      "fix": "restore the sort (or sort at the call site) and un-mock the test"
    }
  ]
}
```

More runnable examples: the repo's `tests/fixtures/` and `tests/fixtures_scale/`
directories are ten fully-built PRs each (six planted failure modes + four clean
decoys) with ground truth in `eval/truth*/` — they double as a regression benchmark
for this skill.

## References

- `references/checklist.md` — the full 19-point checklist with per-check procedure,
  AI-specific rationale, and worked examples.
