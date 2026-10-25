# EventEase — College Project Evidence & Screenshots Checklist

Practical submission guide for capturing genuine screenshots, logs, and CLI output for the **BCA Cloud Computing and Virtualization** project report.

> **Instruction for Students**:
> Do not use fake or synthetic screenshots. Follow the exact commands and navigation steps below on your machine to capture authentic evidence showing your system running in real-time. Use the Windows Snipping Tool (`Win + Shift + S`) or Print Screen to save each screenshot to your lab report.

---

## Evidence Checklist Table

| # | Milestone Description | Environment | Command / URL to Capture | Target Observation in Screenshot |
| :-: | :--- | :--- | :--- | :--- |
| **01** | **Automated Test Results** | Windows PowerShell | `powershell -File .\scripts\test.ps1` | `30 passed` in green text with 0 failures across all unit test suites. |
| **02** | **Application Homepage** | Web Browser | `http://127.0.0.1:5000` | Modern hero section, active stats counters, and evaluation credentials table. |
| **03** | **Health Endpoint Response** | Web Browser / CLI | `http://127.0.0.1:5000/health` or `.\scripts\health_check.ps1` | JSON output displaying `status: "UP"`, `database: "connected"`, and UTC timestamp. |
| **04** | **Admin Dashboard** | Web Browser | Login as `admin@eventease.local` -> `/admin/dashboard` | Metric summary cards, Chart.js graphs, and recent registration activity feed. |
| **05** | **User Management Console** | Web Browser | `/admin/users` | List of all system users with role assignment dropdowns and delete buttons. |
| **06** | **Organizer Event Management** | Web Browser | Login as `organizer@eventease.local` -> `/events/manage` | Events table displaying booked seats vs. total capacity with action buttons. |
| **07** | **Event Creation Form** | Web Browser | `/events/create` | Form with title, category, date, start/end time, venue, capacity, and deadline fields. |
| **08** | **Event Detail & Registration** | Web Browser | `/events/1` (logged in as `participant@eventease.local`) | Event logistics cards, capacity progress bar, and "Confirm Registration" button. |
| **09** | **Digital Pass Confirmation** | Web Browser | `/registrations/success/<code\>` | Successful registration alert, unique registration pass badge, and event details. |
| **10** | **Participant Dashboard** | Web Browser | `/participant/dashboard` | List of registered events with confirmed status badges and cancel options. |
| **11** | **Attendee Roster & CSV Export**| Web Browser | `/events/1/participants` and downloaded CSV | Attendee table and downloaded `participants_event_1.csv` file opened in Excel/Notepad. |
| **12** | **Docker Image Build** | Windows PowerShell | `docker images \| Select-String "eventease"` | Image named `eventease:v1.0` with image ID and size in the output table. |
| **13** | **Running Docker Container** | Windows PowerShell | `docker ps` | Container `eventease-app` showing `STATUS: Up ... (healthy)` and port mapping `0.0.0.0:5000->5000/tcp`. |
| **14** | **Docker Inspect Health Status** | Windows PowerShell | `docker inspect --format='{{json .State.Health}}' eventease-app` | JSON snippet showing `Status: "healthy"` and HTTP 200 health log. |
| **15** | **Docker Compose Stack** | Windows PowerShell | `docker compose ps` | Service `eventease-app` running in state `Up (healthy)`. |
| **16** | **Docker Hub Image (If Pushed)** | Docker Hub Website | `https://hub.docker.com/r/<your-username>/eventease` | Webpage showing published repository with tag `v1.0`. *(Optional)* |
| **17** | **Minikube Node Status** | Windows PowerShell | `kubectl get nodes` | Node `minikube` showing `STATUS: Ready`. |
| **18** | **Kubernetes Pods & Namespace** | Windows PowerShell | `kubectl get pods -n eventease -o wide` | 2 replica pods showing `STATUS: Running` and `READY: 1/1`. |
| **19** | **Kubernetes Deployments** | Windows PowerShell | `kubectl get deployments -n eventease` | Deployment `eventease-deployment` showing `UP-TO-DATE: 2`, `AVAILABLE: 2`. |
| **20** | **Kubernetes Services** | Windows PowerShell | `kubectl get services -n eventease` | Both `eventease-service` (ClusterIP) and `eventease-nodeport-service` (NodePort 30080). |
| **21** | **Minikube Browser Access** | Web Browser | `minikube service eventease-nodeport-service -n eventease` | Browser window showing EventEase homepage accessed via the Minikube IP or tunnel. |
| **22** | **Horizontal Pod Scaling** | Windows PowerShell | `kubectl scale deployment eventease-deployment --replicas=4 -n eventease; kubectl get pods -n eventease` | Output showing 4 active Pod replicas in the `eventease` namespace. |
| **23** | **Rolling Update & Rollback** | Windows PowerShell | `kubectl rollout history deployment/eventease-deployment -n eventease` | Revisions 1 and 2 listed in the deployment rollout history table. |
| **24** | **Lambda Local Execution** | Windows PowerShell | `python serverless/lambda_function.py` | JSON output displaying `statusCode: 200`, `success: true`, and cryptographic hash signature. |
| **25** | **Serverless Test Suite** | Windows PowerShell | `pytest tests/test_serverless.py -v` | All 7 serverless tests passing green with 0 errors. |

