# Contributing

## Branches

- `main` is the stable line.
- Do not commit directly to `main`.
- Name branches `type/short-description` (for example `fix/visit-count` or `docs/release-steps`).

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
type: short summary
```

Common types are `feat`, `fix`, `docs`, `chore`, and `ci`.

## Pull requests

1. Open a pull request against `main`.
2. Fill in the pull request template.
3. `composer validate`, `composer lint`, and `composer test` must pass.
4. A maintainer merges. Do not force-push `main`.

## Releases

Bump the plugin version and the Stable tag in `readme.txt` together. Tag `vX.Y.Z` and publish a GitHub release. There is no separate build artifact. Sites install this directory with its bundled production `vendor/`.
