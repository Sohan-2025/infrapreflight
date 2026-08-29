from analyzer.severity import calculate_severity


def test(
    resource_type,
    action,
    attributes
):

    severity = calculate_severity(
        resource_type,
        action,
        attributes
    )

    print(
        f"{resource_type:<35} "
        f"{action:<10} "
        f"→ {severity}"
    )


# ---------------------------------------------------------
# Test cases
# ---------------------------------------------------------

test(
    "aws_iam_policy",
    "UPDATE",
    [
        {
            "attribute": "policy",
            "before": "Allow",
            "after": "Deny"
        }
    ]
)


test(
    "aws_security_group",
    "UPDATE",
    [
        {
            "attribute": "ingress",
            "before": [],
            "after": [
                {
                    "from_port": 3306
                }
            ]
        }
    ]
)


test(
    "aws_instance",
    "UPDATE",
    [
        {
            "attribute": "instance_type",
            "before": "t3.micro",
            "after": "t3.small"
        }
    ]
)


test(
    "aws_instance",
    "UPDATE",
    [
        {
            "attribute": "tags",
            "before": {
                "Environment": "dev"
            },
            "after": {
                "Environment": "production"
            }
        }
    ]
)


test(
    "aws_instance",
    "REPLACE",
    [
        {
            "attribute": "ami",
            "before": "ami-old",
            "after": "ami-new"
        }
    ]
)
