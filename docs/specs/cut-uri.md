# Cut URI Spec

A Cut URI deterministically identifies a compiled cut from an RCFC recipe at a specific commit.

Format:
```
chcut://{commit_sha}/{rcfc_hash}?audience={profile}&v=0.1
```

- `commit_sha`: git commit SHA used to compile
- `rcfc_hash`: BLAKE3 hash (base32) of the canonicalized recipe (excluding `source.commit_sha`)
- `audience`: audience_profile from the recipe
- `v`: Cut URI spec version (0.1)

Example:
```
chcut://a1b2c3d4/3MZ6Q7WKPA?audience=dev&v=0.1
```

Usage:
- Include in YouTube descriptions and Release manifests.
- Use as a stable reference when sharing variants on social media.