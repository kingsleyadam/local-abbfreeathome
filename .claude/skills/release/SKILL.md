---
name: release
description: Prepare and publish a local-abbfreeathome release to PyPI and GitHub, including choosing the version, the release PR, optional release highlights, tagging, prereleases, and backport releases from release/X.Y branches. Use when asked to cut, prepare, tag, or publish a release or bump the package version.
---

# Releasing local-abbfreeathome

Pushing a tag is irreversible: it publishes to PyPI. Never push a tag without
explicit confirmation from the user of the exact tag and commit.

## How publishing works

- `.github/workflows/publish.yaml` builds on every push but only publishes on tag
  pushes. It uploads to PyPI (trusted publishing), then creates a GitHub release
  with generated notes and Sigstore-signed artifacts.
- Tags are bare versions with no `v` prefix: `3.11.1`, `3.12.0b1`.
- Tags containing `a` or `b` are created as GitHub prereleases.
- If `.github/release-notes/<exact-tag>.md` exists at the tagged commit, it is
  prepended to the generated notes (see `.github/release-notes/README.md`).
- Generated notes are grouped by PR labels using `.github/release.yml`.
- The version lives only in `pyproject.toml` (`version = "X.Y.Z"`).

## 1. Choose the version

1. Find the latest release and the PRs merged since it:

   ```sh
   git fetch --tags origin
   gh release list --limit 5
   gh pr list --state merged --base main --search "merged:>$(git log -1 --format=%cI <last-tag>)" \
     --json number,title,labels --limit 100
   ```

2. Pick the bump from the highest version-impact label among those PRs:
   `Semver-Major` -> major, `Semver-Minor` -> minor, otherwise patch.
   Flag any merged PR missing a version-impact label (documentation-only PRs
   are exempt) and confirm the version with the user before continuing.

## 2. Open the release PR

1. Branch from up-to-date `main` as `release/X.Y.Z`.
2. Update `version` in `pyproject.toml`.
3. Review the changes since the last tag (PR descriptions and diffs, not just
   titles) for anything worth calling out to users: new features or APIs,
   behavior changes, breaking changes or migration steps, and notable fixes.
   Present a short list of candidates with the reason each matters, and ask the
   user which, if any, to include as highlights. If they choose some, write
   `.github/release-notes/X.Y.Z.md` following the style of existing files there:
   a `## Highlights` heading, a short summary, a `###` section per item with its
   PR number, and brief usage examples for new APIs. If nothing stands out or the
   user declines, rely on the generated notes.
4. Open a PR to `main` titled `Bump version to X.Y.Z`, or
   `Prepare X.Y.Z release` when it includes highlights. Label it with the
   matching `Semver-Major`/`Semver-Minor`/`Semver-Patch`, plus `documentation`
   when it includes highlights.
5. Wait for CI to pass and for the user to merge it.

## 3. Tag and publish

1. After the PR is merged, tag the merge commit on `main`:

   ```sh
   git fetch origin main
   git log -1 --format='%h %s' origin/main   # confirm it is the release PR
   ```

2. Show the user the tag name and commit, and get explicit confirmation. Then:

   ```sh
   git tag X.Y.Z origin/main
   git push origin X.Y.Z
   ```

3. Watch the publish run and verify the result:

   ```sh
   gh run list --workflow publish.yaml --limit 1
   gh run watch <run-id>
   gh release view X.Y.Z
   ```

   Confirm the version appears on <https://pypi.org/p/local-abbfreeathome>.

## Prereleases

Use PEP 440 tags such as `X.Y.Zb1` or `X.Y.Za1`, with the same value in
`pyproject.toml`. Follow the same steps; the GitHub release is marked as a
prerelease automatically. To test packaging without publishing to PyPI, run
`gh workflow run publish-testpypi.yaml --ref <branch>`.

## Backport releases

Use these to ship a fix for an older minor line, for example `3.10.1` after
`3.11.0` is released.

1. Create or update `release/X.Y` from the last tag of that line
   (`git switch -c release/X.Y X.Y.Z` or check out the existing branch).
2. Cherry-pick the fix commits from `main`, then commit the version bump in
   `pyproject.toml` (`Bump version to X.Y.Z`) and push the branch.
3. Run the tests, get explicit confirmation, then tag the branch head and push
   the tag as above.
4. The publish workflow marks every non-prerelease as GitHub "Latest", so restore
   the newest release afterwards:

   ```sh
   gh release edit <newest-tag> --latest
   ```
