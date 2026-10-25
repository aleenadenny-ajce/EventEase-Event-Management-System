# EventEase — Event Management System
## College Microproject Report
### Course: Bachelor of Computer Applications (BCA)
### Subject: Cloud Computing & Virtualization Practical Lab

---

## 1. Abstract

In modern academic and organizational environments, managing campus events, technical symposiums, hackathons, and cultural fests is frequently plagued by fragmented registration processes, capacity overselling, manual paper check-ins, and lack of real-time attendance tracking. **EventEase** is a comprehensive, cloud-native Event Management System developed to address these operational challenges.

The project demonstrates a production-grade multi-tier web application built using Python Flask, Bootstrap 5, SQLite, Docker, Kubernetes (Minikube), and AWS Serverless computing (AWS Lambda & API Gateway). It models the full software development and cloud operations lifecycle: from secure role-based authentication and concurrency-safe seat booking to containerization, orchestration with self-healing health probes, zero-downtime rolling updates, and event-driven serverless notification services.

---

## 2. Problem Statement

Traditional university event management relies on isolated spreadsheets, paper sign-up sheets, and disparate social media notices, resulting in:
1. **Concurrency and Overbooking**: Multiple participants attempting to claim the final available seats simultaneously cause oversubscription when databases lack transaction locking.
2. **Lack of Role-Based Governance**: Administrators, faculty coordinators, and student attendees require distinct operational boundaries, access levels, and auditing capabilities.
3. **Deployment Friction**: Applications hardcoded for a single operating system fail to achieve reproducible deployment across development, testing, and production environments.
4. **Scalability Constraints**: Monolithic applications struggle to adapt to massive registration spikes preceding major deadlines without dynamic resource allocation.

---

## 3. Project Objectives & Scope

### 3.1 Objectives:
- Develop an intuitive, mobile-responsive web portal for discovering, creating, and registering for events.
- Implement strict Role-Based Access Control (RBAC) supporting **Admin**, **Organizer**, and **Participant** personas.
- Guarantee relational data integrity and prevent race conditions using atomic database transactions.
- Package the entire application stack into an optimized, secure Docker container running as a non-root user with health check probes.
- Orchestrate container deployments using Kubernetes (Minikube), demonstrating declarative scaling, Pod replication, and zero-downtime rolling updates.
- Design an independent, event-driven serverless microservice using AWS Lambda and API Gateway for digital pass validation and email dispatch simulation.
- Provide a 100% automated test suite with full coverage of critical application workflows.

### 3.2 Scope:
The system encompasses academic, technical, cultural, and sports events. It manages event lifecycles (Upcoming, Ongoing, Completed, Cancelled), attendee quotas, CSV roster generation, digital pass issuance, and system monitoring via synthetic `/health` endpoints.

---

## 4. Requirements Specification

### 4.1 Functional Requirements:
1. **Authentication & Authorization**:
   - User account registration with email uniqueness validation.
   - Secure login/logout using session-based authentication.
   - Password encryption using PBKDF2 with SHA-256 and cryptographic salts.
   - Protected routes based on roles (`admin`, `organizer`, `participant`).
2. **Event Lifecycle Management**:
   - Organizers and admins can create, view, edit, and delete events.
   - Events enforce titles, categories, venues, dates, times, capacity limits, and registration cut-off deadlines.
   - Live seat counter calculating remaining seats dynamically.
3. **Registration & Booking Engine**:
   - Concurrency protection: atomicity ensured via `BEGIN IMMEDIATE` transaction locks.
   - Automatic rejection of duplicate registrations for the same user and event.
   - Automatic rejection when registration deadline has expired or capacity is exhausted.
   - Issuance of unique cryptographic digital passes (`EVT-XXXXXX`).
   - Participant cancellation allowing seats to be reallocated.
4. **Reporting & Analytics**:
   - Visual dashboard cards and status distribution charts (Chart.js).
   - Export of participant rosters as downloadable CSV spreadsheets.
5. **System Observability**:
   - Dedicated `/health` endpoint reporting uptime, version, and database connectivity.

### 4.2 Non-Functional Requirements:
- **Portability**: Runs across Windows, Linux, and macOS natively or containerized.
- **Security**: Principle of Least Privilege in Docker (non-root `eventuser`), CSRF protection, and separation of secrets via environment variables.
- **Reliability & Self-Healing**: Liveness and readiness probes restart failed containers and reroute traffic.
- **Performance**: Sub-100ms response times for database reads; sub-second container startup.

---

## 5. Technology Stack Summary

