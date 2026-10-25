# EventEase — Kubernetes & Minikube Deployment Guide

Part of the **BCA Cloud Computing and Virtualization** microproject curriculum (Module 4).

---

## 1. Architecture & Orchestration Overview

This directory contains production-style Kubernetes manifests configuring the **EventEase** microproject inside a single-node or multi-node Kubernetes cluster using **Minikube**.

```
                           [ Web Browser (Student / Evaluator) ]
                                            │
                                            ▼ (NodePort: 30080)
┌───────────────────────────────────────────┴───────────────────────────────────────────┐
│ Kubernetes Cluster (Minikube / eventease Namespace)                                   │
│                                                                                       │
│  ┌──────────────────────────────┐          ┌───────────────────────────────────────┐  │
│  │ Service: eventease-nodeport  │          │ Service: eventease-service            │  │
│  │ (Type: NodePort, Port: 30080)│          │ (Type: ClusterIP, Port: 5000)         │  │
│  └──────────────┬───────────────┘          └──────────────────┬────────────────────┘  │
│                 │                                             │                       │
│                 └─────────────────────┬───────────────────────┘                       │
│                                       ▼                                               │
│                 ┌───────────────────────────────────────────┐                         │
│                 │ Deployment: eventease-deployment          │                         │
│                 │ (Replicas: 2, RollingUpdate Strategy)     │                         │
│                 └─────────────────────┬─────────────────────┘                         │
│                                       │                                               │
│                 ┌─────────────────────┴─────────────────────┐                         │
│                 ▼                                           ▼                         │
│  ┌──────────────────────────────┐            ┌──────────────────────────────┐         │
│  │ Pod: eventease-deployment-1  │            │ Pod: eventease-deployment-2  │         │
│  │  - Container: eventease:v1.0 │            │  - Container: eventease:v1.0 │         │
│  │  - Health Probe: /health:5000│            │  - Health Probe: /health:5000│         │
│  │  - ConfigMap & Secret Mount  │            │  - ConfigMap & Secret Mount  │         │
│  │  - Storage: EmptyDir Volume  │            │  - Storage: EmptyDir Volume  │         │
│  └──────────────────────────────┘            └──────────────────────────────┘         │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Kubernetes Concepts Explained

| Concept | Explanation for College Viva |
| :--- | :--- |
| **Pod** | The smallest deployable computing unit in Kubernetes, wrapping one or more containers sharing storage and network IP. |
| **Deployment** | A declarative controller that manages Pod creation, replica counts, rolling updates, and self-healing. |
| **ReplicaSet** | Maintains a stable set of replica Pods running at any given time, managed automatically by the Deployment. |
| **Service** | An abstraction defining a logical set of Pods and a policy to access them (ClusterIP for internal, NodePort for external). |
| **ConfigMap** | Decouples non-sensitive configuration artifacts (e.g. environment names, ports) from container image code. |
| **Secret** | Stores confidential configuration values (passwords, auth tokens, secret keys) securely in base64 encoded format. |
| **Probes** | `livenessProbe` checks if the application is alive (restarts Pod if it fails); `readinessProbe` checks if the application is ready to accept user traffic. |
| **Rolling Update** | Incrementally replaces old Pod instances with new ones with zero downtime using `maxSurge` and `maxUnavailable`. |
| **Rollback** | Reverts a faulty deployment to a previous healthy revision instantly using `rollout undo`. |

---

## 3. Step-by-Step Minikube Deployment Workflow

### Step 1: Start Minikube
Launch the Minikube cluster using the Docker virtualization driver:
```powershell
minikube start --driver=docker
```

Verify that the Kubernetes node is ready:
```powershell
kubectl get nodes
```

### Step 2: Build & Load Docker Image into Minikube
Build the local EventEase image first:
```powershell
docker build -t eventease:v1.0 .
```

Load the local image directly into Minikube's Docker runtime (avoids needing a public Docker Hub pull):
```powershell
minikube image load eventease:v1.0
```

Verify the image exists inside Minikube:
```powershell
minikube image ls | Select-String "eventease"
```

### Step 3: Create Namespace
```powershell
kubectl apply -f kubernetes/namespace.yaml
```

### Step 4: Create ConfigMap
```powershell
kubectl apply -f kubernetes/configmap.yaml
```

### Step 5: Create Secret
Create the required `eventease-secret` with a strong key:
```powershell
kubectl create secret generic eventease-secret `
  --from-literal=SECRET_KEY="eventease-demo-secret-key-32bytes-bca2026" `
  -n eventease
