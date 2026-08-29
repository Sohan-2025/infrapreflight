from analyzer.risk import (
    calculate_risk,
    calculate_confidence,
    recommendation,
    analyze,
)


def test_low_risk():
    result = analyze(
        severity="LOW",
        blast_radius_count=0,
        dependency_count=0,
        synthetic_failures=0,
        synthetic_total=5,
    )

    assert result["risk_score"] < 50
    assert result["recommendation"] == "SAFE_TO_PROCEED"


def test_high_risk():
    result = analyze(
        severity="CRITICAL",
        blast_radius_count=5,
        dependency_count=4,
        synthetic_failures=3,
        synthetic_total=5,
    )

    assert result["risk_score"] >= 75
    assert result["recommendation"] == "BLOCK"


def test_confidence_with_passing_tests():
    confidence = calculate_confidence(
        synthetic_failures=0,
        synthetic_total=5,
        dependency_data_available=True,
        blast_radius_available=True,
    )

    assert confidence == 100


def test_manual_review():
    assert recommendation(60, 100) == "MANUAL_REVIEW"


def test_review_required_when_confidence_low():
    assert recommendation(20, 40) == "REVIEW_REQUIRED"


if __name__ == "__main__":
    test_low_risk()
    test_high_risk()
    test_confidence_with_passing_tests()
    test_manual_review()
    test_review_required_when_confidence_low()

    print("All Stage 7 tests passed.")