| Layer | Technologies Selected | Rationale |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap 5.3, Bootstrap Icons, Chart.js | Lightweight, responsive, zero heavy build dependencies (no npm needed). |
| **Backend** | Python 3.12 / 3.14, Flask, Werkzeug | Clean architectural patterns, lightweight WSGI standard, rapid execution. |
| **Database** | SQLite 3 | Embedded, zero-configuration relational database with full ACID compliance. |
| **Containerization** | Docker, Docker Compose | Industry-standard OCI container packaging with isolated host volume persistence. |
| **Orchestration** | Kubernetes, Minikube, kubectl | Declarative container orchestration, multi-pod replication, and rolling updates. |
| **Serverless** | AWS Lambda, Amazon API Gateway, Amazon S3, AWS SAM | Cost-optimized event-driven microservice architecture with sub-millisecond billing. |
| **Testing** | pytest | Automated test framework executing integration, unit, and health check suites. |

---

## 6. Database Design & Schema

The relational schema is defined in `database/schema.sql` and initialized via `database/init_db.py`.

### Tables and Constraints:
1. **`users`**:
   - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
   - `name`: TEXT NOT NULL
   - `email`: TEXT UNIQUE NOT NULL
   - `password_hash`: TEXT NOT NULL
   - `role`: TEXT NOT NULL CHECK(role IN ('admin', 'organizer', 'participant'))
   - `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
2. **`categories`**:
   - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
   - `name`: TEXT UNIQUE NOT NULL
   - `description`: TEXT
3. **`events`**:
   - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
   - `title`: TEXT NOT NULL
   - `description`: TEXT NOT NULL
   - `category`: TEXT NOT NULL REFERENCES categories(name)
   - `date`: TEXT NOT NULL (YYYY-MM-DD)
   - `start_time`: TEXT NOT NULL (HH:MM)
   - `end_time`: TEXT NOT NULL (HH:MM)
   - `venue`: TEXT NOT NULL
   - `capacity`: INTEGER NOT NULL CHECK(capacity > 0)
   - `registration_deadline`: TEXT NOT NULL
   - `status`: TEXT NOT NULL DEFAULT 'Upcoming' CHECK(status IN ('Upcoming', 'Ongoing', 'Completed', 'Cancelled'))
   - `organizer_id`: INTEGER REFERENCES users(id) ON DELETE SET NULL
   - `poster_path`: TEXT DEFAULT 'default_event.jpg'
   - `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   - `updated_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
4. **`registrations`**:
   - `id`: INTEGER PRIMARY KEY AUTOINCREMENT
   - `registration_code`: TEXT UNIQUE NOT NULL
   - `user_id`: INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
   - `event_id`: INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE
   - `registration_date`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   - `status`: TEXT NOT NULL DEFAULT 'Confirmed' CHECK(status IN ('Confirmed', 'Cancelled'))
   - *Constraint*: UNIQUE(user_id, event_id)

---

## 7. Module-by-Module Implementation Details

### 7.1 Module 1 & 2: Virtualization & Hypervisor Management
- Evaluated physical hardware computing versus virtualized computing.
- Contrasted Bare-Metal (Type-1: KVM/ESXi) and Hosted (Type-2: VirtualBox) hypervisors.
- Documented automated VM management using PowerShell (`VBoxManage`) on Windows and `virsh` on enterprise Linux.
- Covered snapshot differencing disks and full versus linked cloning workflows.

### 7.2 Module 3: Docker Containerization
- Built production Dockerfile using `python:3.12-slim` base image.
- Enforced security using unprivileged `eventuser` (UID 1001).
- Added multi-factor healthcheck probe testing `http://localhost:5000/health`.
- Configured `docker-compose.yml` to bind-mount host `./database` and `./static/uploads` to persist SQLite data across container recreation.

### 7.3 Module 4: Kubernetes Orchestration
- Provisioned local single-node cluster using Minikube.
- Configured dedicated `eventease` namespace.
- Separated configuration from code using `ConfigMap` and base64-encoded `Secret`.
- Deployed 2-replica `Deployment` with CPU/Memory requests (100m / 128Mi) and limits (500m / 256Mi).
- Configured both `ClusterIP` (internal) and `NodePort: 30080` (external browser access) Services.
- Successfully verified horizontal scaling to 4 replicas and zero-downtime rolling update rollbacks.
- Documented multi-pod SQLite shared state trade-offs versus enterprise cloud databases (AWS RDS).

### 7.4 Module 5: AWS Serverless Computing
- Implemented stateless Lambda handler in `serverless/lambda_function.py`.
- Supports dual invocation: API Gateway HTTP API proxy JSON string parsing and direct SDK payload invocation.
- Generated SHA-256 digital pass authenticity signatures.
- Declared complete AWS infrastructure-as-code using AWS SAM template (`serverless/template.yaml`) including encrypted S3 bucket and IAM least-privilege policies.
- Verified 100% of serverless behaviors locally without requiring AWS billing or credentials.

---

## 8. Verification & Automated Testing Record

