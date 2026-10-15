---
name: ship-it
description: >-
  Releases main, with or without a milestone: reads the commits and CHANGELOG `[Unreleased]`
  entries since the last release, proposes the next minor version, bumps each version file
  and moves the entries under the new version in one MR, then offers a tag on its merge
  commit. Use when the user asks to "cut a release", "release main", "ship 1.4", "ship it" or
  "bump the version".
---

# ship-it

## 1. Propose

- Last release: the newest `v*` tag on main; no tag → the last commit that changed the version
  file.
- Read the commits on main since the last release and the CHANGELOG `[Unreleased]` entries.
- Propose the next minor version; the user approves it, names another version or declines.
- No version file or no CHANGELOG `[Unreleased]` entries → say so in the proposal; create neither.
- The project's `CLAUDE.md` forbids tagging → the **Tag:** line reads `none, CLAUDE.md forbids
  tagging`.
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

- Once that MR merges → offer a `v<version>` tag on its merge commit, unless `CLAUDE.md` forbids
  tagging.
