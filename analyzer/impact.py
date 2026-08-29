"""
InfraPreflight - Impact Analysis Engine

Stage 4:
Combines Terraform change information, severity, dependency
information and blast radius into a standardized risk report.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


SEVERITY_SCORE = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
}


def normalize_severity(value: Any) -> str:
    """
    Convert different severity representations into:
    LOW / MEDIUM / HIGH
    """
    if value is None:
        return "LOW"

    value = str(value).upper().strip()

    if value in {"HIGH", "CRITICAL"}:
        return "HIGH"

    if value in {"MEDIUM", "MODERATE"}:
        return "MEDIUM"

    return "LOW"


def calculate_blast_radius_size(blast_radius: Any) -> int:
    """
    Count unique affected resources.
    """

    if isinstance(blast_radius, list):
        return len(set(str(x) for x in blast_radius))

    if isinstance(blast_radius, dict):
        resources = set()

        for values in blast_radius.values():
            if isinstance(values, list):
                resources.update(str(x) for x in values)

        return len(resources)

    return 0


def collect_affected_resources(blast_radius: Any) -> list[str]:
    """
    Convert different blast-radius formats into a single list.
    """

    resources: set[str] = set()

    if isinstance(blast_radius, list):
        resources.update(str(x) for x in blast_radius)

    elif isinstance(blast_radius, dict):
        for values in blast_radius.values():
            if isinstance(values, list):
                resources.update(str(x) for x in values)

    return sorted(resources)


def calculate_confidence(
    severity: str,
    blast_radius_size: int,
    causal_paths: list[list[str]],
) -> float:
    """
    Estimate confidence in the static impact analysis.

    This is NOT runtime confidence yet.
    Runtime evidence will be added in a later stage.
    """

    confidence = 0.70

    # More dependency evidence increases confidence.
    if causal_paths:
        confidence += 0.10

    # A small, clearly identified blast radius is easier
    # to reason about.
    if 1 <= blast_radius_size <= 3:
        confidence += 0.10

    # High severity changes deserve conservative treatment.
    if severity == "HIGH":
        confidence += 0.05

    return min(round(confidence, 2), 0.95)


def calculate_risk_score(
    severity: str,
    blast_radius_size: int,
    causal_path_count: int,
) -> int:
    """
    Produce a deterministic 0-100 risk score.

    Factors:
      severity
      blast radius
      dependency evidence
    """

    severity_score = SEVERITY_SCORE.get(severity, 1)

    score = severity_score * 20

    if blast_radius_size >= 1:
        score += min(blast_radius_size * 10, 40)

    if causal_path_count >= 1:
        score += min(causal_path_count * 5, 20)

    return min(score, 100)


def determine_risk_level(score: int) -> str:
    """
    Convert numerical risk score to LOW / MEDIUM / HIGH.
    """

    if score >= 70:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    return "LOW"


def determine_recommendation(risk_level: str) -> str:
    """
    Convert risk level into a PR recommendation.
    """

    if risk_level == "HIGH":
        return "BLOCK"

    if risk_level == "MEDIUM":
        return "REVIEW"

    return "PASS"


def build_impact_report(analysis: dict[str, Any]) -> dict[str, Any]:
    """
    Build the standardized InfraPreflight risk report.

    The function intentionally accepts flexible input because
    earlier pipeline stages may produce slightly different
    JSON structures.
    """

    changed_resource = (
        analysis.get("changed_resource")
        or analysis.get("changed_resources")
        or analysis.get("resource")
    )

    # Normalize changed resources.
    if isinstance(changed_resource, str):
        changed_resources = [changed_resource]

    elif isinstance(changed_resource, list):
        changed_resources = [
            str(resource)
            for resource in changed_resource
        ]

    else:
        changed_resources = []

    severity = normalize_severity(
        analysis.get("severity")
    )

    blast_radius = analysis.get(
        "blast_radius",
        []
    )

    affected_resources = collect_affected_resources(
        blast_radius
    )

    # If the changed resource itself isn't in the blast radius,
    # include it because it is definitely impacted.
    for resource in changed_resources:
        if resource not in affected_resources:
            affected_resources.append(resource)

    affected_resources = sorted(set(affected_resources))

    causal_paths = analysis.get(
        "minimal_causal_paths",
        []
    )

    if not isinstance(causal_paths, list):
        causal_paths = []

    blast_radius_size = len(affected_resources)

    causal_path_count = len(causal_paths)

    risk_score = calculate_risk_score(
        severity=severity,
        blast_radius_size=blast_radius_size,
        causal_path_count=causal_path_count,
    )

    risk_level = determine_risk_level(risk_score)

    confidence = calculate_confidence(
        severity=severity,
        blast_radius_size=blast_radius_size,
        causal_paths=causal_paths,
    )

    risk_factors = []

    if severity == "HIGH":
        risk_factors.append(
            "High-severity infrastructure change"
        )
    elif severity == "MEDIUM":
        risk_factors.append(
            "Medium-severity infrastructure change"
        )

    if blast_radius_size >= 4:
        risk_factors.append(
            "Large dependency blast radius"
        )
    elif blast_radius_size >= 2:
        risk_factors.append(
            "Multiple downstream resources may be affected"
        )

    if causal_path_count > 0:
        risk_factors.append(
            "Dependency causal path identified"
        )

    if not causal_paths:
        risk_factors.append(
            "No causal dependency path available"
        )

    report = {
        "schema_version": "1.0",

        "engine": {
            "name": "InfraPreflight Impact Analysis Engine",
            "stage": 4,
        },

        "summary": {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "confidence": confidence,
            "recommendation": determine_recommendation(
                risk_level
            ),
        },

        "changed_resources": changed_resources,

        "impact": {
            "affected_resources": affected_resources,
            "blast_radius_size": blast_radius_size,
            "causal_path_count": causal_path_count,
        },

        "risk_factors": risk_factors,

        "causal_paths": causal_paths,

        "evidence": {
            "static_analysis": True,
            "runtime_evidence": False,
            "sandbox_simulation": False,
        },
    }

    return report


def load_json(path: str) -> dict[str, Any]:
    """
    Load a JSON analysis file.
    """

    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}"
        )

    with file_path.open(
        "r",
        encoding="utf-8-sig",
    ) as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            "Input JSON must contain an object."
        )

    return data


def save_json(
    report: dict[str, Any],
    path: str,
) -> None:
    """
    Save the standardized risk report.
    """

    output_path = Path(path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=2,
        )


def main() -> None:
    """
    Command-line entry point.

    Usage:

        python -m analyzer.impact input.json output.json
    """

    if len(sys.argv) != 3:
        print(
            "Usage: python -m analyzer.impact "
            "<input.json> <output.json>"
        )
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        analysis = load_json(input_file)

        report = build_impact_report(
            analysis
        )

        save_json(
            report,
            output_file,
        )

        print()
        print("=" * 70)
        print("INFRAPREFLIGHT IMPACT ANALYSIS")
        print("=" * 70)

        print(
            f"Risk Score     : "
            f"{report['summary']['risk_score']}/100"
        )

        print(
            f"Risk Level     : "
            f"{report['summary']['risk_level']}"
        )

        print(
            f"Confidence     : "
            f"{report['summary']['confidence'] * 100:.0f}%"
        )

        print(
            f"Recommendation : "
            f"{report['summary']['recommendation']}"
        )

        print(
            f"Blast Radius   : "
            f"{report['impact']['blast_radius_size']}"
        )

        print()
        print(
            f"Saved report to: {output_file}"
        )
        print("=" * 70)
        print()

    except Exception as error:
        print(
            f"ERROR: {error}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()