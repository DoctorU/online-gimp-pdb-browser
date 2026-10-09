# Rebuilding and Publishing

The site deploys through GitHub Actions Pages artifacts. Each run fetches the latest [GIMP](https://www.gimp.org/) `master`, generates a fresh procedure catalog, assembles the static site under `_site/`, and deploys that artifact to GitHub Pages. The workflow does not commit generated files or push to a `gh-pages` branch; a `gh-pages` branch is not required.

The `data/pdb.json` catalog is ignored by Git and recreated during each workflow run. Its source links point to the exact [GIMP](https://www.gimp.org/) commit used to build it.

## Workflow Triggers

The workflow is `.github/workflows/pages.yml`. It has four trigger paths:

1. **Push to `main`:** Every push to `main` starts a build, including a pull request merge. A branch ruleset is needed if changes must arrive through reviewed pull requests rather than direct pushes.
2. **Rebuild tag:** Pushing a tag whose name matches `rebuild-pdb-*` starts a build. For example, `rebuild-pdb-20261009-143000` matches. Tags point to commits, not branches; the workflow does not verify that a tagged commit is reachable from `main`. A tag-triggered run checks out the tagged website commit, so tag the current `main` commit when you intend to publish current site code. Restrict matching tag creation in GitHub settings as described below.
3. **Manual dispatch:** In GitHub, open **Actions**, select **Build and deploy Script-Fu Index**, choose **Run workflow**, select `main`, and start the run. The workflow must be present on the default branch for this option to be available. Users need sufficient repository permissions to dispatch workflows.
4. **Daily schedule:** The workflow runs every day at 06:23 UTC. It fetches the latest [GIMP](https://www.gimp.org/) `master` and rebuilds even if [GIMP](https://www.gimp.org/) has had no new commits since the previous run.

These are independent event paths. There are no path filters, so any push to `main` starts a build.

## First-Time GitHub Setup

1. Push the workflow and site files to `main` (normally by merging a pull request).
2. In repository **Settings → Pages**, set the build and deployment source to **GitHub Actions**. This one-time setting is required; a workflow file alone does not enable Pages.
3. In **Settings → Actions → General**, ensure GitHub Actions are allowed for this repository. The workflow grants `contents: read`, `pages: write`, and `id-token: write`; it does not have permission to write repository contents.
4. Open **Actions → Build and deploy Script-Fu Index** to follow the run. The deployment summary provides the Pages URL.

The `actions/upload-pages-artifact` step packages `_site` as a Pages artifact. The `actions/deploy-pages` step publishes that artifact through GitHub Pages. Neither step writes a commit to `gh-pages`. If a `gh-pages` branch exists, it may remain read-only.

## Repository Rules

Repository rules are configured in GitHub, not by this document or the workflow file.

- **Protect `main`:** In **Settings → Rules → Rulesets**, create an active branch ruleset targeting the default branch `main`. Require pull requests and any desired approvals or status checks; disable force pushes and deletion. Configure administrator bypass according to your policy.
- **Restrict rebuild tags:** Create an active tag ruleset targeting `rebuild-pdb-*`. Restrict tag creation, update, and deletion to administrators or other explicitly trusted users. This controls who can trigger tag builds, but does not ensure a tag points to a commit on `main`.
- **Manual dispatch:** Limit repository write access to trusted collaborators. For deployment approval, configure required reviewers on the `github-pages` environment in **Settings → Environments**.

A public repository can be read and forked by anyone; public visibility alone does not grant permission to push to it.

## Manual Rebuild Commands

To create a rebuild tag at the current `main` commit:

```sh
git switch main
git pull --ff-only origin main
tag="rebuild-pdb-$(date -u +%Y%m%d-%H%M%S)"
git tag "$tag"
git push origin "$tag"
```

This tags the checked-out `main` commit. The repository's tag ruleset should restrict who may push matching tags.

## Local Build and Preview

From the website repository root, fetch [GIMP](https://www.gimp.org/) source and generate the catalog:

```sh
git clone --depth 1 https://github.com/GNOME/gimp.git /tmp/gimp
python3 scripts/build_pdb.py \
  --source-dir /tmp/gimp/plug-ins/script-fu/scripts \
  --pdb-c-dir /tmp/gimp/app/pdb \
  --revision "$(git -C /tmp/gimp rev-parse HEAD)"
python3 -m http.server 8000
```

Open `http://localhost:8000`. The generated `data/pdb.json` is local build output and is intentionally not committed. The project license is GPL-3.0-or-later; see [LICENSE](LICENSE).
