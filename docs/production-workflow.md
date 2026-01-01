# Manual Sora Production Workflow

This document describes the production workflow for creating Claude Holiday episodes using the Sora web application.

---

## Overview

Claude Holiday uses a **manual production workflow** via the Sora web app rather than automated API compilation. This approach is required because:

1. **Duration Requirements**: Sora API cannot generate 25-second clips; only the web app supports this duration
2. **Photorealistic Keyframes**: API cannot use photorealistic keyframes generated from image models
3. **Character Persistence**: The web app's "cameo" feature allows characters established in Episode 0 to persist consistently across all 11 episodes

### Episode Structure

Each episode is **25 seconds all-in**, which includes:
- 1 second for title card (at start)
- 24 seconds of content

Episodes are rendered as **single continuous clips** to maintain visual coherence.

---

## Episode 0: Character Genesis

Episode 0 ("Checking In") serves as the **character genesis episode**. This episode establishes the visual identity of all recurring characters.

### Primary Characters to Extract

| Character | Description | Cameo Name |
|-----------|-------------|------------|
| **Emma** | Professional woman, ~32, auburn hair, 5'6" athletic build | `emma_protagonist` |
| **Cody** | Innkeeper, early 40s, 6'1", salt-pepper beard, red flannel | `cody_innkeeper` |
| **Claude** | Love interest (introduced Ep01) | `claude_love_interest` |
| **Sonny** | Chaotic replacement (introduced Ep05) | `sonny_chaos` |

### Character Genesis Process

1. **Render Episode 0 first** in Sora web app using prompts from `episodes/ep00_checking_in/episode.yaml`

2. **Review renders** for consistent, high-quality character depictions

3. **Extract reference frames** from the best render:
   - Frame where Emma's face is clearly visible (front or 3/4 angle)
   - Frame where Cody's face is clearly visible
   - Save to `assets/characters/` with descriptive names:
     ```
     assets/characters/
     ├── emma_protagonist_ref.png
     ├── cody_innkeeper_ref.png
     └── README.md
     ```

4. **Create cameos in Sora**:
   - Upload reference frames to Sora web app
   - Create cameo for each character
   - Name consistently: `emma_protagonist`, `cody_innkeeper`

---

## Cameo Creation in Sora

### Creating a Cameo from Episode 0 Renders

