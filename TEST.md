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
repo_url: https://waewoo:glpat-z3z8MZWyIson-qpVvFjjaW86MQp1OjF1ZnMwCw.01.120u3igft@gitlab.com/waewoo/prompt-manager-data
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
poetry run prompt-manager sync --repo https://waewoo:glpat-z3z8MZWyIson-qpVvFjjaW86MQp1OjF1ZnMwCw.01.120u3igft@gitlab.com/waewoo/prompt-manager-data
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

## Contact et Support

Pour signaler des bugs ou demander de l'aide :
- GitHub Issues: https://github.com/anthropics/claude-code/issues
- Documentation: Voir README.md
