from analyzer.sandbox import (
    build_sandbox_plan,
    print_sandbox_plan,
)


resources = [
    {
        "address": "local_file.config",
        "type": "local_file",
        "action": "UPDATE",
    },
    {
        "address": "local_file.application",
        "type": "local_file",
        "action": "REPLACE",
    },
    {
        "address": "local_file.backup",
        "type": "local_file",
        "action": "CREATE",
    },
    {
        "address": "aws_lambda_function.reporting",
        "type": "aws_lambda_function",
        "action": "UPDATE",
    },
    {
        "address": "aws_vpc.production",
        "type": "aws_vpc",
        "action": "UPDATE",
    },
]


plan = build_sandbox_plan(resources)

print_sandbox_plan(plan)