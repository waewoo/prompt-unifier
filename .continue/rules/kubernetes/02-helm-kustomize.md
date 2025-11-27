---
name: 'Kubernetes Configuration Management: Helm & Kustomize'
description: Best practices for using Helm and Kustomize to manage Kubernetes manifests,
  and guidelines for choosing between them.
globs:
- helm/**/*.yaml
- k8s/**/*.yaml
alwaysApply: false
category: deployment
version: 1.0.0
tags:
- kubernetes
- helm
- kustomize
- standards
- configuration-management
author: prompt-unifier
language: yaml
---
# Kubernetes Configuration Management: Helm & Kustomize

This document provides best practices for using Helm and Kustomize, two popular tools for managing
Kubernetes manifests, and offers guidance on when to choose one over the other.

## 1. Helm Standards

Helm is a package manager for Kubernetes. It defines discrete applications or services with a Chart.

### Chart Structure

- **Standard Layout**: Adhere to the standard Helm Chart directory structure.
- **`Chart.yaml`**: Define `name`, `version`, `apiVersion`, `appVersion`, `description`, and
  optionally `dependencies`.
- **`values.yaml`**: Contains the default configuration values for the chart.
  - **Structure**: Organize values hierarchically.
  - **Comments**: Document each configurable value.
  - **Templates**: Reference values in `templates/` using `{{ .Values.myKey }}`.
- **`templates/`**: Contains the Kubernetes manifest templates (`.yaml.tpl` or `.yaml`).
  - **Generality**: Keep templates generic. All environment-specific configurations should come from
    `values.yaml` or overrides.
  - **Named Templates**: Use `_helpers.tpl` for reusable Helm partials/named templates.
  - **`NOTES.txt`**: Provide clear instructions for post-installation steps.

### Values and Overrides

- **Customization**: Use `values.yaml` to define defaults and provide custom `values.yaml` files or
  `--set` flags for environment-specific overrides.
- **Environment-Specific Overrides**:
  - Store environment-specific `values.yaml` files alongside your `Application` definitions in your
    GitOps repository (e.g., `argocd/envs/prod/values.yaml`).
  - Use `values.render.helm.values` in ArgoCD `Application` to specify multiple values files.

### Dependencies

- **Subcharts**: Use subcharts (`dependencies` field in `Chart.yaml`) for reusable components that
  are deployed as part of the main application (e.g., a common database chart).
- **External Dependencies**: For truly independent services, deploy them as separate Helm releases,
  possibly managed by separate ArgoCD Applications.

## 2. Kustomize Standards

Kustomize allows you to customize raw, template-free YAML files for multiple purposes, leaving the
original YAML untouched.

### Base and Overlays

- **`base`**: Contains the original, un-modified Kubernetes manifests that are common across all
  environments (e.g., `deployment.yaml`, `service.yaml`).
- **`overlays`**: Contains environment-specific modifications to the `base` manifests.
  - **Structure**: Create a directory for each environment (e.g., `overlays/dev`, `overlays/prod`).
  - **`kustomization.yaml`**: Each `base` and `overlay` directory must contain a
    `kustomization.yaml` file.
  - **Patches**: Use `patchesStrategicMerge` or `patchesJson6902` to apply specific changes without
    modifying the base files.
  - **Generators**: Use `ConfigMapGenerator` and `SecretGenerator` for environment-specific
    configuration.

```yaml
# Example: Overlay structure
.
├── k8s/
│   ├── base/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── kustomization.yaml
│   └── overlays/
│       ├── dev/
│       │   ├── kustomization.yaml  # Patches to dev deployment
│       │   └── dev-config.yaml     # ConfigMap for dev
│       └── prod/
│           ├── kustomization.yaml  # Patches to prod deployment
│           └── prod-config.yaml    # ConfigMap for prod
```

### Patches

- **`patchesStrategicMerge`**: Used for merging entire YAML documents. Good for modifying existing
  fields or adding new ones.
- **`patchesJson6902`**: Used for precise JSON-style patching with operations like `add`, `remove`,
  `replace`. More verbose but very powerful.

```yaml
# Example: patchesStrategicMerge in overlays/prod/kustomization.yaml
resources:
  - ../../base

patchesStrategicMerge:
  - production-deployment.yaml # This file contains partial Deployment YAML

# production-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3 # Override base replica count
  template:
    spec:
      containers:
      - name: my-app
        resources:
          limits:
            cpu: 1000m
            memory: 1Gi # Override base resource limits
```

### Generators

- **`ConfigMapGenerator` and `SecretGenerator`**: Use these to create ConfigMaps and Secrets from
  files or literal values. Kustomize automatically adds a hash to the name, ensuring immutability
  and triggering rolling updates.

## 3. Choosing Between Helm and Kustomize

| Feature             | Helm                                | Kustomize                                     | Recommendation                                                                                       |
| ------------------- | ----------------------------------- | --------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **Primary Use**     | Package manager for applications    | Customization tool for YAML manifests         |                                                                                                      |
| **Abstraction**     | High-level abstraction (charts)     | Low-level YAML manipulation                   | Choose Helm for reusable, sharable applications; Kustomize for fine-grained environmental overrides. |
| **Templating**      | Full Jinja2 templating              | No templating (patches raw YAML)              | Helm if complex logic or conditionals are needed in manifest generation.                             |
| **Install/Upgrade** | Manages releases, rollback, history | Direct `kubectl apply -k`                     | Helm for lifecycle management of entire applications.                                                |
| **Multi-tenancy**   | Good for multiple installations     | Good for environmental variations             | Helm for deploying N instances of the *same* app; Kustomize for N environments of the *same* config. |
| **Learning Curve**  | Steeper (chart design, functions)   | Easier (direct YAML patches)                  | Kustomize for simpler projects or quick customizations.                                              |
| **Dependencies**    | Supports subcharts                  | Managed implicitly via `base` and `resources` | Helm for application-centric dependencies.                                                           |

- **Hybrid Approach**: It's common to use Helm to manage third-party applications (e.g., Prometheus,
  Cert-Manager) and Kustomize to manage your own application's manifests and environmental
  overrides. ArgoCD can deploy both.