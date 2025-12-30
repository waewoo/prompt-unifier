# Raw Idea

**Feature Name**: Extend validate command with functional testing via YAML

**Description**:
Extend the existing 'validate' command to support functional testing via YAML.

Current behavior:
- 'prompt-unifier validate <file>' checks SCAFF structure (syntax).

New behavior:
- 'prompt-unifier validate <file> --test' (or auto-detect) should look for a corresponding '.test.yaml' file.
- If found, it runs the Functional Validation Engine using the scenarios defined in the YAML.

Requirements:
1. Pure Python implementation (no heavy libs).
2. Support assertion types in YAML: 'contains', 'not-contains', 'regex', 'max-length'.
3. If '--test' is used but no YAML file exists, show a clear warning.
4. Report both Syntax (SCAFF) and Functional (YAML) results in the output.
