# CLAUDE HOLIDAY

> An experiment in **community-composable media** — a 12-episode vertical micro-series parodying Hallmark holiday rom-coms through the lens of AI companionship.

**Created by**: John Swords
**Collaboration**: GPT-5 × Sora-2-Pro
**Format**: 9:16 vertical · 24fps · ~25s per episode
**Total Runtime**: ~5 minutes (12 episodes)

**What makes this different**: There is no single definitive version. Your cut is valid and referenceable.

---

## 🚀 30 Seconds to Your First Cut

**Zero setup. Five commands. Your own AI holiday rom-com, ready to ship.**

```bash
# 1. Generate multiple video candidates for each scene (saves cut ID)
./ch candidates --recipe recipes/examples/dev-default.yaml

# 2. Pick your favorite takes from each scene (creates visual contact sheet)
./ch select --cut-manifest output/cuts/<id>/manifest/cut.manifest.json

# 3. Stitch your selections into final episodes with overlays
./ch compile --recipe recipes/examples/dev-default.yaml

# 4. Generate YouTube metadata (title, description, tags)
./ch ytmeta --cut-manifest output/cuts/<id>/manifest/cut.manifest.json

# 5. Package everything for release (videos + metadata + manifest)
./ch bundle --cut-manifest output/cuts/<id>/manifest/cut.manifest.json
```

**That's it.** You now have:
- ✅ 12 professional episodes ready for YouTube
- ✅ Your unique Cut URI (like a git commit hash for video)
- ✅ Complete metadata and release package
- ✅ Your timeline registered in the multiverse

**No API keys needed** — uses prebaked footage. **No coding required** — just run the commands.

→ *Watch your first episode in under a minute. Ship your timeline today.*

---

## 🧬 Composable Media — What Does That Mean?

**CLAUDE HOLIDAY** isn't just a video series you can fork. It's a new format where:

- **Config-driven "recipes" (RCFC)** define every cut — episodes, overlays, timing, provider choices
- **No canonical version exists** — the "Prime" timeline is one interpretation, yours is equally valid
- **Reproducible by design** — every cut gets a deterministic Cut URI for reference
- **Community remixing IS the medium** — fork, tweak YAML, run one command, publish your timeline

**Traditional media**: One creator → One product → Many consumers
**Composable media**: Open foundation → Infinite interpretations → Community of co-creators

Read the full philosophy in [`docs/charter.md`](docs/charter.md)

### 🧾 RCFC Recipes — The Technical Foundation

**RCFC** (Recipe-Cut Format Configuration) is the YAML format that makes composability work:

```yaml
timeline: "Prime 2025"
episodes:
  - ep00_checking_in
  - ep01_first_contact
  # ... choose which episodes to include

overlays:
  enable: true
  style: minimal
  # ... configure visual overlays

provider:
  type: prebaked  # or 'sora' to generate new footage
  # ... provider-specific options
```

**What makes RCFC special:**
- **Deterministic**: Same recipe = same Cut URI
- **Reproducible**: Anyone can rebuild your exact cut
- **Human-readable**: Non-coders can edit YAML
- **Extensible**: New options without breaking old recipes

**Release bundles** include:
- Videos (per episode + full series)
- Captions/subtitles
- Recipe snapshot (frozen config)
- Metadata (Cut URI, timeline, manifest)

→ Everything needed to reference, reproduce, or remix your cut.

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

The repository is designed to support **two modes**: content creation (making episodes) and timeline creation (assembling cuts).

