# Changelog - Git Integration & Repository Management

## [1.2.0] - 2025-11-12 - Rules Directory Synchronization

### ✨ Added

#### Rules Directory Synchronization
- **Sync command now extracts rules/ directory** in addition to prompts/
- rules/ directory is optional - sync works with or without it
- prompts/ directory remains required for repository validation
- Both directories are automatically synchronized when present in the repository

**Files Modified:**
- `src/prompt_manager/git/service.py` - Updated `extract_prompts_dir()` method
- `src/prompt_manager/cli/commands.py` - Updated sync command messages
- `agent-os/specs/.../spec.md` - Updated specification

**Tests Added:**
- `tests/git/test_service.py::test_extract_prompts_dir_also_copies_rules_directory`
- `tests/git/test_service.py::test_extract_prompts_dir_works_without_rules_directory`

**Behavior:**
```bash
# Repository structure (example)
my-prompts-repo/
├── prompts/          # Required - contains prompt templates
│   ├── prompt1.md
│   └── prompt2.md
└── rules/            # Optional - contains coding standards, guidelines
    ├── rule1.md
    └── rule2.md

# After sync
~/.prompt-manager/storage/
├── prompts/          # Always synced
│   ├── prompt1.md
│   └── prompt2.md
└── rules/            # Synced if present in repository
    ├── rule1.md
    └── rule2.md
```

**Output Changes:**
```bash
# Before
Syncing prompts...
Extracting prompts...
Synced to: /path/storage/prompts

# After
Syncing prompts and rules...
Extracting prompts and rules...
Synced to: /path/storage
```

**Use Cases:**
- **Coding Standards:** Store Python/JavaScript/etc. coding standards in rules/
- **Best Practices:** Share team best practices and guidelines
- **Testing Standards:** Document testing requirements and patterns
- **Documentation Templates:** Provide documentation structure templates

**Backward Compatibility:**
✅ Fully backward compatible - existing repositories with only prompts/ continue to work
✅ No breaking changes to API or CLI interface
✅ Optional feature - repositories don't need rules/ directory

---

## [1.1.0] - 2025-11-12 - Post-Implementation Improvements

### ✨ Added

#### Option `--version`
- Added `--version` and `-v` global option to CLI
- Displays application version in format: "prompt-manager version X.Y.Z"
- Eager callback (processed before commands)
- Exit code: 0

**Files Modified:**
- `src/prompt_manager/cli/main.py`

**Usage:**
```bash
poetry run prompt-manager --version
# Output: prompt-manager version 0.1.0
```

---

#### Make Run Shortcut
- Added `make run ARGS="<command>"` target to Makefile
- Provides convenient shortcut for development
- Consistent with other make targets (test, lint, check)

**Files Modified:**
- `Makefile`

**Usage:**
```bash
make run ARGS="--version"
make run ARGS="init"
make run ARGS="sync --repo <url>"
```

---

### 🔄 Changed

#### Init Command - Now Idempotent
- **Breaking Change:** `init` no longer fails if already initialized
- Creates only missing components instead of failing
- Returns exit code 0 even when already initialized (was: exit code 1)
- Displays clear status:
  - Green messages for created items
  - Dim/gray messages for existing items
- Reads existing `storage_path` from config if available

**Migration Guide:**
- Scripts expecting init to fail on re-run need updating
- Now safe to call `init` multiple times
- Can be used for "repair" if config files are missing

**Files Modified:**
- `src/prompt_manager/cli/commands.py` (function `init()`)

**Tests Modified:**
- `tests/cli/test_git_commands.py::test_init_is_idempotent_when_already_exists`
- `tests/integration/test_git_integration.py::test_init_is_idempotent`

**Before:**
```bash
poetry run prompt-manager init
# (if already initialized)
# Error: .prompt-manager/ directory already exists.
# Exit code: 1
```

**After:**
```bash
poetry run prompt-manager init
# ✓ Already initialized (all components exist)
# Exists: /path/.prompt-manager
# Exists: /path/.prompt-manager/config.yaml
# Exit code: 0
```

---

### 🐛 Fixed

#### Temporary Directory Cleanup
- **Issue:** Temporary directories were cleaned up prematurely
- **Cause:** Using `TemporaryDirectory()` context manager returned path but deleted directory immediately
- **Fix:** Changed to `tempfile.mkdtemp()` with manual cleanup in try/finally blocks

**Files Modified:**
- `src/prompt_manager/git/service.py` (method `clone_to_temp()`)
- `src/prompt_manager/cli/commands.py` (sync command cleanup)
- `tests/git/test_service.py` (test updated)

**Impact:**
- Resolves "Reference at 'HEAD' does not exist" errors
- More reliable Git operations
- Proper cleanup in all cases (success and error)

