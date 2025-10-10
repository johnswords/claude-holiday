# Episode 00 — "Checking In"

**Status**: Pre-production

## Synopsis
City Girl arrives at small-town inn, meets Cody the innkeeper who demonstrates perfect memory and context retention.

## Production Notes
- Introduces Cody (GPT Codex) character
- Establishes her baseline: stressed, overworked
- No romantic tension yet

## Workflow
1. Extract scene details from `docs/master_script.md`
2. Write individual Sora-2-Pro prompts in `prompts/`
3. Generate test renders → `renders/drafts/`
4. Iterate on prompts
5. Final render → `renders/final/`
6. Master export → `../../output/episodes/`

## Files
- `script.md` - Episode-specific script extract
- `prompts/` - Sora-2-Pro generation prompts
  - `01_stinger.txt`
  - `02_title_card.txt`
  - `03_main_scene.txt`
  - `04_closing_card.txt`
- `assets/` - Episode-specific images, audio
- `renders/drafts/` - Test renders
- `renders/final/` - Approved final render
