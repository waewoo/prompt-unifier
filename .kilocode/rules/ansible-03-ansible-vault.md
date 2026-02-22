# Ansible Vault Standards

Best practices for encrypting sensitive data with Ansible Vault and managing vault files.

**Category:** security | **Tags:** ansible, vault, security, secrets, standards | **Version:** 1.0.0 | **Author:** prompt-unifier | **Language:** yaml | **AppliesTo:** **/*.yml, **/*.yaml

# Ansible Vault Standards

This document outlines the best practices for using Ansible Vault to encrypt sensitive data,
ensuring that credentials and other secrets are never stored in plain text in version control.

## 1. Encryption of Sensitive Data

- **Principle**: All sensitive data (passwords, API keys, private keys, database credentials, etc.)
  must be encrypted using Ansible Vault.
- **Never Commit Plaintext Secrets**: Sensitive information must **NEVER** be committed to Git in
  plaintext.
- **Granularity**: Encrypt only the sensitive values, not entire files, unless the entire file is
  sensitive. This allows for easier diffs and merges of non-sensitive parts.

```yaml
# Bad: Plaintext password in vars/main.yml
db_password: "mysecretpassword"  # pragma: allowlist secret

# Good: Encrypted password in vars/main.yml (after ansible-vault encrypt_string)
db_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  636430623938393031303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030
```

## 2. Stratégies de Rotation des Secrets

- **Principe**: Les secrets doivent être régulièrement renouvelés pour minimiser les risques en cas
  de compromission.
- **Automatisation**: Utiliser des outils ou des scripts pour automatiser la rotation des secrets.
- **Exemple**:
  - **Base de données**: Configurer la base de données pour une rotation automatique des mots de
    passe, et mettre à jour le secret dans le coffre-fort (Vault, Secrets Manager) en conséquence.
  - **Clés API**: Générer de nouvelles clés API et invalider les anciennes à intervalles réguliers.

## 3. Gestion des Fichiers Vault

### Organisation

- **Principe**: Organiser les fichiers Vault de manière logique, souvent par environnement ou par
  type de secret.
- **Exemple**:
  - `group_vars/all/vault.yml`: Secrets globaux (très peu).
  - `group_vars/production/vault.yml`: Secrets spécifiques à la production.
  - `host_vars/webserver1/vault.yml`: Secrets spécifiques à un hôte.
  - `roles/my_role/vars/vault.yml`: Secrets spécifiques à un rôle.

### Vault Password Management

- **Principe**: Le mot de passe du Vault ne doit jamais être stocké en clair.
- **Méthodes**:
  - **`--vault-password-file`**: Utiliser un fichier contenant le mot de passe, protégé par les
    permissions du système de fichiers.
  - **`--vault-id`**: Utiliser un `vault-id` pour référencer un script ou un programme qui fournit
    le mot de passe (e.g., un gestionnaire de secrets comme HashiCorp Vault, AWS Secrets Manager).
  - **Environnement Variable**: `ANSIBLE_VAULT_PASSWORD_FILE` ou `ANSIBLE_VAULT_PASSWORD`.

```bash
# Exécuter un playbook avec un fichier de mot de passe
ansible-playbook site.yml --vault-password-file ~/.ansible/vault_pass.txt

# Exécuter avec un vault-id (e.g., pour AWS Secrets Manager)
ansible-playbook site.yml --vault-id aws_secrets_manager@aws
```

## 4. Intégration CI/CD

- **Principe**: Intégrer le déchiffrement du Vault dans votre pipeline CI/CD de manière sécurisée.
- **Méthode**: Le mot de passe du Vault doit être fourni au pipeline via une variable
  d'environnement sécurisée ou un gestionnaire de secrets intégré au CI/CD (e.g., GitHub Actions
  Secrets, GitLab CI/CD Variables).
- **Accès Limité**: Le pipeline CI/CD doit avoir un accès limité et temporaire au mot de passe du
  Vault.