---
name: k8s-debug
description: Systematic Kubernetes debugging workflow for diagnosing pod failures,
  networking issues, and resource constraints in any cluster.
mode: code
license: MIT
metadata:
  tags:
  - kubernetes
  - debugging
  - devops
  version: '1.0'
---
# Kubernetes Debug Skill

## When to Use

Apply this skill when:
- A Kubernetes pod is in `CrashLoopBackOff`, `Pending`, `OOMKilled`, `Error`, or `Terminating` state
- The user asks "why is my pod not starting?" or "my deployment is down"
- A service is unreachable and network or DNS issues are suspected
- The user asks to diagnose or troubleshoot a Kubernetes workload

Do NOT apply when the user is writing new manifests or Helm charts (not a debugging scenario).

## Step 1 — Identify the Symptom

```bash
kubectl get pods -n <namespace>          # Check pod status
kubectl get events -n <namespace> --sort-by='.lastTimestamp' | tail -20
```

Common status patterns:

| Status | Likely cause |
|---|---|
| `Pending` | Insufficient resources, no matching node, PVC not bound |
| `CrashLoopBackOff` | App error, bad entrypoint, missing config |
| `ImagePullBackOff` | Wrong image name/tag, missing registry credentials |
| `OOMKilled` | Memory limit too low |
| `Error` | Container exited non-zero |
| `Terminating` (stuck) | Finalizer blocking deletion |

## Step 2 — Inspect the Pod

```bash
# Full pod description with events
kubectl describe pod <pod-name> -n <namespace>

# Container logs (current)
kubectl logs <pod-name> -n <namespace> -c <container>

# Previous container logs (after crash)
kubectl logs <pod-name> -n <namespace> -c <container> --previous
```

## Step 3 — Resource Constraints

```bash
kubectl top pods -n <namespace>
kubectl describe node <node-name> | grep -A5 "Allocated resources"
```

Check: requests vs limits. If `OOMKilled`, increase memory limit or optimize the app.

## Step 4 — ConfigMaps & Secrets

```bash
kubectl get configmap <name> -n <namespace> -o yaml
kubectl get secret <name> -n <namespace> -o jsonpath='{.data}' | base64 -d
```

Verify: all expected env vars are present and correctly mounted.

## Step 5 — Network Issues

```bash
# Test DNS resolution from inside a pod
kubectl run debug --image=busybox --rm -it -- nslookup <service-name>.<namespace>

# Test connectivity to a service
kubectl run debug --image=curlimages/curl --rm -it -- curl http://<service>.<namespace>:80

# Check service endpoints
kubectl get endpoints <service-name> -n <namespace>
```

Empty endpoints → no pods match the service selector. Check labels.

## Step 6 — Common Fixes

```bash
# Force restart a deployment
kubectl rollout restart deployment/<name> -n <namespace>

# Scale down then up
kubectl scale deployment/<name> --replicas=0 -n <namespace>
kubectl scale deployment/<name> --replicas=2 -n <namespace>

# Remove a stuck finalizer
kubectl patch pod <name> -n <namespace> -p '{"metadata":{"finalizers":[]}}' --type=merge
```

## Reporting

After diagnosis, summarise:

```
**Pod**: <name>
**Issue**: <root cause>
**Evidence**: <key log line or event>
**Fix applied**: <command or change>
**Next steps**: <monitoring or prevention>
```