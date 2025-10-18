# RCFC — Recipe for Cut Format (v0.1.0)

RCFC describes how to compile a specific "cut" of Claude Holiday from episode manifests and optional overlays/captions.

## Goals

- Reproducible: a recipe deterministically defines outputs.
- Addressable: each recipe yields a stable Cut URI.
- Accessible: tweak YAML, not code.

## Schema (v0.1.0)

- `schema_version` (string): "0.1.0"
- `metadata` (object):
  - `title` (string): human title of the cut
  - `author` (string, optional)
  - `created` (string, ISO 8601)
- `timeline` (string, optional): label for this cut/timeline (e.g., "Prime 2025" or "alice/dev-glossary-extended")
- `project` (object):
  - `name` (string) — e.g., "Claude Holiday"
  - `repo_url` (string)
- `source` (object):
  - `commit_sha` (string) — git commit used
- `audience_profile` (string): "general" | "dev" | "custom"
- `scope` (object):
  - `include_episodes` (array of strings) — e.g., ["ep00_checking_in"]
  - `include_bonus` (array of strings, optional)
- `overlays` (object):
  - `enabled` (boolean)
  - `density` (string): "low" | "medium" | "high"
  - `theme` (string)
- `ending` (string): "agnostic" | "meta"
- `captions` (object):
  - `track` (string): "general" | "dev_glossary"
  - `language` (string): "en-US"
- `render` (object):
  - `fps` (integer): e.g., 24
  - `aspect` (string): "9:16"
  - `resolution` (string): "1080x1920"
- `audio` (object, optional):
  - `ambiences` (array of strings)
  - `stingers` (array of strings)
- `provider` (object):
  - `name` (string): "prebaked" | "dummy" | "sora"
  - `options` (object): provider-specific options
- `social` (object, optional):
  - `platforms` (array): ["youtube-short","tiktok","reels"]
  - `trims` (object): platform-specific trim hints (optional)

See JSON Schema at: `schemas/rcfc.schema.json`.

## Example

```yaml
schema_version: "0.1.0"
metadata:
  title: "Claude Holiday — Dev Default"
  author: "Your Name"
  created: "2025-01-01T12:00:00Z"
timeline: "Prime 2025"
project:
  name: "Claude Holiday"
  repo_url: "https://github.com/YOURNAME/claude_holiday"
source:
  commit_sha: "<git sha here>"
audience_profile: "dev"
scope:
  include_episodes: ["ep00_checking_in"]
overlays:
  enabled: true
  density: medium
  theme: brass
ending: "agnostic"
captions:
  track: "dev_glossary"
  language: "en-US"
render:
  fps: 24
  aspect: "9:16"
  resolution: "1080x1920"
provider:
  name: "dummy"
  options: {}
```

## Notes

- Providers:
  - `prebaked`: reuse existing scene clips under episodes/…/renders
  - `dummy`: generate solid color placeholder clips via ffmpeg (no vendor access required)
  - `sora`: future support (not required to participate)
- Overlays:
  - Baked into output during compile; distribution to YouTube is trivial.
- Cut URI:
  - Deterministically built from recipe hash + commit sha. See `docs/specs/cut-uri.md`.