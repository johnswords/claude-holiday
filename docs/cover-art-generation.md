# Cover Art Generation for Claude Holiday

Claude Holiday provides two methods for generating cover art: **basic FFmpeg** and **AI-powered** generation.

## Quick Comparison

| Feature | FFmpeg (`generate_cover_art.py`) | AI (`generate_cover_art_ai.py`) |
|---------|-----------------------------------|----------------------------------|
| **Quality** | Basic colored backgrounds with text | Professional AI-generated artwork |
| **Consistency** | Always identical output | Unique variations each time |
| **Cost** | Free | $0.015-0.040 per image |
| **API Key** | Not required | OpenAI API key required |
| **Speed** | Instant | 5-10 seconds per image |
| **Visual Appeal** | Simple gradients | Photorealistic scenes |

## Basic FFmpeg Generation

Quick placeholder graphics using simple color gradients and text overlays.

### Usage
```bash
# Using ch command
./ch cover-art --theme brass --type all

# Direct script
python3 scripts/generate_cover_art.py --theme brass --type all
```

### Output
- Simple colored backgrounds (orange for brass, black for dev, white for corporate)
- Text overlays with title and subtitle
- Consistent but very basic appearance

### Best For
- Quick placeholders
- Testing pipeline
- When API access isn't available

## AI-Powered Generation

Professional cover art using OpenAI's image generation models, with visuals based on the actual scenes from `docs/master_script.md`.

### Setup
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-key-here"
```

### Usage
```bash
# Using gpt-image-1 (newer, cheaper: $0.015/image)
python3 scripts/generate_cover_art_ai.py \
  --theme brass \
  --type all \
  --model gpt-image-1

# Using DALL-E 3 (established: $0.040/image)
python3 scripts/generate_cover_art_ai.py \
  --theme brass \
  --type all \
  --model dall-e-3

# Custom text for specific timeline
python3 scripts/generate_cover_art_ai.py \
  --theme corporate \
  --type title \
  --title "OLYMPUS ACQUISITION" \
  --subtitle "A CORPORATE TRAGEDY" \
  --model gpt-image-1
```

### Theme Visuals

#### Brass Theme
- **Setting**: Cozy Evergreen Inn with fireplace, vintage registry, snow through windows
- **Palette**: Amber, cream, mahogany, forest green with brass accents
- **Style**: Warm Hallmark domestic drama, golden hour lighting
- **Characters**: Professional woman in charcoal coat, innkeeper in red flannel

#### Dev Theme
- **Setting**: Dark terminal interface with code snippets
- **Palette**: Green phosphor text on black, Matrix-style digital rain
- **Style**: Cyberpunk developer environment, CRT monitor aesthetic
- **References**: Rate limits, API calls, error messages

#### Corporate Theme
- **Setting**: Modern office with glass conference rooms, whiteboards
- **Palette**: Corporate blue, gray, white, sterile fluorescent lighting
- **Style**: Tech company aesthetic, PowerPoint presentations
- **References**: The Software Company of New York, Olympus Corporation

### Model Comparison

**gpt-image-1** (Recommended)
- Latest model (2025)
- 75% cheaper than DALL-E 3
- Better multimodal understanding
- Sizes: 1024x1024, 1024x1536, 1536x1024

**DALL-E 3**
- Established model
- More artistic variations
- Sizes: 1024x1024, 1024x1792, 1792x1024

### Output Examples

Generated assets maintain visual consistency with the actual video content:

- **Title Cards**: Vertical format matching opening title sequence
- **Thumbnails**: Eye-catching YouTube designs with episode numbers
- **Banners**: Wide panoramic views for channel headers
- **Social Squares**: Instagram-ready 1:1 format

### Best Practices

1. **Generate Multiple Variations**: Each generation is unique, create several and choose the best
2. **Match Your Timeline's Mood**: Adjust prompts in the script to match your interpretation
3. **Use Consistent Model**: Stick with one model per timeline for visual consistency
4. **Save Your Favorites**: AI generations can't be exactly reproduced

## Extending the System

### Adding Custom Themes

1. Create a new style guide in `assets/style_guides/`:
```json
{
  "name": "your-theme",
  "extends": "base",
  "mood": {
    "keywords": ["your", "theme", "keywords"],
    "lighting": "your lighting style",
    "atmosphere": "your atmosphere"
  },
  "palette": {
    "primary": {...},
    "secondary": {...}
  }
}
```

2. Update `generate_cover_art_ai.py` to add theme-specific prompts based on your visual style

3. Generate assets:
```bash
python3 scripts/generate_cover_art_ai.py --theme your-theme
```

### Community Contributions

Different timelines can have completely different visual identities:
- **Romantic Timeline**: More Hallmark, less tech
- **Cyberpunk Timeline**: All terminal aesthetics
- **Documentary Timeline**: Behind-the-scenes style
- **Retro Timeline**: 80s VHS aesthetic

## Cost Considerations

Generating a full set (4 images) costs:
- **gpt-image-1**: ~$0.06
- **DALL-E 3**: ~$0.16

For a 12-episode series with unique thumbnails:
- **gpt-image-1**: ~$0.24
- **DALL-E 3**: ~$0.64

## Troubleshooting

### "API key not found"
Set your OpenAI API key:
```bash
export OPENAI_API_KEY="sk-..."
```

### "Model not available"
Some models require special access. Apply at platform.openai.com

### "Size not supported"
Different models support different sizes. The script handles resizing automatically.

### Images look wrong
Check that your theme's prompts in `generate_cover_art_ai.py` match your intended aesthetic.

## Integration with ch Command

The `ch cover-art` command currently uses the basic FFmpeg generator. To use AI generation, run the script directly with your API key set.

Future updates may integrate AI generation into the ch command with an `--ai` flag.