```
claude_holiday/
├── docs/                    # Master documentation
│   ├── master_script.md     # Full 12-episode script
│   ├── charter.md           # Community & composable media philosophy
│   └── timelines.md         # Registry of community timelines
├── recipes/                 # RCFC recipe files
│   └── examples/            # Example recipes to fork
├── episodes/                # Per-episode production workspace
│   ├── ep00_checking_in/
│   │   ├── script.md        # Episode extract
│   │   ├── prompts/         # Sora-2-Pro prompts
│   │   ├── assets/          # Episode-specific files
│   │   └── renders/         # Draft & final renders
│   └── ... (ep01-11)
├── ideas/                   # Brainstorming & development
├── scripts/                 # Code & automation
│   ├── compile_cut.py       # Main recipe compiler
│   └── pack_release.py      # Bundle releases
├── assets/                  # Shared resources (fonts, audio, templates)
├── output/                  # Final deliverables
│   ├── cuts/                # Generated cuts with manifests
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

## 🛠️ Two Workflows: Create Content vs. Create Cuts

### For Content Creators (making new episodes/footage)

1. **Ideation → Writing**
   - Brainstorm in `ideas/`
   - Update `docs/master_script.md`

2. **Episode Prep**
   - Extract episode details to `episodes/[ep_name]/script.md`
   - Write Sora-2-Pro prompts in `episodes/[ep_name]/prompts/`

3. **Production**
   - Run generation scripts from `scripts/`
   - Save drafts to `episodes/[ep_name]/renders/drafts/`

4. **Finalization**
   - Approved render → `episodes/[ep_name]/renders/final/`
   - Content available for recipe system

### For Timeline Creators (making your own cut)

1. **Fork & Setup**
   ```bash
   git clone [your-fork]
   cd claude_holiday
   # Install uv (if not already installed)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # Install dependencies
   uv sync
   ```

2. **Create Your Recipe**
   ```bash
   cp recipes/examples/dev-default.yaml recipes/my-timeline.yaml
   # Edit YAML: choose episodes, overlays, audience, provider
   ```

3. **Compile Your Cut**
   ```bash
   ./ch compile --recipe recipes/my-timeline.yaml
   # Or using uv directly:
   uv run python -m scripts.compile_cut --recipe recipes/my-timeline.yaml
   # Or use the Makefile shortcut:
   make compile-cut
   ```

4. **Publish Your Timeline**
   - Your Cut URI is in `output/cuts/[cut_id]/manifest/cut.manifest.json`
   - Upload videos to YouTube/Vimeo
   - Optional: Open PR to add your timeline to `docs/timelines.md`

**No coding required** — just YAML editing and one command.

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

### Path A: Use Existing Footage (Start Here)

**Prerequisites**: Python 3.11+, Git

```bash
# 1. Clone and setup
git clone [repo-url]
cd claude_holiday
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh
# Install project dependencies
uv sync

# 2. Create your first cut using prebaked footage
cp recipes/examples/dev-default.yaml recipes/my-first-cut.yaml

# 3. Compile it (uses existing footage, no API keys needed)
./ch compile --recipe recipes/my-first-cut.yaml
# Or: uv run python -m scripts.compile_cut --recipe recipes/my-first-cut.yaml

# 4. Watch your cut
open output/cuts/[cut_id]/episodes/ep00_checking_in.mp4

# 5. (Optional) Generate AI-powered cover art (requires OPENAI_API_KEY)
export OPENAI_API_KEY="your-key-here"
./ch cover-art --type all
```

**Your Cut URI** is in the manifest — share it to make your timeline referenceable.
**Your Cover Art** is in `output/cover_art/` — use for YouTube, social media.

### Path B: Generate New Footage

**Prerequisites**: Python 3.11+, OpenAI API access (Sora-2-Pro), Git LFS

```bash
# Extract prompts from master script
uv run python -m scripts.extract_prompts --episode ep00_checking_in

# Generate video
uv run python -m scripts.generate_video --episode ep00_checking_in

# Review draft
open episodes/ep00_checking_in/renders/drafts/latest.mp4
```

---

## 🔧 CLI Reference

The `ch` command provides a unified interface for all Claude Holiday operations:

### Available Commands

```bash
ch compile      # Compile a complete cut from recipe
ch candidates   # Generate candidate renders (no stitching)
ch select       # Create selection templates from candidates
ch bundle       # Pack cut into release bundle
ch ytmeta       # Generate YouTube metadata JSON
ch cover-art    # Generate cover art assets (thumbnails, banners, title cards)
```

### Usage Examples

**Compile a cut:**
```bash
./ch compile --recipe recipes/my-timeline.yaml
```

**Generate candidates for review:**
```bash
./ch candidates --recipe recipes/my-timeline.yaml
# Creates multiple renders per scene in output/tmp/<cut_id>/
```

**Create selection templates:**
```bash
./ch select --cut-manifest output/cuts/<cut_id>/manifest/cut.manifest.json
# Generates episodes/<ep>/renders/selections/<cut_id>.yaml for each episode
```

**Bundle for release:**
```bash
./ch bundle --cut-manifest output/cuts/<cut_id>/manifest/cut.manifest.json
# Creates output/releases/ClaudeHoliday_<cut_id>.zip
```

**Generate YouTube metadata:**
```bash
./ch ytmeta --cut-manifest output/cuts/<cut_id>/manifest/cut.manifest.json
# Creates output/cuts/<cut_id>/manifest/youtube.metadata.json
```

**Generate cover art (requires OPENAI_API_KEY):**
```bash
export OPENAI_API_KEY="your-key-here"
./ch cover-art --type all
# Creates thumbnails, banners, title cards in output/cover_art/

