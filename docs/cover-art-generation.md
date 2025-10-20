# Cover Art Generation for Claude Holiday

Claude Holiday uses AI-powered generation to create professional cover art assets using OpenAI's image generation models.

## Overview

The cover art system generates professional artwork based on the visual descriptions from `docs/master_script.md`, maintaining consistency with the Hallmark holiday aesthetic described in the series.

## Setup

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"
```

## Usage

### Using the ch command (recommended)

Generate all cover art:
```bash
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

Choose OpenAI model:
```bash
./ch cover-art --type all --model gpt-image-1
```

### Using the script directly

```bash
python3 scripts/generate_cover_art.py \
  --type all \
  --model dall-e-3 \
  --episode EP01 \
  --title "CLAUDE HOLIDAY" \
  --subtitle "A COMPOSABLE MICRO-SERIES"
```

## Visual Style

The cover art system generates images matching the master script's aesthetic:

- **Setting**: Cozy Evergreen Inn with fireplace, vintage registry, snow through windows
- **Palette**: Amber, cream, mahogany, forest green with brass accents
- **Style**: Warm Hallmark domestic drama, 3200K fireplace key light, cool exterior rim light
- **Characters**: Professional woman in charcoal coat, innkeeper in red flannel shirt

## Asset Types

The system generates four types of assets:

1. **YouTube Thumbnails** (1280x720)
   - Eye-catching designs with episode numbers
   - Features characters at inn registry desk

2. **YouTube Channel Banner** (2560x1440)
   - Wide panoramic view of Evergreen Inn exterior
   - Golden hour lighting with warm windows

3. **Title Cards** (1080x1920)
   - Vertical format for video openings
   - Deep crimson to golden gradient with snow effect

4. **Social Media Squares** (1080x1080)
   - Instagram-ready format
   - Cozy fireplace scene with CH monogram

## Model Options

### gpt-image-1 (Recommended)
- Latest model (2025)
- Cost: $0.015 per image
- Better multimodal understanding
- Sizes: 1024x1024, 1024x1536, 1536x1024

### DALL-E 3
- Established model
- Cost: $0.040 per image
- More artistic variations
- Sizes: 1024x1024, 1024x1792, 1792x1024

## Cost Considerations

Generating a full set (4 images):
- **gpt-image-1**: ~$0.06
- **DALL-E 3**: ~$0.16

For a 12-episode series with unique thumbnails:
- **gpt-image-1**: ~$0.24
- **DALL-E 3**: ~$0.64

## Best Practices

1. **Generate Multiple Variations**: Each generation is unique, create several and choose the best
2. **Use Consistent Model**: Stick with one model per timeline for visual consistency
3. **Save Your Favorites**: AI generations can't be exactly reproduced
4. **Custom Prompts**: Fork and modify `generate_cover_art.py` for your timeline's aesthetic

## Composability

Since Claude Holiday is community-composable media, different timelines can customize the visual prompts:

- Modify prompts in `generate_cover_art.py` to match your interpretation
- Adjust color palettes, settings, or character descriptions
- Create entirely different aesthetics while maintaining the format

## Troubleshooting

### "API key not found"
Set your OpenAI API key:
```bash
export OPENAI_API_KEY="sk-..."
```

### "Model not available"
Some models require special access. Apply at platform.openai.com

### "Size not supported"
Different models support different sizes. The script handles resizing automatically using FFmpeg.

### Images look different than expected
The AI generates unique variations each time. Generate multiple versions and select your favorite.

## Output Location

All generated assets are saved to:
```
output/cover_art/
├── title_card.png
├── thumbnail_ep00.png
├── thumbnail_ep01.png
├── youtube_banner.png
└── social_square.png
```