import json

from analyzer.dependencies import (
    extract_terraform_references
)


# ---------------------------------------------------------
# Load the COMPLETE Terraform JSON plan
# ---------------------------------------------------------

with open(
    "dependency.json",
    "r",
    encoding="utf-8"
) as file:

    plan = json.load(file)


# ---------------------------------------------------------
# Debug: verify that configuration exists
# ---------------------------------------------------------

print()
print("=" * 70)
print("TERRAFORM DEPENDENCY ANALYSIS")
print("=" * 70)

print()

print(
    "Top-level plan sections:"
)

for key in plan.keys():

    print(
        f"  - {key}"
    )

print()


# ---------------------------------------------------------
# Extract Terraform dependencies
# ---------------------------------------------------------

edges = extract_terraform_references(
    plan
)


# ---------------------------------------------------------
# Display result
# ---------------------------------------------------------

print()

if not edges:

    print(
        "No Terraform resource-to-resource dependencies were found."
    )

else:

    print(
        "DISCOVERED TERRAFORM DEPENDENCIES:"
    )

    print()

    for source, target in edges:

        print(
            f"  {source} -> {target}"
        )


print()
print("=" * 70)