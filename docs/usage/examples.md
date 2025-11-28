# Real-World Examples

Here are some concrete ways different users utilize Prompt Unifier.

## 1. The DevOps Team

**Goal**: Standardize "Incident Response" and "Post-Mortem" prompts across the SRE team.

**Setup**:

1. Create a `sre-prompts` Git repository.
1. Add `incident-triage.md` and `post-mortem-draft.md` with strict frontmatter.
1. Configure CI to validate prompts on every Pull Request.

**Workflow**: On their machines, SREs run:

```bash
prompt-unifier sync
prompt-unifier deploy
```

Now, when an incident occurs, every SRE has the exact same, high-quality prompt available in their
IDE.

## 2. The Solo Developer

**Goal**: Maintain a personal library of coding assistants across multiple machines (laptop,
desktop).

**Setup**:

1. Personal `dotfiles/prompts` repo.
1. Contains prompts for "Refactor to Clean Code", "Generate Unit Tests", "Explain Code".

**Workflow**: The developer adds a prompt on their laptop, pushes to Git. On their desktop:

```bash
prompt-unifier sync
```

The new prompt is instantly available.

## 3. The Multi-Tool User

**Goal**: Use **Kilo Code** for quick scripts and **Continue** for deep coding sessions, sharing the
same core prompts.

**Scenario**: You have a prompt `python-expert.md`.

- In **Kilo Code**, it needs to be in `.kilocode/rules`.
- In **Continue**, it needs to be in `.continue/prompts`.

**Solution**: Prompt Unifier handles this translation automatically.

1. Define `python-expert.md` once in the repository.
1. Run `prompt-unifier deploy`.
1. The tool generates the specific JSON/YAML/Markdown required for *both* tools simultaneously.

## Troubleshooting Scenarios

### "My new prompt isn't showing up"

1. **Check the repo**: Did you push the file to the remote Git repository?
1. **Check sync**: Run `prompt-unifier sync` and look for the filename in the output.
1. **Check validity**: Run `prompt-unifier validate`. If the file is invalid, it might be skipped
   during deployment.
1. **Check tags**: If you are filtering by tags, ensure your prompt has the correct tags in its
   frontmatter.