---

#### RequestsDependencyWarning
- **Issue:** Warning about incompatible urllib3/chardet versions
- **Root Cause:** Outdated Poetry dependencies (not project dependencies)
- **Solution:** `poetry self update`

**Updates Applied:**
- Poetry: → 2.2.1+
- requests: 2.28.1 → 2.32.5
- charset-normalizer: 3.0.1 → 3.4.4
- certifi: 2022.9.24 → 2025.11.12

**Files Modified:**
- None (resolved at Poetry level)

**Documentation:**
- Added "Development Environment" section in `spec.md`
- Recommends running `poetry self update` during setup

---

#### Import Cleanup
- Removed unused `contextlib` import in test file

**Files Modified:**
- `tests/git/test_service.py`

---

### 📝 Documentation

#### Specification Updates
- Updated `spec.md` with all changes:
  - CLI Global Options section added
  - Init idempotence documented
  - Sync with --storage-path option
  - mkdtemp usage instead of TemporaryDirectory
  - Development Environment section
  - Empty repository error handling

**Files Modified:**
- `agent-os/specs/.../spec.md`

---

#### New Verification Document
- Created `verifications/post-implementation-improvements.md`
- Documents all 4 improvements in detail
- Includes examples, tests, and lessons learned

**Files Created:**
- `agent-os/specs/.../verifications/post-implementation-improvements.md`

---

#### README for Spec
- Created comprehensive README for spec directory
- Documents structure and recent changes
- Provides quick links and usage examples

**Files Created:**
- `agent-os/specs/.../README.md`

---

### ✅ Quality Metrics

**Tests:** 180/180 passed ✅
- All existing tests continue to pass
- 2 tests updated for idempotent behavior
- No regressions introduced

**Coverage:** 87.44% (required: 85%) ✅
- Above threshold
- Main uncovered code: error handling edge cases

**Lint:** All checks passed ✅
- Ruff checks: 0 errors
- Code style: consistent

**Type Check:** 26 files, no issues ✅
- mypy strict mode
- All types correct

---

### 🔗 Related Issues

- Init idempotence requested by user for script automation
- Version option standard CLI feature
- Warning urllib3 reported as annoying during development
- Temporary directory cleanup caused mysterious "HEAD not found" errors

---

### 📦 Dependencies

No new dependencies added. All changes use existing packages.

**Poetry Update Required:**
- Minimum Poetry version: 2.2.1
- Run: `poetry self update`

---

### 🚀 Migration Guide

#### For Users

**No action required** - All changes are backward compatible.

Optional improvements:
1. Update Poetry: `poetry self update`
2. Use new shortcuts: `make run ARGS="command"`
3. Benefit from idempotent init (can re-run safely)

#### For Scripts/Automation

**Review init error handling:**

```bash
# Old script (will still work, but can be simplified)
if [ ! -d ".prompt-manager" ]; then
    prompt-manager init
fi

# New script (simpler)
prompt-manager init  # Always succeeds if properly configured
```

#### For Developers

1. Update Poetry: `poetry self update`
2. Pull latest changes
3. Run: `poetry install`
4. Run: `make check` to verify everything works

---

### 📚 Links

- **Spec:** [spec.md](./spec.md)
- **Improvements Doc:** [verifications/post-implementation-improvements.md](./verifications/post-implementation-improvements.md)
- **README:** [README.md](./README.md)

---

## [1.0.0] - 2025-11-11 - Initial Implementation

### ✨ Initial Release

- ✅ Init command implementation
- ✅ Sync command implementation
- ✅ Status command implementation
- ✅ GitService with retry logic
- ✅ ConfigManager for config.yaml handling
- ✅ Centralized storage support (~/.prompt-manager/storage)
- ✅ Rich formatted output
- ✅ Comprehensive error handling
- ✅ 180 tests with 87% coverage
- ✅ Full documentation

**See:**
- [spec.md](./spec.md) - Original specification
- [tasks.md](./tasks.md) - Implementation tasks
- [verifications/final-verification.md](./verifications/final-verification.md) - Initial verification

---

## Summary

| Version | Date | Changes | Tests | Coverage |
|---------|------|---------|-------|----------|
| 1.2.0 | 2025-11-12 | Rules directory sync | 182/182 ✅ | 87.51% ✅ |
| 1.1.0 | 2025-11-12 | Post-impl improvements | 180/180 ✅ | 87.44% ✅ |
| 1.0.0 | 2025-11-11 | Initial implementation | 180/180 ✅ | 87.44% ✅ |

---

**Note:** Version numbers are for spec tracking. Actual application version is in `pyproject.toml`.
