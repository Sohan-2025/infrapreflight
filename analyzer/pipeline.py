import json
from pathlib import Path

from analyzer.risk import analyze


def load_plan(path="dependency.json"):
    """Load Terraform show -json output."""

    plan_path = Path(path)

    if not plan_path.exists():
        raise FileNotFoundError(
            f"Terraform plan JSON not found: {plan_path}"
        )

    with plan_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_changed_resources(plan):
    """Extract resources that Terraform plans to change."""

    changes = []

    for resource in plan.get("resource_changes", []):
        change = resource.get("change", {})
        actions = change.get("actions", [])

        if actions and actions != ["no-op"]:
            address = resource.get("address")

            if address:
                changes.append(
                    {
                        "address": address,
                        "actions": actions,
                    }
                )

    return changes


def get_dependency_edges(plan):
    """
    Extract Terraform dependency relationships.

    Supports:
    1. Explicit depends_on relationships
    2. Implicit Terraform expression references

    Relationships are normalized as:

        dependency -> dependent resource
    """

    edges = []

    # ---------------------------------------------------------
    # Collect all known resource addresses
    # ---------------------------------------------------------

    known_resources = set()

    configuration = plan.get("configuration", {})
    root_module = configuration.get("root_module", {})

    def collect_resources(module):
        for resource in module.get("resources", []):
            address = resource.get("address")

            if address:
                known_resources.add(address)

        for child_module in module.get("child_modules", []):
            collect_resources(child_module)

    if root_module:
        collect_resources(root_module)

    for resource in plan.get("resource_changes", []):
        address = resource.get("address")

        if address:
            known_resources.add(address)

    # ---------------------------------------------------------
    # Helper to add a dependency edge
    # ---------------------------------------------------------

    def add_edge(source, target):
        if source and target and source != target:
            edge = {
                "source": source,
                "target": target,
            }

            if edge not in edges:
                edges.append(edge)

    # ---------------------------------------------------------
    # Extract explicit depends_on relationships
    # ---------------------------------------------------------

    def process_explicit_dependencies(module):
        for resource in module.get("resources", []):
            address = resource.get("address")

            for dependency in resource.get("depends_on", []):
                add_edge(dependency, address)

        for child_module in module.get("child_modules", []):
            process_explicit_dependencies(child_module)

    if root_module:
        process_explicit_dependencies(root_module)

    # ---------------------------------------------------------
    # Extract implicit expression references
    # ---------------------------------------------------------

    def find_references(value):
        references = []

        if isinstance(value, dict):
            for key, item in value.items():
                if key == "references" and isinstance(item, list):
                    references.extend(item)
                else:
                    references.extend(find_references(item))

        elif isinstance(value, list):
            for item in value:
                references.extend(find_references(item))

        return references

    def process_implicit_dependencies(module):
        for resource in module.get("resources", []):
            address = resource.get("address")
            expressions = resource.get("expressions", {})

            references = find_references(expressions)

            for reference in references:
                # Match the longest known resource address.
                # Example:
                # local_file.config.content
                # becomes:
                # local_file.config
                matches = [
                    resource_address
                    for resource_address in known_resources
                    if reference == resource_address
                    or reference.startswith(resource_address + ".")
                ]

                if matches:
                    dependency = max(matches, key=len)
                    add_edge(dependency, address)

        for child_module in module.get("child_modules", []):
            process_implicit_dependencies(child_module)

    if root_module:
        process_implicit_dependencies(root_module)

    # ---------------------------------------------------------
    # Also support simplified test fixtures
    # ---------------------------------------------------------

    for resource in plan.get("resource_changes", []):
        address = resource.get("address")

        for dependency in resource.get("depends_on", []):
            add_edge(dependency, address)

    return edges


def build_graph(edges):
    """Build a forward dependency graph."""

    graph = {}

    for edge in edges:
        source = edge["source"]
        target = edge["target"]

        graph.setdefault(source, [])
        graph[source].append(target)

    return graph


def calculate_blast_radius(changed_resources, edges):
    """
    Calculate resources reachable from changed resources.
    """

    graph = build_graph(edges)

    changed = {
        resource["address"]
        for resource in changed_resources
    }

    visited = set()
    queue = list(changed)

    while queue:
        current = queue.pop(0)

        if current in visited:
            continue

        visited.add(current)

        for dependency in graph.get(current, []):
            if dependency not in visited:
                queue.append(dependency)

    return sorted(visited - changed)


def determine_severity(changed_resources, blast_radius):
    """Assign a simple severity based on change characteristics."""

    replace_count = sum(
        1
        for resource in changed_resources
        if "delete" in resource["actions"]
        and "create" in resource["actions"]
    )

    if replace_count > 0:
        return "CRITICAL"

    if len(blast_radius) >= 3:
        return "HIGH"

    if len(changed_resources) >= 3:
        return "HIGH"

    if len(changed_resources) >= 1:
        return "MEDIUM"

    return "LOW"


def build_report(
    changed_resources,
    dependency_edges,
    blast_radius,
    risk_result,
):
    return {
        "summary": {
            "changed_resource_count": len(changed_resources),
            "dependency_count": len(dependency_edges),
            "blast_radius_count": len(blast_radius),
        },
        "changed_resources": changed_resources,
        "dependencies": dependency_edges,
        "blast_radius": blast_radius,
        "risk": risk_result,
    }


def run_pipeline(plan_path="dependency.json"):
    plan = load_plan(plan_path)

    changed_resources = get_changed_resources(plan)

    dependency_edges = get_dependency_edges(plan)

    blast_radius = calculate_blast_radius(
        changed_resources,
        dependency_edges,
    )

    severity = determine_severity(
        changed_resources,
        blast_radius,
    )

    risk_result = analyze(
        severity=severity,
        blast_radius_count=len(blast_radius),
        dependency_count=len(dependency_edges),
        synthetic_failures=0,
        synthetic_total=0,
    )

    return build_report(
        changed_resources,
        dependency_edges,
        blast_radius,
        risk_result,
    )


if __name__ == "__main__":
    report = run_pipeline()

    print(
        json.dumps(
            report,
            indent=2,
        )
    )