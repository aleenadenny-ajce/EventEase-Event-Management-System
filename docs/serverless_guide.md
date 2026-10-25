# EventEase — Module 5: AWS Serverless Computing Guide

Part of the **BCA Cloud Computing and Virtualization** microproject curriculum.

---

## 1. What is Serverless Computing (FaaS)?

Serverless computing is a cloud-native execution model where cloud providers dynamically manage machine resource allocation. Developers write single-purpose event handlers (**Functions as a Service / FaaS**) without provisioning, patching, or managing physical or virtual servers.

### Architectural Evolution:
```
Traditional Dedicated Hardware  ──►  Virtual Machines (IaaS)  ──►  Containers (Docker/K8s)  ──►  Serverless (FaaS)
(Rent physical racks)                (Manage Guest OS)             (Manage Pods & Clusters)        (Write pure business logic)
```

| Trait | Virtual Machines | Containers (K8s) | Serverless (AWS Lambda) |
| :--- | :--- | :--- | :--- |
| **Billing Model** | Pay per hour/second running | Pay for node cluster capacity | Pay strictly per 1ms invocation |
| **Idle Cost** | 100% cost while idle | 100% cost for reserved resources | **$0.00 when idle** |
| **Scaling Velocity** | Minutes to launch new VM | Seconds to scale Pods | **Milliseconds to scale instances** |
| **OS Maintenance** | Full OS patches required | Container base image updates | Fully managed by AWS |

---

## 2. EventEase Serverless Architecture

In EventEase, the serverless component handles high-frequency asynchronous tasks: **Digital Registration Summary Generation** and **Event Notification Broadcast Simulation**.

```
[ Client / Webhook / EventEase Core ]
                 │
                 ▼ HTTPS POST
   [ Amazon API Gateway (HTTP API) ]
                 │
                 ▼ Proxy Payload
        [ AWS Lambda Function ]
      (eventease-notification-service)
                 │
        ┌────────┴────────┐
        ▼                 ▼
[ Amazon CloudWatch ]  [ Amazon S3 Bucket ]
 (Execution Logs)       (Digital Pass Storage)
```

---

## 3. Dissecting `serverless/lambda_function.py`

The Lambda handler in `serverless/lambda_function.py` is written to be **cloud-agnostic, stateless, and fully unit-testable locally without AWS credentials**.

### Core Actions:
1. `REGISTRATION_SUMMARY`:
   - Validates required fields: `registration_code`, `event_title`, `participant_name`, `participant_email`.
   - Validates email format via regular expressions.
   - Computes a cryptographic SHA-256 verification hash to prevent digital ticket forgery.
   - Emits structured JSON confirmation.
2. `EVENT_NOTIFICATION`:
   - Validates event ID, title, and participant email list.
   - Simulates email dispatch through Amazon SES / SNS.
3. `PING`:
   - Synthetic health check reporting service name, stage, and UTC timestamp.

### Input Agnostic Design:
The handler dynamically inspects the event:
- If called via **Amazon API Gateway**, it extracts and parses `event["body"]`.
- If called via **direct Lambda invocation** (e.g. AWS SDK `boto3` or unit tests), it uses `event` directly.

---

## 4. Local Execution & Testing (Zero AWS Cost)

You do **not** need an AWS account or credit card to test this module.

### Run Handler Directly in Python:
```powershell
python serverless/lambda_function.py
```
*Expected Output:*
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS"
  },
  "body": "{\"success\": true, \"data\": {\"status\": \"CONFIRMED\", \"action\": \"REGISTRATION_SUMMARY\", ...}}"
}
```

### Run Automated Unit Tests:
```powershell
pytest tests/test_serverless.py -v
```
All 7 serverless unit tests validate:
- Direct Lambda invocation
- API Gateway proxy payloads
- Missing field validation (HTTP 422)
- Malformed email rejection (HTTP 422)
- Notification broadcast simulation
- Health ping endpoint
- Unsupported action handling (HTTP 400)

---

## 5. Dissecting the AWS SAM Template (`serverless/template.yaml`)

The template uses the **AWS Serverless Application Model (SAM)**, an extension of AWS CloudFormation:

- **Function Resource (`AWS::Serverless::Function`)**:
  - Runtime: Python 3.12
  - Memory: 128 MB (cost-optimized)
  - Timeout: 10 seconds
  - Policies: `AWSLambdaBasicExecutionRole` (grants permission to write CloudWatch logs only — Least Privilege Principle).
- **HTTP API Gateway Events (`HttpApi`)**:
  - Exposes route `POST /notifications/summary`.
  - Exposes route `GET /notifications/health`.
- **S3 Bucket (`AWS::S3::Bucket`)**:
  - Stores uploaded event posters and generated PDF ticket passes.
  - Configures AES-256 Server-Side Encryption (`SSEAlgorithm: AES256`).
  - Enables `PublicAccessBlockConfiguration` to prevent accidental public data leakage.
  - Enables versioning to guard against accidental deletion.

---

## 6. Cloud Deployment Instructions (Optional — Requires AWS Account)

> **Important**: This section is optional for college lab demonstration. Do not perform these steps unless you have an active AWS account and wish to demonstrate cloud deployment.

### Prerequisites:
1. Install [AWS CLI v2](https://aws.amazon.com/cli/) and configure credentials:
   ```powershell
   aws configure
   ```
2. Install [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html).

### Build Application:
```powershell
sam build -t serverless/template.yaml
```

### Deploy to AWS Cloud:
```powershell
sam deploy --guided
```
- Stack Name: `eventease-serverless-stack`
- AWS Region: `ap-south-1` (Mumbai) or `us-east-1`
- Confirm changes and authorization prompts.

### Invoke Live Cloud API via curl / PowerShell:
```powershell
$cloudUrl = "https://<api-id>.execute-api.ap-south-1.amazonaws.com/notifications/summary"
$body = @{
    action = "REGISTRATION_SUMMARY"
    registration_code = "EVT-REG-1001"
    event_title = "National Cloud Computing Summit 2026"
    participant_name = "Rahul Verma"
    participant_email = "participant@eventease.local"
} | ConvertTo-Json

Invoke-RestMethod -Uri $cloudUrl -Method Post -Body $body -ContentType "application/json"
```

### Teardown & Cost Cleanup:
Always delete provisioned resources after demonstration to avoid unexpected charges:
```powershell
sam delete --stack-name eventease-serverless-stack
```
