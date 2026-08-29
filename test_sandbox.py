from analyzer.sandbox import (
    classify_resource,
    build_sandbox_plan,
)


def test_supported_resource():
    result = classify_resource(
        "local_file.application",
        "local_file",
        "REPLACE",
    )

    assert result.coverage == "SUPPORTED"


def test_mockable_resource():
    result = classify_resource(
        "aws_lambda_function.api",
        "aws_lambda_function",
        "UPDATE",
    )

    assert result.coverage == "MOCKABLE"


def test_evidence_only_resource():
    result = classify_resource(
        "aws_cloudfront_distribution.app",
        "aws_cloudfront_distribution",
        "UPDATE",
    )

    assert result.coverage == "EVIDENCE_ONLY"


def test_unsupported_resource():
    result = classify_resource(
        "aws_vpc.main",
        "aws_vpc",
        "UPDATE",
    )

    assert result.coverage == "UNSUPPORTED"


def test_build_sandbox_plan():

    resources = [
        {
            "address": "local_file.config",
            "type": "local_file",
            "action": "UPDATE",
        },
        {
            "address": "aws_lambda_function.api",
            "type": "aws_lambda_function",
            "action": "UPDATE",
        },
        {
            "address": "aws_cloudfront_distribution.app",
            "type": "aws_cloudfront_distribution",
            "action": "UPDATE",
        },
        {
            "address": "aws_vpc.main",
            "type": "aws_vpc",
            "action": "UPDATE",
        },
    ]

    plan = build_sandbox_plan(resources)

    assert plan["total_resources"] == 4
    assert plan["coverage_percent"] == 50

    assert len(plan["supported"]) == 1
    assert len(plan["mockable"]) == 1
    assert len(plan["evidence_only"]) == 1
    assert len(plan["unsupported"]) == 1


if __name__ == "__main__":
    test_supported_resource()
    test_mockable_resource()
    test_evidence_only_resource()
    test_unsupported_resource()
    test_build_sandbox_plan()

    print("All Stage 5 tests passed.")