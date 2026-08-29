import json
import re

from typing import Any, Dict, List, Tuple


# ---------------------------------------------------------
# Terraform reference normalization
# ---------------------------------------------------------

def normalize_reference(reference: str) -> str:
    """
    Convert a Terraform expression reference into a resource
    address.

    Example:

        aws_iam_role.reporting.name

    becomes:

        aws_iam_role.reporting

    This lets different attribute references point to the
    same Terraform resource node.
    """

    # Remove module prefix for now only when it is not needed.
    # We keep the actual resource address intact otherwise.

    match = re.match(
        r"((?:module\.[A-Za-z0-9_-]+\.)*"
        r"[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)",
        reference
    )

    if match:
        return match.group(1)

    return reference


# ---------------------------------------------------------
# Recursive expression reference extraction
# ---------------------------------------------------------

def collect_references(
    value: Any
) -> List[str]:
    """
    Recursively search a Terraform configuration expression
    for reference information.
    """

    references = []

    if isinstance(value, dict):

        # Terraform expression objects can contain:
        #
        # {
        #     "references": [
        #         "aws_iam_role.example.name"
        #     ]
        # }

        if "references" in value:

            raw_references = value["references"]

            if isinstance(raw_references, list):

                for reference in raw_references:

                    if isinstance(reference, str):

                        references.append(
                            reference
                        )

        # Continue searching nested objects.
        for child in value.values():

            references.extend(
                collect_references(child)
            )

    elif isinstance(value, list):

        for child in value:

            references.extend(
                collect_references(child)
            )

    return references


# ---------------------------------------------------------
# Terraform dependency extraction
# ---------------------------------------------------------

def extract_terraform_references(
    plan: Dict[str, Any]
) -> List[Tuple[str, str]]:
    """
    Extract resource-to-resource relationships from the
    Terraform JSON plan.

    Returns:

        [
            (
                "aws_iam_role.reporting",
                "aws_instance.api"
            )
        ]

    Meaning:

        aws_instance.api depends on aws_iam_role.reporting
    """

    edges = []

    configuration = plan.get(
        "configuration",
        {}
    )

    root_module = configuration.get(
        "root_module",
        {}
    )

    resources = root_module.get(
        "resources",
        []
    )

    for resource in resources:

        target_resource = resource.get(
            "address"
        )

        if not target_resource:
            continue

        # -------------------------------------------------
        # 1. Find references inside expressions
        # -------------------------------------------------

        expressions = resource.get(
            "expressions",
            {}
        )

        references = collect_references(
            expressions
        )

        for reference in references:

            source_resource = normalize_reference(
                reference
            )

            # Avoid self-dependencies.
            if source_resource == target_resource:
                continue

            edges.append(
                (
                    source_resource,
                    target_resource
                )
            )

        # -------------------------------------------------
        # 2. Explicit depends_on relationships
        # -------------------------------------------------

        depends_on = resource.get(
            "depends_on",
            []
        )

        if isinstance(depends_on, list):

            for dependency in depends_on:

                if not isinstance(
                    dependency,
                    str
                ):
                    continue

                source_resource = normalize_reference(
                    dependency
                )

                if source_resource == target_resource:
                    continue

                edges.append(
                    (
                        source_resource,
                        target_resource
                    )
                )

    # -----------------------------------------------------
    # Remove duplicate edges
    # -----------------------------------------------------

    return sorted(
        set(edges)
    )


# ---------------------------------------------------------
# Application dependency loading
# ---------------------------------------------------------

def load_application_dependencies(
    file_path: str
) -> List[Dict[str, str]]:
    """
    Load application-level dependency relationships.
    """

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return data.get(
        "dependencies",
        []
    )


# ---------------------------------------------------------
# Application dependency → graph edges
# ---------------------------------------------------------

def convert_dependencies_to_edges(
    dependencies: List[Dict[str, str]]
) -> List[Tuple[str, str]]:

    edges = []

    for dependency in dependencies:

        source = dependency.get(
            "source"
        )

        target = dependency.get(
            "target"
        )

        if not source or not target:
            continue

        edges.append(
            (
                source,
                target
            )
        )

    return edges