# Generate specific asset:
./ch cover-art --type thumbnail --episode EP05

### Command Details

**`ch compile --recipe <path>`**
- Compiles episodes from an RCFC recipe
- Applies winner selections if available
- Outputs to `output/episodes/<episode_id>/`

**`ch candidates --recipe <path>`**
- Generates multiple candidate renders per scene
- Controlled by `provider.options.num_candidates` in recipe
- Skips stitching (for review workflow)
- Outputs to `output/tmp/<cut_id>/`

**`ch select --cut-manifest <path>`**
- Generates selection YAML templates from candidates
- One file per episode in `episodes/<ep>/renders/selections/`
- Edit these to set `winner_index` per scene
- Then recompile with `ch compile`

**`ch bundle --cut-manifest <path> [--include episodes] [--out dir]`**
- Packages compiled cut into a ZIP bundle
- Includes: videos, manifests, metadata
- Default output: `output/releases/`

**`ch ytmeta --cut-manifest <path>`**
- Generates YouTube-ready metadata JSON
- Title, description, tags, category
- Based on recipe metadata and cut URI

**`ch cover-art [options]`**
- Generates AI-powered cover art using OpenAI's image models
- Requires: `OPENAI_API_KEY` environment variable
- Options:
  - `--type [all|title|thumbnail|banner|social]` (default: all)
  - `--episode <EP##>` (for thumbnails, default: EP00)
  - `--title <text>` (main title, default: CLAUDE HOLIDAY)
  - `--subtitle <text>` (subtitle, default: A COMPOSABLE MICRO-SERIES)
  - `--model <model>` (OpenAI image generation model, optional)
- Outputs to `output/cover_art/`
- Assets include:
  - YouTube thumbnails (1280x720)
  - YouTube channel banner (2560x1440)
  - Title cards for videos (1080x1920)
  - Social media squares (1080x1080)

---

## 📜 License

© 2025 John Swords — All rights semi-reserved

**Disclaimer**: Any resemblance to Hallmark® films or Anthropic Claude™ is purely coincidental and unintentionally hilarious. No trademarks were harmed in the making of this micro-series.

---

## 🤝 How to Participate

Claude Holiday is designed for community participation. Here's how:

### 🎬 Create Your Timeline
- Fork the repo
- Copy an example recipe from `recipes/examples/`
- Edit the YAML to choose episodes, overlays, audience, ending, provider
- Run `./ch compile --recipe your_recipe.yaml`
- Generate cover art: `export OPENAI_API_KEY="your-key-here" && ./ch cover-art --type all`
- Share your Cut URI and publish your videos

### 🎥 Contribute Footage
- Create new episode variants or alternate scenes
- Submit via PR to expand the available content pool
- Others can then reference your footage in their recipes

### 📝 Add Episode Ideas
- Write new episode scripts following the master script format
- Expand the story universe with bonus content
- Create prompts for new scenes

### 🌍 Register Your Timeline
- Open a PR adding your timeline to `docs/timelines.md`
- Include your Cut URI, description, and video links
- Join the growing multiverse of interpretations

**Code of Conduct**: Be excellent to each other. Credit the concept. No hate or harassment. Keep the satire kind and constructive. See [`docs/charter.md`](docs/charter.md) for full guidelines.

---

**Status**: Pre-production (Prime timeline) | Community timelines welcome now

**For creators**: Episode 0 prompt writing → Draft render → Iterate
**For community**: Fork, customize recipes, publish your timeline

*Let's build something that makes people laugh while making them think — together, in infinite variations.*

---

