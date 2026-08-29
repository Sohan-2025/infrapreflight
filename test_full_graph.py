import json

from analyzer.dependencies import (
    load_application_dependencies,
    convert_dependencies_to_edges
)

from analyzer.graph import (
    build_dependency_graph,
    find_blast_radius,
    find_minimal_paths
)


# ---------------------------------------------------------
# 1. Load application dependency information
# ---------------------------------------------------------

dependencies = load_application_dependencies(
    "config/app_dependencies.json"
)


# ---------------------------------------------------------
# 2. Convert dependency objects into graph edges
# ---------------------------------------------------------

edges = convert_dependencies_to_edges(
    dependencies
)


# ---------------------------------------------------------
# 3. Build graph
# ---------------------------------------------------------

graph = build_dependency_graph(
    edges
)


# ---------------------------------------------------------
# 4. Simulate a Terraform change
# ---------------------------------------------------------

changed_resources = [
    "aws_iam_policy.reporting"
]


# ---------------------------------------------------------
# 5. Calculate blast radius
# ---------------------------------------------------------

blast_radius = find_blast_radius(
    graph,
    changed_resources
)


# ---------------------------------------------------------
# 6. Calculate minimal paths
# ---------------------------------------------------------

resource = "aws_iam_policy.reporting"

affected = blast_radius.get(
    resource,
    []
)


minimal_paths = find_minimal_paths(
    graph,
    resource,
    affected
)


# ---------------------------------------------------------
# 7. Build final result
# ---------------------------------------------------------

result = {

    "changed_resource":
        resource,

    "blast_radius":
        affected,

    "minimal_causal_paths":
        minimal_paths
}


print(
    json.dumps(
        result,
        indent=2
    )
)