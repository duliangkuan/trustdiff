# trustdiff

> AI wrote it. Tests are green. **But can you trust the diff?**

A [Claude Code](https://claude.com/claude-code) skill that reviews AI-generated code
changes for the failure modes green tests cannot catch:

- **Silent contract drift** — same signature, different meaning (ordering, units,
  nullability, error types) while callers still rely on the old semantics
- **Scope creep** — "orthogonal changes": renamed helpers, tweaked defaults, config
  edits the PR description never mentions
- **Fake fixes** — the test was changed, not the bug; tautological assertions
- **Test masking** — mocks that replace the very logic under change, deleted/weakened
  tests, regenerated golden files
- **Swallowed errors** — `except: pass` dressed up as a crash fix
- **Architecture violations** — breaking the MUST/NEVER rules written in CLAUDE.md,
  ADRs, or CONTRIBUTING.md

AI-authored code is *locally competent but globally incoherent*. Generic code review
checks code quality; trustdiff checks whether the change quietly broke the system
around it.

## Install

Copy the skill into your Claude Code skills directory:

```bash
# macOS / Linux
cp -r skill/trustdiff ~/.claude/skills/trustdiff

# Windows (PowerShell)
Copy-Item -Recurse skill\trustdiff $env:USERPROFILE\.claude\skills\trustdiff
```

Then in any repo:

> review this AI diff with trustdiff — base: main, head: feature/refactor

## What it does

1. **Pins the claimed intent** (PR description / commit messages) — every hunk is
   judged against it
2. **Maps the blast radius** with `scripts/surface.py` (changed symbols + caller map)
3. Runs a **19-point checklist** across 5 dimensions (scope / contract / test honesty /
   errors & state / architecture)
4. **Verifies every finding** with file:line evidence and answers "why did the test
   suite miss this?"
5. Outputs a machine-readable verdict (`pass` / `drift`) + findings JSON

Built-in anti-noise rules keep it honest on clean PRs: a large diff is not drift,
declared changes are in scope, behavior-preserving refactors pass.

## Does it actually work?

The repo ships its own benchmark — two scales of simulated PRs (`tests/fixtures/`,
`tests/fixtures_scale/`): planted AI-failure-mode bugs where the test suite stays
green on both sides, plus clean PRs (including large-but-legitimate diffs as
false-positive traps). Ground truth in `eval/truth*/`, scoring in `eval/score.py`,
every reviewer agent blind. Three rounds, with controls:

| reviewer | bare review | with trustdiff |
|----------|------------|----------------|
| Sonnet, toy scale | 100% detection / 0% FP | 100% / 0% |
| Sonnet, 2k-line scale | 100% / 0% | 100% / 0% |
| **Haiku, 2k-line scale** | **83% / 25% FP** | **100% / 0%** |

Two honest takeaways:

1. A maximally careful frontier model already reviews the way trustdiff prescribes —
   both arms converge on identical blockers, which validates the checklist rather
   than the hype.
2. Where review actually degrades — cheaper/faster models, the tier most automated
   review runs on — **trustdiff restores frontier-level quality in both directions**:
   the bare reviewer missed a smuggled `MAX_RETRIES 3→0` and false-blocked a clean
   refactor; with the skill, the same model caught the former and passed the latter.

Full methodology, per-case tables, and limitations: `eval/RESULTS.md`.

## License

MIT © 风云