---

## Step-by-Step Procedure for Capturing Evidence

### Step 1: Capture Automated Test Results
1. Open PowerShell in the project workspace:
   ```powershell
   powershell -File .\scripts\test.ps1
   ```
2. Capture the console showing **30 passed** test assertions.

### Step 2: Start Local Server and Capture Web Pages
1. Start the server:
   ```powershell
   powershell -File .\scripts\run.ps1
   ```
2. Open `http://127.0.0.1:5000` in Google Chrome / Edge.
3. Capture the Homepage.
4. Log in as `admin@eventease.local` (Password: `Admin@Password123`) and capture the Admin Dashboard and User Management table.
5. Log out and log in as `participant@eventease.local` (Password: `User@Password123`).
6. Register for an upcoming event and capture the Confirmation Pass screen.

### Step 3: Capture Docker Containers (When Docker Desktop is Running)
1. Build and run the image:
   ```powershell
   docker build -t eventease:v1.0 .
   docker run -d --name eventease-app -p 5000:5000 eventease:v1.0
   ```
2. Wait 15 seconds for the health probe to trigger, then capture:
   ```powershell
   docker ps
   docker logs eventease-app
   ```
3. Stop and clean up:
   ```powershell
   docker stop eventease-app
   docker rm eventease-app
   ```

### Step 4: Capture Kubernetes Orchestration (When Minikube is Running)
1. Follow the commands in `kubernetes/README.md`:
   ```powershell
   minikube start --driver=docker
   kubectl get nodes
   minikube image load eventease:v1.0
   kubectl apply -f kubernetes/namespace.yaml
   kubectl apply -f kubernetes/configmap.yaml
   kubectl create secret generic eventease-secret --from-literal=SECRET_KEY="eventease-demo-secret-key-32bytes-bca2026" -n eventease
   kubectl apply -f kubernetes/deployment.yaml
   kubectl apply -f kubernetes/service.yaml
   ```
2. Capture terminal output for:
   ```powershell
   kubectl get pods,deployments,services -n eventease
   ```
3. Scale the deployment and capture the 4 pods:
   ```powershell
   kubectl scale deployment eventease-deployment --replicas=4 -n eventease
   kubectl get pods -n eventease
   ```

### Step 5: Capture Serverless Microservice Execution
1. Run the Lambda handler locally:
   ```powershell
   python serverless/lambda_function.py
   ```
2. Capture the structured JSON output with the cryptographic digital pass signature.
