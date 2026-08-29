import json

from analyzer.dependencies import (
    extract_terraform_references
)

from analyzer.graph import (
    build_dependency_graph,
    find_blast_radius,
    find_minimal_paths
)


# =========================================================
# 1. Load the COMPLETE Terraform plan
# =========================================================

with open(
    "dependency.json",
    "r",
    encoding="utf-8"
) as file:

    plan = json.load(file)


# =========================================================
# 2. Extract dependencies automatically
# =========================================================

edges = extract_terraform_references(
    plan
)


# =========================================================
# 3. Build NetworkX graph
# =========================================================

graph = build_dependency_graph(
    edges
)


# =========================================================
# 4. Simulate a Terraform change
# =========================================================
#
# In the real system this will come from parser.py.
#
# For now we explicitly choose the resource so we can
# test the graph engine independently.
# =========================================================

changed_resources = [
    "local_file.config"
]


# =========================================================
# 5. Calculate blast radius
# =========================================================

blast_radius = find_blast_radius(
    graph,
    changed_resources
)


# =========================================================
# 6. Calculate causal paths
# =========================================================

all_paths = {}

for resource in changed_resources:

    affected = blast_radius.get(
        resource,
        []
    )

    paths = find_minimal_paths(
        graph,
        resource,
        affected
    )

    all_paths[resource] = paths


# =========================================================
# 7. Build result
# =========================================================

result = {

    "changed_resources":
        changed_resources,

    "discovered_dependencies":
        [
            {
                "source": source,
                "target": target
            }
            for source, target in edges
        ],

    "blast_radius":
        blast_radius,

    "minimal_causal_paths":
        all_paths
}


# =========================================================
# 8. Print JSON
# =========================================================

print()

print(
    json.dumps(
        result,
        indent=2
    )
)

print()