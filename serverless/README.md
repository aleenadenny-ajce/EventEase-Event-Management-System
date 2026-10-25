# EventEase Serverless Notification & Summary Microservice

Part of the **BCA Cloud Computing and Virtualization** microproject portfolio.

## 1. Overview
This module demonstrates **Serverless Architecture (Function as a Service / FaaS)** alongside traditional containerized services. It implements an independent, event-driven notification and digital registration summary engine running on **AWS Lambda** fronted by **Amazon API Gateway (HTTP API)** and connected to an **Amazon S3** media bucket.

### Key Capabilities
- **Digital Registration Summary (`REGISTRATION_SUMMARY`)**: Validates attendee registration payloads and issues a verifiable cryptographic signature.
- **Event Notification Dispatch (`EVENT_NOTIFICATION`)**: Simulates dispatching schedule updates or reminders to participant email lists.
- **Health Ping (`PING`)**: Stateless endpoint for synthetic monitoring.
- **Zero AWS Credential Lock-In for Local Testing**: Runs 100% locally via standard Python and pytest.

---

## 2. Serverless Component Architecture

```
[ Client / Webhook ]
        │
        ▼ (HTTPS POST)
[ Amazon API Gateway ]  (HTTP API Route: /notifications/summary)
        │
        ▼ (Proxy Event)
[ AWS Lambda Handler ]  (Python 3.12, 128MB Memory, <100ms execution)
        │
        ├──> [ AWS CloudWatch Logs ] (Execution audit trail)
        └──> [ Amazon S3 Bucket ]   (Encrypted ticket passes / poster assets)
```

---

## 3. Local Execution & Testing (No AWS Account Required)

### Run Handler Directly in Python:
```powershell
python serverless/lambda_function.py
```

### Run Automated Unit Tests:
```powershell
pytest tests/test_serverless.py -v
```

---

## 4. Deploying to AWS via AWS SAM (Optional)

> **Note**: Requires AWS CLI and AWS SAM CLI installed, plus an active AWS account configured with `aws configure`. If you do not have an AWS account, local testing above is sufficient for microproject demonstration.

### Build Application:
```powershell
sam build -t serverless/template.yaml
```

### Deploy to Cloud:
```powershell
sam deploy --guided
```
Provide the stack name `eventease-serverless-stack` and choose your preferred AWS Region (e.g. `ap-south-1` or `us-east-1`).

### Teardown & Cost Cleanup:
```powershell
sam delete --stack-name eventease-serverless-stack
```
This safely deletes all provisioned cloud resources, preventing unexpected AWS billings.
