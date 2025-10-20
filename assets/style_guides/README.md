# Style Guides for Claude Holiday

This directory contains theme-specific style guides for generating consistent cover art and visual assets across the Claude Holiday project.

## Available Themes

- **base.json** - Shared fundamentals (dimensions, typography, spacing)
- **brass.json** - Warm, cozy Hallmark holiday aesthetic (default)
- **dev.json** - Developer terminal aesthetic with monospace fonts
- **corporate.json** - Sterile corporate aesthetic (Olympus/Atlassian parody)

## How It Works

1. **Base Extension**: Theme guides extend from `base.json`, inheriting shared properties
2. **RCFC Integration**: Recipe files reference themes via `overlays.theme` field
3. **Cover Art Generation**: The `ch cover-art` command (via `generate_cover_art.py`) uses these guides to create:
   - YouTube thumbnails (1280x720)
   - YouTube channel banners (2560x1440)
   - Title cards (1080x1920)
   - Social media squares (1080x1080)

## Creating a New Theme

1. Copy an existing theme file
2. Set `"extends": "base"` to inherit fundamentals
3. Override palette, typography, and mood as needed
4. Run: `./ch cover-art --theme your-theme`

## Theme Selection in Recipes

```yaml
overlays:
  enabled: true
  theme: brass  # or dev, corporate, your-custom-theme
```

## Composability

Since Claude Holiday is community-composable media, different timelines can have different visual identities. Your fork can introduce new themes that match your interpretation's aesthetic.

## Usage

### Using the ch command (recommended):

Generate all cover art for a theme:
```bash
./ch cover-art --theme brass --type all
```

Generate specific asset:
```bash
./ch cover-art --theme dev --type thumbnail --episode EP05
```

Custom text for title cards:
```bash
./ch cover-art --theme corporate \
  --type title \
  --title "MY TIMELINE" \
  --subtitle "A CUSTOM VERSION"
```

### Using the script directly:

```bash
python3 scripts/generate_cover_art.py --theme brass --type all
python3 scripts/generate_cover_art.py --theme dev --type thumbnail --episode EP05
```