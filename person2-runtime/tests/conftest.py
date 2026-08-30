import json
import os
from datetime import datetime, timezone

import pytest

EVIDENCE_DIR = os.path.join(os.path.dirname(__file__), "..", "evidence")
EVIDENCE_PATH = os.path.join(EVIDENCE_DIR, "runtime_evidence.json")

_results = []


def record_result(**kwargs):
    """Called from tests to log one piece of raw runtime evidence."""
    kwargs["timestamp"] = datetime.now(timezone.utc).isoformat()
    _results.append(kwargs)


def pytest_sessionfinish(session, exitstatus):
    os.makedirs(EVIDENCE_DIR, exist_ok=True)

    passed = sum(1 for r in _results if r.get("passed") is True)
    failed = sum(1 for r in _results if r.get("passed") is False)
    unverified = sum(1 for r in _results if r.get("passed") is None)

    evidence = {
        "target_path": [
            "aws_iam_policy.reporting",
            "reporting-api",
            "database (s3 mock: reporting-db-bucket)",
        ],
        "policy_state_tested": os.getenv("IAM_POLICY_STATE", "unknown"),
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "results": _results,
        "summary": {
            "total_tests": len(_results),
            "passed": passed,
            "failed": failed,
            "unverified": unverified,
            "pytest_exit_status": exitstatus,
        },
    }

    with open(EVIDENCE_PATH, "w") as f:
        json.dump(evidence, f, indent=2)

    print(f"\n[evidence] Written to {EVIDENCE_PATH}")
