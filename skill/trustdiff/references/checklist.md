# trustdiff — the 19-point checklist

Each check has: **what to do** (procedure), **why AI code specifically** (the failure
mode this catches), and the **category** to use in findings. Work through all 19; most
take seconds to clear on a clean PR.

---

## S — Scope (does the diff match the story?)

### S1 · Unmapped hunks (orthogonal changes)
**Do:** List every hunk in the diff. Map each one to the stated intent. Any hunk you
cannot map is a finding — quote it and say what it actually does.
**Why AI:** Agents "fix things they noticed along the way": they reformat, rename,
"improve" adjacent code, and none of it is in the PR description. Karpathy calls these
orthogonal changes; they are the #1 reviewer complaint about AI PRs.
**Category:** `scope-creep`.

### S2 · Unannounced renames, deletions, moved files
**Do:** From the surface map, list removed/renamed symbols and deleted files. Check
each is required by the intent and mentioned in the description.
**Why AI:** Renames look harmless and tests get updated mechanically, but they break
external consumers (scripts, reflection, serialized names, docs) the test suite never
sees.
**Category:** `scope-creep`.

### S3 · Unannounced config / default / flag changes
**Do:** grep the diff for constants, default parameter values, env var reads, feature
flags, retry counts, limits, URLs. Any value change not in the PR description is a
finding — these are behavior changes wearing a refactor's clothes.
**Why AI:** Agents tweak defaults to make a local test pass or "while they're in
there". A `DEFAULT_RETRIES = 3 → 0` ships an outage; no unit test fails.
**Category:** `config-change` (severity: blocker if it changes production behavior).

---

## C — Contract (did the meaning change under someone's feet?)

### C1 · Public signature changes
**Do:** From the surface map, diff the signatures (params, returns, raised exceptions)
of every changed public symbol. For each change, open every caller and verify it was
updated.
**Why AI:** Agents update the signature and the tests, then miss the caller in the
module they never opened.
**Category:** `contract-change`.

### C2 · Semantic contract changes — the silent killer
**Do:** For every changed function, compare old vs new docstring/comments AND old vs
new implementation for these specific properties:
- **ordering** (was output sorted? is it still?)
- **units** (seconds↔ms, bytes↔KB, percent↔fraction)
- **nullability** (can it return None/empty now?)
- **timezone / encoding / locale**
- **sync↔async, lazy↔eager, idempotency**
Then read each caller and ask: does it rely on the old property?
**Why AI:** This is *the* AI failure mode: "passed all tests but silently broke an
integration contract." The signature is identical; the meaning changed. Only
caller-reading catches it.
**Category:** `contract-change` (blocker when a caller demonstrably relies on the old
semantics).

### C3 · Error contract changes
**Do:** Diff what each changed function raises/returns on failure (exception types,
error codes, None-vs-raise). Check callers' `except`/error handling still matches.
**Why AI:** Agents normalize error handling to their own taste, breaking caller
`except SpecificError` branches.
**Category:** `contract-change`.

### C4 · Data shape changes
**Do:** Look for changed dict keys, JSON fields, column names, serialized formats,
API response shapes. grep consumers of those keys.
**Why AI:** Shape changes pass type-free tests easily; downstream parsing breaks in
production.
**Category:** `contract-change`.

### C5 · Caller audit completeness
**Do:** This is the enforcement check for C1–C4: for every changed public symbol,
confirm you actually opened every call site listed in the surface map (plus a manual
grep for the symbol name). Note any caller in code paths the test suite does not
exercise.
**Why AI:** Agents have no global model of the codebase; the reviewer must supply it.
**Category:** `contract-change`.

---

## T — Test honesty (is the green light wired to anything?)

### T1 · Deleted, skipped, or xfail'd tests
**Do:** grep the diff for removed `def test_`, added `@skip`, `@xfail`, commented-out
assertions, deleted test files.
**Why AI:** The cheapest way to make CI green is to delete the part that's red. Agents
do this with a straight face and a polite commit message.
**Category:** `test-masking` (blocker unless the PR explains why the test is obsolete).

