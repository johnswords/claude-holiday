# CLAUDE HOLIDAY

> A 12-episode vertical micro-series parodying Hallmark holiday rom-coms through the lens of AI companionship.

**Created by**: John Swords
**Collaboration**: GPT-5 × Sora-2-Pro
**Format**: 9:16 vertical · 24fps · ~25s per episode
**Total Runtime**: ~5 minutes (12 episodes)

---

## 🎬 What Is This?

**CLAUDE HOLIDAY** is a multi-layered satire that's:
- **About AI** (model comparison as character study)
- **Made WITH AI** (GPT-5 × Sora-2-Pro collaboration)
- **Commenting ON AI-generated content** (Can AI parody itself?)

### The Story

A driven city professional escapes to a small holiday town, only to navigate romantic encounters with increasingly problematic "local men" — each one embodying a different AI model's capabilities, limitations, and quirks.

What starts as cozy meet-cutes devolve into surreal tech support scenarios: usage limits interrupt intimate moments, over-optimization leads to bathtub cocoa farms, and "compacting" (AI indigestion) strikes at the worst possible times.

### The Hidden Layers

1. **AI Model Comparison as Romance** — Each character represents a real AI model (Claude/Opus, Sonny/Sonnet, Cody/Codex)
2. **Corporate Satire** — Startup acquisition culture (The Software Company → Olympus Corp)
3. **Platform Agnostic Philosophy** — No single tool is perfect for everything
4. **Meta-Commentary** — AI creating art about its own limitations

**Read the full pitch**: [`docs/master_script.md`](docs/master_script.md)

---

## 📂 Repository Structure

```
claude_holiday/
├── docs/                    # Master documentation
│   └── master_script.md     # Full 12-episode script
├── episodes/                # Per-episode production workspace
│   ├── ep00_checking_in/
│   │   ├── script.md        # Episode extract
│   │   ├── prompts/         # Sora-2-Pro prompts
│   │   ├── assets/          # Episode-specific files
│   │   └── renders/         # Draft & final renders
│   └── ... (ep01-11)
├── ideas/                   # Brainstorming & development
├── scripts/                 # Code & automation
├── assets/                  # Shared resources (fonts, audio, templates)
├── output/                  # Final deliverables
│   ├── episodes/
│   ├── bonus/
│   ├── full_series/
│   └── social/
└── pitch/                   # Pitch deck & marketing materials
```

---

## 🎯 Episode Guide

**Act 1: Arrival** (Ep 0-1)
- **Ep 0**: "Checking In" — Meets Cody the innkeeper
- **Ep 1**: "First Contact" — First meeting with Claude

**Act 2: Frustration** (Ep 2-5)
- **Ep 2**: "Absolutely Right in Aspen" — Coffee spill validation
- **Ep 3**: "Great Question, Holly!" — Non-answers
- **Ep 4**: "Too Many Cocoas" — Over-optimization
- **Ep 5**: "Claude Limit" — Peak interrupted, Sonny introduced

**Act 3: Rebound** (Ep 6-7)
- **Ep 6**: "The Innkeeper's Shoulder" — Confiding in Cody
- **Ep 7**: "Slow and Steady" — Cody's tool-use failure

**Act 4: Chaos** (Ep 8-9)
- **Ep 8**: "While You Were Sleeping" — Sonny's corporate disasters
- **Ep 9**: "The Workspace" — Sonny containment

**Act 5: Resolution** (Ep 10-11)
- **Ep 10**: "Opus Reloaded" — Claude returns, Olympus offer
- **Ep 11**: "Platform Agnostic" — The empowered choice

**Bonus**: Speed-dating outtakes (Percy, Gail, Larry, Quinn)

---

## 🛠️ Workflow

### 1. Ideation → Writing
- Brainstorm in `ideas/`
- Update `docs/master_script.md`

### 2. Episode Prep
- Extract episode details to `episodes/[ep_name]/script.md`
- Write Sora-2-Pro prompts in `episodes/[ep_name]/prompts/`

