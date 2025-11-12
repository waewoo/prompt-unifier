# Security & Secrets Detection - Raw Idea

## Context

Après avoir implémenté l'intégration Git et la synchronisation avec des repositories distants, nous avons identifié un risque majeur : l'exposition accidentelle de secrets (tokens, API keys, credentials) dans le code ou la documentation.

**Incident récent :**
- Token GitLab (`glpat-*`) exposé dans TEST.md et plusieurs fichiers
- Dû être retiré manuellement en plusieurs commits
- Risque de fuite si détecté tardivement

## Problème

Sans mécanismes de détection automatique, les développeurs peuvent facilement :
1. Committer des secrets par erreur (tokens, passwords, API keys)
2. Ne pas détecter les vulnérabilités dans les dépendances Python
3. Introduire du code non sécurisé (injections SQL, XSS, etc.)
4. Exposer des informations sensibles dans les logs ou configs

**Impact :**
- 🔴 Sécurité compromise si secrets exposés dans le repository public
- 🔴 Vulnérabilités non détectées peuvent être exploitées
- 🟡 Temps perdu à nettoyer les commits après détection manuelle
- 🟡 Risque de devoir révoquer et regénérer tous les secrets

## Objectif

Implémenter une couche de sécurité complète qui :
1. **Empêche** les commits contenant des secrets
2. **Détecte** les vulnérabilités de sécurité dans le code et les dépendances
3. **Automatise** ces vérifications localement (pre-commit) et en CI/CD
4. **Documente** les bonnes pratiques de sécurité pour l'équipe

## Solution proposée

### 1. Secrets Detection (Pre-commit + CI)

**Outils à intégrer :**
- **detect-secrets** (Yelp) - Détection de patterns de secrets
- **gitleaks** - Alternative/complément pour patterns Git
- **trufflehog** - Scan de l'historique Git

**Fonctionnalités :**
- Scan des fichiers avant commit
- Patterns personnalisables (API keys, tokens, passwords, etc.)
- Baseline pour exceptions légitimes (fixtures de test)
- Blocage du commit si secrets détectés
- Scan complet du repo en CI

### 2. Dependency Security Scanning

**Outils à intégrer :**
- **safety** - Scan des vulnérabilités Python (CVE database)
- **pip-audit** - Alternative plus récente et complète
- **Dependabot** - Alertes automatiques GitHub (si applicable)

**Fonctionnalités :**
- Scan de poetry.lock et requirements
- Alertes sur vulnérabilités critiques/hautes
- Suggestions de mise à jour
- Échec du build CI si vulnérabilités critiques

### 3. SAST (Static Application Security Testing)

**Outils à intégrer :**
- **bandit** - SAST spécifique Python
- **semgrep** - Analyse sémantique multi-langage
- **pylint security plugins** - Extensions de sécurité

**Règles à vérifier :**
- Injections SQL potentielles
- Désérialisation non sécurisée (pickle)
- Utilisation de `eval()` ou `exec()`
- Gestion faible des credentials
- Cryptographie faible ou obsolète
- Path traversal vulnerabilities
- Command injection

### 4. Pre-commit Configuration

**Hooks à ajouter :**
```yaml
# .pre-commit-config.yaml
repos:
  # Secrets detection
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  # Security scanning
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ['-c', 'pyproject.toml']

  # Dependency check (optionnel en pre-commit, surtout en CI)
  - repo: local
    hooks:
      - id: safety-check
        name: Safety vulnerability scan
        entry: poetry run safety check
        language: system
        pass_filenames: false
```

### 5. GitLab CI Configuration

**Pipeline stages à ajouter :**
```yaml
# .gitlab-ci.yml
stages:
  - security
  - test
  - build

secrets-detection:
  stage: security
  script:
    - detect-secrets scan --baseline .secrets.baseline
    - gitleaks detect --source . --no-git
  allow_failure: false

dependency-scan:
  stage: security
  script:
    - poetry run safety check --json
    - poetry run pip-audit
  allow_failure: false  # Bloque si critiques

sast-scan:
  stage: security
  script:
    - poetry run bandit -r src/ -f json -o bandit-report.json
    - poetry run semgrep --config auto src/
  artifacts:
    reports:
      sast: bandit-report.json
  allow_failure: true  # Warning seulement initialement
```

## Scope

### In Scope ✅
- Configuration pre-commit hooks pour secrets detection
- Configuration pre-commit hooks pour SAST (bandit)
- Configuration GitLab CI avec security scanning complet
- Documentation des outils et leur utilisation
- Baseline pour exceptions légitimes
- Security policy documentation
- Guide pour développeurs sur bonnes pratiques

### Out of Scope ❌
- DAST (Dynamic Application Security Testing) - pas d'application web
- Penetration testing automatisé
- Container scanning - pas de containers actuellement
- License compliance checking (peut être ajouté plus tard)
- Code signing et artifacts verification
- Production monitoring et alerting

## Bénéfices attendus

1. **Prévention :** 0 secrets committés accidentellement
2. **Détection précoce :** Vulnérabilités détectées avant merge
3. **Conformité :** Standards de sécurité respectés automatiquement
4. **Éducation :** Développeurs apprennent les bonnes pratiques
5. **Confiance :** Repository plus sûr pour open-source ou partage

## Métriques de succès

- ✅ 0 secrets détectés en production après implémentation
- ✅ 100% des PRs scannées avant merge
- ✅ Temps de feedback < 5 minutes en CI
- ✅ 0 vulnérabilités critiques non patchées
- ✅ Documentation complète et suivie par l'équipe

## Prochaines étapes

1. Recherche et évaluation des outils (detect-secrets vs gitleaks)
2. Configuration initiale pre-commit hooks
3. Scan complet du repo actuel et création baseline
4. Configuration GitLab CI pipeline
5. Documentation et guide développeur
6. Formation équipe sur utilisation des outils

## Références

- [detect-secrets](https://github.com/Yelp/detect-secrets)
- [gitleaks](https://github.com/gitleaks/gitleaks)
- [bandit](https://github.com/PyCQA/bandit)
- [safety](https://github.com/pyupio/safety)
- [semgrep](https://semgrep.dev/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitLab Security Scanning](https://docs.gitlab.com/ee/user/application_security/)
