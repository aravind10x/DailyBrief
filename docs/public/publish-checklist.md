# Publish Checklist

## Recommended Release Strategy

Use a **fresh public history** instead of publishing the current internal working history.

Best options:

1. Create a fresh public repo and copy in the cleaned tree.
2. Or create an orphan branch and stage only the public-safe files.

## Files That Should Not Go Public

Double-check that these stay untracked or absent:

- `AGENTS.md`
- `CLAUDE.md`
- `TODO.md`
- `PROGRESS.md`
- anything under `docs/superpowers/`
- local `.env` files
- generated debug outputs
- local screenshots you do not want published

## Asset Placement

Use this location:

- screenshots: `docs/public/assets/screenshots/`

## Final Verification

Run:

```bash
./scripts/verify-public-release.sh
```

Expected result:

- frontend lint passes
- frontend build passes
- backend tests pass or skip cleanly
- public-safety grep returns no hits

## Final README Pass

Before publishing:

- embed the final screenshot set
- add 3-5 screenshots
- keep the README honest about the current product scope

## Publication Steps

### Option A: Fresh repo

1. Create a new GitHub repo for the public version.
2. Copy this cleaned working tree into a fresh directory.
3. Initialize git and make the first public commit.
4. Push to the new repo.

### Option B: Orphan branch

```bash
git checkout --orphan public-release
git reset
git add .
git commit -m "Public demo release"
```

Then push that branch to a new public remote or set it as the basis for publication.

## Final Human Review

Before pushing:

- scan the file list one last time
- open the README in GitHub preview if possible
- click through the app manually once
- confirm the screenshots match the current UI
