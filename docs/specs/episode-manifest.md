# Episode Manifest Spec

Episode manifests define the content structure for each episode. They live at `episodes/{episode_id}/episode.yaml` and are consumed by providers during cut compilation.

## Relationship to RCFC

- **RCFC recipes** define *how* to compile (provider, overlays, audience)
- **Episode manifests** define *what* to compile (scenes, prompts, overlays)

This separation allows the same episode content to be compiled differently based on recipe configuration.

## Schema

### Required Fields

```yaml
episode_id: string     # Directory name, e.g., "ep00_checking_in"
title: string          # Display title, e.g., "Episode 00 — Checking In"
scenes: array          # Ordered list of scene objects
```

### Optional Fields

```yaml
captions_cues: array   # Caption timing hints (usually empty)
```

## Scene Structure

Each scene in the `scenes` array requires:

```yaml
scenes:
  - id: string              # Unique within episode, e.g., "s1", "s2"
    title: string           # Human-readable scene name
    duration_sec: number    # Scene duration in seconds
    sora_prompt: string     # Multi-line Sora-2-Pro generation prompt
    overlays: array         # Optional overlay definitions
```

### Scene ID Convention

Use `s1`, `s2`, `s3`, etc. for sequential scenes. These IDs are referenced in render selection files and candidate outputs.

### Duration

Duration in seconds determines:
- FFmpeg clip length for dummy/prebaked providers
- Sora generation length target
- Overlay timing validation

## Sora Prompt Structure

The `sora_prompt` field uses YAML multi-line syntax (`>`) and follows a structured format:

```yaml
sora_prompt: >
  STYLE SPINE — [genre/mood]; palette [colors]; [emotional arc]
  SUBJECT — [character description]; [wardrobe]; [physical details]
  SET & LIGHT — [location]; [lighting setup with color temp]; [atmosphere]
  CAMERA — [movement]; [height]; [lens feel]; [DoF]
  ACTION BEATS (0.00–{duration}s)
    0.00–X.X  [action description]
    X.X–Y.Y   [next beat]
    ...
  AUDIO — [ambient sounds]; [specific audio cues]
  CONTINUITY — [consistency notes]; [avoid items]
  Dialogue:
  - Character (emotion, timing): "Line"
```

### Prompt Sections

| Section | Purpose |
|---------|---------|
| STYLE SPINE | Genre, color palette, emotional journey |
| SUBJECT | Character descriptions with physical details |
| SET & LIGHT | Location, lighting setup, color temperatures |
| CAMERA | Movement, framing, lens characteristics |
| ACTION BEATS | Timestamped choreography (required for consistency) |
| AUDIO | Sound design guidance |
| CONTINUITY | Cross-scene consistency requirements |
| Dialogue | Character lines with timing and emotional notes |

### Compact Prompt Style

For simpler scenes, a condensed format is acceptable:

```yaml
sora_prompt: >
  9:16 vertical. Professional woman sits alone on inn lobby couch
  at 2:59am, exhausted, coffee mug in hand, watching clock intently.
  Clock visible showing seconds ticking toward 3:00am. Warm lobby
  lighting contrasts with dark windows. 24fps, anticipation building.
```

## Overlays

Scene-level overlays are defined per-scene and merged with recipe-level overlay settings during compilation.

```yaml
overlays:
  - spec: string           # Overlay identifier, e.g., "rate_limit_error"
    text: string           # Display text
    start_sec: number      # When overlay appears within scene
    duration_sec: number   # How long overlay displays
    position: string       # Screen position
    track: string          # Overlay track, e.g., "dev_glossary"
```

### Position Values

| Value | Location |
|-------|----------|
| `top_left` | Upper left corner |
| `top_right` | Upper right corner |
| `bottom_left` | Lower left corner |
| `bottom_right` | Lower right corner |
| `center` | Center of frame |

### Overlay Tracks

Tracks group overlays for filtering:

- `dev_glossary` — Technical/developer humor overlays
- `general` — General audience overlays

