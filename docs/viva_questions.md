# EventEase — College Project Viva Questions & Answers

Comprehensive preparation guide for the **BCA Cloud Computing and Virtualization** microproject examination.

---

### Q1. What is the difference between a Type-1 and Type-2 hypervisor?
**Answer:**
A **Type-1 (Bare-Metal)** hypervisor runs directly on the physical hardware without a host OS (e.g. VMware ESXi, KVM, Hyper-V), delivering maximum performance and low latency.
A **Type-2 (Hosted)** hypervisor runs as an application on top of an existing host operating system (e.g. Oracle VirtualBox, VMware Workstation), making it easier for desktop development.

---

### Q2. How does containerization differ from traditional hardware virtualization?
**Answer:**
Virtual machines virtualize the underlying hardware, requiring a complete guest operating system (several GBs) with its own kernel. Containers virtualize at the operating system level, sharing the host Linux kernel and running isolated processes via cgroups and namespaces, resulting in startup times in milliseconds and MB-sized images.

---

### Q3. Why do we run the container as a non-root user (`eventuser`) in the Dockerfile?
**Answer:**
To enforce the **Principle of Least Privilege**. If an attacker exploits a vulnerability inside a container running as root, they could potentially break out to the host system with root privileges. Running as an unprivileged user prevents unauthorized system modifications.

---

### Q4. What is the difference between Docker `CMD` and `ENTRYPOINT`?
**Answer:**
`ENTRYPOINT` specifies the permanent executable that should always run when the container starts. `CMD` provides default arguments to that executable, which can be easily overridden from the command line during `docker run`.

---

### Q5. What is the purpose of `.dockerignore`?
**Answer:**
It excludes unnecessary files and directories (such as `.venv`, `.git`, `.pytest_cache`, and temporary files) from the Docker build context. This speeds up build times, keeps image layers compact, and prevents leaking sensitive files like `.env` into the image.

---

### Q6. How does Docker implement container data persistence?
**Answer:**
By default, container filesystems are ephemeral (erased when the container is deleted). Persistence is achieved using **Docker Volumes** (managed by Docker on the host) or **Bind Mounts** (mounting a specific host directory into the container, as used for `./database` in `docker-compose.yml`).

---

### Q7. What are Kubernetes Pods?
**Answer:**
A Pod is the smallest and simplest deployable unit in Kubernetes. It encapsulates one or more containers that share the same network namespace (IP address and port space), IPC namespace, and shared storage volumes.

---

### Q8. What is the difference between a Kubernetes Deployment and a ReplicaSet?
**Answer:**
A **ReplicaSet** ensures that a specified number of Pod replicas are running at any given moment. A **Deployment** is a higher-level declarative object that manages ReplicaSets, enabling automated rolling updates, rollback history, and declarative scaling.

---

### Q9. What is the difference between `livenessProbe` and `readinessProbe`?
**Answer:**
- **`livenessProbe`**: Checks if the container process is alive. If it fails, Kubernetes kills and restarts the container.
- **`readinessProbe`**: Checks if the container is ready to accept incoming user network traffic. If it fails, Kubernetes removes the Pod's IP from the Service's endpoint list so traffic is not routed to it.

---

### Q10. What is the difference between `ClusterIP` and `NodePort` Services?
**Answer:**
- **`ClusterIP`**: Default service type. Exposes the service on an internal cluster IP accessible only from within the Kubernetes cluster.
- **`NodePort`**: Exposes the service on each Node's IP at a static port (between 30000–32767). Allows external web browsers to access the application directly from the host.

---

### Q11. What is the difference between a ConfigMap and a Secret in Kubernetes?
**Answer:**
A **ConfigMap** stores non-sensitive configuration data (environment names, hostnames, ports) in plain text. A **Secret** stores sensitive credentials (passwords, encryption keys, tokens) encoded in base64 to prevent accidental exposure.

---

### Q12. How does a Kubernetes Rolling Update ensure zero-downtime deployments?
**Answer:**
Through parameters `maxSurge` (how many extra pods can be created above target replicas) and `maxUnavailable` (how many pods can be unavailable). Kubernetes spins up new Pods with the new version, waits for them to pass readiness probes, and only then gracefully terminates the old Pods.

---

