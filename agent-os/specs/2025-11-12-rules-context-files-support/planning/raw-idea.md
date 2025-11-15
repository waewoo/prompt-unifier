# Rules/Context Files Support - Raw Idea

## Context

Actuellement, le système synchronise les fichiers rules depuis le repository Git (item 3.6 complété), mais il ne les valide pas ni ne les gère dans les commandes comme `list` ou `validate`. Les rules sont simplement copiés dans `~/.prompt-manager/storage/rules/` sans validation de format.

**État actuel:**
- ✅ Git sync des rules/ fonctionne (item 3.6)
- ❌ Pas de validation de format pour les rules
- ❌ `validate` command ne vérifie pas les rules
- ❌ `list` command ne montre pas les rules
- ❌ Pas de distinction claire entre prompts et rules dans l'UI

## Problème

Sans validation et support approprié des rules:
1. **Qualité incertaine:** Les rules peuvent avoir un format invalide sans qu'on le sache
2. **Visibilité limitée:** Les développeurs ne peuvent pas lister facilement les rules disponibles
3. **Validation manquante:** Pas de vérification automatique du format des rules
4. **Expérience utilisateur incomplète:** Les commandes CLI ne supportent pas les rules de manière cohérente

**Impact:**
- 🟡 Risque de rules mal formatés dans le repository
- 🟡 Difficulté à découvrir quels rules sont disponibles
- 🟡 Pas de feedback sur la qualité des rules
- 🟡 Expérience utilisateur fragmentée

## Objectif

Étendre le système pour supporter pleinement les fichiers rules avec:
1. **Même format que les prompts:** YAML frontmatter + >>> separator
2. **Validation complète:** Réutiliser le moteur de validation existant
3. **Support CLI:** Commandes `list`, `validate` gèrent prompts ET rules
4. **Filtrage et affichage:** Distinction claire dans l'UI

## Solution proposée

### 1. Format des Rules (identique aux prompts)

```yaml
---
name: python-style-guide
description: Python coding standards and best practices
type: rule
category: coding-standards
tags:
  - python
  - pep8
  - style
version: 1.0.0
---
>>>
# Python Style Guide

## Naming Conventions
- Use snake_case for functions and variables
- Use PascalCase for classes
- Use UPPER_CASE for constants

## Code Organization
- Maximum line length: 100 characters
- Use type hints for function signatures
- Docstrings required for all public functions
```

**Différences avec prompts:**
- `type: rule` au lieu de `type: prompt`
- `category` pour organiser les rules (coding-standards, architecture, security, etc.)
- Pas de champ `tools` (les rules ne sont pas déployés vers des outils)

### 2. Validation des Rules

**Réutiliser le moteur existant:**
- Modèle Pydantic `RuleFile` similaire à `PromptFile`
- Même parser YAML frontmatter + >>> separator
- Validation spécifique aux rules (type, category)

**Schéma de validation:**
```python
class RuleFile(BaseModel):
    """Représente un fichier rule validé"""
    name: str
    description: str
    type: Literal["rule"] = "rule"
    category: str  # coding-standards, architecture, security, testing, etc.
    tags: list[str] = []
    version: str = "1.0.0"
    content: str  # Contenu après >>>
```

### 3. Extension des Commandes

#### 3.1 `validate` Command

**Avant:**
```bash
prompt-manager validate  # Valide seulement prompts/
```

**Après:**
```bash
# Valider tout (prompts + rules)
prompt-manager validate

# Valider seulement les prompts
prompt-manager validate --type prompts

# Valider seulement les rules
prompt-manager validate --type rules
```

#### 3.2 `list` Command (nouvelle)

```bash
# Lister tout
prompt-manager list

# Lister seulement les prompts
prompt-manager list --type prompts

# Lister seulement les rules
prompt-manager list --type rules

# Filtrer par catégorie (rules)
prompt-manager list --type rules --category coding-standards

# Filtrer par tags
prompt-manager list --tags python,pep8
```

**Output example:**
```
📋 Prompts (3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name                 Description                Tools
────────────────────────────────────────────────────
code-review          Review code for bugs       continue, cursor
bug-fixer            Fix Python bugs            aider
refactor-helper      Refactor legacy code       continue

📜 Rules (2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name                 Description                Category
────────────────────────────────────────────────────
python-style         Python coding standards    coding-standards
api-design           REST API best practices    architecture
```

### 4. Structure de Répertoire

```
~/.prompt-manager/storage/
├── prompts/
│   ├── code-review.md
│   ├── bug-fixer.md
│   └── refactor-helper.md
└── rules/
    ├── coding-standards/
    │   ├── python-style.md
    │   └── javascript-style.md
    ├── architecture/
    │   └── api-design.md
    └── security/
        └── auth-guidelines.md
```

**Organisation:**
- Rules organisés par catégorie (optionnel)
- Structure plate aussi supportée
- Même extension `.md` que les prompts

### 5. Modèle de Données Unifié

```python
from typing import Literal, Union

class BaseFile(BaseModel):
    """Base pour prompts et rules"""
    name: str
    description: str
    tags: list[str] = []
    version: str = "1.0.0"
    content: str

class PromptFile(BaseFile):
    """Fichier prompt"""
    type: Literal["prompt"] = "prompt"
    tools: list[str]
    author: str | None = None

class RuleFile(BaseFile):
    """Fichier rule"""
    type: Literal["rule"] = "rule"
    category: str
    applies_to: list[str] = []  # Languages/frameworks applicables

ContentFile = Union[PromptFile, RuleFile]
```

## Scope

### In Scope ✅
- Validation des fichiers rules (même format que prompts)
- Extension de la commande `validate` pour supporter rules
- Nouvelle commande `list` pour lister prompts et rules
- Filtrage par type, catégorie, tags
- Affichage Rich avec distinction visuelle prompts vs rules
- Documentation du format rules
- Tests pour validation des rules

### Out of Scope ❌
- Déploiement des rules vers des outils (rules restent en local)
- Édition interactive des rules (future feature)
- Templates de rules (future feature)
- Versioning avancé des rules (future feature)
- Merge de rules (future feature)

## Bénéfices attendus

1. **Qualité garantie:** Validation automatique du format des rules
2. **Visibilité:** Lister facilement tous les rules disponibles
3. **Expérience cohérente:** Même workflow pour prompts et rules
4. **Organisation:** Catégorisation claire des rules
5. **Maintenance:** Détection précoce des problèmes de format

## Métriques de succès

- ✅ 100% des rules validés automatiquement
- ✅ Commande `list` affiche prompts ET rules
- ✅ Filtrage par type/catégorie fonctionne
- ✅ Temps de validation < 2 secondes pour 50 files
- ✅ Documentation complète du format rules
- ✅ Tests couvrent validation des rules (>95%)

## Prochaines étapes

1. Créer modèle Pydantic `RuleFile`
2. Étendre le parser pour supporter type="rule"
3. Implémenter commande `list` avec Rich UI
4. Étendre commande `validate` avec flag `--type`
5. Créer exemples de rules dans le repo
6. Documentation du format rules
7. Tests unitaires et d'intégration

## Références

- Spec item 3.6 (Rules Directory Synchronization) - déjà implémenté
- Modèles Pydantic existants dans `src/prompt_manager/models/`
- Validation engine dans `src/prompt_manager/validation/`
- CLI commands dans `src/prompt_manager/cli/commands.py`
