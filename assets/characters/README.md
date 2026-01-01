# Character Reference Frames

This directory stores photorealistic reference frames extracted from Episode 0 renders. These frames are used to create Sora cameos for character consistency across all episodes.

## Purpose

The Sora web app's "cameo" feature requires reference images to maintain character identity. By extracting frames from Episode 0 (the character genesis episode), we establish the visual ground truth for all recurring characters.

## Files

| Filename | Character | Description |
|----------|-----------|-------------|
| `emma_protagonist_ref.png` | Emma | Professional woman, ~32, auburn hair, 5'6" athletic build |
| `cody_innkeeper_ref.png` | Cody | Innkeeper, early 40s, 6'1", salt-pepper beard, red flannel |
| `claude_love_interest_ref.png` | Claude | Primary love interest (extracted from Ep01) |
| `sonny_chaos_ref.png` | Sonny | Chaotic replacement (extracted from Ep05) |

## Extraction Guidelines

When extracting reference frames:

1. **Face visibility**: Choose frames where face is clearly visible (front or 3/4 angle preferred)
2. **Good lighting**: Avoid underexposed or overexposed frames
3. **Minimal motion blur**: Select still moments, not mid-action
4. **Costume consistency**: Match the costume described in episode manifests
5. **Resolution**: Export at highest available quality (1080x1920 source)

## Cameo Naming Convention

When creating cameos in Sora web app, use these exact names:

- `emma_protagonist`
- `cody_innkeeper`
- `claude_love_interest`
- `sonny_chaos`

Consistent naming ensures prompts can reference cameos reliably across all episodes.

## Workflow

1. Render Episode 0 in Sora web app
2. Review render for quality character depictions
3. Extract best frames and save here with `_ref.png` suffix
4. Upload to Sora and create cameos
5. Reference cameos in subsequent episode prompts

See `docs/production-workflow.md` for complete production workflow.
