# EventEase — System Architecture & Design Document

Part of the **BCA Cloud Computing and Virtualization** microproject portfolio.

---

## 1. High-Level System Architecture

EventEase is built following a modular, multi-tier cloud-native architecture combining a **monolithic core application (Flask)**, a **relational datastore (SQLite)**, **container orchestration (Kubernetes & Docker)**, and an **event-driven serverless microservice (AWS Lambda & API Gateway)**.

```mermaid
flowchart TD
    subgraph Clients["Presentation Layer (Client Devices)"]
        Browser["Desktop & Mobile Web Browsers\n(HTML5 / CSS3 / Bootstrap 5 / JS)"]
        CurlClient["CLI & Automation Probes\n(curl / PowerShell scripts)"]
    end

    subgraph K8sCluster["Container Orchestration Layer (Kubernetes / Minikube)"]
        direction TB
        NodePort["NodePort Service :30080\n(External Host Access)"]
        ClusterIP["ClusterIP Service :5000\n(Internal Traffic Routing)"]

        subgraph PodReplicas["EventEase Pods (Replicas)"]
            Pod1["Pod 1: eventease-app\n• Python 3.12 Flask Engine\n• Non-root eventuser\n• Probes: /health"]
            Pod2["Pod 2: eventease-app\n• Python 3.12 Flask Engine\n• Non-root eventuser\n• Probes: /health"]
        end

        ConfigMap["ConfigMap: eventease-config\n(APP_NAME, PORT, HOST)"]
        Secret["Secret: eventease-secret\n(SECRET_KEY)"]
        
        ConfigMap -.-> Pod1
        ConfigMap -.-> Pod2
        Secret -.-> Pod1
        Secret -.-> Pod2
    end

    subgraph DataLayer["Data & Persistence Layer"]
        DB[(SQLite Embedded Database\neventease.db\n• WAL Mode\n• Foreign Keys ON\n• Transaction Locks)]
        StaticAssets["Static Storage\n(CSS / JS / Uploaded Posters)"]
    end

    subgraph ServerlessLayer["AWS Serverless Microservice Layer"]
        APIGW["Amazon API Gateway\n(HTTP API: /notifications)"]
        Lambda["AWS Lambda Function\n(eventease-notification-service\nPython 3.12 FaaS)"]
        S3Bucket["Amazon S3 Bucket\n(Encrypted Ticket Archive)"]
        CloudWatch["Amazon CloudWatch\n(Logs & Performance Metrics)"]
    end

    Browser --> NodePort
    CurlClient --> NodePort
    NodePort --> ClusterIP
    ClusterIP --> Pod1
    ClusterIP --> Pod2
    Pod1 --> DB
    Pod2 --> DB
    Pod1 --> StaticAssets
    Pod2 --> StaticAssets

    Pod1 -.->|Async Webhook / HTTP POST| APIGW
    APIGW --> Lambda
    Lambda --> S3Bucket
    Lambda --> CloudWatch
```

---

## 2. Database Entity-Relationship (ER) Diagram

The datastore enforces relational integrity, foreign key constraints, cascading deletions, and uniqueness rules.

```mermaid
erDiagram
    USERS ||--o{ EVENTS : "creates and organizes"
    USERS ||--o{ REGISTRATIONS : "books and registers"
    CATEGORIES ||--o{ EVENTS : "classifies"
    EVENTS ||--o{ REGISTRATIONS : "receives bookings"

    USERS {
        INTEGER id PK "Auto Increment"
        TEXT name "Full Name"
        TEXT email UK "Unique Login Identifier"
        TEXT password_hash "PBKDF2:SHA256 Hash"
        TEXT role "admin | organizer | participant"
        TIMESTAMP created_at "Account creation timestamp"
    }

    CATEGORIES {
        INTEGER id PK "Auto Increment"
        TEXT name UK "Category Title (e.g. Technical, Workshop)"
        TEXT description "Detailed Category Description"
    }

    EVENTS {
        INTEGER id PK "Auto Increment"
        TEXT title "Event Headline"
        TEXT description "Detailed Description"
        TEXT category FK "References categories(name)"
        TEXT date "ISO Event Date (YYYY-MM-DD)"
        TEXT start_time "Start Time (HH:MM)"
        TEXT end_time "End Time (HH:MM)"
        TEXT venue "Physical Auditorium / Virtual Link"
        INTEGER capacity "Maximum Permitted Participants"
        TEXT registration_deadline "Cut-off Date (YYYY-MM-DD)"
        TEXT status "Upcoming | Ongoing | Completed | Cancelled"
        INTEGER organizer_id FK "References users(id)"
        TEXT poster_path "Path to uploaded banner"
        TIMESTAMP created_at "Creation timestamp"
        TIMESTAMP updated_at "Last modified timestamp"
    }

    REGISTRATIONS {
        INTEGER id PK "Auto Increment"
        TEXT registration_code UK "Unique Pass ID (e.g. EVT-A1B2C3)"
        INTEGER user_id FK "References users(id) ON DELETE CASCADE"
        INTEGER event_id FK "References events(id) ON DELETE CASCADE"
        TIMESTAMP registration_date "Booking timestamp"
        TEXT status "Confirmed | Cancelled"
    }
```

