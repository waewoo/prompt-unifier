---
name: Kubernetes Manifest Standards
description: Best practices for writing robust, secure, and maintainable Kubernetes
  YAML manifests.
globs:
- k8s/**/*.yaml
- k8s/**/*.yml
- helm/**/*.yaml
alwaysApply: false
category: standards
version: 1.0.0
tags:
- kubernetes
- manifests
- yaml
- standards
- security
author: prompt-unifier
language: yaml
---
# Kubernetes Manifest Standards

This document outlines best practices for writing Kubernetes YAML manifests, ensuring applications are deployed securely, efficiently, and reliably.

## 1. Structure and Readability

- **YAML Format**: Use consistent YAML formatting (e.g., 2 spaces indentation).
- **Resource per File**: Ideally, define one Kubernetes resource per YAML file for clarity and easier management with Git.
- **Order of Fields**: Follow a consistent order of fields within a resource (e.g., `apiVersion`, `kind`, `metadata`, `spec`).
- **Comments**: Use comments sparingly to explain complex logic or non-obvious configurations.

## 2. Resource Limits and Requests

- **Principle**: Always define `resources.limits` and `resources.requests` for all containers.
- **Reason**:
  - **Requests**: Guarantee a minimum amount of CPU/memory for the container, ensuring it can run.
  - **Limits**: Prevent a container from consuming excessive resources, protecting other pods on the node and the node itself.
- **Benefit**: Improves cluster stability, enables efficient scheduling, and prevents resource starvation.

```yaml
# Good: Defined resource requests and limits
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

## 3. Health Checks (Liveness and Readiness Probes)

- **Principle**: Always define `livenessProbe` and `readinessProbe` for all application containers.
- **`livenessProbe`**: Kubernetes uses liveness probes to know when to restart a container. If the probe fails, the container is restarted.
- **`readinessProbe`**: Kubernetes uses readiness probes to know when a container is ready to start accepting traffic. If the probe fails, the pod is removed from the Service's endpoints.
- **Types**: Prefer `HTTPGet` or `TCPSocket` probes over `Exec` probes for simplicity and efficiency.

```yaml
# Good: Defined liveness and readiness probes
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 15
  periodSeconds: 20
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
  failureThreshold: 3
```

## 4. Labels and Annotations

- **Principle**: Use labels for identifying and organizing Kubernetes objects. Use annotations for non-identifying metadata.
- **Labels**:
  - **Purpose**: Used for selecting objects (e.g., by Services, Deployments, ArgoCD).
  - **Standard Labels**: `app.kubernetes.io/name`, `app.kubernetes.io/instance`, `app.kubernetes.io/version`, `app.kubernetes.io/component`, `app.kubernetes.io/part-of`, `app.kubernetes.io/managed-by`.
  - **Custom Labels**: Define custom labels for team, environment, project, etc.
- **Annotations**:
  - **Purpose**: Store arbitrary non-identifying metadata (e.g., build information, contact info, ArgoCD sync options).

```yaml
# Good: Consistent labels and annotations
metadata:
  name: my-app-deployment
  labels:
    app.kubernetes.io/name: my-app
    app.kubernetes.io/instance: my-app-prod
    environment: production
    team: backend
  annotations:
    build.ci.com/id: "12345"
    argocd.argoproj.io/sync-wave: "2"
```

## 5. Namespaces and RBAC

- **Namespaces**:
  - **Principle**: Organize resources into logical namespaces (e.g., `dev`, `staging`, `prod`, `kube-system`).
  - **Benefit**: Provides scope for resource names, access control, and resource quotas.
- **RBAC (Role-Based Access Control)**:
  - **Principle**: Implement RBAC to grant least privilege access to Kubernetes resources.
  - **Components**: Use `Role` (namespace-scoped) or `ClusterRole` (cluster-scoped) to define permissions, and `RoleBinding` or `ClusterRoleBinding` to grant those permissions to users or Service Accounts.
  - **Service Accounts**: Applications running in pods should use dedicated Service Accounts with minimal necessary permissions.

```yaml
# Good: Dedicated Service Account with minimal permissions
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app-sa
  namespace: my-app-prod

---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: my-app-pod-reader
  namespace: my-app-prod
rules:
- apiGroups: [""] # "" indicates the core API group
  resources: ["pods", "pods/log"]
  verbs: ["get", "watch", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: my-app-pod-reader-binding
  namespace: my-app-prod
subjects:
- kind: ServiceAccount
  name: my-app-sa
  namespace: my-app-prod
roleRef:
  kind: Role
  name: my-app-pod-reader
  apiGroup: rbac.authorization.k8s.io
```

## 6. Security Context

- **Principle**: Define a `securityContext` for pods and containers to enforce security policies.
- **`runAsNonRoot`**: Always run containers as a non-root user.
- **`readOnlyRootFilesystem`**: Set the root filesystem to read-only.
- **`allowPrivilegeEscalation: false`**: Prevent processes in the container from gaining more privileges than their parent process.
- **`capabilities`**: Drop unnecessary Linux capabilities.

```yaml
# Good: Secure securityContext
securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
    add:
      - NET_BIND_SERVICE # Example: if app needs to bind to ports < 1024
```

## 7. Configuration Management

- **`ConfigMap` and `Secret`**: Use `ConfigMap` for non-sensitive configuration data and `Secret` for sensitive data.
- **Injection**: Inject `ConfigMap` and `Secret` data into pods as environment variables or mounted files.
- **Avoid Hardcoding**: Never hardcode configuration or secrets directly in Deployment manifests.