1. Open Sora web app at [sora.com](https://sora.com)

2. Navigate to your Episode 0 render

3. Find a frame with clear character visibility:
   - Face visible (ideally front or 3/4 view)
   - Good lighting
   - Minimal motion blur

4. Click "Create Cameo" or equivalent in Sora interface

5. Name the cameo consistently:
   - `emma_protagonist` (not "Emma" or "protagonist_emma")
   - `cody_innkeeper`
   - `claude_love_interest`
   - `sonny_chaos`

6. Confirm cameo is saved to your Sora account

### Using Cameos in Subsequent Episodes

When rendering Episodes 1-11, reference cameos in your prompts:

```
STYLE SPINE — warm Hallmark domestic drama; palette amber/cream/mahogany
SUBJECT — [CAMEO: emma_protagonist] wearing charcoal coat;
          [CAMEO: claude_love_interest] in navy peacoat
...
```

Alternatively, use Sora's cameo insertion UI to add characters directly.

---

## Per-Episode Production

### Workflow Summary

```
For each episode (ep01 through ep10):
  1. Load prompts from episodes/{episode_id}/episode.yaml
  2. Open Sora web app
  3. Insert relevant cameos
  4. Request 25-second single-clip render
  5. Review output
  6. Download to episodes/{episode_id}/renders/final/
  7. Rename to {episode_id}_final.mp4
```

### Detailed Steps

1. **Load Episode Prompts**
   ```bash
   # Read the episode manifest
   cat episodes/ep01_first_contact/episode.yaml
   ```

2. **Prepare Sora Prompt**
   - Copy the `sora_prompt` field from each scene
   - For multi-scene episodes, you may need to combine or render as one continuous shot
   - Add cameo references: `[CAMEO: emma_protagonist]`

3. **Configure Render Settings**
   - Duration: 25 seconds
   - Aspect ratio: 9:16 (vertical)
   - Resolution: 1080x1920

4. **Submit Render**
   - Include all relevant cameos
   - Wait for generation (may take several minutes)

5. **Review Output**
   - Check character consistency
   - Verify timing matches episode manifest
   - Ensure no visual artifacts

6. **Download and Organize**
   ```bash
   # Download to appropriate location
   mv ~/Downloads/sora_render.mp4 \
      episodes/ep01_first_contact/renders/final/ep01_first_contact_final.mp4
   ```

---

## Render Organization

Maintain this directory structure for each episode:

```
episodes/
└── ep00_checking_in/
    ├── episode.yaml           # Episode manifest (prompts, timing)
    ├── README.md              # Episode notes
    └── renders/
        ├── drafts/            # Work-in-progress renders
        │   ├── v1_2025-01-01.mp4
        │   └── v2_2025-01-02.mp4
        ├── candidates/        # Multiple options for review
        │   ├── option_a.mp4
        │   ├── option_b.mp4
        │   └── option_c.mp4
        └── final/             # Selected final render
            └── ep00_checking_in_final.mp4
```

### Naming Conventions

| Directory | Purpose | Naming Pattern |
|-----------|---------|----------------|
| `drafts/` | WIP iterations | `v{n}_{date}.mp4` |
| `candidates/` | Review options | `option_{letter}.mp4` or descriptive |
| `final/` | Production-ready | `{episode_id}_final.mp4` |

---

## Quality Review Checklist

Before marking an episode render as final, verify:

- [ ] **Character consistency**: Cameos match across episodes (Emma looks like Emma)
- [ ] **Runtime**: ~25 seconds total
- [ ] **Title card**: Visible/integrated in first 1 second (or confirm title handled separately)
- [ ] **Audio ambience**: Present and appropriate (if applicable)
- [ ] **Visual quality**: No artifacts, glitches, or temporal inconsistencies
- [ ] **Scene intent**: Matches `episode.yaml` description and dialogue timing
- [ ] **Aspect ratio**: 9:16 vertical format
- [ ] **Resolution**: 1080x1920 or higher

### Common Issues and Fixes

| Issue | Diagnosis | Solution |
|-------|-----------|----------|
| Character looks different | Cameo not applied correctly | Re-render with explicit cameo reference |
| Duration wrong | Sora defaulted to different length | Explicitly set 25s in render settings |
| Motion artifacts | Complex camera movement | Simplify camera direction, reduce simultaneous actions |
| Dialogue timing off | Too much action scripted | Reduce action beats, focus on key moments |

---

## Compilation Workflow

After all episodes are rendered manually:

### Step 1: Verify All Finals Exist

```bash
# Check that all episodes have final renders
for ep in episodes/ep*/; do
  final="${ep}renders/final/$(basename $ep)_final.mp4"
  if [ -f "$final" ]; then
    echo "OK: $final"
  else
    echo "MISSING: $final"
  fi
done
```

### Step 2: Create Production Recipe

Create or update `recipes/prime-2025.yaml`:

```yaml
schema_version: "0.1.0"
metadata:
  title: "Claude Holiday — Prime 2025"
  author: "John Swords"
  created: "2025-01-01T00:00:00Z"
timeline: "Prime 2025"
project:
  name: "Claude Holiday"
  repo_url: "https://github.com/johnswords/claude_holiday"
source:
  commit_sha: "HEAD"
audience_profile: "general"
scope:
  include_episodes:
    - "ep00_checking_in"
    - "ep01_first_contact"
    - "ep02_absolutely_right"
    - "ep03_great_question"
    - "ep04_too_many_cocoas"
    - "ep05_claude_limit"
    - "ep06_innkeepers_shoulder"
    - "ep07_slow_and_steady"
    - "ep08_while_you_were_sleeping"
    - "ep09_the_workspace"
    - "ep10_opus_reloaded"
overlays:
  enabled: true
  density: medium
  theme: default
ending: "agnostic"
captions:
  track: "general"
  language: "en-US"
render:
  fps: 24
  aspect: "9:16"
  resolution: "1080x1920"
provider:
  name: "prebaked"  # Uses renders from episodes/*/renders/final/
  options: {}
social:
  platforms: ["youtube_shorts", "instagram_reels", "tiktok"]
  trims: {}
```

### Step 3: Compile Cut

```bash
# Compile using prebaked provider (reads from renders/final/)
./ch compile --recipe recipes/prime-2025.yaml

# Output will be in:
# output/cuts/{cut_id}/
```

### Step 4: Bundle for Release

```bash
# Create release bundle
./ch bundle --cut-manifest output/cuts/{cut_id}/manifest/cut.manifest.json

# Creates: output/releases/ClaudeHoliday_{cut_id}.zip
```

---

## Troubleshooting

### Cameo Not Working

**Symptoms**: Character looks completely different in new episode

**Diagnosis**:
1. Check cameo is properly saved in Sora account
2. Verify cameo name matches exactly in prompt
3. Confirm cameo was created from clear reference frame

**Solution**:
1. Re-extract reference frame from Episode 0
2. Recreate cameo with cleaner frame
3. Test with simple prompt before full episode

### Need to Re-Render Single Episode

```bash
# 1. Move old final to drafts
mv episodes/ep05_claude_limit/renders/final/ep05_claude_limit_final.mp4 \
   episodes/ep05_claude_limit/renders/drafts/old_final_$(date +%Y%m%d).mp4

# 2. Re-render in Sora web app

# 3. Download new render to final/
mv ~/Downloads/new_render.mp4 \
   episodes/ep05_claude_limit/renders/final/ep05_claude_limit_final.mp4

# 4. Re-compile
./ch compile --recipe recipes/prime-2025.yaml
```

### Continuity Issues Across Episodes

**Problem**: Character appearance drifts across episodes

**Solution**:
1. Always use same cameo reference (don't create new ones)
2. Include explicit continuity notes in prompts:
   ```
   CONTINUITY — [CAMEO: emma_protagonist] wearing same charcoal coat
   from Episode 0; auburn hair shoulder-length; maintain athletic build
   ```
3. If severe drift, consider:
   - Re-rendering affected episodes
   - Creating stronger reference frames
   - Using multiple reference angles in cameo

### Audio Sync Issues

**Problem**: Ambience doesn't match scene mood

**Note**: Sora generates video; audio may need post-processing

**Options**:
1. Accept Sora's generated audio
2. Apply overlays via `./ch compile` with audio settings
3. Post-process with external audio tools if needed

---

## Reference

### Episode Index

| ID | Title | Key Characters |
|----|-------|----------------|
| ep00 | Checking In | Emma, Cody |
| ep01 | First Contact | Emma, Claude |
| ep02 | Absolutely Right in Aspen | Emma, Claude |
| ep03 | Great Question, Holly! | Emma, Claude |
| ep04 | Too Many Cocoas | Emma, Claude |
| ep05 | Claude Limit | Emma, Claude, Sonny (intro) |
| ep06 | The Innkeeper's Shoulder | Emma, Cody |
| ep07 | Slow and Steady | Emma, Cody |
| ep08 | While You Were Sleeping | Emma, Sonny |
| ep09 | The Workspace | Emma, Sonny |
| ep10 | Opus Reloaded | Emma, Claude |

### File Locations

- Episode manifests: `episodes/{ep_id}/episode.yaml`
- Sora prompts: Within episode manifests
- Final renders: `episodes/{ep_id}/renders/final/{ep_id}_final.mp4`
- Character references: `assets/characters/`
- Production recipes: `recipes/`

### CLI Commands

```bash
./ch compile --recipe <recipe>        # Compile cut from recipe
./ch candidates --recipe <recipe>     # Generate candidates (dummy/sora)
./ch select --cut-manifest <manifest> # Create selection templates
./ch bundle --cut-manifest <manifest> # Pack release bundle
./ch ytmeta --cut-manifest <manifest> # Generate YouTube metadata
```