Overlays are only rendered when the RCFC recipe enables overlays and matches the track's audience profile.

### Example with Overlays

```yaml
- id: "s2"
  title: "The Explanation"
  duration_sec: 10
  sora_prompt: >
    9:16 vertical. Man delivers technical explanation...
  overlays:
    - spec: "rate_limit_error"
      text: "HTTP 429: Rate limit exceeded"
      start_sec: 2.0
      duration_sec: 2.5
      position: "bottom_left"
      track: "dev_glossary"
    - spec: "cron_reset"
      text: "cron(0 3 * * FRI)"
      start_sec: 6.0
      duration_sec: 2.0
      position: "bottom_right"
      track: "dev_glossary"
```

## Captions Cues

The `captions_cues` field provides timing hints for caption generation. Usually left empty as captions are derived from dialogue timing in prompts:

```yaml
captions_cues: []
```

When populated, format is:

```yaml
captions_cues:
  - start_sec: 2.0
    end_sec: 5.0
    text: "Caption text here"
```

## Complete Example

```yaml
episode_id: "ep00_checking_in"
title: "Episode 00 — Checking In"
scenes:
  - id: "s1"
    title: "Arrival & Stress"
    duration_sec: 8
    sora_prompt: >
      STYLE SPINE — warm Hallmark domestic drama; palette amber/cream/mahogany/forest green; harried to relief
      SUBJECT — professional woman ~32; shoulder-length auburn hair; tailored charcoal coat, designer rolling suitcase
      SET & LIGHT — cozy inn lobby, dusk; warm window key light 3200K + fireplace fill
      CAMERA — handheld follow-through, eye-level; dolly push toward registry desk; 35mm feel; medium DoF f/4
      ACTION BEATS (0.00–8.0s)
        0.00–2.0  she bursts through door; snow dusting shoulders; phone at right ear
        2.0–5.0   pacing left-right 3 steps; gesticulation with left hand
        5.0–6.5   phone lowered; sharp exhale; eyes close; shoulder drop 3 inches
        6.5–8.0   innkeeper rises behind desk; warm smile forms
      CONTINUITY — charcoal coat/auburn hair consistent; avoid signage/legible text
      Dialogue:
      - Woman (frustrated, 2.0–5.0s): "Yes, I'll have the deck reviewed by Monday!"
      - Innkeeper (warm, 6.5–8.0s): "Welcome to Evergreen Inn. Long journey?"
    overlays: []
  - id: "s2"
    title: "The Registry"
    duration_sec: 10
    sora_prompt: >
      ...
    overlays: []
  - id: "s3"
    title: "Relief & Settling"
    duration_sec: 7
    sora_prompt: >
      ...
      Dialogue:
      - (No dialogue - visual storytelling only)
    overlays: []
captions_cues: []
```

## Best Practices

### Sora Prompts

1. **Be specific about timing** — Use ACTION BEATS with exact timestamps
2. **Maintain continuity** — Reference wardrobe, hair, props across scenes
3. **Include audio guidance** — Even though audio is separate, it helps coherence
4. **Avoid readable text** — Sora struggles with text generation
5. **Specify color temperatures** — 2700K-3200K for warm Hallmark feel

### Scene Structure

1. **Keep scenes 7-12 seconds** — Short attention span format
2. **End on emotional beats** — Each scene should have clear resolution
3. **Plan for vertical** — 9:16 aspect ratio, compose for mobile

### Overlays

1. **Don't overlap timing** — Overlays on same track shouldn't conflict
2. **Leave breathing room** — Start 1-2 seconds into scene, end before cut
3. **Match track to content** — Technical humor on `dev_glossary` track

## File Locations

- Episode manifests: `episodes/{episode_id}/episode.yaml`
- Render outputs: `episodes/{episode_id}/renders/`
- Winner selections: `episodes/{episode_id}/renders/selections/{cut_id}.yaml`

## See Also

- [RCFC Spec](rcfc.md) — Recipe format for compilation
- [Cut URI Spec](cut-uri.md) — Deterministic cut identification
