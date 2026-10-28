---
name: ship-it
description: >-
  Releases main, with or without a milestone: reads the commits and CHANGELOG `[Unreleased]`
  entries since the last release, proposes the next version in the last release's scheme (`0.x`,
  CalVer `YY.MM.MICRO` or SemVer), bumps each version file and moves the entries under the new
  version in one MR, then offers a tag on its merge commit. Use when the user asks to "cut a
  release", "release main", "ship 26.11", "ship it" or "bump the version".
---

# ship-it

## 1. Propose

- Last release: the newest `v*` tag on main; no tag → the last commit that changed the version
  file.
- Read the commits on main since the last release and the CHANGELOG `[Unreleased]` entries.
- Propose the next version from the last release's version, its tag or else the version file;
  the user approves it, names another version or declines:
  - No tag and no version file → `0.1.0`.
  - A `0.x` version → the next minor: `v0.4.0` → `0.5.0`.
  - A CalVer `YY.MM.MICRO` version → this month's `YY.MM`, MICRO one above the last release's in
    the same month, else 0: `v26.11.0` → `26.11.1` in November 2026, `26.12.0` in December.
  - A CalVer month has no leading zero: `27.5.0`, never `27.05.0`.
  - A SemVer version at `1.0` or above → the next minor, unless the user names a CalVer version.
- No version file or no CHANGELOG `[Unreleased]` entries → say so in the proposal; create neither.
- The project's `CLAUDE.md` or `AGENTS.md` forbids tagging → the **Tag:** line reads
  `none, <that file> forbids tagging`.
- Lay out the proposal as:

```
- **Version:** <current> → <next>
- **Commits:** <n> since <last tag or version commit>
- **CHANGELOG:** <n> `[Unreleased]` entries move under `[<next>] - <date>`
- **Tag:** `v<next>` on the MR's merge commit, offered once it merges
```

## 2. Bump

- One MR: bump each version file, rename the CHANGELOG `[Unreleased]` to `[<version>] - <date>`
  and add an empty `[Unreleased]` above it.

## 3. Tag

- Once that MR merges → offer a `v<version>` tag on its merge commit, unless `CLAUDE.md` or
  `AGENTS.md` forbids tagging.
