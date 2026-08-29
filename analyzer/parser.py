import json
from typing import Any, Dict, List


# Terraform/provider-generated attributes.
# These often appear as changed during replacement
# but are not meaningful user-level changes.
IGNORED_ATTRIBUTES = {
    "id",
    "content_md5",
    "content_sha1",
    "content_sha256",
    "content_sha512",
    "content_base64sha256",
    "content_base64sha512",
}


def load_plan(plan_path: str) -> Dict[str, Any]:
    """
    Load Terraform JSON plan.
    """

    with open(plan_path, "r", encoding="utf-8-sig") as file:
        return json.load(file)


def determine_action(actions: List[str]) -> str:
    """
    Convert Terraform's action list into a readable action.
    """

    if actions == ["create"]:
        return "CREATE"

    if actions == ["delete"]:
        return "DELETE"

    if actions == ["update"]:
        return "UPDATE"

    if set(actions) == {"delete", "create"}:
        return "REPLACE"

    return "UNKNOWN"


def find_changed_attributes(
    before: Dict[str, Any],
    after: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Find attributes whose values changed.

    This first version handles the common Terraform case
    where resource attributes are simple key/value pairs.
    """

    changes = []

    all_keys = set(before.keys()) | set(after.keys())

    for key in sorted(all_keys):

        # Ignore Terraform/provider-generated values.
        if key in IGNORED_ATTRIBUTES:
            continue

        before_value = before.get(key)
        after_value = after.get(key)

        if before_value != after_value:

            changes.append({
                "attribute": key,
                "before": before_value,
                "after": after_value
            })

    return changes


def extract_changed_resources(
    plan: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Extract all resources that Terraform says are changing.
    """

    changed_resources = []

    for resource in plan.get("resource_changes", []):

        address = resource.get("address")

        resource_type = resource.get("type")

        change = resource.get("change", {})

        actions = change.get("actions", [])

        before = change.get("before") or {}

        after = change.get("after") or {}

        action = determine_action(actions)

        changed_attributes = find_changed_attributes(
            before,
            after
        )

        changed_resources.append({
            "address": address,
            "type": resource_type,
            "action": action,
            "changed_attributes": changed_attributes
        })

    return changed_resources