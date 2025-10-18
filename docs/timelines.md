# Claude Holiday — Timelines Registry

We track community "timelines" (distinct cuts) here. Add yours with a PR.

## How to add your timeline

1) Create a recipe with a descriptive `timeline` field
   - Example: `timeline: "Prime 2025"` or `timeline: "alice/dev-glossary-extended"`
2) Compile your cut and generate the manifest:
   - `python scripts/compile_cut.py --recipe your_recipe.yaml`
3) Build YouTube metadata (optional):
   - `python scripts/yt/metadata.py --cut-manifest output/cuts/<cut_id>/manifest/cut.manifest.json`
4) (Optional) Pack a release bundle for your fork
   - `python scripts/pack_release.py --cut-manifest output/cuts/<cut_id>/manifest/cut.manifest.json --include episodes --out output/releases`
5) Open a PR adding an entry below with your Cut URI and links.

## Prime Timeline (maintained by project)

- Year: 2025
- Timeline: Prime 2025
- Cut URI: tbd
- YouTube Playlist: tbd

## Community Timelines

- Timeline: <your timeline name>
  - Cut URI: chcut://<sha>/<hash>?audience=<profile>&v=0.1
  - Repo: <link to your fork>
  - YouTube: <link to playlist or video>
  - Notes: <optional>