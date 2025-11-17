---
name: ArgoCD Application Standards
description: Best practices for defining ArgoCD Application resources for GitOps deployments.
globs:
- argocd/**/*.yaml
- argocd/**/*.yml
alwaysApply: false
category: deployment
version: 1.0.0
tags:
- argocd
- kubernetes
- gitops
- standards
- deployment
author: prompt-unifier
language: yaml
---
# ArgoCD Application Standards

This document outlines best practices for defining ArgoCD `Application` resources, ensuring consistent, reliable, and secure GitOps deployments to Kubernetes clusters.

## 1. Application Spec Structure

- **`apiVersion` and `kind`**: Always `argoproj.io/v1alpha1` and `Application`.
- **`metadata.name`**: Unique and descriptive (e.g., `my-app-prod`, `infra-monitoring-dev`).
- **`metadata.namespace`**: Deploy ArgoCD Applications into the `argocd` namespace or a dedicated GitOps namespace.
- **`spec.project`**: Always specify the ArgoCD project (e.g., `default`, `my-team-project`). This provides logical grouping and RBAC.
- **`spec.source`**:
  - **`repoURL`**: The Git repository URL containing your Kubernetes manifests (e.g., `git@github.com:my-org/k8s-configs.git`).
  - **`path`**: The path within the repository to the manifests (e.g., `environments/prod/my-app`).
  - **`targetRevision`**: Always pin to a specific Git branch (`main`, `release-v1.2`) or a Git tag (`v1.0.0`). Avoid `HEAD` for production.
  - **`helm` or `kustomize`**: If using Helm or Kustomize, configure the respective fields.
- **`spec.destination`**:
  - **`server`**: The Kubernetes API server URL (e.g., `https://kubernetes.default.svc` for in-cluster, or external cluster URL).
  - **`namespace`**: The target namespace in the destination cluster where resources will be deployed.

```yaml
# Good: Well-structured ArgoCD Application
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app-prod
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/my-org/k8s-configs.git
    targetRevision: main # Or a specific tag like 'v1.0.0'
    path: environments/prod/my-app
  destination:
    server: https://kubernetes.default.svc
    namespace: my-app-prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

## 2. Sync Policies

- **`spec.syncPolicy.automated`**:
  - **`prune: true`**: Always enable pruning. This ensures that resources removed from Git are also removed from the cluster.
  - **`selfHeal: true`**: Enable self-healing. ArgoCD will automatically revert any manual changes made to resources in the cluster that deviate from Git.
  - **`allowEmpty: false`**: (Default) Prevents syncing an empty Git directory, which would delete all resources.
- **`spec.syncPolicy.syncOptions`**:
  - **`CreateNamespace=true`**: Useful for ensuring the target namespace exists.
  - **`ApplyOutOfSyncOnly=true`**: Only apply changes to resources that are out-of-sync.
  - **`ServerSideApply=true`**: Prefer server-side apply for better merge semantics.
- **Manual Sync**: For highly sensitive applications, `automated` sync can be disabled, requiring manual syncs via the UI or CLI.

## 3. Health Assessment Customization

- **Principle**: Customize health checks for resources that ArgoCD might not correctly assess by default (e.g., custom resources, jobs).
- **Method**: Use `resource.customizations` in `argocd-cm` ConfigMap or `resource.health.lua` in the Application manifest.
- **Benefit**: Provides accurate health status in the ArgoCD UI, improving operational visibility.

## 4. Prune and Self-Heal Policies

- **Prune**:
  - **`prune: true`**: (As above) Ensures resources deleted from Git are removed from the cluster.
  - **`syncPolicy.managedNamespaceMetadata.labels` / `annotations`**: Use this to prevent ArgoCD from pruning labels/annotations that are managed by other controllers (e.g., `cert-manager`).
- **Self-Heal**:
  - **`selfHeal: true`**: (As above) Reverts manual changes in the cluster.
  - **`syncPolicy.retry`**: Configure retry behavior for failed syncs.

## 5. Separation of Repositories

- **Principle**: Separate your application code repository from your Kubernetes configuration repository.
- **Application Code Repo**: Contains source code, Dockerfiles, CI pipelines.
- **Kubernetes Config Repo (GitOps Repo)**: Contains all Kubernetes manifests, Helm charts, Kustomize overlays, and ArgoCD `Application` definitions.
- **Benefit**:
  - **Security**: Prevents developers from directly modifying production Kubernetes manifests.
  - **Auditability**: All infrastructure changes go through Git, providing a clear audit trail.
  - **CI/CD**: Decouples application build/test from infrastructure deployment.

## 6. Resource Hooks

- **Principle**: Use ArgoCD hooks (`argocd.argoproj.io/hook`) for pre-sync, sync, and post-sync operations.
- **Use Cases**: Database migrations (`PreSync`), smoke tests (`PostSync`), data seeding.
- **Hook Deletion Policy**: Define `argocd.argoproj.io/hook-delete-policy` to control when hook resources are deleted (e.g., `HookSucceeded`, `BeforeHookCreation`).

```yaml
# Example: PreSync hook for database migration
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
spec:
  template:
    spec:
      containers:
      - name: migrate
        image: my-app-migration-image:latest
        command: ["./migrate.sh"]
      restartPolicy: Never
  backoffLimit: 0
```