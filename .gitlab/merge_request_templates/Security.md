# 🛡️ Checklist Sécurité MR

## 📋 Auto-validation Développeur
- [ ] **Secrets** : Aucun mot de passe, clé d'API ou certificat n'est présent dans le code.
- [ ] **Dépendances** : Pas de nouvelles dépendances introduites sans validation (ex: licenses copyleft).
- [ ] **Logs** : Aucune donnée sensible (PII, tokens) n'est logguée en clair.
- [ ] **Entrées** : Toutes les entrées utilisateur sont validées/assainies (Anti-XSS/SQLi).

## 🔍 Analyse Automatique
- [ ] SAST (Static Analysis) : Le pipeline est au vert sans vulnérabilité critique.
- [ ] Secret Detection : Le job GitLab a validé l'absence de secrets.
- [ ] Dependency Scanning : Pas de CVE critique détectée.

## 📝 Note Additionnelle
*Expliquez ici tout impact potentiel sur la sécurité du système.*