---

## 3. Concurrency-Safe Event Registration Sequence

To prevent race conditions, overselling seats, and duplicate bookings, registration utilizes database-level transactions with immediate exclusive table locks (`BEGIN IMMEDIATE`).

```mermaid
sequenceDiagram
    autonumber
    actor Participant as Student / Participant
    participant App as Flask Web Server
    participant DB as SQLite Relational Database

    Participant->>App: POST /events/{id}/register (Session Auth Cookie)
    App->>App: Verify Authentication (@login_required)
    
    App->>DB: BEGIN IMMEDIATE (Acquire Write Lock)
    App->>DB: SELECT * FROM events WHERE id = ?
    DB-->>App: Return Event Details
    
    alt Event Not Found or Not 'Upcoming'
        App->>DB: ROLLBACK
        App-->>Participant: 400 Bad Request / Flash Warning
    else Registration Deadline Passed
        App->>DB: ROLLBACK
        App-->>Participant: Error: Deadline Expired
    end

    App->>DB: SELECT id, status FROM registrations WHERE user_id = ? AND event_id = ?
    DB-->>App: Existing Registration Status

    alt Already Confirmed
        App->>DB: ROLLBACK
        App-->>Participant: Info: Already Registered for this event
    end

    App->>DB: SELECT COUNT(*) FROM registrations WHERE event_id = ? AND status = 'Confirmed'
    DB-->>App: Confirmed Count

    alt Confirmed Count >= Capacity
        App->>DB: ROLLBACK
        App-->>Participant: Error: Event Capacity Reached (Overbooking Blocked)
    else Seats Available
        App->>App: Generate Unique Code (EVT-XXXXXX)
        App->>DB: INSERT INTO registrations (registration_code, user_id, event_id, status)
        App->>DB: COMMIT (Release Write Lock)
        App-->>Participant: 302 Redirect -> /registrations/success/{code}
    end
```

---

## 4. Role-Based Access Control (RBAC) Architecture

```mermaid
flowchart LR
    Visitor["Anonymous Visitor"]
    Participant["Participant User"]
    Organizer["Faculty Organizer"]
    Admin["System Administrator"]

    subgraph Routes["Application Endpoints & Capabilities"]
        PublicViews["Public Views\n• Browse Events\n• Search & Filter\n• View Event Detail\n• System Health (/health)"]
        AuthViews["Auth Views\n• Login / Register\n• Password Hash Validation"]
        PartViews["Participant Portal\n• Register for Event\n• View My Passes\n• Cancel Registration"]
        OrgViews["Organizer Portal\n• Create / Edit Event\n• View Attendee Roster\n• Export Roster CSV"]
        AdminViews["Admin Console\n• Platform Metrics & Charts\n• Global User Management\n• Delete Any Event\n• Reassign Roles"]
    end

    Visitor --> PublicViews
    Visitor --> AuthViews

    Participant --> PublicViews
    Participant --> PartViews

    Organizer --> PublicViews
    Organizer --> PartViews
    Organizer --> OrgViews

    Admin --> PublicViews
    Admin --> PartViews
    Admin --> OrgViews
    Admin --> AdminViews
```

---

## 5. Serverless Microservice Integration Pattern

The serverless component runs decoupled from the core application:
1. **Event Notification**: Broadcasters send JSON events containing event title, date, and recipient email addresses to Amazon API Gateway.
2. **Lambda Ingestion**: The `eventease-notification-service` Lambda function validates the schema and authorization.
3. **Cryptographic Verification**: Generates a verifiable SHA-256 digital signature for digital passes.
4. **CloudWatch Metrics**: Automatically logs invocation duration, cold starts, and errors with zero manual agent configuration.
