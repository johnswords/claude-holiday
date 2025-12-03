# Claude Holiday Community Charter

All media is personal. Claude Holiday is an experiment in community-composable media:
- Open repository, permissive forking.
- Config-driven "recipes" that describe cuts anyone can build.
- No single definitive version: your cut is valid and referenceable.

## Principles

1) Openness
- Everything needed to reproduce a cut is committed or referenced.
- Providers are abstracted so you can use prebaked footage or generate your own.

2) Reproducibility
- Cuts are defined by an RCFC recipe (YAML) and get a deterministic Cut URI.
- Release bundles include videos, captions, the recipe snapshot, and metadata.

3) Accessibility
- Non-coders can tweak a recipe and run one command.
- Future web front-ends can write RCFC recipes for you.

4) Respect
- Parody, satire, and critique are welcome; keep it kind and constructive.

## How To Participate

- Fork the repo.
- Copy an example recipe in `recipes/examples/`.
- Edit the YAML to choose episodes, overlays, audience, ending, and provider.
- Run `./ch compile --recipe your_recipe.yaml`.
- Optionally `./ch bundle --cut-manifest output/cuts/<cut_id>/manifest/cut.manifest.json` to zip a release bundle.
- Share your Cut URI and upload the videos (e.g., to YouTube).

## Code of Conduct

- Be excellent to each other.
- Credit the concept and link the repository.
- No hate or harassment. Respect the community and the satire tone.

🖤 Have fun, remix responsibly.

## Annual Cadence

Claude Holiday is intended to be an annual creative project. Each year, we aim to reflect and capture the spirit of what has happened in software development with AI. New episodes, new jokes, and new commentary—same community-driven foundation.

## Timelines (Prime + Community Forks)

We refer to each distinct cut or community fork as a "timeline."

- Prime timeline: the main repository's default cut for the current year.
- Community timelines: forks or recipe-based cuts produced by contributors.

How to publish your timeline:
- Include a `timeline` field in your RCFC recipe (e.g., `"timeline": "Prime 2025"` or `"timeline": "alice/dev-glossary-extended"`).
- Open a PR adding your timeline to `docs/timelines.md` with your Cut URI and link.
- Optional: attach a Release bundle to your fork's GitHub Releases for easy download.