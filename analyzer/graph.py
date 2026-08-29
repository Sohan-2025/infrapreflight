import networkx as nx
from typing import List, Dict, Tuple


def build_dependency_graph(
    dependencies: List[Tuple[str, str]]
) -> nx.DiGraph:
    """
    Build a directed dependency graph.

    Each tuple is:

        (source, target)

    Meaning:

        source -> target

    Example:

        aws_iam_policy.reporting
            ->
        reporting-api
    """

    graph = nx.DiGraph()

    for source, target in dependencies:

        graph.add_edge(
            source,
            target
        )

    return graph


def find_blast_radius(
    graph: nx.DiGraph,
    changed_resources: List[str]
) -> Dict[str, List[str]]:
    """
    Find all downstream nodes affected by each
    changed resource.
    """

    blast_radius = {}

    for resource in changed_resources:

        if resource not in graph:

            blast_radius[resource] = []

            continue

        affected_nodes = nx.descendants(
            graph,
            resource
        )

        blast_radius[resource] = sorted(
            affected_nodes
        )

    return blast_radius


def find_minimal_paths(
    graph: nx.DiGraph,
    source: str,
    targets: List[str]
) -> List[List[str]]:
    """
    Find the shortest dependency path from a changed
    resource to each affected target.
    """

    paths = []

    for target in targets:

        try:

            path = nx.shortest_path(
                graph,
                source,
                target
            )

            paths.append(path)

        except nx.NetworkXNoPath:

            continue

    return paths