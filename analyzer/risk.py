import json
from pathlib import Path


SEVERITY_WEIGHT = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "CRITICAL": 4,
}


def clamp(value, minimum=0, maximum=100):
    return max(minimum, min(maximum, value))


def calculate_risk(
    severity="MEDIUM",
    blast_radius_count=0,
    dependency_count=0,
    synthetic_failures=0,
    synthetic_total=0,
):
    """
    Calculate a simple infrastructure change risk score.

    Higher score = higher risk.
    """

    severity_score = SEVERITY_WEIGHT.get(
        str(severity).upper(),
        SEVERITY_WEIGHT["MEDIUM"],
    )

    severity_component = severity_score * 15

    blast_component = min(blast_radius_count * 10, 30)

    dependency_component = min(dependency_count * 5, 20)

    if synthetic_total > 0:
        failure_rate = synthetic_failures / synthetic_total
        synthetic_component = failure_rate * 30
    else:
        synthetic_component = 0

    risk_score = (
        severity_component
        + blast_component
        + dependency_component
        + synthetic_component
    )

    return round(clamp(risk_score), 2)


def calculate_confidence(
    synthetic_failures=0,
    synthetic_total=0,
    dependency_data_available=True,
    blast_radius_available=True,
):
    """
    Calculate confidence in the risk assessment.
    """

    confidence = 50

    if dependency_data_available:
        confidence += 15

    if blast_radius_available:
        confidence += 15

    if synthetic_total > 0:
        failure_rate = synthetic_failures / synthetic_total

        if failure_rate == 0:
            confidence += 20
        elif failure_rate < 0.25:
            confidence += 10
        else:
            confidence -= 5

    return round(clamp(confidence), 2)


def recommendation(risk_score, confidence_score):
    """
    Convert risk + confidence into an operational recommendation.
    """

    if confidence_score < 50:
        return "REVIEW_REQUIRED"

    if risk_score >= 75:
        return "BLOCK"

    if risk_score >= 50:
        return "MANUAL_REVIEW"

    return "SAFE_TO_PROCEED"


def analyze(
    severity="MEDIUM",
    blast_radius_count=0,
    dependency_count=0,
    synthetic_failures=0,
    synthetic_total=0,
):
    risk_score = calculate_risk(
        severity=severity,
        blast_radius_count=blast_radius_count,
        dependency_count=dependency_count,
        synthetic_failures=synthetic_failures,
        synthetic_total=synthetic_total,
    )

    confidence_score = calculate_confidence(
        synthetic_failures=synthetic_failures,
        synthetic_total=synthetic_total,
        dependency_data_available=dependency_count >= 0,
        blast_radius_available=blast_radius_count >= 0,
    )

    return {
        "risk_score": risk_score,
        "confidence_score": confidence_score,
        "recommendation": recommendation(
            risk_score,
            confidence_score,
        ),
    }


if __name__ == "__main__":
    result = analyze(
        severity="HIGH",
        blast_radius_count=2,
        dependency_count=2,
        synthetic_failures=0,
        synthetic_total=5,
    )

    print(json.dumps(result, indent=2))