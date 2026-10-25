# EventEase — Event Management System
### BCA Cloud Computing & Virtualization Practical Microproject

[![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-green.svg)](https://palletsprojects.com/p/flask/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Minikube-326CE5.svg)](https://kubernetes.io/)
[![Serverless](https://img.shields.io/badge/AWS-Lambda%20%2B%20SAM-orange.svg)](https://aws.amazon.com/lambda/)
[![Tests](https://img.shields.io/badge/pytest-30%20Passed-brightgreen.svg)](https://docs.pytest.org/)

---

## 1. Project Overview

**EventEase** is a complete, modular, and cloud-ready **Event Management System** built for the **BCA Cloud Computing and Virtualization** curriculum. It enables academic institutions to publish workshops, technical summits, hackathons, and cultural fests while allowing students to discover events, register with concurrency safeguards, and generate digital event passes.

Beyond the full-stack web application, the project serves as a comprehensive practical demonstration of:
1. **Virtualization Fundamentals & VM Automation** (Oracle VirtualBox, Linux KVM, `VBoxManage`, `virsh`)
2. **Containerization with Docker & Docker Compose** (Non-root user security, persistent volume mounts, healthcheck probes)
3. **Container Orchestration with Kubernetes & Minikube** (Replicas, Pod scaling, rolling updates, rollbacks, ConfigMaps, Secrets, ClusterIP & NodePort Services)
4. **Serverless Cloud Computing** (AWS Lambda, Amazon API Gateway, S3 asset storage, SHA-256 digital pass signing, AWS SAM)

---

## 2. Evaluation Demo Accounts

Pre-seeded test accounts for college examiners and evaluators (local development only):

| Role | Email Address | Password | Permissions & Capabilities |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin@eventease.local` | `Admin@Password123` | Full control: Platform metrics, Chart.js analytics, global event management, user role updates, user deletion. |
| **Faculty Organizer** | `organizer@eventease.local` | `Organizer@Password123` | Create events, edit assigned events, view attendee rosters, export attendee details as CSV. |
| **Student Participant** | `participant@eventease.local` | `User@Password123` | Discover events, search & filter, register for passes, view registered events, cancel registrations. |

---

## 3. Quick Start on Windows PowerShell

Run these simple commands inside **Windows PowerShell** to set up and run the project:

### Step 1: Automated Environment Setup
Installs dependencies in `.venv` and seeds the SQLite database:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

### Step 2: Run Automated Tests (30 Tests)
Verifies authentication, events, concurrency, healthcheck, and serverless handlers:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\test.ps1
```
*Result: 30 passed in ~14 seconds with 0 warnings.*

### Step 3: Start the Web Application
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run.ps1
```
Open your browser at: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

### Step 4: Test Service Health Endpoint
In a separate PowerShell window:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\health_check.ps1
```
Or open **[http://127.0.0.1:5000/health](http://127.0.0.1:5000/health)** in your browser.

---

## 4. Complete Project Directory Structure

```text
EventEase/
├── app.py                     # Main Flask backend (routes, RBAC decorators, /health, concurrency locks)
├── config.py                  # Environment-driven configuration classes (Config, TestConfig)
├── requirements.txt           # Python package dependencies
├── Dockerfile                 # Production Dockerfile (python:3.12-slim, non-root user, healthcheck)
├── docker-compose.yml         # Compose specification with SQLite & uploads volume persistence
├── .dockerignore              # Excludes virtual environments, caches, and test artifacts
├── .gitignore                 # Excludes local databases, private keys, virtual environment
├── .env.example               # Template for production environment variables
├── README.md                  # Master college project submission documentation
├── pytest.ini                 # Pytest runner configuration
├── database/
│   ├── init_db.py             # Database initialization script (schema & demo seed caller)
│   ├── seed_data.py           # Realistic college demo events, users, and categories
│   ├── schema.sql             # Relational DDL schema with foreign keys and unique constraints
│   └── eventease.db           # SQLite local database file (auto-generated)
├── templates/
│   ├── base.html              # Base layout with navbar, alerts, footer, and session controls
│   ├── index.html             # Homepage with stats counters, featured events, demo credentials
│   ├── login.html             # Role-aware login form with credential autofill buttons
│   ├── register.html          # Participant account registration form
│   ├── events.html            # Event catalog with keyword search, category & status filters
│   ├── event_detail.html      # Logistics, live seat progress bar, booking button
│   ├── registration_success.html # Digital ticket confirmation pass with unique pass code
│   ├── admin_dashboard.html   # Admin metrics cards, Chart.js graphs, recent events feed
│   ├── organizer_dashboard.html # Organizer event management table with quick actions
│   ├── participant_dashboard.html # Participant personal registered events & status badges
│   ├── manage_events.html     # Comprehensive search & filter event management directory
│   ├── manage_users.html      # User administration console with role change & delete buttons
│   ├── registrations.html     # Participant attendee roster view
│   ├── 404.html               # Custom 404 Not Found error page
│   └── 500.html               # Custom 500 Internal Server Error page
├── static/
│   ├── css/style.css          # Modern custom CSS styles with Inter typography & gradients
│   ├── js/main.js             # Form validation, confirm dialogs, and Chart.js integration
│   ├── images/                # Vector SVG banners and logo assets
│   └── uploads/               # User-uploaded poster images
├── tests/
│   ├── conftest.py            # Pytest fixtures with isolated temporary SQLite test database
│   ├── test_auth.py           # Registration, login, password hashing, and RBAC tests
│   ├── test_events.py         # Event CRUD, searching, filtering, and management tests
│   ├── test_registrations.py  # Concurrency, full capacity, deadline, and CSV export tests
│   ├── test_health.py         # /health endpoint liveness and database connectivity tests
│   └── test_serverless.py     # AWS Lambda unit tests (direct & API Gateway proxy payloads)
├── scripts/
│   ├── setup.ps1              # Automated setup and database seeder for Windows PowerShell
│   ├── run.ps1                # Web application launcher
│   ├── test.ps1               # Automated test runner
│   └── health_check.ps1       # CLI diagnostic probe querying /health
├── docs/
│   ├── project_report.md      # Comprehensive academic microproject report
│   ├── architecture.md        # System architecture, Mermaid ER diagram, sequence flow
│   ├── docker_guide.md        # Module 3 Docker & Docker Hub practical guide
│   ├── kubernetes_guide.md    # Module 4 Kubernetes & Minikube practical guide
│   ├── serverless_guide.md    # Module 5 AWS Serverless (Lambda, API GW, S3) guide
│   ├── virtualization_guide.md# Modules 1 & 2 Virtualization & VM Automation guide
│   ├── viva_questions.md      # 25 college viva questions with short, crisp answers
│   └── screenshots_checklist.md # Practical checklist for capturing submission screenshots
├── kubernetes/
│   ├── namespace.yaml         # Isolates objects in 'eventease' namespace
│   ├── configmap.yaml         # Non-sensitive configuration (APP_NAME, PORT, HOST)
│   ├── secret.yaml.example    # Base64 SECRET_KEY template and creation commands
│   ├── deployment.yaml        # 2 replicas, rolling updates, resource limits, health probes
│   ├── service.yaml           # ClusterIP internal service and NodePort external service
│   └── README.md              # Minikube image loading, scaling, and rollback commands
└── serverless/
    ├── lambda_function.py     # Independent FaaS handler for ticket verification & notifications
    ├── requirements.txt       # Serverless function dependencies
    ├── template.yaml          # AWS SAM infrastructure-as-code template
    └── README.md              # Serverless execution and AWS deployment guide
```

---

## 5. Module 3: Docker Containerization

### Build Image:
```powershell
docker build -t eventease:v1.0 .
```

### Run Standalone Container:
```powershell
docker run -d --name eventease-app -p 5000:5000 eventease:v1.0
```

### Inspect Container Health:
```powershell
docker ps
docker logs eventease-app
```
*(The container runs as non-root user `eventuser` and automatically transitions to `(healthy)` via its built-in `/health` probe).*

### Run with Docker Compose (With Volume Persistence):
```powershell
docker compose up -d --build
docker compose ps
docker compose down
```

---

## 6. Module 4: Kubernetes & Minikube Orchestration

### Start Minikube & Load Image:
```powershell
minikube start --driver=docker
kubectl get nodes
minikube image load eventease:v1.0
```

### Deploy Manifests:
```powershell
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl create secret generic eventease-secret --from-literal=SECRET_KEY="eventease-demo-secret-key-32bytes-bca2026" -n eventease
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
```

### Verify Cluster Status:
```powershell
kubectl get pods,deployments,services -n eventease
```

### Open Application in Browser:
```powershell
minikube service eventease-nodeport-service -n eventease
```

### Demonstrate Horizontal Scaling:
```powershell
kubectl scale deployment eventease-deployment --replicas=4 -n eventease
kubectl get pods -n eventease
```

### Demonstrate Rolling Update & Rollback:
```powershell
kubectl rollout history deployment/eventease-deployment -n eventease
kubectl rollout undo deployment/eventease-deployment -n eventease
```

---

## 7. Module 5: AWS Serverless Computing

The independent serverless microservice in `serverless/lambda_function.py` handles high-frequency asynchronous digital pass signing and notification dispatch simulation.

### Run Locally (No AWS Account Required):
```powershell
python serverless/lambda_function.py
```

### Run Serverless Unit Tests:
```powershell
pytest tests/test_serverless.py -v
```

### Deploy to Cloud via AWS SAM (Optional):
```powershell
sam build -t serverless/template.yaml
sam deploy --guided
sam delete --stack-name eventease-serverless-stack
```

---

## 8. College Project Documentation Links

- [Academic Project Report](file:///c:/Users/aleen/OneDrive/Desktop/event%20mangement%20system/docs/project_report.md)
- [System Architecture & ER Diagram](file:///c:/Users/aleen/OneDrive/Desktop/event%20mangement%20system/docs/architecture.md)
- [Docker Practical Guide](file:///c:/Users/aleen/OneDrive/Desktop/event%20mangement%20system/docs/docker_guide.md)
- [Kubernetes & Minikube Guide](file:///c:/Users/aleen/OneDrive/Desktop/event%20mangement%20system/docs/kubernetes_guide.md)
- [Virtualization & VM Automation Guide](file:///c:/Users/aleen/OneDrive/Desktop/event%20mangement%20system/docs/virtualization_guide.md)
- [AWS Serverless Guide](file:///c:/Users/aleen/OneDrive/Desktop/event%20mangement%20system/docs/serverless_guide.md)
- [25 Viva Questions & Answers](file:///c:/Users/aleen/OneDrive/Desktop/event%20mangement%20system/docs/viva_questions.md)
- [Evidence & Screenshots Checklist](file:///c:/Users/aleen/OneDrive/Desktop/event%20mangement%20system/docs/screenshots_checklist.md)

---

## 9. License & Academic Attribution
Developed as an educational microproject for the **BCA Cloud Computing & Virtualization** practical laboratory. All demo credentials and local database keys are intended strictly for local development and academic evaluation.
