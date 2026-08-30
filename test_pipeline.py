from analyzer.pipeline import (
    get_changed_resources,
    get_dependency_edges,
    calculate_blast_radius,
    determine_severity,
)


def sample_plan():
    return {
        "resource_changes": [
            {
                "address": "local_file.config",
                "change": {
                    "actions": ["update"],
                },
                "depends_on": [],
            },
            {
                "address": "local_file.application",
                "change": {
                    "actions": ["create"],
                },
                "depends_on": [
                    "local_file.config",
                ],
            },
            {
                "address": "local_file.backup",
                "change": {
                    "actions": ["create"],
                },
                "depends_on": [
                    "local_file.application",
                ],
            },
        ]
    }


def test_changed_resources():
    plan = sample_plan()

    changes = get_changed_resources(plan)

    assert len(changes) == 3
    assert changes[0]["address"] == "local_file.config"


def test_dependencies():
    plan = sample_plan()

    edges = get_dependency_edges(plan)

    assert len(edges) == 2

    assert {
        "source": "local_file.config",
        "target": "local_file.application",
    } in edges


def test_blast_radius():
    plan = sample_plan()

    changes = get_changed_resources(plan)
    edges = get_dependency_edges(plan)

    blast = calculate_blast_radius(
        changes,
        edges,
    )

    assert isinstance(blast, list)


def test_severity():
    severity = determine_severity(
        [
            {
                "address": "local_file.config",
                "actions": ["update"],
            }
        ],
        [
            "local_file.application",
            "local_file.backup",
            "local_file.database",
        ],
    )

    assert severity == "HIGH"


if __name__ == "__main__":
    test_changed_resources()
    test_dependencies()
    test_blast_radius()
    test_severity()

    print("All Stage 8 tests passed.")