The test suite in `tests/` executes 30 automated integration and unit tests using pytest.

| Test File | Test Case Name | Verified Behavior | Status |
| :--- | :--- | :--- | :---: |
| `test_auth.py` | `test_register_success` | Valid user registration and redirect to login | PASSED |
| `test_auth.py` | `test_register_duplicate_email` | Prevents registering existing email address | PASSED |
| `test_auth.py` | `test_register_password_mismatch` | Form validation catches mismatched passwords | PASSED |
| `test_auth.py` | `test_login_success` | Validates session creation and redirect | PASSED |
| `test_auth.py` | `test_login_invalid_password` | Rejects incorrect credentials | PASSED |
| `test_auth.py` | `test_logout` | Clears user session | PASSED |
| `test_auth.py` | `test_role_access_control` | 403 Forbidden on unauthorized role routes | PASSED |
| `test_events.py` | `test_browse_events` | Public browsing page loads all published events | PASSED |
| `test_events.py` | `test_search_and_filter_events`| Filtering by keyword and category | PASSED |
| `test_events.py` | `test_event_detail_page` | Detail view and 404 on nonexistent ID | PASSED |
| `test_events.py` | `test_create_event_authorized` | Organizers can publish new events | PASSED |
| `test_events.py` | `test_create_event_unauthorized`| Participants cannot publish events | PASSED |
| `test_events.py` | `test_edit_event` | Modifying dates, capacity, and titles | PASSED |
| `test_events.py` | `test_delete_event` | Deletion and cascade handling | PASSED |
| `test_events.py` | `test_manage_events_access` | Table filtering in management console | PASSED |
| `test_health.py` | `test_health_check_healthy` | HTTP 200 and "status: UP", "database: connected" | PASSED |
| `test_health.py` | `test_health_check_unhealthy` | HTTP 503 and "status: DOWN" when database fails | PASSED |
| `test_registrations.py`| `test_successful_registration` | Concurrency-safe booking and code generation | PASSED |
| `test_registrations.py`| `test_duplicate_registration` | Rejects multiple confirmed passes for same user | PASSED |
| `test_registrations.py`| `test_full_capacity_rejection` | Rejects booking when capacity is 0 | PASSED |
| `test_registrations.py`| `test_expired_deadline_rejection`| Rejects booking after registration deadline | PASSED |
| `test_registrations.py`| `test_cancel_registration` | Allows participant to release seat | PASSED |
| `test_registrations.py`| `test_csv_export_roster` | Generates valid CSV attendee spreadsheet | PASSED |
| `test_serverless.py` | `test_lambda_registration_summary_direct` | Direct invocation of FaaS handler | PASSED |
| `test_serverless.py` | `test_lambda_registration_summary_apigw` | API Gateway proxy payload parsing | PASSED |
| `test_serverless.py` | `test_lambda_missing_fields_validation` | HTTP 422 on incomplete payload | PASSED |
| `test_serverless.py` | `test_lambda_invalid_email_validation` | HTTP 422 on malformed email | PASSED |
| `test_serverless.py` | `test_lambda_event_notification` | FaaS notification broadcast simulation | PASSED |
| `test_serverless.py` | `test_lambda_health_ping` | FaaS synthetic monitoring ping | PASSED |
| `test_serverless.py` | `test_lambda_unsupported_action`| HTTP 400 on unrecognized action | PASSED |

**Test Execution Summary**: `30 passed in 14.33 seconds (100% pass rate, 0 warnings)`.

---

## 9. Conclusion, Limitations & Future Enhancements

### 9.1 Conclusion:
EventEase successfully fulfills all curricular and practical requirements for a BCA Cloud Computing and Virtualization microproject. The application bridges software development with cloud operations, demonstrating virtual machine concepts, containerization, Kubernetes multi-pod orchestration, and serverless computing in an integrated, working system.

### 9.2 Limitations:
- **Embedded Database in Multi-Pod Clusters**: In Kubernetes, running multiple replicas with local SQLite creates separate isolated database instances per Pod rather than a shared datastore.
- **Synchronous Notification Dispatch**: In the local development environment, notifications are processed synchronously without an asynchronous message broker (like RabbitMQ or AWS SQS).

### 9.3 Future Enhancements:
- **Cloud Database Migration**: Replace SQLite with Amazon RDS (PostgreSQL/Aurora) to enable true multi-pod shared state across geographically distributed Kubernetes clusters.
- **Payment Gateway Integration**: Add Razorpay / Stripe webhooks for ticketed conferences.
- **Dynamic QR Code Check-in**: Generate scannable QR codes for physical event badge scanning using mobile camera scanners.
- **CI/CD Automation**: Implement GitHub Actions pipeline to automatically run pytest, build Docker images, and deploy to Kubernetes on every Git push.