### Q13. Why can't multiple Kubernetes Pod replicas share a local SQLite database?
**Answer:**
SQLite is an embedded, file-based database that locks local files directly on disk. Because each Pod in a cluster has an isolated filesystem (or separate container volume), writes to Pod 1 are not synchronized to Pod 2. Multi-replica cloud systems require an external network-accessible database service such as Amazon RDS PostgreSQL or MySQL.

---

### Q14. What is Serverless Computing / Function as a Service (FaaS)?
**Answer:**
A cloud execution model where cloud providers automatically provision, manage, and scale server infrastructure. Developers upload small, stateless functions triggered by events (e.g. HTTP requests, file uploads). You only pay for the exact execution duration (down to milliseconds) with zero cost when idle.

---

### Q15. What is a "cold start" in AWS Lambda?
**Answer:**
A cold start occurs when a Lambda function is invoked for the first time or after a period of inactivity. AWS must provision an underlying microVM (Firecracker), download the code package, and initialize the runtime, causing an initial invocation latency of a few hundred milliseconds.

---

### Q16. How does Amazon API Gateway integrate with AWS Lambda?
**Answer:**
API Gateway acts as the HTTP entry point. In a **Lambda Proxy Integration**, API Gateway passes the entire HTTP request (headers, path, query parameters, body) as a JSON dictionary to the Lambda `event` parameter, and translates Lambda's JSON response dictionary directly into an HTTP response.

---

### Q17. How does EventEase prevent overbooking when multiple participants register at the exact same millisecond?
**Answer:**
EventEase wraps the registration process in an **exclusive database transaction** using `BEGIN IMMEDIATE`. This immediately acquires a write lock on the SQLite database, forcing concurrent requests to wait, checking capacity against current confirmed bookings, inserting the registration, and committing before the next request evaluates available seats.

---

### Q18. How does the application store user passwords securely?
**Answer:**
Passwords are never stored in plain text. They are hashed using **PBKDF2 (Password-Based Key Derivation Function 2)** with **SHA-256** and a cryptographic random salt via Werkzeug's `generate_password_hash()`. When logging in, `check_password_hash()` compares the hash securely against timing attacks.

---

### Q19. What is Minikube and why is it used in college practicals?
**Answer:**
Minikube is an open-source tool that provisions a lightweight, local single-node Kubernetes cluster inside a virtual machine or Docker container on Windows, macOS, or Linux. It allows testing production Kubernetes YAML manifests locally without requiring a costly multi-node cloud provider account.

---

### Q20. What is AWS SAM (Serverless Application Model)?
**Answer:**
AWS SAM is an open-source framework extending AWS CloudFormation. It provides shorthand syntax (`template.yaml`) to declare Lambda functions, API Gateway endpoints, and S3 buckets, and includes a CLI tool (`sam`) to build, test, and deploy serverless architectures locally and in the cloud.

---

### Q21. What is the role of the `/health` endpoint in containerized applications?
**Answer:**
The `/health` endpoint exposes real-time application and database status as JSON. Orchestrators like Kubernetes and Docker query this endpoint at regular intervals to verify that the web service is responding and database connectivity is healthy, automatically restarting unhealthy containers.

---

### Q22. What is the difference between Virtual Machine cloning and snapshots?
**Answer:**
A **snapshot** records the delta state of a VM's disk and memory at a specific timestamp, intended for short-term rollback. A **clone** creates a separate, permanent virtual machine with its own MAC address, IP, and UUID, either as a standalone full clone or a dependent linked clone.

---

### Q23. What is KVM and how does it interact with Linux?
**Answer:**
KVM (Kernel-based Virtual Machine) is a loadable kernel module (`kvm.ko`) that turns the Linux kernel into a Type-1 hypervisor. It utilizes hardware virtualization extensions (Intel VT-x or AMD-V) while delegating process scheduling and memory management to the host Linux kernel.

---

### Q24. How does Role-Based Access Control (RBAC) protect administrative routes in EventEase?
**Answer:**
Using custom Python decorators (`@login_required` and `@roles_required('admin', 'organizer')`). Before executing the route handler, the decorator checks the user's active session role stored in cryptographically signed cookies. If unauthorized, it aborts execution with an HTTP 403 Forbidden status.

---

### Q25. What happens when you run `kubectl rollout undo deployment/eventease-deployment`?
**Answer:**
Kubernetes checks the deployment's revision history in etcd, retrieves the pod template from the previous stable revision, and triggers a rolling update to revert all running replica pods back to that earlier version with zero downtime.
