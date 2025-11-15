# Guide de Test Manuel - Prompt Manager

Ce document décrit les tests manuels à effectuer pour valider toutes les fonctionnalités de l'application prompt-manager.

## Table des Matières

1. [Prérequis](#prérequis)
2. [Tests des Commandes de Base](#tests-des-commandes-de-base)
3. [Tests de la Commande Init](#tests-de-la-commande-init)
4. [Tests de la Commande Sync](#tests-de-la-commande-sync)
5. [Tests de la Commande Status](#tests-de-la-commande-status)
6. [Tests de Validation](#tests-de-validation)
7. [Tests de Gestion d'Erreurs](#tests-de-gestion-derreurs)
8. [Nettoyage](#nettoyage)

---

## Prérequis

### Installation
```bash
cd /root/travail/prompt-manager
poetry install
```

**Résultat attendu:** Installation réussie de toutes les dépendances

### Vérification de l'installation
```bash
poetry run prompt-manager --version
```

**Résultat attendu:** Affichage de la version (ex: `0.1.0`)

---

## Tests des Commandes de Base

### Test 1.1: Affichage de l'aide générale

```bash
poetry run prompt-manager --help
```

**Résultat attendu:**
- Liste des commandes disponibles: `init`, `sync`, `status`, `validate`
- Description courte de chaque commande
- Options globales (--help, --version)

### Test 1.2: Affichage de l'aide pour init

```bash
poetry run prompt-manager init --help
```

**Résultat attendu:**
- Description de la commande init
- Option `--storage-path` avec sa description
- Exemples d'utilisation

### Test 1.3: Affichage de l'aide pour sync

```bash
poetry run prompt-manager sync --help
```

**Résultat attendu:**
- Description de la commande sync
- Options `--repo` et `--storage-path`
- Exemples d'utilisation

### Test 1.4: Affichage de l'aide pour status

```bash
poetry run prompt-manager status --help
```

**Résultat attendu:**
- Description de la commande status
- Aucune option requise
- Exemples d'utilisation

---

## Tests de la Commande Init

### Test 2.1: Initialisation dans un nouveau répertoire

```bash
# Créer un répertoire de test
mkdir -p /tmp/test-prompt-manager-1
cd /tmp/test-prompt-manager-1

# Initialiser
poetry run prompt-manager init
```

**Résultat attendu:**
- Message "✓ Initialization complete"
- Création de `.prompt-manager/` dans le répertoire courant
- Création de `.prompt-manager/config.yaml`
- Création de `~/.prompt-manager/storage/`
- Création de `~/.prompt-manager/storage/prompts/`
- Création de `~/.prompt-manager/storage/rules/`
- Création de `~/.prompt-manager/storage/.gitignore`
- Message indiquant les prochaines étapes

**Vérifications:**
```bash
# Vérifier la structure créée
ls -la .prompt-manager/
cat .prompt-manager/config.yaml
ls -la ~/.prompt-manager/storage/
```

**Contenu attendu de config.yaml:**
```yaml
repo_url: null
last_sync_timestamp: null
last_sync_commit: null
storage_path: /root/.prompt-manager/storage
```

### Test 2.2: Initialisation avec storage path personnalisé

```bash
# Créer un répertoire de test
mkdir -p /tmp/test-prompt-manager-2
cd /tmp/test-prompt-manager-2

# Initialiser avec storage personnalisé
poetry run prompt-manager init --storage-path /tmp/custom-storage
```

**Résultat attendu:**
- Message "✓ Initialization complete"
- Création de `.prompt-manager/config.yaml` avec `storage_path: /tmp/custom-storage`
- Création de `/tmp/custom-storage/prompts/`
- Création de `/tmp/custom-storage/rules/`

**Vérifications:**
```bash
cat .prompt-manager/config.yaml | grep storage_path
ls -la /tmp/custom-storage/
```

### Test 2.3: Tentative de ré-initialisation (cas d'erreur)

```bash
# Dans le même répertoire que Test 2.1
cd /tmp/test-prompt-manager-1

# Essayer d'initialiser à nouveau
poetry run prompt-manager init
```

**Résultat attendu:**
- Message d'erreur: "Error: .prompt-manager/ directory already exists. Project is already initialized."
- Code de sortie: 1
- Aucune modification des fichiers existants

---

## Tests de la Commande Sync

### Test 3.1: Sync sans initialisation préalable (cas d'erreur)

```bash
# Créer un nouveau répertoire sans init
mkdir -p /tmp/test-prompt-manager-3
cd /tmp/test-prompt-manager-3

# Essayer de sync
poetry run prompt-manager sync --repo git@gitlab.com:waewoo/prompt-manager-data.git
```

**Résultat attendu:**
- Message d'erreur: "Error: Configuration not found. Run 'prompt-manager init' first."
- Code de sortie: 1

### Test 3.2: Première synchronisation avec repository URL

```bash
# Initialiser d'abord
cd /tmp/test-prompt-manager-1
poetry run prompt-manager init

# Première sync avec URL
# Note: Utilisez SSH ou configurez git credential helper au lieu de mettre le token dans l'URL
poetry run prompt-manager sync --repo git@gitlab.com:waewoo/prompt-manager-data.git
```

**Résultat attendu:**
- Message "Syncing prompts..."
- Affichage de l'URL du repository
- Affichage du chemin de storage
- Message "Cloning repository..."
- Message "Extracting prompts..."
- Message "✓ Sync complete"
- Affichage du commit hash (ex: "d0ec0a5")
- Affichage du chemin de synchronisation

**Vérifications:**
```bash
# Vérifier que les prompts ont été synchronisés
ls -la ~/.prompt-manager/storage/prompts/

# Vérifier que le config a été mis à jour
cat .prompt-manager/config.yaml
```

**Contenu attendu de config.yaml (après sync):**
```yaml
repo_url: git@gitlab.com:waewoo/prompt-manager-data.git
last_sync_timestamp: 2025-11-12T09:36:00+00:00  # (ou la date actuelle)
last_sync_commit: d0ec0a5
storage_path: /root/.prompt-manager/storage
```

### Test 3.3: Synchronisation suivante sans spécifier l'URL

```bash
# Dans le même répertoire que Test 3.2
cd /tmp/test-prompt-manager-1

# Sync sans --repo (doit lire l'URL du config)
poetry run prompt-manager sync
```

**Résultat attendu:**
- Utilisation automatique de l'URL configurée
- Même processus que Test 3.2
- Message "✓ Sync complete"

### Test 3.4: Sync avec URL différente (changement de repository)

```bash
cd /tmp/test-prompt-manager-1

# Sync avec une nouvelle URL (si vous avez un autre repo de test)
# Pour ce test, on utilise la même URL pour simplifier
poetry run prompt-manager sync --repo git@gitlab.com:waewoo/prompt-manager-data.git
```

**Résultat attendu:**
- Synchronisation réussie avec la nouvelle URL
- Mise à jour de `repo_url` dans config.yaml

### Test 3.5: Sync sans URL et sans config (cas d'erreur)

```bash
# Créer un nouveau répertoire et initialiser
mkdir -p /tmp/test-prompt-manager-4
cd /tmp/test-prompt-manager-4
poetry run prompt-manager init

# Essayer de sync sans --repo
poetry run prompt-manager sync
```

**Résultat attendu:**
- Message d'erreur: "Error: No repository URL configured. Use --repo flag to specify a repository."
- Code de sortie: 1

### Test 3.6: Sync avec URL invalide (cas d'erreur)

```bash
cd /tmp/test-prompt-manager-1

# Essayer avec une URL invalide
poetry run prompt-manager sync --repo https://invalid-url-that-does-not-exist.com/repo.git
```

**Résultat attendu:**
- Message d'erreur indiquant le problème (résolution DNS, repository introuvable, etc.)
- Code de sortie: 1
- Message d'aide pour vérifier l'URL

### Test 3.7: Sync avec repository vide (cas d'erreur)

```bash
# Si vous avez un repository vide pour tester
# Sinon, skip ce test
# poetry run prompt-manager sync --repo <empty-repo-url>
```

**Résultat attendu (si applicable):**
- Message d'erreur: "Repository is empty (no commits found)."
- Instructions pour ajouter des commits au repository
- Code de sortie: 1

### Test 3.8: Sync avec repository sans dossier prompts/ (cas d'erreur)

```bash
# Si vous avez un repository sans prompts/ pour tester
# Sinon, skip ce test
# poetry run prompt-manager sync --repo <repo-without-prompts-dir>
```

**Résultat attendu (si applicable):**
- Message d'erreur: "Repository does not contain a prompts/ directory."
- Code de sortie: 1

---

## Tests de la Commande Status

### Test 4.1: Status sans initialisation (cas d'erreur)

```bash
# Créer un nouveau répertoire sans init
mkdir -p /tmp/test-prompt-manager-5
cd /tmp/test-prompt-manager-5

# Essayer status
poetry run prompt-manager status
```

**Résultat attendu:**
- Message d'erreur: "Error: Configuration not found. Run 'prompt-manager init' first."
- Code de sortie: 1

### Test 4.2: Status après init mais avant sync

```bash
cd /tmp/test-prompt-manager-1
# Réinitialiser pour test propre
rm -rf .prompt-manager
poetry run prompt-manager init

# Vérifier status
poetry run prompt-manager status
```

**Résultat attendu:**
- Affichage du titre "Prompt Manager Status"
- Affichage du chemin de storage
- Message "Repository: Not configured"
- Suggestion d'exécuter la commande sync
- Pas d'information de sync
- Code de sortie: 0

### Test 4.3: Status après sync réussi

```bash
cd /tmp/test-prompt-manager-1

# Sync d'abord
# Note: Utilisez SSH ou configurez git credential helper au lieu de mettre le token dans l'URL
poetry run prompt-manager sync --repo git@gitlab.com:waewoo/prompt-manager-data.git

# Vérifier status
poetry run prompt-manager status
```

**Résultat attendu:**
- Affichage du titre "Prompt Manager Status"
- Affichage du chemin de storage
- Affichage de l'URL du repository
- Affichage de "Last sync: X minutes ago" (format lisible)
- Affichage du commit hash (ex: "d0ec0a5")
- Message "Checking for updates..."
- Message "✓ Up to date" (si pas de nouveaux commits)
- OU "⚠ Updates available (X commits behind)" (si nouveaux commits disponibles)
- Code de sortie: 0

### Test 4.4: Status avec repository inaccessible

```bash
cd /tmp/test-prompt-manager-1

# Modifier le config pour utiliser une URL invalide
# (ou couper la connexion réseau si possible)
# Pour ce test, on peut modifier temporairement le config

# Sauvegarder config
cp .prompt-manager/config.yaml .prompt-manager/config.yaml.backup

# Modifier l'URL
sed -i 's|https://.*|https://invalid-url.com/repo.git|' .prompt-manager/config.yaml

# Vérifier status
poetry run prompt-manager status

# Restaurer config
mv .prompt-manager/config.yaml.backup .prompt-manager/config.yaml
```

**Résultat attendu:**
- Affichage des informations en cache (dernier sync, commit)
- Message "⚠ Could not check for updates"
- Message "Check network connection or repository access"
- Code de sortie: 0 (status est informatif seulement)

---

## Tests de Validation

### Test 5.1: Validation d'un répertoire avec prompts valides

```bash
# Créer un répertoire de test avec un prompt valide
mkdir -p /tmp/test-prompts
cat > /tmp/test-prompts/example.md << 'EOF'
---
name: example-prompt
description: An example prompt for testing
version: 1.0.0
author: Test User
tags:
  - example
  - test
---

# Example Prompt

This is an example prompt for testing validation.

Variables:
- {{variable1}}: Description of variable 1
- {{variable2}}: Description of variable 2
EOF

# Valider
poetry run prompt-manager validate /tmp/test-prompts
```

**Résultat attendu:**
- Message de succès indiquant que tous les prompts sont valides
- Affichage du nombre de fichiers validés
- Code de sortie: 0

### Test 5.2: Validation avec option --json

```bash
poetry run prompt-manager validate /tmp/test-prompts --json
```

**Résultat attendu:**
- Sortie au format JSON avec les résultats de validation
- Code de sortie: 0

### Test 5.3: Validation avec répertoire invalide (cas d'erreur)

```bash
poetry run prompt-manager validate /tmp/does-not-exist
```

**Résultat attendu:**
- Message d'erreur: "Error: Directory '/tmp/does-not-exist' does not exist"
- Code de sortie: 1

### Test 5.4: Validation avec fichier au lieu de répertoire (cas d'erreur)

```bash
touch /tmp/test-file.txt
poetry run prompt-manager validate /tmp/test-file.txt
```

**Résultat attendu:**
- Message d'erreur: "Error: '/tmp/test-file.txt' is not a directory"
- Code de sortie: 1

### Test 5.5: Validation d'un prompt avec erreurs

```bash
# Créer un prompt invalide (YAML malformé)
mkdir -p /tmp/test-prompts-invalid
cat > /tmp/test-prompts-invalid/invalid.md << 'EOF'
---
name: invalid-prompt
description: Missing closing ---
version: 1.0.0

This is invalid because the frontmatter is not closed properly
EOF

# Valider
poetry run prompt-manager validate /tmp/test-prompts-invalid
```

**Résultat attendu:**
- Message d'erreur indiquant les problèmes trouvés
- Détails sur les erreurs de validation
- Code de sortie: 1

---

## Tests des Règles (Rules)

### Test 5.6: Validation d'un répertoire avec règles valides

```bash
# Créer un répertoire de test avec une règle valide
mkdir -p /tmp/test-rules
cat > /tmp/test-rules/python-style.md << 'EOF'
name: python-style-guide
description: Python coding standards and best practices
type: rule
category: coding-standards
tags:
  - python
  - pep8
  - style
version: 1.0.0
author: team-platform
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
EOF

# Valider
poetry run prompt-manager validate /tmp/test-rules
```

**Résultat attendu:**
- Message de succès indiquant que tous les fichiers sont valides
- Affichage du nombre de fichiers validés (incluant les règles)
- Code de sortie: 0

### Test 5.7: Validation d'une règle avec catégorie manquante (cas d'erreur)

```bash
# Créer une règle invalide sans catégorie
mkdir -p /tmp/test-rules-invalid
cat > /tmp/test-rules-invalid/invalid-rule.md << 'EOF'
name: invalid-rule
description: Rule missing required category field
type: rule
>>>
# Invalid Rule

This rule is missing the required 'category' field.
EOF

# Valider
poetry run prompt-manager validate /tmp/test-rules-invalid
```

**Résultat attendu:**
- Message d'erreur indiquant que le champ 'category' est manquant
- Code de sortie: 1

### Test 5.8: Validation d'une règle avec catégorie personnalisée (warning)

```bash
# Créer une règle avec catégorie personnalisée
cat > /tmp/test-rules/custom-category.md << 'EOF'
name: custom-rule
description: Rule with custom category
type: rule
category: my-custom-category
>>>
# Custom Rule

This rule uses a custom category.
EOF

# Valider
poetry run prompt-manager validate /tmp/test-rules
```

**Résultat attendu:**
- Warning indiquant que la catégorie n'est pas standard
- Liste des catégories valides suggérées
- Validation réussie malgré le warning
- Code de sortie: 0

### Test 5.9: Validation d'une règle avec applies_to

```bash
# Créer une règle avec applies_to
cat > /tmp/test-rules/api-design.md << 'EOF'
name: api-design-patterns
description: REST API design best practices
type: rule
category: architecture
tags:
  - rest
  - api
  - http
version: 1.2.0
applies_to:
  - python
  - fastapi
  - flask
>>>
# API Design Patterns

## Resource Naming
- Use plural nouns for collections: `/users`, `/posts`
- Use singular for singletons: `/profile`
EOF

# Valider
poetry run prompt-manager validate /tmp/test-rules
```

**Résultat attendu:**
- Validation réussie
- Affichage confirmant la règle avec le champ applies_to
- Code de sortie: 0

### Test 5.10: Validation mixte prompts et règles

```bash
# Créer un répertoire avec les deux types
mkdir -p /tmp/test-mixed
cat > /tmp/test-mixed/prompt.md << 'EOF'
name: example-prompt
description: An example prompt
>>>
This is a prompt.
EOF

cat > /tmp/test-mixed/rule.md << 'EOF'
name: example-rule
description: An example rule
type: rule
category: testing
>>>
This is a rule.
EOF

# Valider
poetry run prompt-manager validate /tmp/test-mixed
```

**Résultat attendu:**
- Validation réussie pour les deux types de fichiers
- Distinction claire entre prompts et règles dans l'output
- Code de sortie: 0

### Test 5.11: Validation d'une règle avec nom invalide (cas d'erreur)

```bash
# Créer une règle avec nom invalide (pas en kebab-case)
cat > /tmp/test-rules-invalid/invalid-name.md << 'EOF'
name: InvalidName_With_Underscores
description: Rule with invalid name format
type: rule
category: testing
>>>
# Invalid Name

This rule has an invalid name format.
EOF

# Valider
poetry run prompt-manager validate /tmp/test-rules-invalid
```

**Résultat attendu:**
- Message d'erreur indiquant que le nom doit être en kebab-case
- Exemples de noms valides fournis
- Code de sortie: 1

---

## Tests de Gestion d'Erreurs

### Test 6.1: Permissions insuffisantes (cas d'erreur)

```bash
# Créer un répertoire sans permissions d'écriture
mkdir -p /tmp/test-no-write
chmod 555 /tmp/test-no-write
cd /tmp/test-no-write

# Essayer d'initialiser
poetry run prompt-manager init

# Restaurer permissions
chmod 755 /tmp/test-no-write
```

**Résultat attendu:**
- Message d'erreur: "Error: Permission denied. Check directory permissions."
- Code de sortie: 1

### Test 6.2: Vérification de retry sur erreur réseau

```bash
cd /tmp/test-prompt-manager-1

# Sync avec une URL qui timeout (pour tester le retry)
# Note: Ce test peut prendre du temps (plusieurs tentatives)
# Si vous n'avez pas d'URL qui timeout, skip ce test
# poetry run prompt-manager sync --repo https://example-timeout-url.com/repo.git
```

**Résultat attendu (si applicable):**
- Messages "Network error. Retrying... (attempt X/3)"
- Délai exponentiel entre les tentatives (1s, 2s, 4s)
- Message d'erreur final après 3 tentatives
- Code de sortie: 1

---

## Tests de Nettoyage Temporaire

### Test 7.1: Vérification du nettoyage des répertoires temporaires

```bash
cd /tmp/test-prompt-manager-1

# Noter le nombre de répertoires temporaires avant
BEFORE=$(ls /tmp | grep -c tmp || echo 0)

# Faire plusieurs syncs
poetry run prompt-manager sync
poetry run prompt-manager sync
poetry run prompt-manager sync

# Noter le nombre de répertoires temporaires après
AFTER=$(ls /tmp | grep -c tmp || echo 0)

# Afficher la différence
echo "Répertoires temporaires avant: $BEFORE"
echo "Répertoires temporaires après: $AFTER"
echo "Note: Devrait être similaire (nettoyage automatique)"
```

**Résultat attendu:**
- Les répertoires temporaires sont nettoyés après chaque sync
- Pas d'accumulation de répertoires `/tmp/tmp*` après les opérations

---

## Tests de Workflow Complet

### Test 8.1: Workflow équipe complète (nouveau membre)

```bash
# Simuler un nouveau membre d'équipe qui rejoint un projet
mkdir -p /tmp/team-project
cd /tmp/team-project

# Le projet existe déjà avec .prompt-manager/
mkdir -p .prompt-manager
cat > .prompt-manager/config.yaml << 'EOF'
repo_url: git@gitlab.com:waewoo/prompt-manager-data.git
last_sync_timestamp: null
last_sync_commit: null
storage_path: /root/.prompt-manager/storage
EOF

# Le nouveau membre sync simplement
poetry run prompt-manager sync

# Vérifier le status
poetry run prompt-manager status
```

**Résultat attendu:**
- Sync réussi en utilisant l'URL du config
- Prompts disponibles dans `~/.prompt-manager/storage/prompts/`
- Status affiche les informations correctes
- Code de sortie: 0

### Test 8.2: Workflow mise à jour quotidienne

```bash
cd /tmp/test-prompt-manager-1

# Vérifier s'il y a des mises à jour
poetry run prompt-manager status

# Faire la mise à jour
poetry run prompt-manager sync

# Vérifier le nouveau status
poetry run prompt-manager status
```

**Résultat attendu:**
- Status affiche l'état actuel
- Sync met à jour les prompts si nécessaire
- Nouveau status confirme la synchronisation

---

## Nettoyage Final

### Nettoyage des répertoires de test

```bash
# Supprimer tous les répertoires de test
rm -rf /tmp/test-prompt-manager-*
rm -rf /tmp/test-prompts*
rm -rf /tmp/custom-storage
rm -rf /tmp/team-project
rm -rf /tmp/test-file.txt
rm -rf /tmp/test-no-write

echo "Nettoyage terminé"
```

### Nettoyage du storage centralisé (optionnel)

```bash
# Si vous voulez nettoyer complètement le storage centralisé
rm -rf ~/.prompt-manager/

echo "Storage centralisé nettoyé"
```

---

## Checklist de Test

Utilisez cette checklist pour suivre votre progression :

### Commandes de Base
- [ ] Test 1.1: Help général
- [ ] Test 1.2: Help init
- [ ] Test 1.3: Help sync
- [ ] Test 1.4: Help status

### Init
- [ ] Test 2.1: Init basique
- [ ] Test 2.2: Init avec storage personnalisé
- [ ] Test 2.3: Erreur ré-initialisation

### Sync
- [ ] Test 3.1: Erreur sync sans init
- [ ] Test 3.2: Première sync avec URL
- [ ] Test 3.3: Sync suivante sans URL
- [ ] Test 3.4: Sync avec URL différente
- [ ] Test 3.5: Erreur sync sans URL configurée
- [ ] Test 3.6: Erreur URL invalide
- [ ] Test 3.7: Erreur repository vide (optionnel)
- [ ] Test 3.8: Erreur sans prompts/ (optionnel)

### Status
- [ ] Test 4.1: Erreur status sans init
- [ ] Test 4.2: Status après init
- [ ] Test 4.3: Status après sync
- [ ] Test 4.4: Status avec réseau inaccessible

### Validation
- [ ] Test 5.1: Validation prompts valides
- [ ] Test 5.2: Validation JSON
- [ ] Test 5.3: Erreur répertoire inexistant
- [ ] Test 5.4: Erreur fichier au lieu de répertoire
- [ ] Test 5.5: Validation avec erreurs

### Règles (Rules)
- [ ] Test 5.6: Validation règles valides
- [ ] Test 5.7: Erreur catégorie manquante
- [ ] Test 5.8: Warning catégorie personnalisée
- [ ] Test 5.9: Validation avec applies_to
- [ ] Test 5.10: Validation mixte prompts/règles
- [ ] Test 5.11: Erreur nom invalide (kebab-case)

### Gestion d'Erreurs
- [ ] Test 6.1: Permissions insuffisantes
- [ ] Test 6.2: Retry réseau (optionnel)

### Nettoyage
- [ ] Test 7.1: Vérification nettoyage temporaire

### Workflow
- [ ] Test 8.1: Workflow équipe
- [ ] Test 8.2: Workflow mise à jour

### Nettoyage Final
- [ ] Nettoyage répertoires de test
- [ ] Nettoyage storage (optionnel)

---

## Notes de Test

Utilisez cet espace pour noter vos observations pendant les tests :

```
Date: ______________
Testeur: ______________

Observations:
-
-
-

Problèmes rencontrés:
-
-
-

Tests réussis: ___ / ___
Tests échoués: ___ / ___
```

---

## Résolution de Problèmes Courants

### Le sync échoue avec "Reference at 'HEAD' does not exist"
- **Cause:** Bug corrigé dans la version actuelle
- **Solution:** Vérifier que vous utilisez la dernière version du code

### Le storage n'est pas créé
- **Cause:** Permissions insuffisantes
- **Solution:** Vérifier les permissions du répertoire home

### Les prompts ne sont pas synchronisés
- **Cause:** Le repository ne contient pas de dossier prompts/
- **Solution:** Vérifier la structure du repository distant

### Config.yaml corrompu
- **Cause:** Modification manuelle incorrecte
- **Solution:** Supprimer .prompt-manager/ et ré-initialiser

---

## Tests de la Commande Deploy

### Test 9.1: Deploy d'un prompt vers Continue (succès)

```bash
# Assurer que le storage est synchronisé
cd /tmp/test-prompt-manager-1
poetry run prompt-manager sync

# Deploy un prompt spécifique vers Continue
poetry run prompt-manager deploy "code-review" --handlers continue
```

**Résultat attendu:**
- Message "Deploying to continue..."
- Message "✓ Deployment to continue successful."
- Fichier créé dans `~/.continue/prompts/code-review.md`
- Frontmatter contient `name`, `description`, `invokable: true`
- Backup créé si fichier existait (ex: code-review.md.bak)
- Code de sortie: 0

**Vérifications:**
```bash
cat ~/.continue/prompts/code-review.md | head -10
# Vérifier présence de name, description, invokable: true
ls ~/.continue/prompts/ | grep code-review
```

### Test 9.2: Deploy d'une règle vers Continue (succès)

```bash
# Deploy une règle spécifique
poetry run prompt-manager deploy "python-style" --handlers continue
```

**Résultat attendu:**
- Message "Deploying to continue..."
- Message "✓ Deployment to continue successful."
- Fichier créé dans `~/.continue/rules/python-style.md`
- Frontmatter contient `name`, optionnels comme `globs`, `description`, `alwaysApply: false`
- Backup créé si fichier existait
- Code de sortie: 0

**Vérifications:**
```bash
cat ~/.continue/rules/python-style.md | head -10
ls ~/.continue/rules/ | grep python-style
```

### Test 9.3: Deploy avec handlers multiples (succès)

```bash
# Si d'autres handlers sont implémentés, tester avec plusieurs
# Pour l'instant, seulement continue
poetry run prompt-manager deploy "code-review" --handlers continue
```

**Résultat attendu:**
- Déploiement réussi pour le handler spécifié
- Code de sortie: 0

### Test 9.4: Deploy sans handler spécifié (succès)

```bash
poetry run prompt-manager deploy "code-review"
```

**Résultat attendu:**
- Déploiement vers tous les handlers enregistrés (actuellement continue)
- Messages de succès pour chaque handler
- Code de sortie: 0

### Test 9.5: Deploy d'un prompt inexistant (erreur)

```bash
poetry run prompt-manager deploy "non-existent-prompt" --handlers continue
```

**Résultat attendu:**
- Message d'erreur: "Prompt 'non-existent-prompt' not found in storage"
- Code de sortie: 1

### Test 9.6: Deploy avec handler invalide (erreur)

```bash
poetry run prompt-manager deploy "code-review" --handlers invalid-handler
```

**Résultat attendu:**
- Message d'erreur: "ToolHandler with name 'invalid-handler' not found."
- Code de sortie: 1

### Test 9.7: Vérification du mécanisme de backup

```bash
# Créer un fichier existant dans Continue
echo "old content" > ~/.continue/prompts/code-review.md

# Deploy à nouveau
poetry run prompt-manager deploy "code-review" --handlers continue

# Vérifier backup
ls ~/.continue/prompts/ | grep code-review.bak
cat ~/.continue/prompts/code-review.md  # Nouveau contenu
```

**Résultat attendu:**
- Backup créé: code-review.md.bak avec "old content"
- Fichier principal mis à jour avec nouveau contenu
- Message de backup dans l'output

### Test 9.8: Vérification de déploiement

```bash
# Après deploy, vérifier que le contenu est correct
poetry run prompt-manager deploy "code-review" --handlers continue

# Le handler vérifie automatiquement, mais pour manuel:
cat ~/.continue/prompts/code-review.md | grep -E "(name|description|invokable)"
```

**Résultat attendu:**
- Frontmatter correct avec name, description, invokable: true
- Contenu du prompt présent

### Test 9.9: Deploy avec filtrage par tags (CLI)

**Prérequis:** Avoir des prompts/rules avec différents tags dans le storage

```bash
# Synchroniser le storage avec des prompts taggés
cd /tmp/test-prompt-manager-1
poetry run prompt-manager sync

# Vérifier les tags des prompts (exemple)
# code-review.md devrait avoir tags: ["python", "review"]
# python-style.md devrait avoir tags: ["python", "style"]

# Deploy uniquement les items avec tag "python"
poetry run prompt-manager deploy --tags python --handlers continue

# Vérifier les fichiers déployés
ls ~/.continue/prompts/
ls ~/.continue/rules/
```

**Résultat attendu:**
- Seuls les prompts/rules contenant le tag "python" sont déployés
- Items sans ce tag sont ignorés
- Messages de déploiement uniquement pour items filtrés
- Code de sortie: 0

### Test 9.10: Deploy avec tags multiples (CLI)

```bash
# Deploy items avec tags "python" OU "review"
poetry run prompt-manager deploy --tags python,review --handlers continue

# Vérifier
ls ~/.continue/prompts/ | wc -l
```

**Résultat attendu:**
- Items contenant au moins un des tags spécifiés sont déployés
- Plus d'items que le test 9.9 (qui ne filtrait que "python")
- Code de sortie: 0

### Test 9.11: Configuration de deploy_tags dans config.yaml

```bash
cd /tmp/test-prompt-manager-1

# Éditer manuellement config.yaml pour ajouter deploy_tags
cat > .prompt-manager/config.yaml << 'EOF'
repo_url: https://github.com/example/prompts.git
last_sync_timestamp: 2024-11-15T10:00:00+00:00
last_sync_commit: abc1234
storage_path: ~/.prompt-manager/storage
deploy_tags:
  - python
  - review
EOF

# Deploy sans options (utilise deploy_tags de config)
poetry run prompt-manager deploy --handlers continue

# Vérifier
ls ~/.continue/prompts/
```

**Résultat attendu:**
- Seuls les items avec tags "python" OU "review" sont déployés
- Comportement identique à `--tags python,review`
- Config.yaml est utilisé automatiquement
- Code de sortie: 0

### Test 9.12: Configuration de target_handlers dans config.yaml

```bash
# Éditer config.yaml pour ajouter target_handlers
cat >> .prompt-manager/config.yaml << 'EOF'
target_handlers:
  - continue
EOF

# Deploy sans option --handlers (utilise config)
poetry run prompt-manager deploy code-review

# Vérifier
ls ~/.continue/prompts/code-review.md
```

**Résultat attendu:**
- Déploiement vers "continue" uniquement (depuis config)
- Pas besoin de spécifier --handlers
- Code de sortie: 0

### Test 9.13: Override de config avec options CLI

```bash
# Config contient deploy_tags: ["python"] et target_handlers: ["continue"]
cat > .prompt-manager/config.yaml << 'EOF'
repo_url: https://github.com/example/prompts.git
storage_path: ~/.prompt-manager/storage
deploy_tags:
  - python
target_handlers:
  - continue
EOF

# Override avec --tags pour déployer tous les items (tag différent)
poetry run prompt-manager deploy --tags review --handlers continue
```

**Résultat attendu:**
- Les options CLI `--tags review` et `--handlers continue` ont priorité
- Les valeurs de config.yaml sont ignorées
- Seuls items avec tag "review" déployés
- Code de sortie: 0

### Test 9.14: Deploy sans nom (tous les items filtrés)

```bash
# Config avec deploy_tags
cat > .prompt-manager/config.yaml << 'EOF'
repo_url: https://github.com/example/prompts.git
storage_path: ~/.prompt-manager/storage
deploy_tags:
  - python
target_handlers:
  - continue
EOF

# Deploy TOUS les items qui matchent les filtres (pas de nom spécifié)
poetry run prompt-manager deploy

# Vérifier
ls ~/.continue/prompts/
ls ~/.continue/rules/
```

**Résultat attendu:**
- Tous les prompts ET rules avec tag "python" sont déployés
- Pas seulement un item spécifique
- Messages de déploiement pour chaque item
- Résumé: "X items deployed to continue"
- Code de sortie: 0

### Test 9.15: Deploy sans filtres (tous items, tous handlers)

```bash
# Config SANS deploy_tags ni target_handlers
cat > .prompt-manager/config.yaml << 'EOF'
repo_url: https://github.com/example/prompts.git
storage_path: ~/.prompt-manager/storage
EOF

# Deploy sans options
poetry run prompt-manager deploy
```

**Résultat attendu:**
- TOUS les prompts et rules dans le storage sont déployés
- Déploiement vers TOUS les handlers enregistrés (actuellement continue)
- Pas de filtrage appliqué
- Code de sortie: 0

### Test 9.16: Deploy avec tags vides (désactiver filtrage config)

```bash
# Config avec deploy_tags
cat > .prompt-manager/config.yaml << 'EOF'
storage_path: ~/.prompt-manager/storage
deploy_tags:
  - python
EOF

# Override pour désactiver le filtrage par tags
poetry run prompt-manager deploy --tags ""
```

**Résultat attendu:**
- Le filtrage par tags est désactivé
- TOUS les items sont déployés (ignore deploy_tags de config)
- Code de sortie: 0

### Test 9.17: Vérification du message "No content files match"

```bash
# Deploy avec un tag qui n'existe sur aucun item
poetry run prompt-manager deploy --tags nonexistent-tag --handlers continue
```

**Résultat attendu:**
- Message: "No content files match the specified criteria."
- Aucun déploiement effectué
- Code de sortie: 0 (pas une erreur, juste aucun match)

---

## Contact et Support

Pour signaler des bugs ou demander de l'aide :
- GitHub Issues: https://github.com/anthropics/claude-code/issues
- Documentation: Voir README.md
