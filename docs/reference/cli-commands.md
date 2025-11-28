# CLI Reference

This reference provides details for all available commands in the `prompt-unifier` CLI.

## Global Options

All commands support the following global options:

- `--version`: Show the version and exit
- `--verbose` / `-v` (`INTEGER`): Increase verbosity level (e.g., `-v` for INFO, `-vv` for DEBUG)
- `--log-file TEXT`: Write logs to the specified file path
- `--help`: Show this message and exit

______________________________________________________________________

## `validate`

Validate prompt and rule files in a directory.

```bash
prompt-unifier validate [OPTIONS] [DIRECTORY]
```

**Description**: Scans a directory or specific file to ensure it complies with the Prompt Unifier
YAML frontmatter schema.

**Arguments**:

- `DIRECTORY`: Directory to validate (defaults to synchronized storage).

**Options**:

- `--json`: Output validation results in JSON format.
- `--type` / `-t` (`TEXT`): Content type to validate: `all`, `prompts`, or `rules` (default: `all`).
- `--scaff` / `--no-scaff`: Enable/disable SCAFF methodology validation (default: `scaff`).

______________________________________________________________________

## `init`

Initialize prompt-unifier in current directory.

```bash
prompt-unifier init [OPTIONS]
```

**Description**: Creates the `~/.prompt-unifier` directory structure, including the `config.yaml`
file and the `storage` directory. It is safe to run this multiple times; it will not overwrite
existing configuration unless specified.

**Options**:

- `--storage-path TEXT`: Optional custom storage directory path (defaults to
  `~/.prompt-unifier/storage/`).

______________________________________________________________________

## `sync`

Synchronize prompts from Git repositories.

```bash
prompt-unifier sync [OPTIONS]
```

**Description**: Connects to the configured Git repositories, pulls the latest changes, and updates
the local storage. If no repository is configured, it will prompt or error out.

**Options**:

- `--repo TEXT`: Git repository URL. Can be specified multiple times to synchronize from several
  repositories in a single run. **Example**:
  `prompt-unifier sync --repo https://gitlab.com/repo1.git --repo https://gitlab.com/repo2.git`
- `--storage-path TEXT`: Override storage path for this sync (defaults to config value or
  `~/.prompt-unifier/storage/`).

______________________________________________________________________

## `status`

Display sync status and check for updates.

```bash
prompt-unifier status [OPTIONS]
```

**Description**: Shows the synchronization status of configured repositories and their last commit
information.

______________________________________________________________________

## `list`

List available prompts and rules.

```bash
prompt-unifier list [OPTIONS]
```

**Description**: Displays a formatted table of all prompts and rules currently stored locally,
showing their names, descriptions, and compatibility.

**Options**:

- `--tool` / `-t` (`TEXT`): Filter by target tool.
- `--tag TEXT`: Filter by tag.
- `--sort` / `-s` (`TEXT`): Sort by `'name'` or `'date'` (default: `name`).

______________________________________________________________________

## `deploy`

Deploy prompts and rules to tool handlers.

```bash
prompt-unifier deploy [OPTIONS]
```

**Description**: Reads prompts and rules from local storage and installs them into the configuration
directories of enabled tools (e.g., Kilo Code, Continue).

**Options**:

- `--name TEXT`: Name of the prompt to deploy (optional).
- `--tags TEXT`: Tags to filter (comma-separated, optional).
- `--handlers TEXT`: Handlers to deploy to (comma-separated, optional).
- `--base-path TEXT`: Custom base path for handler deployment (overrides `config.yaml`).
- `--clean`: Remove orphaned prompts/rules in destination (creates backups).
- `--dry-run`: Preview deployment without executing any file operations.
