# Git GitOps Workflow Standards

Best practices for implementing a robust GitOps workflow with ArgoCD and Kubernetes.

**Category:** deployment | **Tags:** gitops, argocd, kubernetes, workflow, standards | **Version:** 1.0.0 | **Author:** prompt-unifier | **Language:** en | **AppliesTo:** argocd/**/*.yaml, argocd/**/*.yml, k8s/**/*.yaml, k8s/**/*.yml

# GitOps Workflow Standards

This document outlines the best practices for implementing a robust GitOps workflow, leveraging Git
as the single source of truth for declarative infrastructure and applications, with ArgoCD as the
automated deployment tool.

## 1. Git as the Single Source of Truth

- **Principle**: All desired states for infrastructure and applications must be declared in Git. No
  manual changes should be made directly to the Kubernetes cluster.
- **Benefit**: Provides a clear audit trail, version control, easy rollback, and a single pane of
  glass for understanding the system's state.
- **ArgoCD Enforcement**: ArgoCD continuously monitors the Git repository and the live cluster
  state, automatically synchronizing any deviations.

## 2. Repository Structure

- **Separation of Concerns**: Maintain separate Git repositories for:
  - **Application Code**: Contains the application source code, Dockerfiles, and CI pipelines.
  - **Kubernetes Configuration (GitOps Repo)**: Contains all Kubernetes manifests, Helm charts,
    Kustomize overlays, and ArgoCD `Application` definitions.
- **Monorepo vs. Polyrepo**:
  - **Polyrepo**: Separate GitOps repo per application or per team. Simpler to manage access and
    ownership.
  - **Monorepo**: A single GitOps repo for all applications and environments. Easier to manage
    cross-cutting concerns and dependencies. Choose based on organizational scale and complexity.

```
# Example GitOps Repository Structure
.
├── argocd/                               # ArgoCD Application definitions
│   ├── applications/
│   │   ├── my-app-dev.yaml
│   │   └── my-app-prod.yaml
│   └── projects/
│       ├── default.yaml
│       └── my-team.yaml
├── environments/                         # Kubernetes manifests organized by environment
│   ├── dev/
│   │   ├── my-app/
│   │   │   ├── deployment.yaml
│   │   │   └── service.yaml
│   │   └── infra/
│   │       └── prometheus.yaml
│   ├── prod/
│   │   ├── my-app/
│   │   │   ├── deployment.yaml
│   │   │   └── service.yaml
│   │   └── infra/
│   │       └── prometheus.yaml
├── helm-charts/                          # Custom Helm charts
│   └── my-app-chart/
│       ├── Chart.yaml
│       └── values.yaml
└── README.md
```

## 3. Branching Strategy for GitOps

- **Principle**: Use a branching strategy that supports safe, controlled deployments and rollbacks.
- **`main` Branch**: Represents the desired state of the production environment. All merges to
  `main` should trigger a production deployment.
- **`develop` / `staging` Branches**: Represent the desired state of development or staging
  environments. Merges to these branches trigger deployments to their respective environments.
- **Feature Branches**: All changes (application updates, infrastructure changes) are developed on
  feature branches, reviewed, and then merged into the appropriate environment branch.

## 4. Pull Request (PR) Workflow

- **Principle**: All changes to the GitOps repository must go through a Pull Request (PR) review
  process.
- **Automated Checks**: PRs must trigger CI pipelines that perform:
  - **Linting**: YAML linting, Helm linting, Kustomize validation.
  - **Validation**: `kubectl diff`, `kubeval`, `conftest` (for policy enforcement).
  - **Security Scanning**: `kube-linter`, `trivy` (for container images referenced).
- **Manual Review**: At least one other engineer must review and approve the PR. Reviewers should
  focus on:
  - **Correctness**: Does the manifest achieve the desired outcome?
  - **Security**: Are there any security misconfigurations?
  - **Impact**: What is the blast radius of the change?
  - **Adherence to Standards**: Does it follow Kubernetes and GitOps best practices?

## 5. Rollback Procedures

- **Principle**: Rollbacks should be as simple and fast as forward deployments.
- **Git-Driven Rollback**: To roll back to a previous state, revert the problematic commit(s) in the
  GitOps repository and push the change. ArgoCD will automatically detect the change and synchronize
  the cluster to the previous desired state.
- **ArgoCD Rollback**: ArgoCD also provides a UI/CLI mechanism to roll back to a previous sync
  operation, which effectively performs a Git revert and sync.

## 6. Multi-Cluster Management

- **Principle**: Manage multiple Kubernetes clusters (e.g., dev, prod, DR) from a single GitOps
  repository.
- **Method**:
  - **Separate Directories**: Use distinct directories within the GitOps repo for each cluster's
    configuration.
  - **ArgoCD `Application` per Cluster**: Define an ArgoCD `Application` for each cluster, pointing
    to its respective configuration path and destination cluster.
  - **ArgoCD `App of Apps` Pattern**: Use a parent ArgoCD `Application` to deploy other
    `Application` resources, simplifying the management of many applications across multiple
    clusters.

```yaml
# Example: App of Apps pattern
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: prod-cluster-apps
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/my-org/k8s-configs.git
    targetRevision: main
    path: argocd/applications/prod # This path contains other Application manifests
  destination:
    server: https://kubernetes.default.svc # Points to the production cluster
    namespace: argocd
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```