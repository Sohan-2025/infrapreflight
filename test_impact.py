import json
from pathlib import Path

from analyzer.impact import (
    build_impact_report,
    calculate_risk_score,
    determine_risk_level,
    determine_recommendation,
)


def test_high_risk_change():

    analysis = {
        "changed_resource": "aws_iam_policy.reporting",
        "severity": "HIGH",
        "blast_radius": [
            "reporting-api",
            "reporting-db",
        ],
        "minimal_causal_paths": [
            [
                "aws_iam_policy.reporting",
                "reporting-api",
            ],
            [
                "aws_iam_policy.reporting",
                "reporting-api",
                "reporting-db",
            ],
        ],
    }

    report = build_impact_report(analysis)

    assert report["summary"]["risk_level"] == "HIGH"

    assert (
        report["summary"]["recommendation"]
        == "BLOCK"
    )

    assert (
        report["impact"]["blast_radius_size"]
        == 3
    )

    assert (
        report["impact"]["causal_path_count"]
        == 2
    )


def test_low_risk_change():

    analysis = {
        "changed_resource": "local_file.documentation",
        "severity": "LOW",
        "blast_radius": [
            "local_file.documentation"
        ],
        "minimal_causal_paths": [],
    }

    report = build_impact_report(analysis)

    assert report["summary"]["risk_level"] == "LOW"

    assert (
        report["summary"]["recommendation"]
        == "PASS"
    )


def test_medium_risk_change():

    analysis = {
        "changed_resource": "aws_instance.web",
        "severity": "MEDIUM",
        "blast_radius": [
            "aws_instance.web",
            "web-service",
        ],
        "minimal_causal_paths": [
            [
                "aws_instance.web",
                "web-service",
            ]
        ],
    }

    report = build_impact_report(analysis)

    assert report["summary"]["risk_level"] in {
        "MEDIUM",
        "HIGH",
    }


def test_risk_score_bounds():

    score = calculate_risk_score(
        severity="HIGH",
        blast_radius_size=100,
        causal_path_count=100,
    )

    assert 0 <= score <= 100


def test_risk_level_mapping():

    assert determine_risk_level(20) == "LOW"

    assert determine_risk_level(50) == "MEDIUM"

    assert determine_risk_level(80) == "HIGH"


def test_recommendation_mapping():

    assert determine_recommendation("LOW") == "PASS"

    assert (
        determine_recommendation("MEDIUM")
        == "REVIEW"
    )

    assert (
        determine_recommendation("HIGH")
        == "BLOCK"
    )


if __name__ == "__main__":
    test_high_risk_change()
    test_low_risk_change()
    test_medium_risk_change()
    test_risk_score_bounds()
    test_risk_level_mapping()
    test_recommendation_mapping()

    print()
    print("All Stage 4 tests passed.")
    print()