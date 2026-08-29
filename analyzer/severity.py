from typing import Any, Dict, List


# ---------------------------------------------------------
# Resource types where a change can directly affect
# permissions, networking, availability, or data.
# ---------------------------------------------------------

HIGH_RISK_RESOURCE_TYPES = {
    "aws_iam_policy",
    "aws_iam_role_policy",
    "aws_iam_role_policy_attachment",
    "aws_security_group",
    "aws_security_group_rule",
    "aws_network_acl",
    "aws_network_acl_rule",
    "aws_route",
    "aws_route_table",
    "aws_route_table_association",
    "aws_vpc",
    "aws_subnet",
    "aws_nat_gateway",
    "aws_internet_gateway",
    "aws_db_instance",
    "aws_rds_cluster",
}


MEDIUM_RISK_RESOURCE_TYPES = {
    "aws_instance",
    "aws_launch_template",
    "aws_autoscaling_group",
    "aws_lb",
    "aws_lb_listener",
    "aws_lb_target_group",
    "aws_s3_bucket",
    "aws_cloudwatch_log_group",
}


# ---------------------------------------------------------
# Attributes that are usually metadata rather than
# runtime-impacting configuration.
# ---------------------------------------------------------

LOW_RISK_ATTRIBUTES = {
    "tags",
    "tags_all",
    "description",
}


# ---------------------------------------------------------
# Keywords that indicate potentially dangerous changes.
# ---------------------------------------------------------

HIGH_RISK_KEYWORDS = {
    "policy",
    "permission",
    "iam",
    "security_group",
    "network",
    "route",
    "subnet",
    "vpc",
    "ingress",
    "egress",
    "authorization",
    "access",
    "password",
    "secret",
    "database",
    "availability",
}


def calculate_severity(
    resource_type: str,
    action: str,
    changed_attributes: List[Dict[str, Any]]
) -> str:
    """
    Estimate the potential runtime risk of a Terraform change.

    This is intentionally deterministic.
    We are NOT using an ML model for the basic risk classification.
    """

    # -----------------------------------------------------
    # DELETE / REPLACE can remove or recreate infrastructure.
    # -----------------------------------------------------

    if action in {"DELETE", "REPLACE"}:
        return "HIGH"

    # -----------------------------------------------------
    # Certain resource types are inherently sensitive.
    # -----------------------------------------------------

    if resource_type in HIGH_RISK_RESOURCE_TYPES:
        return "HIGH"

    # -----------------------------------------------------
    # Inspect individual changed attributes.
    # -----------------------------------------------------

    for change in changed_attributes:

        attribute = change.get(
            "attribute",
            ""
        ).lower()

        # Example:
        # policy.Statement[0].Action
        # security_group.ingress
        # network_interface
        for keyword in HIGH_RISK_KEYWORDS:

            if keyword in attribute:
                return "HIGH"

    # -----------------------------------------------------
    # Medium-risk infrastructure.
    # -----------------------------------------------------

    if resource_type in MEDIUM_RISK_RESOURCE_TYPES:
        return "MEDIUM"

    # -----------------------------------------------------
    # If every changed attribute is metadata,
    # classify it as LOW.
    # -----------------------------------------------------

    if changed_attributes:

        all_low_risk = True

        for change in changed_attributes:

            attribute = change.get(
                "attribute",
                ""
            )

            root_attribute = (
                attribute
                .split(".")[0]
                .split("[")[0]
            )

            if root_attribute not in LOW_RISK_ATTRIBUTES:

                all_low_risk = False
                break

        if all_low_risk:
            return "LOW"

    # -----------------------------------------------------
    # Unknown infrastructure changes get MEDIUM risk.
    #
    # This is safer than pretending they are LOW risk.
    # -----------------------------------------------------

    return "MEDIUM"