### 🎥 Candidate Review Flow (generate → review → stitch)

You can generate multiple candidates per scene, review them, choose winners, and then stitch the episode.

1) Generate candidates only (no stitching yet)
```bash
./ch candidates --recipe recipes/examples/dev-default.yaml
# Note manifest path printed; keep the cut_id handy
```

2) Create selections YAMLs (one per episode) from the candidates
```bash
./ch select --cut-manifest output/cuts/<cut_id>/manifest/cut.manifest.json
# Generates: episodes/<ep>/renders/selections/<cut_id>.yaml
# Also creates: output/cuts/<cut_id>/review.html (visual contact sheet)
```

**Selection file format:**
- **Path pattern**: `episodes/<ep_id>/renders/selections/<cut_id>.yaml`
- **Winner index**: 1-based (1 = first candidate, 2 = second, etc.)
- **Default**: `winner_index: 1` for all scenes

Edit the YAML files to set `winner_index` per scene based on the HTML contact sheet review.

3) Compile using your selections (just run compile again; it picks up selections automatically)
```bash
./ch compile --recipe recipes/examples/dev-default.yaml
```

Tips:
- Set `provider.options.num_candidates` in your recipe to control how many candidates are generated per scene.
- Prebaked provider will reuse any existing footage and duplicate into candidate slots if needed.
- Overlays are applied only to selected winners so your review clips stay clean.

---

## 🧭 Understanding Timelines

**What's a timeline?** Each distinct cut or interpretation of Claude Holiday. Think of it as a parallel universe version of the series.

### Timeline Types

**Prime Timeline** (`timeline: "Prime 2025"`)
- The main repository's default cut for 2025
- Created by John Swords
- Reference implementation, not canonical

**Community Timelines** (e.g., `timeline: "alice/dev-glossary-extended"`)
- Your fork + custom recipe = your timeline
- Equally valid as any other interpretation
- Can remix episodes, change overlays, reorder, add commentary
- Each gets a unique Cut URI for reference

### Publishing Your Timeline

1. **Label it**: Add `timeline: "YourName/description"` to your RCFC recipe
2. **Generate it**: Run `compile_cut.py` to get your Cut URI
3. **Share it**: Upload videos to YouTube/Vimeo with Cut URI in description
4. **Register it**: PR to `docs/timelines.md` with your timeline details

**Why this matters**: No single "official" version means every interpretation contributes to the cultural conversation. Your cut is part of the canon.

See [`docs/charter.md`](docs/charter.md) for the full philosophy on timelines and composable media.

---

## 🛠️ Development Setup

This project uses **uv** for fast, reliable Python dependency management. It replaces pip, virtualenv, and other tools with a single fast solution.

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone [your-fork]
cd claude_holiday

# Install all dependencies (creates virtual environment automatically)
uv sync

# Install development dependencies
uv sync --group dev
```

### Development Commands

We provide a `Makefile` with common development tasks:

```bash
make help        # Show all available commands
make test        # Run test suite
make lint        # Check code quality with ruff
make format      # Auto-format code
make typecheck   # Run type checking with mypy
make coverage    # Generate test coverage report
make clean       # Remove build artifacts
```

### Running Scripts

All scripts can be run through uv:

```bash
# Using uv directly
uv run python -m scripts.compile_cut --recipe recipes/my-cut.yaml
uv run python -m scripts.apply_overlays --input video.mp4

# Using Makefile shortcuts
make compile-cut
make apply-overlays

# Activate virtual environment for direct access
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows
```

### Why uv?

- **10-100x faster** than pip and pip-tools
- **Built-in virtual environment** management
- **Deterministic** dependency resolution with lock files
- **Cross-platform** with consistent behavior
- **Single tool** replaces pip, virtualenv, pip-tools, and more

---

## 📅 Annual Cadence

Claude Holiday is designed as an **annual creative project**. Each year:
- New episodes reflect what's happened in AI/software development
- New jokes, commentary, and cultural moments
- Same community-driven foundation
- Prior year timelines remain referenceable

**Think of it like**: An annual variety show where last year's episodes are archived but accessible, and this year's content is fresh. Your 2025 timeline will always be your 2025 timeline—frozen in time, infinitely reproducible.

This creates a growing **archive of AI culture** through the lens of satire, year after year.
