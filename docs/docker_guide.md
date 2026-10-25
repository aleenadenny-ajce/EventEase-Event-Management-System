# EventEase — Module 3: Docker & Docker Hub Practical Guide

Part of the **BCA Cloud Computing and Virtualization** microproject curriculum.

---

## 1. Containerization vs. Traditional Virtualization

| Dimension | Virtual Machines (VMs) | Docker Containers |
| :--- | :--- | :--- |
| **Abstraction Level** | Hardware abstraction (Hypervisor) | OS-level virtualization (Kernel sharing) |
| **Guest OS** | Includes full Guest OS (GBs in size) | Shares Host OS kernel (MBs in size) |
| **Startup Latency** | Minutes (boots full operating system) | Milliseconds to seconds (starts process) |
| **Resource Efficiency** | High memory and CPU overhead | Minimal overhead, near-native performance |
| **Portability** | Hypervisor-dependent disk images (.vmdk, .vdi) | Standard OCI image format runs anywhere |

---

## 2. Docker Architecture & Core Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Docker Client (CLI: docker build, docker run, docker push)                   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (REST API / Named Pipe)
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ Docker Daemon / Engine (dockerd)                                            │
│                                                                             │
│  ┌───────────────────────────────┐     ┌──────────────────────────────────┐ │
│  │ Local Images                  │     │ Running Containers               │ │
│  │  • python:3.12-slim           │     │  • eventease-app                 │ │
│  │  • eventease:v1.0             │     │    - Port: 5000 -> 5000          │ │
│  └───────────────────────────────┘     │    - Volumes: ./database -> /app │ │
│                                        │    - Healthcheck: /health (UP)   │ │
│                                        └──────────────────────────────────┘ │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ (HTTPS Push / Pull)
┌──────────────────────────────────────▼──────────────────────────────────────┐
│ Docker Registry (Docker Hub: hub.docker.com / Local Registry)                │
└─────────────────────────────────────────────────────────────────────────────┘
```

- **Docker Image**: A read-only, layered blueprint containing application code, runtimes, system tools, and libraries.
- **Docker Container**: A runnable, isolated instance of an image executed within a Linux cgroup and namespace sandbox.
- **Dockerfile**: A declarative text manifest defining the step-by-step assembly of an image.
- **Docker Compose**: A tool for defining and running multi-container Docker applications via declarative YAML.

---

## 3. Dissecting the EventEase Dockerfile

The `Dockerfile` in the root workspace adheres to enterprise production best practices:

```dockerfile
# 1. Base Image: Minimal official Python 3.12 slim image
FROM python:3.12-slim

# 2. Environment variables: Disables bytecode generation (.pyc) and enables unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    HOST=0.0.0.0 \
    FLASK_ENV=production

# 3. System packages: Install curl for healthcheck probing and clear apt cache to keep image small
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# 4. Security Principle of Least Privilege: Create dedicated non-root user
RUN useradd -m -u 1001 -s /bin/bash eventuser

# 5. Set working directory
WORKDIR /app

# 6. Dependency layer caching: Copy requirements first so code edits don't trigger reinstallation
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 7. Copy application codebase
COPY . .

# 8. Ownership and permissions: Ensure eventuser owns writable directories
RUN mkdir -p database static/uploads && \
    chown -R eventuser:eventuser /app

# 9. Switch from root to unprivileged user
USER eventuser

# 10. Expose application port
EXPOSE 5000

# 11. Built-in Container Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 12. Startup command
CMD ["python", "app.py"]
```

---

## 4. Step-by-Step Tested Docker Commands

Run these commands inside **Windows PowerShell** at the project root directory:

### Step 1: Verify Docker Installation & Daemon
```powershell
docker --version
docker info
```
*(If Docker Desktop is installed on Windows, make sure Docker Desktop is launched and running in the system tray before running commands).*

### Step 2: Build the Container Image
```powershell
docker build -t eventease:v1.0 .
```
Verify the image was created:
```powershell
docker images | Select-String "eventease"
```

### Step 3: Run the Container
Run the container in detached mode with port forwarding (`5000:5000`) and a custom name:
```powershell
docker run -d --name eventease-app -p 5000:5000 eventease:v1.0
```

### Step 4: Monitor Container Status & Health
Check active containers, port bindings, and health status:
```powershell
docker ps
```
*(Notice the `STATUS` column transitions from `(health: starting)` to `(healthy)` once the initial 10-second period passes and `/health` returns HTTP 200).*

### Step 5: Inspect Live Container Logs
```powershell
docker logs eventease-app
```
Follow logs in real-time:
```powershell
docker logs -f eventease-app
```

### Step 6: Detailed Container Inspection
Inspect internal IP, mounts, environment variables, and healthcheck results:
```powershell
docker inspect eventease-app
```

### Step 7: Test the Application in Browser or CLI
- **Web Browser**: Open `http://localhost:5000`
- **PowerShell Health Probe**:
  ```powershell
  Invoke-RestMethod -Uri http://localhost:5000/health
  ```

### Step 8: Stop and Clean Up Container
```powershell
docker stop eventease-app
docker rm eventease-app
```

---

## 5. Docker Compose Workflow

Docker Compose automates volume mounting to preserve SQLite data and uploaded posters on the host machine across container restarts.

### Launch with Docker Compose:
```powershell
docker compose up -d --build
```

### Check Running Compose Services:
```powershell
docker compose ps
```

### View Aggregated Logs:
```powershell
docker compose logs -f
```

### Stop Compose Stack:
```powershell
docker compose down
```

---

## 6. Docker Hub Distribution (Publishing & Pulling)

To demonstrate image distribution for college evaluation, follow this standard procedure using your Docker Hub account:

### 1. Authenticate with Docker Hub:
```powershell
docker login
```
*(Enter your Docker Hub username and personal access token / password).*

### 2. Tag the Local Image with Your Username:
```powershell
docker tag eventease:v1.0 <your-dockerhub-username>/eventease:v1.0
```

### 3. Push Image to Docker Hub:
```powershell
docker push <your-dockerhub-username>/eventease:v1.0
```

### 4. Pull and Run from Anywhere:
```powershell
docker pull <your-dockerhub-username>/eventease:v1.0
docker run -d --name eventease-cloud -p 5000:5000 <your-dockerhub-username>/eventease:v1.0
```