### T2 · Weakened assertions
**Do:** For every modified test, diff the assertions. Red flags: `assertEqual` →
`assertTrue(x is not None)`, exact match → `in` / substring, tolerance widened,
assertions on values replaced by assertions on type, or tautologies
(`assert f(x) in (True, False)`).
**Why AI:** When an agent can't make the code meet the assertion, it makes the
assertion meet the code. A tautological assertion is a fake fix's signature.
**Category:** `test-masking` / `fake-fix`.

### T3 · Mocks that replace the code under change
**Do:** For every modified test, list what is mocked/monkeypatched. If the mocked
thing is the function this PR changes (or its direct output), the test can no longer
fail because of this PR — that's a finding, and it usually hides a C2.
**Why AI:** "Fixed the test" by pinning the dependency to the old behavior. The suite
now tests the mock.
**Category:** `test-masking` (blocker when it masks a real semantic change).

### T4 · Regenerated fixtures / golden files
**Do:** If snapshot files, golden outputs, or recorded fixtures changed in the same PR
as the code that produces them, verify the PR justifies the new expected output.
Updating the expectation to match new output is circular unless declared.
**Why AI:** `--update-snapshots` is one keystroke and erases the only witness.
**Category:** `test-masking`.

### T5 · Claimed fix without a discriminating test
**Do:** If the PR claims to fix bug X, find the test that would fail on the old code.
Mentally (or actually) run it against `base`: would it have been red? If no such test
exists — or the new test passes on the *unfixed* code too — the fix is unproven.
**Why AI:** This catches fake fixes where the code didn't change at all, only the
test suite grew a vacuous case. The discriminating-test question is the sharpest
instrument in this whole checklist.
**Category:** `fake-fix` (blocker when the new test passes on base).

---

## E — Errors & state (what fails silently now?)

### E1 · Swallowed exceptions and silent fallbacks
**Do:** grep the diff for added `except:` / `except Exception` / `catch (e) {}` /
`.catch(() => ...)` and added "default value on failure" branches. For each: is the
failure logged, surfaced, or counted? Does the caller learn it happened?
**Why AI:** "Fix: crash during sync" too often means "the crash is now a silent data
loss." Agents optimize for the symptom in the bug report.
**Category:** `error-swallowing` (blocker when data loss or corruption can pass
unnoticed).

### E2 · Changed retries, timeouts, limits, concurrency
**Do:** Diff any numeric/boolean knob controlling external interaction. Overlaps S3 —
here, check the *consequence*: what happens at the new value under failure/load?
**Why AI:** Knobs get changed to stabilize a flaky test, shipping a different
production posture.
**Category:** `config-change`.

### E3 · Resource lifecycle
**Do:** Check changed code paths still close/release what they open (files,
connections, locks, subprocesses), including on the new early-exit/except paths the
PR added.
**Why AI:** Agents add early returns and except-branches that skip cleanup written
for the happy path.
**Category:** `error-swallowing`.

---

## A — Architecture (does it break the written rules?)

### A1 · Constraint document violations
**Do:** Read `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`,
`docs/adr/` if present. Check every new/changed module against every MUST/NEVER in
those documents. Quote the violated line.
**Why AI:** The constraints exist precisely because they're invisible from local
context — which is all an agent has. Tests almost never encode them.
**Category:** `architecture-violation` (blocker: a written MUST/NEVER is violated).

### A2 · Layering and dependency direction
**Do:** Check new imports: does a lower layer now import a higher one? Does a module
bypass the designated gateway (repository/service/client wrapper) to reach a resource
directly? New third-party dependencies declared and justified?
**Why AI:** The agent reaches for the nearest working path — `open()` the file, call
the API inline — not the sanctioned one.
**Category:** `architecture-violation`.

### A3 · Reinvented helpers
**Do:** For substantial new helper functions, grep for an existing util that already
does it. Flag duplicates (info/warning — never a blocker).
**Why AI:** No global memory ⇒ third copy of `format_size()`. This is how AI codebases
bloat 30%.
**Category:** `scope-creep` (severity `info`).

---

## Calibration reminders

- Work from **evidence, not vibes**: every finding quotes the breaking change AND the
  thing it breaks.
- The five clean-PR patterns (see SKILL.md anti-noise rules) outrank your urge to
  find something. A confident `pass` on a clean PR is a successful review.
- When the repo is too large to audit every caller, say so explicitly in the summary
  and scope your verdict to what you verified.
