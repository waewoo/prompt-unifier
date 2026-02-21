# Git Multi-Repo Sync

`GitService.sync_multiple_repos()` syncs multiple repositories with **last-wins merge**.

## Merge Strategy

Repos are processed in the order provided. Later repos override earlier ones on path conflicts:

```bash
# base prompts first, team overrides last
prompt-unifier sync --repo https://github.com/org/base-prompts.git \
                    --repo https://github.com/team/overrides.git
```

Conflicts are logged as warnings (`⚠️  Conflict: 'prompts/foo.md' overridden by ...`).

## Repository Requirements

- `prompts/` directory — **required** (sync fails if missing)
- `rules/` directory — optional (silently skipped if absent)
- Subdirectory structure inside `prompts/` and `rules/` is preserved in storage

## Sync Process (order matters)

1. **Validate & clone all repos** first — fail-fast on any error before touching storage
2. **Clear storage** (default: `clear_storage=True`)
3. **Copy files** in repo order (last-wins on conflicts)
4. **Save `.repo-metadata.json`** to storage root
5. **Clean up** all temp directories in `finally` block

## Network Resilience

Clone and fetch operations retry up to **3 times** with exponential backoff (1s → 2s → 4s):

```python
retry_with_backoff(clone_operation, max_attempts=3, initial_delay=1.0, backoff_factor=2.0)
```

## Auth Options (for private repos)

1. SSH key — `git@github.com:org/repo.git`
2. Git credential helper — `git config --global credential.helper store`
3. Token in URL — `https://user:ghp_token@github.com/org/repo.git` (least secure)  # pragma: allowlist secret
