import os
import json
import logging
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reporting-api")

app = FastAPI(title="Reporting API - InfraPreflight Sandbox")

# --- Configuration (injected by docker-compose / .env) ---
IAM_POLICY_STATE = os.getenv("IAM_POLICY_STATE", "allow")  # "allow" | "deny"
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL", "http://localstack:4566")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DB_BUCKET = os.getenv("DB_BUCKET", "reporting-db-bucket")
DB_OBJECT_KEY = os.getenv("DB_OBJECT_KEY", "report.json")

s3_client = boto3.client(
    "s3",
    endpoint_url=AWS_ENDPOINT_URL,
    region_name=AWS_REGION,
    aws_access_key_id="test",
    aws_secret_access_key="test",
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "reporting-api"}


@app.get("/reports")
def get_reports():
    """
    Simulates the runtime path: Reporting API -> Database (S3 mock).
    Access is gated by IAM_POLICY_STATE, which represents the exact
    IAM policy change being validated (Allow -> Deny per the PR diff).
    """
    request_time = datetime.now(timezone.utc).isoformat()

    if IAM_POLICY_STATE.lower() == "deny":
        logger.warning("IAM policy state=DENY - blocking database access")
        return JSONResponse(
            status_code=403,
            content={
                "error": "AccessDenied",
                "message": "reporting-service is not authorized to access the database resource",
                "policy_state": "deny",
                "timestamp": request_time,
            },
        )

    # policy_state == allow -> attempt the real downstream call
    try:
        obj = s3_client.get_object(Bucket=DB_BUCKET, Key=DB_OBJECT_KEY)
        body = json.loads(obj["Body"].read())
        return JSONResponse(
            status_code=200,
            content={
                "status": "ok",
                "policy_state": "allow",
                "data": body,
                "timestamp": request_time,
            },
        )
    except ClientError as e:
        # Downstream failure that is NOT a policy denial (e.g. bucket missing)
        # -> this is the "unverified / uncertain" case, not a clean pass/fail.
        logger.error(f"Downstream error hitting mock database: {e}")
        return JSONResponse(
            status_code=502,
            content={
                "error": "DownstreamUnavailable",
                "message": str(e),
                "policy_state": "allow",
                "timestamp": request_time,
            },
        )
