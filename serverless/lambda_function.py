"""AWS Lambda Function: Event Notification and Registration Summary Service.
Independent serverless microservice designed for EventEase BCA Cloud Computing microproject.
Stateless, tested locally without AWS credentials, handles API Gateway proxy integration.
"""

import os
import json
import re
from datetime import datetime, timezone
import hashlib

# Configuration loaded from environment variables
ORGANIZATION_NAME = os.getenv("ORGANIZATION_NAME", "EventEase Campus Hub")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@eventease.local")
STAGE = os.getenv("STAGE", "dev")

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


def lambda_handler(event, context=None):
    """Entry point for AWS Lambda invocations (direct or API Gateway proxy).

    Parameters:
        event (dict): API Gateway event or direct invocation dictionary.
        context (LambdaContext): Runtime metadata (optional, None in local tests).

    Returns:
        dict: Standard API Gateway HTTP response dictionary with statusCode, headers, and body.
    """
    try:
        # 1. Parse payload whether coming from API Gateway proxy or direct invocation
        payload = {}
        if isinstance(event, dict):
            if "body" in event and event["body"] is not None:
                # API Gateway proxy integration transmits request body as string
                if isinstance(event["body"], str):
                    try:
                        payload = json.loads(event["body"])
                    except json.JSONDecodeError:
                        return error_response(400, "Malformed JSON syntax in request body.")
                elif isinstance(event["body"], dict):
                    payload = event["body"]
            else:
                # Direct Lambda invocation or test payload
                payload = event

        if not payload or not isinstance(payload, dict):
            return error_response(400, "Missing or empty JSON request payload.")

        # 2. Extract action type
        action = payload.get("action", "").upper().strip()
        if not action:
            return error_response(400, "Field 'action' is required (e.g. 'REGISTRATION_SUMMARY', 'EVENT_NOTIFICATION').")

        # 3. Route to respective handler
        if action == "REGISTRATION_SUMMARY":
            return handle_registration_summary(payload)
        elif action == "EVENT_NOTIFICATION":
            return handle_event_notification(payload)
        elif action == "PING":
            return success_response({
                "service": "EventEase-NotificationService",
                "stage": STAGE,
                "status": "HEALTHY",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        else:
            return error_response(400, f"Unsupported action '{action}'. Permitted actions: REGISTRATION_SUMMARY, EVENT_NOTIFICATION, PING.")

    except Exception as exc:
        return error_response(500, f"Internal serverless execution error: {str(exc)}")


def handle_registration_summary(payload):
    """Processes digital registration summary generation and verification code generation."""
    reg_code = payload.get("registration_code", "").strip()
    event_title = payload.get("event_title", "").strip()
    participant_name = payload.get("participant_name", "").strip()
    participant_email = payload.get("participant_email", "").strip()

    # Input validation
    missing_fields = []
    if not reg_code:
        missing_fields.append("registration_code")
    if not event_title:
        missing_fields.append("event_title")
    if not participant_name:
        missing_fields.append("participant_name")
    if not participant_email:
        missing_fields.append("participant_email")

    if missing_fields:
        return error_response(422, f"Missing required fields for REGISTRATION_SUMMARY: {', '.join(missing_fields)}.")

    if not EMAIL_REGEX.match(participant_email):
        return error_response(422, f"Invalid participant_email format: '{participant_email}'.")

    # Generate cryptographic verification hash for ticket authenticity
    hash_seed = f"{reg_code}:{participant_email}:{event_title}:{STAGE}".encode("utf-8")
    security_signature = hashlib.sha256(hash_seed).hexdigest()[:16].upper()

    summary_data = {
        "status": "CONFIRMED",
        "action": "REGISTRATION_SUMMARY",
        "registration_code": reg_code,
        "event_title": event_title,
        "participant_name": participant_name,
        "participant_email": participant_email,
        "security_signature": security_signature,
        "issued_by": ORGANIZATION_NAME,
        "support_email": SUPPORT_EMAIL,
        "summary_message": f"Hello {participant_name}, your seat for '{event_title}' is confirmed under pass #{reg_code}.",
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

    return success_response(summary_data, status_code=200)


def handle_event_notification(payload):
    """Simulates event reminder broadcast or schedule alteration notification."""
    event_id = payload.get("event_id")
    event_title = payload.get("title", "").strip()
    notification_type = payload.get("type", "REMINDER").upper().strip()
    recipients = payload.get("recipients", [])

    if not event_id or not event_title:
        return error_response(422, "Fields 'event_id' and 'title' are required for EVENT_NOTIFICATION.")

    if not isinstance(recipients, list) or len(recipients) == 0:
        return error_response(422, "Field 'recipients' must be a non-empty list of email addresses.")

    valid_recipients = [e for e in recipients if isinstance(e, str) and EMAIL_REGEX.match(e)]
    if not valid_recipients:
        return error_response(422, "No valid email addresses found in 'recipients' list.")

    return success_response({
        "status": "DISPATCHED",
        "action": "EVENT_NOTIFICATION",
        "event_id": event_id,
        "event_title": event_title,
        "notification_type": notification_type,
        "total_dispatched": len(valid_recipients),
        "recipients_count": len(valid_recipients),
        "dispatch_timestamp": datetime.now(timezone.utc).isoformat(),
        "delivery_gateway": f"AWS-SNS/SES Simulation ({STAGE})"
    }, status_code=200)


def success_response(data, status_code=200):
    """Formats standardized API Gateway 200/201 response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS"
        },
        "body": json.dumps({"success": True, "data": data})
    }


def error_response(status_code, error_message):
    """Formats standardized API Gateway error response."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({
            "success": False,
            "error": {
                "code": status_code,
                "message": error_message,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        })
    }


if __name__ == "__main__":
    # Local CLI test execution
    sample_event = {
        "action": "REGISTRATION_SUMMARY",
        "registration_code": "EVT-REG-1001",
        "event_title": "National Cloud Computing Summit 2026",
        "participant_name": "Rahul Verma",
        "participant_email": "participant@eventease.local"
    }
    result = lambda_handler(sample_event)
    print("Local Lambda Execution Output:")
    print(json.dumps(result, indent=2))
