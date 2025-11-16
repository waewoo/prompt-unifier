# Specification: GitLab Release Automation

## Goal
Implement automated Git tagging and GitLab Release creation in the CI/CD pipeline, including version bumping, changelog generation, and distribution package (sdist, wheel) publication.

## User Stories
- As a developer, I want a `Makefile` target to easily trigger a new release.
- As a developer, I want the version to be automatically bumped following Semantic Versioning.
- As a developer, I want the changelog to be automatically generated from commit messages.
- As a user, I want to find `sdist` and `wheel` distribution packages attached to GitLab Releases.

## Specific Requirements

**1. Makefile `release` Target**
- Create a new `release` target in the `Makefile`.
- This target will accept a `VERSION_BUMP` argument (e.g., `patch`, `minor`, `major`).
- The `release` target will:
    - Run `make check` to ensure all quality checks pass.
    - Automatically bump the version in `pyproject.toml` using `poetry version $(VERSION_BUMP)`.
    - Commit the version bump with a message like "chore(release): Bump version to vX.Y.Z".
    - Create a Git tag `vX.Y.Z` (where X.Y.Z is the new version).
    - Push the commit and the tag to the `main` branch.

**2. GitLab CI/CD `release` Stage and Job**
- Add a new `release` stage to `.gitlab-ci.yml` after the `test` stage.
- Create a `create-release` job in the `release` stage.
- This job will:
    - Run `only: tags` to be triggered only when a Git tag is pushed.
    - Run `only: main` to ensure releases are only created from the `main` branch.
    - Depend on the `test` stage (or `check` if a `check` stage is added to CI).
    - Build `sdist` and `wheel` distribution packages using `poetry build`.
    - Use the GitLab Release CLI to create a new release.
        - The release title will be the Git tag name (e.g., `v1.0.0`).
        - The release description will be the auto-generated changelog.
        - The `sdist` and `wheel` artifacts will be attached to the release.
    - The job should use `image: python:3.12` and install `poetry` and `release-cli`.

**3. Auto-generated Changelog**
- The release process will generate a changelog based on Git commit messages.
- This implies a Conventional Commits-like structure for commit messages (e.g., `feat:`, `fix:`, `chore:`).
- The changelog content will be used as the description for the GitLab Release.
- A tool like `git-conventional-commits` or a custom script will be used to generate the changelog.

**4. Semantic Versioning**
- The `poetry version` command will be used to ensure Semantic Versioning (major, minor, patch) for version bumps.

**5. Distribution Packages**
- `poetry build` will be used to create `sdist` and `wheel` packages.
- These packages will be stored as job artifacts and then attached to the GitLab Release.

## Visual Design
No visual assets provided.

## Existing Code to Leverage

**GitLab CI/CD Pipeline (`.gitlab-ci.yml`)**
- Existing stages (`security`, `lint`, `typecheck`, `test`) and job structures can be used as a template for the new `create-release` job.
- The `before_script` section for installing `poetry` and dependencies can be reused.
- The `artifacts` section in existing jobs provides a pattern for storing build artifacts.

**Makefile (`Makefile`)**
- Existing targets like `check` provide a pattern for running prerequisite commands.
- The general structure and `.PHONY` declaration can be followed.

## Out of Scope
- Manual `pyproject.toml` version updates.
- Manually maintained `CHANGELOG.md`.
- Publishing to PyPI or other package indexes.
- Releasing from branches other than `main`.
- Interactive prompts during the release process.
- Advanced release management features (e.g., release branches, hotfixes).

## Technical Considerations
- **GitLab CI/CD Variables**: `CI_COMMIT_TAG` will be used to get the tag name for the release. `CI_PROJECT_ID` and `CI_JOB_TOKEN` might be needed for `release-cli`.
- **Git Configuration**: The CI job will need Git configured to push tags (e.g., `git config user.name "GitLab CI"`, `git config user.email "ci@gitlab.com"`).
- **Changelog Tool**: Research and select a suitable tool or script for generating changelogs from commit history. `git-conventional-commits` is a strong candidate.
- **Error Handling**: Ensure the `Makefile` target and CI job handle errors gracefully and provide informative messages.
- **Security**: Ensure that the `CI_JOB_TOKEN` has appropriate permissions for creating releases and pushing tags.
