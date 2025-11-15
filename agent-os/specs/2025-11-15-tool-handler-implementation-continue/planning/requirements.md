# Spec Requirements: Tool Handler Implementation: Continue

## Initial Description
Tool Handler Implementation: Continue & Kilo Code

## Requirements Discussion

### First Round Questions

**Q1:** I assume the primary goal is to create concrete implementations of the `ToolHandler` protocol for "Continue" and "Kilo Code", following the strategy architecture already in place. Is that correct?
**Answer:** oui

**Q2:** For the "Continue" handler, I assume that deploying a prompt involves copying the prompt file to the user's `.continue/` directory. Is this correct, or are there other steps to consider?
**Answer:** non il faut convertir les fichiers dans le format appropprié et les copier dans le repertoire apporpier pour que cela soit reconnu par continue. Plus bas je t'ai msi la doc continue.

**Q3:** For the "Kilo Code" handler, could you specify where the prompts should be deployed? I assume there is a specific configuration directory for Kilo Code, but I am not familiar with it.
**Answer:** on va se limiter au plugin continue dans un premier temps.. on fera kilo code dans ue autre task group. (met a jour la roadmap et les spec de cette feature en conséquence)

**Q4:** I plan to implement a backup mechanism for each handler. Before deploying a new prompt, the old prompt (if it exists) will be backed up with a `.bak` extension. Does this approach seem good to you?
**Answer:** oui

**Q5:** For deployment verification, I propose that each handler verifies that the prompt file has been copied to the expected location and that its content is correct. Is this sufficient?
**Answer:** oui

**Q6:** What is out of scope for this feature? For example, should we worry about converting prompts to a specific format for each tool, or can we assume that prompts are already in the correct format?
**Answer:** oui comme indiqué au point 1

### Existing Code to Reference
No similar existing features identified for reference.

### Follow-up Questions

**Follow-up 1:** Pour le déploiement vers 'Continue', je vais créer un ContinueToolHandler qui effectuera les étapes suivantes :
   a. Lire le prompt prompt-manager.
   b. S'assurer que le frontmatter YAML contient invokable: true. Si ce n'est pas le cas, l'ajouter.
   c. Copier le fichier de prompt dans le répertoire ~/.continue/prompts/.
   Est-ce que ce processus vous semble correct ?
**Answer:** ok

**Follow-up 2:** La documentation mentionne que les règles sont stockées dans .continue/rules/. Devons-nous également gérer le déploiement des règles vers 'Continue' dans ce gestionnaire d'outils, ou devons-nous nous concentrer uniquement sur les prompts pour l'instant ?
**Answer:** oui tu gere les rules et les prompts

**Follow-up 3:** Pour la réutilisation du code, j'ai examiné le code existant. La classe GitService dans src/prompt_manager/git/service.py est un bon exemple de la manière de gérer les opérations sur les fichiers et les répertoires. Je vais m'en inspirer pour le ContinueToolHandler. Êtes-vous d'accord avec cette approche ?
**Answer:** ok

## Visual Assets

No visual assets provided.

## Requirements Summary

### Functional Requirements
- Implement a `ContinueToolHandler` that conforms to the `ToolHandler` protocol.
- The `ContinueToolHandler` should read `prompt-manager` prompts and rules.
- For prompts, the `ContinueToolHandler` should ensure the YAML frontmatter contains `invokable: true`, adding it if missing.
- The `ContinueToolHandler` should copy the processed prompt files to the `~/.continue/prompts/` directory.
- The `ContinueToolHandler` should copy the rule files to the `~/.continue/rules/` directory.
- Implement a backup mechanism: before deploying a new prompt or rule, the old file (if it exists) will be backed up with a `.bak` extension.
- Verify deployment by checking if the prompt/rule file has been copied to the expected location and its content is correct.

### Reusability Opportunities
- The `GitService` class in `src/prompt_manager/git/service.py` can serve as a model for handling file and directory operations within the `ContinueToolHandler`.

### Scope Boundaries
**In Scope:**
- Implementation of `ContinueToolHandler`.
- Conversion and deployment of `prompt-manager` prompts to "Continue" format.
- Deployment of `prompt-manager` rules to "Continue".
- Backup mechanism for prompts and rules.
- Deployment verification for prompts and rules.

**Out of Scope:**
- Implementation of "Kilo Code" tool handler (will be a separate task group).

### Technical Considerations
- The `ContinueToolHandler` will need to parse and modify YAML frontmatter for prompts.
- File system operations (read, write, copy, backup) will be central to the handler's logic.
- Error handling during file operations and YAML processing should be robust.
