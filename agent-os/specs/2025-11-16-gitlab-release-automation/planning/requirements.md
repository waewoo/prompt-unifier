# Spec Requirements: GitLab Release Automation

## Initial Description
GitLab Release Automation — Implement automated Git tagging and GitLab Release creation in the CI/CD pipeline, including version bumping, changelog generation, and distribution package (sdist, wheel) publication.

## Requirements Discussion

### First Round Questions

**Q1:** I assume the release process should be triggered manually in GitLab CI/CD, rather than automatically on every push to `main`. Is that correct, or should it be automated under specific conditions (e.g., commit message contains `[release]`)?
**Answer:** I want a makefile generate release in gitlab

**Q2:** For version bumping, should we follow Semantic Versioning (e.g., `major.minor.patch`)? And should the version bump be handled automatically by the CI/CD pipeline (e.g., `poetry version patch`), or should the developer manually update `pyproject.toml` before triggering the release?
**Answer:** Semantic Versioning for bumps? => YES Automatic or manual pyproject.toml updates? => Automatic

**Q3:** Regarding changelog generation, should we automatically generate it from Git commit messages (e.g., using Conventional Commits), or should it be a manually maintained `CHANGELOG.md` file that the release process simply includes?
**Answer:** auto-generated from commits

**Q4:** For distribution packages, I assume we should build both `sdist` (source distribution) and `wheel` (binary distribution) using `poetry build`. Is this correct, and should these artifacts be attached to the GitLab Release?
**Answer:** oui

**Q5:** Should the release job run on a specific branch (e.g., `main` or `master`) only, or should it be possible to create releases from other branches (e.g., `release/vX.Y.Z`)?
**Answer:** main only

**Q6:** Are there any specific naming conventions for Git tags (e.g., `vX.Y.Z`) or GitLab Release titles that we should adhere to?
**Answer:** yes

**Q7:** Should the release process include publishing the package to a Python package index (e.g., PyPI), or is the GitLab Release with attached artifacts sufficient for now?
**Answer:** GitLab Release artifacts

### Existing Code to Reference
**Similar Features Identified:**
- CI/CD jobs: Existing jobs for `lint`, `typecheck`, `test`, `sast-scan`, `secrets-scan`, `dependency-scan` will serve as dependencies for the release job.
- Makefile targets: A new `release` target will be created, following existing `Makefile` conventions.

## Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
No visual assets provided.

## Requirements Summary

### Functional Requirements
- A `Makefile` target will initiate the release process.
- Version bumping will be automatic and follow Semantic Versioning.
- Changelog will be auto-generated from Git commits.
- `sdist` and `wheel` distribution packages will be built using `poetry build` and attached to the GitLab Release.
- The release job will run only on the `main` branch.
- Git tags and GitLab Release titles will follow `vX.Y.Z` naming conventions.
- GitLab Release artifacts will be sufficient (no PyPI publication for now).

### Reusability Opportunities
- Leverage existing GitLab CI/CD quality check jobs as prerequisites for the release job.
- Follow existing `Makefile` conventions for the new `release` target.

### Scope Boundaries
**In Scope:**
- `Makefile` target for triggering release.
- Automatic Semantic Versioning bump.
- Auto-generated changelog from commits.
- Building `sdist` and `wheel` distributions.
- Attaching distributions to GitLab Release.
- Release job restricted to `main` branch.
- `vX.Y.Z` tag/release naming.
- GitLab Release artifacts only (no PyPI).

**Out of Scope:**
- Manual `pyproject.toml` version updates.
- Manually maintained `CHANGELOG.md`.
- Publishing to PyPI.
- Releasing from branches other than `main`.

### Technical Considerations
- Use `poetry version` for automatic version bumping.
- Use `git tag` and `git push --tags` for tagging.
- Use GitLab Release CLI or API for creating releases.
- Integrate with existing GitLab CI/CD pipeline.
- Ensure `poetry build` is used for package creation.
