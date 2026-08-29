import json

with open("tfplan.json", "r", encoding="utf-8-sig") as f:
    plan = json.load(f)

for resource in plan["resource_changes"]:

    address = resource["address"]
    resource_type = resource["type"]
    change = resource["change"]

    actions = change["actions"]
    before = change.get("before") or {}
    after = change.get("after") or {}

    # Determine overall action
    if actions == ["create"]:
        action = "CREATE"
    elif actions == ["delete"]:
        action = "DELETE"
    elif actions == ["update"]:
        action = "UPDATE"
    elif set(actions) == {"delete", "create"}:
        action = "REPLACE"
    else:
        action = "UNKNOWN"

    print("=" * 60)
    print("INFRASTRUCTURE CHANGE")
    print("=" * 60)

    print(f"Resource : {address}")
    print(f"Type     : {resource_type}")
    print(f"Action   : {action}")
    print()

    # Find attributes whose values changed
    changed_attributes = []

    all_keys = set(before.keys()) | set(after.keys())

    for key in all_keys:
        if before.get(key) != after.get(key):
            changed_attributes.append(key)

    if changed_attributes:
        print("CHANGED ATTRIBUTES:")
        print()

        for key in sorted(changed_attributes):
            print(f"  {key}")
            print(f"    BEFORE: {before.get(key)}")
            print(f"    AFTER : {after.get(key)}")
            print()

    print("=" * 60)