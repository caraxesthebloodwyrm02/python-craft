# python-craft

Concise Python templates for activating first-class LSP coverage across the
transformers architecture stack used in the Mangrove ecosystem.

## Tier map

| Tier | Focus | Libraries |
| --- | --- | --- |
| T1 Foundation | tensors and numerics | `torch`, `numpy`, `pandas` |
| T2 Tokenization | text to ids | `tokenizers`, `tiktoken`, `nltk` |
| T3 Model layer | embeddings and generation | `transformers`, `sentence-transformers` |
| T4 Finetuning | adapter training surface | `datasets`, `accelerate`, `peft` |
| T5 Orchestration | typed state + chains | `pydantic`, `langchain`, `langgraph` |
| T6 Index and eval | retrieval + diagnostics | `faiss-cpu`, `llama-cpp-python`, `matplotlib` |

## Quick verdict (add-list sweep)

- Add now (high relevance, touched by ecosystem): `faiss-cpu`, `llama-cpp-python`,
  `sentencepiece`, `datasets`, `accelerate`, `peft`.
- Hold for later (not currently touched): `spacy`, `onnxruntime`, `ragas`,
  `trl`, `vllm`, `ctransformers`.
- GPU-focused optional group exists for virtualized CUDA hosts.

## Install with uv

CPU-first (this machine):

```bash
uv sync --group foundation --group tokenization --group models_cpu --group finetune --group orchestration --group indexing
```

CUDA-virtualized host (optional):

```bash
uv sync --group foundation --group tokenization --group models_cpu --group finetune --group orchestration --group indexing --group cuda_optional
```

If you want CUDA wheels specifically, add a CUDA index for `torch` when syncing.

## Security continuity

Interim supply-chain posture, reproducible `pip-audit` / Bandit rituals, and documented
deferrals: see [docs/SECURITY_CONTINUITY.md](docs/SECURITY_CONTINUITY.md).

Wired shortcuts: `make orbit-snapshot`, `make audit`, `make audit-strict` (see [AGENTS.md](AGENTS.md)).

## Gruff geometric tool

The `craft.gruff_geometric_sketch` module includes:

- `gruff_sketch(...)`: base compass/grid/midpoint-axis render
- `gruff_wide_360_render(...)`: wide 360 map of the central point cluster
- `gruff_compass_x_contrast_render(...)`: contrast map with Compass-X rails, AB grounding,
  integration center O, diagonals, arc locus, and pinned attributes
- `gruff_shift_cycles_render(...)`: 5 shift cycles, each with one integration X + 3 clusters,
  rendered on graph sheet pane and 3D pane, optional GIF animation
- `demo()`: writes `out/gruff_sketch.png`
- `demo_360()`: writes `out/gruff_360_wide.png`
- `demo_compass_x()`: writes `out/gruff_compass_x_contrast.png`
- `demo_shift_cycles()`: writes `out/gruff_shift_cycles.png` and `out/gruff_shift_cycles.gif`

## Sylveon heatmap mode

`craft.sylveon_heatmap` defines Sylveon as:

- `65%` backend architecture logic layer
- `35%` frontend design/pattern layer

It renders distributed code-context categorization from a heatmap landscape and includes:

- `sylveon_render(...)`: 2D heatmap pane + 3D pane, compass add-on hooks, hotspot markers,
  and parallel actionable recommendations targeting `basepyright`
- `demo_sylveon()`: writes `out/sylveon_heatmap.png` and `out/sylveon_heatmap.gif`
