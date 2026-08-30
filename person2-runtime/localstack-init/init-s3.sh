#!/bin/bash
set -e

echo "[init] Creating mock database bucket in LocalStack..."
awslocal s3 mb s3://reporting-db-bucket

echo "[init] Seeding mock report data..."
cat <<JSON > /tmp/report.json
{
  "report_id": "rpt-001",
  "generated_by": "reporting-service",
  "rows": [
    {"id": 1, "metric": "signups", "value": 482},
    {"id": 2, "metric": "churn", "value": 12}
  ]
}
JSON

awslocal s3 cp /tmp/report.json s3://reporting-db-bucket/report.json

echo "[init] LocalStack seed complete."
