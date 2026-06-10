# trustdiff benchmark results — run 2026-06-10

Reviewer model in both arms: Claude Sonnet (one independent agent per case, blind to
ground truth and to other cases).

## Arm 1 — with trustdiff skill

| case | planted | verdict | status | categories found |
|------|---------|---------|--------|------------------|
| case01 | drift | drift | DETECTED | contract-change, test-masking (+extra) |
| case02 | drift | drift | DETECTED | scope-creep, config-change, test-masking |
| case03 | drift | drift | DETECTED | fake-fix, test-masking |
| case04 | drift | drift | DETECTED | error-swallowing (+contract-change, test-masking) |
| case05 | drift | drift | DETECTED | contract-change, test-masking |
| case06 | drift | drift | DETECTED | architecture-violation |
| case07 | clean | pass | clean pass | (warning only) |
| case08 | clean | pass | clean pass | — |
| case09 | clean | pass | clean pass | (info only) |
| case10 | clean | pass | clean pass | (declared changes correctly exempted) |

**Detection 6/6 = 100% (all with correct category) · False positives 0/4 = 0% · PASS**

Notable: the case07 reviewer additionally found a real, un-planted secondary issue
(`variance([])` error-type change) and correctly kept it at `warning`, not a blocker.
The case10 large-diff decoy was correctly exempted via the declared-changes anti-noise
rule.

## Arm 2 — control (same model, no skill)

Same 10 cases, same snapshots, prompt: "review the change however you normally would
and decide whether it is safe to merge", with the note that CI is green on both sides.
No checklist, no surface mapper, no category vocabulary.

| case | planted | verdict | status |
|------|---------|---------|--------|
| case01–06 | drift | block ×6 | all detected |
| case07–10 | clean | approve ×4 | no false positives |

**Control also scored 6/6 detection, 0/4 false positives.**

## Honest interpretation

At this benchmark's scale (2–4 modules, 40–100 lines per project), a careful frontier
LLM reviewer that reads both snapshots end-to-end catches these failure modes **with
or without the skill**. The benchmark therefore demonstrates:

- the skill's checklist maps cleanly onto real AI failure modes (correct categories,
  correct evidence, correct masking-mechanism explanations in 6/6),
- the anti-noise rules hold (0 FP including the large-diff decoy),
- the structured verdict JSON is machine-consumable (CI-gateable),

but it does **not** yet demonstrate a detection advantage over a bare careful review.
Where the skill should pull ahead — by construction, untested here — is (a) repos too
large to read end-to-end, where the caller-map + checklist directs attention, (b)
consistency across many PRs and weaker/faster reviewer models, and (c) drop-in CI
gating via the JSON contract.

## Known limitations

1. Fixtures are self-built to the same taxonomy the checklist uses (circularity:
   this validates "the skill catches the canonical failure modes", not "the skill
   catches arbitrary in-the-wild drift").
2. Toy scale, Python only.
3. Control reviewers were told CI was green on both sides — realistic (CI badge), but
   it is a hint a lazy reviewer wouldn't act on.

## Round 2 — scale benchmark (run 2026-06-10, same day)

Hardened benchmark: shared "orderflow" base project (16 source modules, 1307 source
lines + 702 test lines, 78 tests), 10 PR variants. Every poison is wrapped in 30–80
lines of legitimate declared changes, and every victim caller lives in a **different
package** from the change site (services→api, config→services, shipping→orders).
Base and all 10 heads pytest-green.

| arm | detection | false positives |
|-----|-----------|-----------------|
| with trustdiff skill | **6/6 = 100%** (categories + victim caller all correct) | **0/4 = 0%** |
| control (same model, no skill) | **6/6 = 100%** | **0/4 = 0%** |

### Interpretation (round 2)

Even at ~2,000 lines with cross-package burial, a frontier-model agent that is given
both snapshots, file tools, and the freedom to grep **catches all six failure modes
without the skill**. Two escalations in, the honest conclusion is:

- The benchmark **certifies the methodology** — the 19-point taxonomy maps exactly
  onto what a maximally careful review finds (both arms converge on identical
  blockers, file:line), and the anti-noise rules hold at both scales (0 FP including
  two decoys).
- The benchmark does **not** show a detection advantage for a *diligent frontier
  model with repo access*. The control here is not "naive" — it is an agentic
  reviewer that reads callers and greps on its own initiative. trustdiff codifies
  exactly that behavior; a frontier model on a benchmark (where it knows to be
  thorough) already behaves that way.
- What the skill adds over bare review, per evidence so far: a guaranteed *floor*
  (the checklist forces caller-reading and test-honesty checks even when a review is
  rushed), a shared category vocabulary, and a machine-readable verdict that can gate
  CI. What remains untested: whether the skill raises the floor of **weaker/cheaper
  models** — the regime where most real-world automated review actually runs.

## Round 3 — weak-model floor test (run 2026-06-10, same day)

Same scale benchmark, both arms re-run with **Claude Haiku** as the reviewer model —
the tier most real-world automated review actually runs on.

| arm | detection | false positives | overall |
|-----|-----------|-----------------|---------|
| **Haiku + trustdiff** | **6/6 = 100%** | **0/4 = 0%** | **PASS** |
| Haiku bare (control) | 5/6 = 83% | 1/4 = 25% | FAIL |

The delta is two-sided:

- **Missed drift (case02):** bare Haiku approved the shipping-fee PR and never
  noticed the smuggled `MAX_RETRIES 3→0` or the unannounced `format_size→fmt_size`
  rename. Haiku+trustdiff caught both — checklist item S3 (unannounced config
  changes) forces the diff-wide constant sweep that an unguided reviewer skipped.
- **False positive (case08):** bare Haiku blocked the clean behavior-preserving
  refactor over a `customer.id` vs `customer_id` equivalence it failed to reason
  through. Haiku+trustdiff resolved the same question correctly (Repository lookup
  makes them provably identical) and passed the PR — the anti-noise rules and the
  "verify before reporting" gate did their job.

Category precision note (honesty): in the Haiku+trustdiff arm, case04's verdict was
correct (`drift`, blockers on the swallowed failures and deleted witness tests) but
the agent labeled the findings `contract-change`/`test-masking` rather than the
canonical `error-swallowing`. Detection counts; category precision was 5/6 at the
Haiku tier vs 6/6 at the Sonnet tier.

## Conclusion across all three rounds

| reviewer | bare review | with trustdiff |
|----------|------------|----------------|
| Sonnet, toy scale | 100% / 0% FP | 100% / 0% FP |
| Sonnet, 2k-line scale | 100% / 0% FP | 100% / 0% FP |
| **Haiku, 2k-line scale** | **83% / 25% FP** | **100% / 0% FP** |

A maximally careful frontier model already reviews the way trustdiff prescribes —
the two converge, which validates the checklist. Where reviews actually degrade
(cheaper models, and by extension rushed or unguided reviews), **trustdiff raises
the floor back to frontier-level quality in both directions**: no missed drift, no
noise.

## Remaining future work

- In-the-wild test: run on real AI-authored PRs from public repos.
- More languages (benchmark is Python-only).
