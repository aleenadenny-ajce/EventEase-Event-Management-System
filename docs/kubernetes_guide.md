# EventEase — Module 4: Kubernetes & Minikube Practical Guide

Part of the **BCA Cloud Computing and Virtualization** microproject curriculum.

---

## 1. Why Container Orchestration?

While Docker allows running individual containers, enterprise cloud environments require an orchestrator to manage hundreds of containers across clusters of physical machines. **Kubernetes (K8s)** provides:

1. **Self-Healing**: Automatically restarts containers that fail health checks, replaces Pods when nodes die, and terminates unresponsive containers.
2. **Service Discovery & Load Balancing**: Exposes containers via stable DNS names and distributes network traffic evenly across healthy Pod replicas.
3. **Automated Rollouts & Rollbacks**: Incrementally updates application code while monitoring readiness probes, rolling back instantly if defects emerge.
4. **Horizontal Pod Autoscaling**: Dynamically increases or decreases the number of running container replicas based on CPU/memory utilization.
5. **Secret & Configuration Management**: Injects environment parameters and credentials without rebuilding container images.

---

## 2. Kubernetes Architectural Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Control Plane (Master Node)                                                 │
│  • kube-apiserver: Exposes the Kubernetes API (REST frontend)               │
│  • etcd: Consistent, highly-available key-value store for cluster state     │
│  • kube-scheduler: Assigns newly created Pods to available Worker Nodes     │
│  • kube-controller-manager: Runs core controllers (Node, ReplicaSet, etc.)  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ Worker Node (Minikube Node)                                                 │
│  • kubelet: Agent ensuring containers are running in Pods as requested      │
│  • kube-proxy: Maintains network rules across nodes for Service routing     │
│  • Container Runtime: Docker / containerd running the container images       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Dissecting the EventEase Kubernetes Manifests

All configuration files are organized in the `kubernetes/` folder:

| File | Resource Kind | Purpose |
| :--- | :--- | :--- |
| `namespace.yaml` | `Namespace` | Isolates all EventEase cluster resources under the dedicated `eventease` namespace. |
| `configmap.yaml` | `ConfigMap` | Injects non-sensitive environment variables (`APP_NAME`, `PORT`, `HOST`) into containers. |
| `secret.yaml.example` | `Secret` | Injects sensitive `SECRET_KEY` into containers using base64 encryption. |
| `deployment.yaml` | `Deployment` | Declares 2 replicas of `eventease:v1.0`, rolling update parameters, compute requests/limits, and `/health` probes. |
| `service.yaml` | `Service` | Defines both a `ClusterIP` (internal routing) and a `NodePort` (external browser port 30080). |

---

## 4. Complete Minikube Deployment Workflow

Follow these tested commands in **Windows PowerShell**:

### Step 1: Start Minikube Cluster
```powershell
minikube start --driver=docker
```
Verify the single-node Minikube cluster is healthy:
```powershell
kubectl get nodes
```
*Expected Output:*
```text
NAME       STATUS   ROLES           AGE   VERSION
minikube   Ready    control-plane   1m    v1.36.1
```

### Step 2: Build & Load Local Image into Minikube
Build the local image if not already built:
```powershell
docker build -t eventease:v1.0 .
```

Load the image directly into Minikube's Docker daemon so Kubernetes does not attempt to pull it from the internet:
```powershell
minikube image load eventease:v1.0
```

Verify image is present in Minikube:
```powershell
minikube image ls | Select-String "eventease"
```

### Step 3: Apply Namespace
```powershell
kubectl apply -f kubernetes/namespace.yaml
```

### Step 4: Apply ConfigMap
```powershell
kubectl apply -f kubernetes/configmap.yaml
```

### Step 5: Create Secret
```powershell
kubectl create secret generic eventease-secret `
  --from-literal=SECRET_KEY="eventease-demo-secret-key-32bytes-bca2026" `
  -n eventease
```

### Step 6: Deploy Application & Services
```powershell
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
```

---

## 5. Cluster Inspection & Verification Commands

### View All Resources in Namespace:
```powershell
kubectl get all -n eventease
```

### Check Pod Status and IP Allocations:
```powershell
kubectl get pods -n eventease -o wide
```
*Look for `STATUS: Running` and `READY: 1/1` on both Pods.*

### Inspect Deployment Events & Health Probes:
```powershell
kubectl describe deployment eventease-deployment -n eventease
```
*Notice the Liveness probe (`HTTP-GET /health`) and Readiness probe configuration in the output.*

### Inspect Live Container Logs across Replicas:
```powershell
kubectl logs -l app=eventease -n eventease --tail=30
```

### Open the Application in Your Web Browser:
```powershell
minikube service eventease-nodeport-service -n eventease
```
Minikube will create a direct tunnel and open your default browser pointing to the application.

---

## 6. Practical Lab Demonstrations for College Viva

### Demonstration A: Horizontal Pod Scaling
Scale the Deployment from 2 replicas to 4 replicas:
```powershell
kubectl scale deployment eventease-deployment --replicas=4 -n eventease
```
Observe new Pods spinning up:
```powershell
kubectl get pods -n eventease -w
```
Scale back down to 2 replicas:
```powershell
kubectl scale deployment eventease-deployment --replicas=2 -n eventease
```

### Demonstration B: Zero-Downtime Rolling Update & Rollback
Check rollout history:
```powershell
kubectl rollout history deployment/eventease-deployment -n eventease
```

Simulate an image update:
```powershell
kubectl set image deployment/eventease-deployment eventease=eventease:v2.0 -n eventease
```
Observe rollout status:
```powershell
kubectl rollout status deployment/eventease-deployment -n eventease
```

Rollback immediately to previous revision:
```powershell
kubectl rollout undo deployment/eventease-deployment -n eventease
```
Verify successful rollback:
```powershell
kubectl rollout status deployment/eventease-deployment -n eventease
```

---

## 7. Architectural Analysis: Multi-Pod SQLite Limitation

> **Crucial College Defense Concept**:
> SQLite is an **in-process embedded datastore**. It writes directly to a single disk file on the local filesystem.
> 
> In our Kubernetes deployment:
> - Each Pod mounts an ephemeral `emptyDir` volume.
> - While this allows each Pod to self-initialize and serve reads/healthchecks independently, transactions executed on Pod 1 are **not synchronized** to Pod 2.
> - In an enterprise multi-replica cloud environment, this is solved by using an **external managed database service** (such as **Amazon RDS PostgreSQL / AWS Aurora**), or an enterprise shared filesystem with distributed lock management (NFS RWX).
> 
> Articulating this limitation and the corresponding cloud solution demonstrates superior architectural comprehension during your viva!

---

## 8. Teardown & Resource Cleanup

To delete all Kubernetes objects created for EventEase:
```powershell
kubectl delete -f kubernetes/service.yaml
kubectl delete -f kubernetes/deployment.yaml
kubectl delete -f kubernetes/configmap.yaml
kubectl delete secret eventease-secret -n eventease
kubectl delete -f kubernetes/namespace.yaml
```
Stop the Minikube virtual cluster:
```powershell
minikube stop
```
