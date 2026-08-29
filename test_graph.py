import json

from analyzer.graph import (
    build_dependency_graph,
    find_blast_radius,
    find_minimal_paths
)


# ---------------------------------------------------------
# STEP 1
# Define our dependency relationships
# ---------------------------------------------------------

dependencies = [

    (
        "aws_iam_policy.reporting",
        "reporting-api"
    ),

    (
        "reporting-api",
        "reporting-db"
    )
]


# ---------------------------------------------------------
# STEP 2
# Build graph
# ---------------------------------------------------------

graph = build_dependency_graph(
    dependencies
)


# ---------------------------------------------------------
# STEP 3
# Pretend the IAM policy changed
# ---------------------------------------------------------

changed_resources = [
    "aws_iam_policy.reporting"
]


# ---------------------------------------------------------
# STEP 4
# Find blast radius
# ---------------------------------------------------------

blast_radius = find_blast_radius(
    graph,
    changed_resources
)


# ---------------------------------------------------------
# STEP 5
# Find minimal paths
# ---------------------------------------------------------

affected_nodes = blast_radius[
    "aws_iam_policy.reporting"
]


minimal_paths = find_minimal_paths(
    graph,
    "aws_iam_policy.reporting",
    affected_nodes
)


# ---------------------------------------------------------
# STEP 6
# Display result
# ---------------------------------------------------------

result = {

    "changed_resource":
        "aws_iam_policy.reporting",

    "blast_radius":
        affected_nodes,

    "minimal_causal_paths":
        minimal_paths
}


print(
    json.dumps(
        result,
        indent=2
    )
)