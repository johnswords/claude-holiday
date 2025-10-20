# Style Guides for Claude Holiday

This directory contains the style guide for generating consistent cover art and visual assets across the Claude Holiday project.

## Available Style Files

- **base.json** - Shared fundamentals (dimensions, typography, spacing)
- **default.json** - Claude Holiday visual style based on master script's Hallmark aesthetic

## How It Works

1. **Base Extension**: The default style guide extends from `base.json`, inheriting shared properties
2. **Cover Art Generation**: AI-powered generation using OpenAI's image models (dall-e-3, gpt-image-1)

   Generates:
   - YouTube thumbnails (1280x720)
   - YouTube channel banners (2560x1440)
   - Title cards (1080x1920)
   - Social media squares (1080x1080)

## Usage

### Using the ch command (requires OPENAI_API_KEY):

Generate all cover art:
```bash
export OPENAI_API_KEY="your-key-here"
./ch cover-art --type all
```

Generate specific asset:
```bash
./ch cover-art --type thumbnail --episode EP05
```

Custom text for title cards:
```bash
./ch cover-art \
  --type title \
  --title "MY TIMELINE" \
  --subtitle "A CUSTOM VERSION"
```

Choose OpenAI model (dall-e-3 or gpt-image-1):
```bash
./ch cover-art --type all --model gpt-image-1
```

### Using the script directly:

```bash
export OPENAI_API_KEY="your-key-here"
python3 scripts/generate_cover_art.py --type all --model dall-e-3
```

## Composability

Since Claude Holiday is community-composable media, different timelines can customize the visual prompts and style. Forks can modify the prompts in `generate_cover_art.py` to match their interpretation's aesthetic.