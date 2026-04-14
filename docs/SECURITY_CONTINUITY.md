# Security continuity (interim posture + local rituals)

This document closes the loop between **continuous operations** (“the show must go on”) and **known supply-chain risk**. It defines **reproducible local scans** (the contrasting margin: what we measured vs what we accept until upstream fixes land).

**Rhyme-and-reasons (session scope):** prose checkpoint only — **code-backed symbol audit for external Semantic Officer modules is explicitly deferred** for this zoomed view; do not block shipping on that hunt.

---

## Reproduce locally (dependency + OSV)

From the repository root:

```bash
uv export --all-groups --format requirements.txt --no-hashes -o /tmp/python-craft-reqs.txt >/dev/null
uv tool run pip-audit -r /tmp/python-craft-reqs.txt --skip-editable -s osv -f markdown
```

Notes:

- `--skip-editable` skips the workspace root (`-e .`), which is not published on PyPI for vulnerability matching.
- `-s osv` queries the **Open Source Vulnerabilities** database (Google OSV).

---

## Reproduce locally (static patterns / Bandit)

```bash
uv tool run bandit -r src/craft -ll -f txt
```

---

## Known finding (as of last ritual): `diskcache` / CVE-2025-69872

- **Observed path:** `diskcache` is pulled in via **`llama-cpp-python`** (see `uv export` comment edges).
- **Advisory:** [CVE-2025-69872 (NVD)](https://nvd.nist.gov/vuln/detail/CVE-2025-69872) — unsafe deserialization risk class associated with default **pickle** usage when an attacker can **write** to the cache directory.

**Interim operational measures (pick what matches your threat model):**

1. **Trust boundary:** only run LLM cache paths on **operator-controlled** filesystems; never point cache roots at shared or world-writable locations.
2. **Permissions:** harden directory ACLs for any configured cache root (principle: attacker must not obtain write capability).
3. **Reduce attack surface:** if you do not need `llama-cpp-python` / indexing tiers, **omit** those dependency groups in production installs.
4. **Track upstream:** when PyPI-resolvable upgrades or patched releases exist for your graph, bump `uv.lock` and re-run the ritual above.

`pip-audit` may list **no fix version** yet; that is normal for interim posture — the margin is “known + managed,” not “pretend green.”

---

## Known pattern class: Bandit B615 (Hugging Face Hub)

Bandit may report **B615** — *unsafe Hugging Face Hub download without revision pinning* — on demo-style calls such as `from_pretrained(model_name)` without a pinned `revision` (commit SHA).

**Interim guidance:**

- Treat as **supply-chain hygiene** for anything promoted beyond local demos.
- Prefer **`revision=`** (commit SHA or tag you trust) when downloading weights in reproducible pipelines.

Current flagged surfaces (re-scan after edits): `src/craft/t3_transformers.py`, `src/craft/t4_finetune_surface.py`.

---

## When to refresh this margin

- After any **`uv.lock`** change touching `llama-cpp-python`, `torch`, or other high-churn deps.
- Before tagging a release or publishing templates to a wider audience.
- After adopting a **new optional group** (`cuda_optional`, etc.).