```
*(Or if using a YAML file, copy `kubernetes/secret.yaml.example` to `kubernetes/secret.yaml` and run `kubectl apply -f kubernetes/secret.yaml`)*

### Step 6: Deploy Application & Services
```powershell
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
```

---

## 4. Verification and Cluster Inspection

### View All Cluster Resources:
```powershell
kubectl get pods,deployments,services -n eventease
```

### Inspect Pod Lifecycle and Readiness:
```powershell
kubectl get pods -n eventease -o wide
```

### Check Deployment Specification & Events:
```powershell
kubectl describe deployment eventease-deployment -n eventease
```

### View Live Application Logs:
```powershell
kubectl logs -l app=eventease -n eventease --tail=50
```

### Access EventEase in Your Web Browser:
```powershell
minikube service eventease-nodeport-service -n eventease
```
*Minikube will output the active local browser URL (e.g. `http://127.0.0.1:<random-port>` or `http://<minikube-ip>:30080`).*

---

## 5. Demonstrating Cloud Scaling (Replication)

Demonstrate horizontal scaling from 2 to 4 replicas for examiner viva:
```powershell
kubectl scale deployment eventease-deployment --replicas=4 -n eventease
```

Watch new Pods initialize and transition to `Running`:
```powershell
kubectl get pods -n eventease -w
```

Scale back down to 2 replicas:
```powershell
kubectl scale deployment eventease-deployment --replicas=2 -n eventease
```

---

## 6. Demonstrating Rolling Updates and Zero-Downtime Rollbacks

### Check Rollout Status:
```powershell
kubectl rollout status deployment/eventease-deployment -n eventease
```

### View Deployment Revision History:
```powershell
kubectl rollout history deployment/eventease-deployment -n eventease
```

### Trigger a Rolling Update:
Simulate updating the application image to `eventease:v2.0`:
```powershell
kubectl set image deployment/eventease-deployment eventease=eventease:v2.0 -n eventease
```

Observe how Kubernetes terminates old pods only after new pods pass readiness probes:
```powershell
kubectl rollout status deployment/eventease-deployment -n eventease
```

### Rollback to Previous Revision:
If an update has defects, roll back immediately:
```powershell
kubectl rollout undo deployment/eventease-deployment -n eventease
```

---

## 7. Important Architectural Note: Multi-Pod Storage & SQLite

> **College Examination Notice**:
> SQLite is an **embedded, in-process file database**. When running across multiple Pod replicas in Kubernetes:
> 1. In this educational demonstration, each Pod uses an `emptyDir` scratch mount where SQLite auto-initializes upon Pod start.
> 2. **Multi-Pod limitation**: Writes made to Pod 1 are stored in Pod 1's local file and are NOT automatically synchronized to Pod 2.
> 3. **Production Cloud Pattern**: In real-world enterprise deployments, multi-replica workloads connect to a managed external database cluster (such as **Amazon RDS PostgreSQL / Aurora MySQL**), or use an NFS-backed ReadWriteMany (RWX) Persistent Volume with distributed lock coordination.
> 
> Acknowledging this distinction demonstrates mastery of cloud architecture fundamentals during project presentation!

---

## 8. Teardown and Cleanup Commands

To remove all Kubernetes objects created for this project:
```powershell
kubectl delete -f kubernetes/service.yaml
kubectl delete -f kubernetes/deployment.yaml
kubectl delete -f kubernetes/configmap.yaml
kubectl delete secret eventease-secret -n eventease
kubectl delete -f kubernetes/namespace.yaml
```
