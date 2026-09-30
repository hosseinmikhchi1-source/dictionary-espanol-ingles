# Enrichment Runbook

**Note:** This runbook is for the owner to run on a rented GPU server. The coding agent builds the framework but does not run large batches.

---

## Overview

This guide explains how to:
1. Rent a GPU server
2. Install a model server (Ollama or vLLM)
3. Run the pilot (300 lemmas)
4. Run full batches
5. Copy results back
6. Ingest into the database

---

## Step 1: Rent a GPU Server

Recommended providers:
- **Vast.ai** — cheap, pay-per-hour
- **RunPod** — easy to use
- **Lambda Labs** — reliable

Recommended GPU: **RTX 3090** or better (24GB VRAM)

---

## Step 2: Install Model Server

### Option A: Ollama (Recommended)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model (example: Llama 3.1 8B)
ollama pull llama3.1:8b

# Start the server
ollama serve
```

### Option B: vLLM

```bash
# Install vLLM
pip install vllm

# Start the server
python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3.1-8B-Instruct \
  --host 0.0.0.0 \
  --port 8000
```

---

## Step 3: Configure Environment

On your local machine, set these environment variables:

```bash
export LLM_BASE_URL=http://YOUR_GPU_SERVER:8000/v1
export LLM_MODEL=llama3.1:8b
export LLM_MODEL_JUDGE=llama3.1:8b  # or a different model
export LLM_API_KEY=ollama  # or your API key
```

---

## Step 4: Run the Pilot

```bash
# Run pilot on 300 stratified lemmas
python -m enrich run --task examples --limit 300 --offset 0 --run-name pilot_examples

# Review the pilot
python -m enrich review-export --task examples --sample 50 --seed 42
# Review the CSV, then:
python -m enrich review-import pilot_review.csv

# Check stats
python -m enrich stats
```

**Gate:** Scale up only if examples approval rate ≥ 90% after review.

---

## Step 5: Run Full Batches

Run in this order, each followed by `judge`:

```bash
# 1. Examples
python -m enrich run --task examples --limit 10000 --offset 0 --run-name batch_examples
python -m enrich run --task judge --limit 10000 --offset 0 --run-name judge_examples

# 2. Relations
python -m enrich run --task relations --limit 5000 --offset 0 --run-name batch_relations
python -m enrich run --task judge --limit 5000 --offset 0 --run-name judge_relations

# 3. Collocations
python -m enrich run --task collocations --limit 5000 --offset 0 --run-name batch_collocations
python -m enrich run --task judge --limit 5000 --offset 0 --run-name judge_collocations

# 4. False friends
python -m enrich run --task false_friends --limit 1000 --offset 0 --run-name batch_false_friends

# 5. Gap senses
python -m enrich run --task gap_senses --limit 2000 --offset 0 --run-name batch_gap_senses
```

---

## Step 6: Copy Results Back

```bash
# On your local machine
rsync -avz user@gpu-server:/path/to/data/enrichment/ ./data/enrichment/
```

---

## Step 7: Ingest into Database

```bash
# Run ETL with enrichment ingestion
python -m etl.etl
python -m etl ingest-enrichment
```

---

## Step 8: Shut Down GPU Server

```bash
# Stop the model server
# Then terminate the GPU instance
```

---

## Troubleshooting

### Out of memory
- Use a smaller model (e.g., 7B instead of 13B)
- Reduce batch size
- Use quantization (e.g., 4-bit)

### Rate limiting
- Reduce `LLM_CONCURRENCY`
- Add delays between requests

### Poor quality output
- Adjust temperature (`LLM_TEMPERATURE_EXAMPLES`)
- Update prompt version
- Try a different model
