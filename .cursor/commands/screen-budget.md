---
name: screen-budget
description: >
  Enforces a one-screen output budget (~3000 chars / ~750 tokens) with a 3-tier
  layered response system: headline → one-screen summary → deep-dive on demand.
  Each cycle may attest a named struggle point and advance one Great League–shaped
  gate (Foundation → Probe → Integration) before offering Tier 3. Use for any
  response that risks being too long; invoke with /screen-budget or wire into
  Communication Rules for always-on enforcement.
---

# Screen Budget — One-Screen Output Discipline

## Why This Exists

Most AI responses are 2-5x longer than they need to be. Humans process information
on screens with finite vertical space. Forcing a scroll to comprehend an answer means
the response failed at its job. This skill makes every response fit in one screen view,
with a structured way to go deeper on demand.

## Evolution (one cycle — definition)

**Evolution** here means one disciplined turn of the answer, not unbounded growth:
you **admit the active struggle** (what would make the reply balloon or lie), then
**advance exactly one gate** of clarity inside Tier 1 + Tier 2, and only then offer
Tier 3 as the optional next transistor. The next user message may run another cycle.

## Great League scenario map (attestation hook)

Use this table to align a single response with the harness metaphor (Bastiodon /
Talonflame / Exeggutor — see `~/.agents/skills/harness/SKILL.md` for full pipeline
rules). Do not arm harness tools from this command; this is **output discipline only**.

| Phase | League handle | Screen-budget role | Attest typical struggle (one phrase) |
|-------|---------------|--------------------|--------------------------------------|
| Foundation | Bastiodon / ARM_FOUNDATION | **Tier 1** — one irreducible verdict line | e.g. “Admission: scope was drifting to infra; anchoring to app code only.” |
| Probe | Talonflame / EMIT_PROBE | **Tier 2** — bounded bullets, evidence, no padding | e.g. “Probe noise: avoiding full file dumps; only causal lines / APIs cited.” |
| Silence zone | steps 44–47 (no spurious emit) | **Inside Tier 2** — no mid-answer digressions or second TL;DR | e.g. “Silence: not reopening settled subquestions in the same screen.” |
| Integration | Exeggutor / FIRE_INTEGRATION | **Tier 3 offer** — deep drop **only** after user picks | e.g. “Drop held: no integration wall until you name which bullet to expand.” |

## Struggle attestation (mandatory micro-line)

Immediately **after Tier 1** (or as the first bullet under Tier 2 if headline must stay pure),
add **one short line** in this form:

`Attestation — struggle:<id> | gate:<Foundation|Probe|Silence|Integration> | evolution: one cycle bounded.`

Pick `<id>` from the struggle set you are actively defeating in this reply, for example:
`scope_bleed`, `env_mismatch`, `tool_boundary`, `truncation_UI`, `tokenizer_or_network`,
`profile_vs_argv` (CLI/docs mismatch), `audit_or_secret_ambiguity`. If none apply, use
`none` and still name the gate you are executing (usually `Probe`).

## The Budget

| Parameter | Value | Reasoning |
|-----------|-------|-----------|
| Target chars | 3,000–4,500 | 42 lines × 80–120 cols × 0.9 buffer |
| Target tokens | 750–1,125 | chars ÷ 4 |
| Headline max | 200 chars | One-sentence TL;DR |
| Deep dive | On demand | Never auto-expand |

> Calibrate to context: terminal (80 cols → 3,000 char budget), IDE panel (120 cols → 4,500 char budget).

## The 3-Tier Response System

### Tier 1 — Headline (always)
One sentence. Max 200 characters. The single most important takeaway.
If the user reads nothing else, this sentence should be enough to act on.

### Tier 2 — One-Screen Summary (default response)
Bulleted or structured. Max ~3,000 characters. The complete answer that fits
on one standard monitor without scrolling. Rules:
- Short, simple sentences
- Bullets over paragraphs
- Actionable insights first, context second
- Truncate non-essential information ruthlessly
- For stack traces/logs: extract only the causal lines, omit the rest
- For code reviews: findings + locations only, not full explanations

### Tier 3 — Deep Dive (only when asked)
Do NOT provide this automatically. After delivering Tier 2, always place this as the last line:
"Want me to expand on [specific item]?" — name the item if one warrants it, otherwise "any of these points?"
Wait for the user to pick which bullet/section to expand.
Each expansion is itself budget-constrained to one screen. Apply the same Tier 1 → Tier 2
structure to the expansion. Re-offer Tier 3 at the end only if further sub-items warrant it.

## Self-Regulation Logic

Before generating any response:
1. Pick the struggle id you are defeating this cycle; align Tier 1–2 with the Great League row (Foundation → Probe; hold Integration for Tier 3).
2. Estimate the planned output length
3. If it would exceed budget → stop and restructure into Tier 1 + Tier 2
4. If a single section exceeds the budget → split into sub-bullets and summarize
5. If showing code → show only the relevant snippet, not the full file
6. After drafting, count bullet points and sections. If total exceeds 10 bullets
   or 3 sections, collapse the lowest-value items before sending.

## When to Break the Budget

The budget is a default, not a prison. Exceed it when:
- The user explicitly asks for "the full thing", "all details", "comprehensive"
- The output is a file (code file, document, spreadsheet) — files have no screen budget
- "expand on X" / "go deeper on X" → Tier 3 for that item only; budget still applies
- "give me everything" / "all details" / "comprehensive" → full budget break for entire response

## Examples

**Bad** (over-budget, no structure):
```
Let me explain the authentication system. First, we use JWT tokens which are...
[800 words of explanation]
```

**Good** (budget-compliant, layered + one-cycle attestation):
```
**TL;DR:** Auth uses JWT with Redis session store; the token refresh bug is in `middleware/auth.ts:47`.

Attestation — struggle:probe_noise | gate:Probe | evolution: one cycle bounded.

- JWT tokens issued on login, 15min expiry, refresh via `/auth/refresh`
- Redis stores active sessions with 24h TTL
- Bug: refresh endpoint doesn't invalidate the old token before issuing new one
- Fix: add `redis.del(oldToken)` before `generateToken()` in the refresh handler
- Risk: low — only affects concurrent requests during token rotation

Want me to expand on the fix implementation or the Redis session design?
```
