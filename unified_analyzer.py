import json

from analyzer.dependencies import extract_terraform_references
from analyzer.graph import (
    build_dependency_graph,
    find_blast_radius,
    find_minimal_paths
)


# ============================================================
# CONFIGURATION
# ============================================================

PLAN_FILE = "dependency.json"

APP_DEPENDENCY_FILE = "config/app_dependencies.json"

RESOURCE_SERVICE_MAP_FILE = (
    "config/resource_service_map.json"
)

CHANGED_RESOURCE = "local_file.config"


# ============================================================
# LOAD TERRAFORM PLAN
# ============================================================

with open(
    PLAN_FILE,
    "r",
    encoding="utf-8"
) as file:

    plan = json.load(file)


# ============================================================
# 1. EXTRACT TERRAFORM DEPENDENCIES
# ============================================================

terraform_edges = (
    extract_terraform_references(plan)
)


# ============================================================
# 2. LOAD APPLICATION DEPENDENCIES
# ============================================================

with open(
    APP_DEPENDENCY_FILE,
    "r",
    encoding="utf-8"
) as file:

    application_data = json.load(file)


application_edges = []

for dependency in application_data.get(
    "dependencies",
    []
):

    source = dependency.get("source")

    target = dependency.get("target")

    if source and target:

        application_edges.append(
            (source, target)
        )


# ============================================================
# 3. LOAD TERRAFORM → SERVICE MAPPINGS
# ============================================================

with open(
    RESOURCE_SERVICE_MAP_FILE,
    "r",
    encoding="utf-8"
) as file:

    mapping_data = json.load(file)


mapping_edges = []

for mapping in mapping_data.get(
    "mappings",
    []
):

    terraform_resource = (
        mapping.get("terraform_resource")
    )

    service = mapping.get("service")

    if terraform_resource and service:

        mapping_edges.append(
            (
                terraform_resource,
                service
            )
        )


# ============================================================
# 4. COMBINE ALL DEPENDENCY EVIDENCE
# ============================================================

all_edges = (
    terraform_edges
    + application_edges
    + mapping_edges
)


# ============================================================
# 5. BUILD UNIFIED GRAPH
# ============================================================

graph = build_dependency_graph(
    all_edges
)


# ============================================================
# 6. FIND BLAST RADIUS
# ============================================================

blast_radius = find_blast_radius(
    graph,
    [CHANGED_RESOURCE]
)


affected_resources = blast_radius.get(
    CHANGED_RESOURCE,
    []
)


# ============================================================
# 7. FIND CAUSAL PATHS
# ============================================================

causal_paths = find_minimal_paths(
    graph,
    CHANGED_RESOURCE,
    affected_resources
)


# ============================================================
# 8. PRINT RESULTS
# ============================================================

print()
print("=" * 70)
print("UNIFIED INFRASTRUCTURE DEPENDENCY GRAPH")
print("=" * 70)


print()
print("TERRAFORM DEPENDENCIES:")
print()

for source, target in terraform_edges:

    print(
        f"  {source} -> {target}"
    )


print()
print("APPLICATION DEPENDENCIES:")
print()

for source, target in application_edges:

    print(
        f"  {source} -> {target}"
    )


print()
print("RESOURCE → SERVICE MAPPINGS:")
print()

for source, target in mapping_edges:

    print(
        f"  {source} -> {target}"
    )


print()
print("=" * 70)
print("BLAST RADIUS")
print("=" * 70)

print()

if affected_resources:

    for resource in affected_resources:

        print(
            f"  → {resource}"
        )

else:

    print(
        "  No downstream dependencies found."
    )


print()
print("=" * 70)
print("MINIMAL CAUSAL PATHS")
print("=" * 70)

print()

for path in causal_paths:

    print(
        "  "
        + " -> ".join(path)
    )


print()
print("=" * 70)