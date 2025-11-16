# Spec Requirements: Recursive File Discovery for Deploy Command

## Initial Description
Implement recursive file discovery for `prompts/` and `rules/` directories when using the `deploy` command. The current functionality only processes files at the root of these directories. The new feature should traverse all subdirectories within `prompts/` and `rules/` to include all nested prompt and rule files in the deployment process.

## Requirements Discussion

### First Round Questions

**Q1:** Je suppose que le changement principal est de modifier la découverte de fichiers pour qu'elle recherche récursivement dans tous les sous-dossiers de `prompts/` et `rules/`, au lieu de ne regarder qu'à la racine. Est-ce exact ?
**Answer:** oui

**Q2:** Pour des raisons de cohérence, je pense que cette recherche récursive devrait s'appliquer à toutes les commandes qui lisent les prompts/règles (comme `validate`, `list`, `status`), et pas seulement à `deploy`. Êtes-vous d'accord avec cette approche ?
**Answer:** oui

**Q3:** Devrions-nous ignorer certains noms de fichiers ou de dossiers lors de la recherche, comme les dossiers `archives/` ou les fichiers commençant par un `_` ? Ou est-ce que tout fichier est pertinent ?
**Answer:** tous les fichiers

**Q4:** Si deux fichiers dans des sous-dossiers différents ont le même `name` dans leur en-tête YAML, comment devrions-nous gérer ce conflit ? Le déploiement devrait-il échouer, ou l'un des fichiers devrait-il avoir la priorité ?
**Answer:** ca doit etre un echec avec un message d'erreur...

**Q5:** Y a-t-il des aspects qui devraient rester inchangés ? Par exemple, je suppose que la logique de la commande `sync` qui récupère les dossiers depuis Git ne devrait pas être modifiée.
**Answer:** non ca ne chnage pas

### Existing Code to Reference
**Similar Features Identified:**
- Feature: File scanning in `BatchValidator` - Path: `src/prompt_manager/core/batch_validator.py`
- Components to potentially reuse: `FileScanner` in `src/prompt_manager/utils/file_scanner.py` already performs recursive scanning. The `deploy` command's file discovery needs to be updated to match this recursive behavior.
- Backend logic to reference: The existing `glob` calls in the `deploy` command will be modified.

### Visual Assets

### Files Provided:
No visual assets provided.

### Visual Insights:
No visual assets provided.

## Requirements Summary

### Functional Requirements
- The `deploy` command must recursively discover all `.md` files within the `prompts/` and `rules/` subdirectories of the storage path.
- If two or more discovered files (prompts or rules) have the same `title` in their YAML frontmatter, the `deploy` command must fail with an informative error message, indicating the conflicting files.
- The recursive discovery should also implicitly apply to `list` and `status` commands once they are implemented, ensuring consistency.
- The `validate` command already performs recursive discovery via `FileScanner`, so no change is needed for its file discovery mechanism.
- **New:** The relative path of the prompt/rule file within its `prompts/` or `rules/` source directory must be preserved when deploying to the target handler's location. This means the target handler should reproduce the same subdirectory structure.

### Reusability Opportunities
- The `FileScanner` class in `src/prompt_manager/utils/file_scanner.py` provides a good model for recursive file discovery.
- The existing parsing logic using `ContentFileParser` should be reused.

### Scope Boundaries
**In Scope:**
- Modifying the `deploy` command's file discovery to be recursive.
- Adding a conflict detection mechanism for duplicate `title` fields in frontmatter during deployment.
- Ensuring consistency with `validate` command's existing recursive behavior.
- Preserving the relative subdirectory structure of prompts/rules during deployment to target handlers.

**Out of Scope:**
- Modifying the `sync` command's logic for retrieving files from Git.
- Changing the `FileScanner`'s existing recursive behavior (it's already recursive).
- Implementing `list` or `status` commands (they are on the roadmap but not part of this spec).

### Technical Considerations
- The change will primarily involve updating `glob` patterns in `src/prompt_manager/cli/commands.py`.
- A new check for duplicate `title` fields will be added in the `deploy` function before handler iteration.
- Error handling for duplicate titles should use `typer.Exit(code=1)`.
- The `deploy` method of `ToolHandler` implementations will need to receive and utilize the relative path information to reproduce the directory structure. This might require modifying the `deploy` method signature in `handlers/protocol.py` and its implementations (e.g., `handlers/continue_handler.py`).