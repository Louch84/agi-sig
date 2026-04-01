---
name: tinylora
description: Run TinyLoRA experiments — fine-tune small models with minimal parameters for reasoning tasks. Based on TinyLoRA paper (Morris et al., 2026): 13 parameters can recover 90% of RL reasoning improvements. Use for rapid iteration on reasoning tasks, testing hypotheses, and efficient model specialization.
---

# TinyLoRA Experiments

## What is TinyLoRA?

From Morris et al. 2026: "Learning to Reason in 13 Parameters"
- Qwen2.5 8B trained to **91% on GSM8K** with only **13 trainable parameters** (26 bytes in bf16)
- Recovers **90% of RL reasoning improvements** at **1000x fewer parameters**
- **RL (not SFT)** is critical — SFT requires 100-1000x larger updates

## Model Setup

We use Qwen2.5 0.5B via Ollama for fast local experiments.

```bash
# Pull the small model
ollama pull qwen2.5:0.5b

# Verify
ollama list | grep qwen2.5
```

## Run an Experiment

```bash
python3 skills/tinylora/scripts/train.py
```

This script:
1. Loads Qwen2.5 0.5B from Ollama
2. Applies a rank-1 LoRA adapter (2 parameters trained)
3. Trains on a simple reasoning task (math word problems)
4. Evaluates before/after accuracy
5. Reports parameter count and performance

## Experiment Log

Location: `skills/tinylora/experiments/`

Format: `YYYY-MM-DD-run-N.md`

Each run logs:
- Task description
- Parameters trained
- Accuracy before/after
- Key observations

## TinyLoRA Training Script

The core training loop uses:
- `peft` for LoRA configuration
- `transformers` + `torch` for model loading
- Rank-1 LoRA: only 2 parameters trained (A and B matrices)
- RL vs SFT: We use RL-style rewards, not supervised fine-tuning

## Research Hypothesis

**Claim:** Tiny LoRA adapters (1-13 parameters) can teach reasoning patterns to small models.

**Test:**
1. Baseline: Qwen2.5 0.5B on GSM8K-style problems
2. After LoRA: Same problems with 13-param adapter
3. Measure: Accuracy improvement

**Expected:** Even 1-13 parameters should show measurable improvement if the claim holds.

## Limitations

- This is CPU-only training — slow but functional
- Small model (0.5B) has limited ceiling
- RL requires reward signal — we use math accuracy as proxy
- Results may not generalize to larger models