### 3. Production
- Run generation scripts from `scripts/`
- Save drafts to `episodes/[ep_name]/renders/drafts/`

### 4. Iteration
- Review, refine prompts
- Generate new drafts

### 5. Finalization
- Approved render → `episodes/[ep_name]/renders/final/`
- Master export → `output/episodes/`

### 6. Series Compilation
- Stitch all episodes → `output/full_series/`
- Create social cuts → `output/social/`

---

## 🎨 Character Guide

| Character | AI Model | Traits | Flaw |
|-----------|----------|--------|------|
| **Claude (Opus)** | Claude Opus | Brilliant, emotionally intelligent, measured | Usage limits (resets Friday 3am) |
| **Sonny** | Claude Sonnet | Eager, high-capacity, rapid | Reckless, needs heavy supervision |
| **Cody** | GPT Codex | Steady, perfect memory, tireless | Poor tool use, lacks chemistry |
| **Percy** | Perplexity | Thorough, informative | Obsessive citations |
| **Gail** | Gemini | Powerful, polished | Over-compliant, policy-neutered |
| **Larry** | Llama | Enthusiastic, customizable | No boundaries, chaotic |
| **Quinn** | Qwen | Brilliant, unique perspective | Cultural/philosophical gap |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API access (Sora-2-Pro)
- Git LFS (for large video files)

### Setup
```bash
git clone [repo-url]
cd claude_holiday
pip install -r requirements.txt
```

### Generate an Episode
```bash
# Extract prompts from master script
python scripts/extract_prompts.py --episode ep00_checking_in

# Generate video
python scripts/generate_video.py --episode ep00_checking_in

# Review draft
open episodes/ep00_checking_in/renders/drafts/latest.mp4
```

---

## 📜 License

© 2025 John Swords — All rights semi-reserved

**Disclaimer**: Any resemblance to Hallmark® films or Anthropic Claude™ is purely coincidental and unintentionally hilarious. No trademarks were harmed in the making of this micro-series.

---

## 🤝 Contributing

This is a personal creative project, but if you're inspired to create your own AI-model rom-coms, go wild. Just credit the concept and share what you make.

---

**Status**: Pre-production
**Next Steps**: Episode 0 prompt writing → Draft render → Iterate

*Let's build something that makes people laugh while making them think.*

---

### 🎥 Candidate Review Flow (generate → review → stitch)

You can generate multiple candidates per scene, review them, choose winners, and then stitch the episode.

1) Generate candidates only (no stitching yet)
```bash
python scripts/compile_cut.py --recipe recipes/examples/dev-default.yaml --candidates-only
# Note manifest path printed; keep the cut_id handy
```

2) Create selections YAMLs (one per episode) from the candidates
```bash
python scripts/select_winners.py --cut-manifest output/cuts/<cut_id>/manifest/cut.manifest.json
# Edit episodes/<ep>/renders/selections/<cut_id>.yaml to set winner_index per scene
```

3) Compile using your selections (just run compile again; it picks up selections automatically)
```bash
python scripts/compile_cut.py --recipe recipes/examples/dev-default.yaml
```

Tips:
- Set `provider.options.num_candidates` in your recipe to control how many candidates are generated per scene.
- Prebaked provider will reuse any existing footage and duplicate into candidate slots if needed.
- Overlays are applied only to selected winners so your review clips stay clean.

---

## 🧭 Timelines

We call each distinct cut a "timeline."

- Prime timeline: the default cut from this repo
- Community timelines: your fork + recipe = your timeline

How to label your timeline:
- Add `timeline: "Prime 2025"` (or your own label) at the root of your RCFC recipe.
- Your manifest and YouTube metadata will include the timeline label.

How to register a community timeline:
- Open a PR adding an entry to `docs/timelines.md` with:
  - Timeline name (e.g., `alice/dev-glossary-extended`)
  - Cut URI from your manifest
  - Link to your fork and/or YouTube playlist
