"""Unit tests for AWS Lambda Notification & Summary microservice."""

import json
import pytest
from serverless.lambda_function import lambda_handler


def test_lambda_registration_summary_direct():
    """Test Lambda handler with direct invocation payload."""
    event = {
        "action": "REGISTRATION_SUMMARY",
        "registration_code": "EVT-REG-9999",
        "event_title": "Cloud Computing & DevOps Summit",
        "participant_name": "Aman Gupta",
        "participant_email": "aman@eventease.local"
    }

    response = lambda_handler(event, None)
    assert response["statusCode"] == 200

    body = json.loads(response["body"])
    assert body["success"] is True
    assert body["data"]["registration_code"] == "EVT-REG-9999"
    assert "security_signature" in body["data"]
    assert "summary_message" in body["data"]


def test_lambda_registration_summary_apigw_proxy():
    """Test Lambda handler with API Gateway proxy payload (JSON string body)."""
    raw_payload = {
        "action": "REGISTRATION_SUMMARY",
        "registration_code": "EVT-REG-7777",
        "event_title": "Kubernetes Deep Dive",
        "participant_name": "Sneha Patel",
        "participant_email": "sneha@eventease.local"
    }

    apigw_event = {
        "resource": "/notifications/summary",
        "path": "/notifications/summary",
        "httpMethod": "POST",
        "body": json.dumps(raw_payload)
    }

    response = lambda_handler(apigw_event, None)
    assert response["statusCode"] == 200

    body = json.loads(response["body"])
    assert body["success"] is True
    assert body["data"]["participant_name"] == "Sneha Patel"


def test_lambda_missing_fields_validation():
    """Test that missing required fields return HTTP 422."""
    incomplete_event = {
        "action": "REGISTRATION_SUMMARY",
        "registration_code": "EVT-REG-1234"
        # missing event_title, participant_name, participant_email
    }

    response = lambda_handler(incomplete_event, None)
    assert response["statusCode"] == 422
    body = json.loads(response["body"])
    assert body["success"] is False
    assert "Missing required fields" in body["error"]["message"]


def test_lambda_invalid_email_validation():
    """Test that malformed email format returns HTTP 422."""
    invalid_email_event = {
        "action": "REGISTRATION_SUMMARY",
        "registration_code": "EVT-REG-1234",
        "event_title": "Docker Summit",
        "participant_name": "Test User",
        "participant_email": "not-an-email-at-all"
    }

    response = lambda_handler(invalid_email_event, None)
    assert response["statusCode"] == 422
    body = json.loads(response["body"])
    assert "Invalid participant_email format" in body["error"]["message"]


def test_lambda_event_notification():
    """Test EVENT_NOTIFICATION action simulates email dispatch."""
    event = {
        "action": "EVENT_NOTIFICATION",
        "event_id": 101,
        "title": "Hackathon 2026 Kickoff",
        "type": "SCHEDULE_REMINDER",
        "recipients": ["user1@eventease.local", "user2@eventease.local"]
    }

    response = lambda_handler(event, None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["success"] is True
    assert body["data"]["total_dispatched"] == 2


def test_lambda_health_ping():
    """Test PING health action."""
    response = lambda_handler({"action": "PING"}, None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["data"]["status"] == "HEALTHY"


def test_lambda_unsupported_action():
    """Test unsupported action returns HTTP 400."""
    response = lambda_handler({"action": "INVALID_ACTION"}, None)
    assert response["statusCode"] == 400
