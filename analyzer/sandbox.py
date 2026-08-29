from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List


SUPPORTED_TYPES = {
    "local_file",
    "aws_s3_bucket",
    "aws_sqs_queue",
    "aws_dynamodb_table",
    "aws_iam_policy",
}

MOCKABLE_TYPES = {
    "aws_lambda_function",
    "aws_api_gateway_rest_api",
    "aws_rds_cluster",
    "aws_db_instance",
}

EVIDENCE_ONLY_TYPES = {
    "aws_cloudfront_distribution",
    "aws_route53_zone",
    "aws_route53_record",
}

UNSUPPORTED_TYPES = {
    "aws_ec2_instance",
    "aws_vpc",
    "aws_nat_gateway",
}


@dataclass
class SandboxResource:
    address: str
    resource_type: str
    coverage: str
    action: str = "unknown"
    reason: str = ""


def classify_resource(
    address: str,
    resource_type: str,
    action: str = "unknown",
) -> SandboxResource:
    """
    Classify a Terraform resource according to how safely
    it can be represented in the local sandbox.
    """

    if resource_type in SUPPORTED_TYPES:
        return SandboxResource(
            address=address,
            resource_type=resource_type,
            coverage="SUPPORTED",
            action=action,
            reason="Can be exercised directly in the local sandbox.",
        )

    if resource_type in MOCKABLE_TYPES:
        return SandboxResource(
            address=address,
            resource_type=resource_type,
            coverage="MOCKABLE",
            action=action,
            reason="The real service is not required; its relevant interface can be mocked.",
        )

    if resource_type in EVIDENCE_ONLY_TYPES:
        return SandboxResource(
            address=address,
            resource_type=resource_type,
            coverage="EVIDENCE_ONLY",
            action=action,
            reason="Dependency can be represented using available evidence, but not faithfully simulated.",
        )

    return SandboxResource(
        address=address,
        resource_type=resource_type,
        coverage="UNSUPPORTED",
        action=action,
        reason="No faithful local simulation is currently configured.",
    )


def build_sandbox_plan(resources: List[Dict]) -> Dict:
    """
    Convert affected resources into a targeted sandbox plan.

    Each input resource should contain:
        address
        type
        action
    """

    classified: List[SandboxResource] = []

    for resource in resources:
        address = resource.get("address", "unknown")
        resource_type = resource.get("type", "unknown")
        action = resource.get("action", "unknown")

        classified.append(
            classify_resource(
                address=address,
                resource_type=resource_type,
                action=action,
            )
        )

    supported = [
        asdict(resource)
        for resource in classified
        if resource.coverage == "SUPPORTED"
    ]

    mockable = [
        asdict(resource)
        for resource in classified
        if resource.coverage == "MOCKABLE"
    ]

    evidence_only = [
        asdict(resource)
        for resource in classified
        if resource.coverage == "EVIDENCE_ONLY"
    ]

    unsupported = [
        asdict(resource)
        for resource in classified
        if resource.coverage == "UNSUPPORTED"
    ]

    total = len(classified)

    if total == 0:
        coverage_percent = 0
    else:
        simulated = len(supported) + len(mockable)
        coverage_percent = round((simulated / total) * 100)

    return {
        "total_resources": total,
        "coverage_percent": coverage_percent,
        "supported": supported,
        "mockable": mockable,
        "evidence_only": evidence_only,
        "unsupported": unsupported,
    }


def print_sandbox_plan(plan: Dict) -> None:
    print("=" * 70)
    print("TARGETED SANDBOX PLAN")
    print("=" * 70)

    print(f"\nTotal affected resources: {plan['total_resources']}")
    print(f"Simulation coverage: {plan['coverage_percent']}%")

    print("\nSUPPORTED:")
    if plan["supported"]:
        for resource in plan["supported"]:
            print(f"  + {resource['address']}")
    else:
        print("  None")

    print("\nMOCKABLE:")
    if plan["mockable"]:
        for resource in plan["mockable"]:
            print(f"  ~ {resource['address']}")
    else:
        print("  None")

    print("\nEVIDENCE ONLY:")
    if plan["evidence_only"]:
        for resource in plan["evidence_only"]:
            print(f"  ? {resource['address']}")
    else:
        print("  None")

    print("\nUNSUPPORTED:")
    if plan["unsupported"]:
        for resource in plan["unsupported"]:
            print(f"  ! {resource['address']}")
    else:
        print("  None")

    print("\n" + "=" * 70)