import json

from analyzer.parser import (
    load_plan,
    extract_changed_resources
)

from analyzer.severity import (
    calculate_severity
)


def main():

    # -----------------------------------------------------
    # 1. Load Terraform plan
    # -----------------------------------------------------

    plan = load_plan(
        "tfplan.json"
    )

    # -----------------------------------------------------
    # 2. Extract resource changes
    # -----------------------------------------------------

    resources = extract_changed_resources(
        plan
    )

    # -----------------------------------------------------
    # 3. Calculate risk for each resource
    # -----------------------------------------------------

    for resource in resources:

        severity = calculate_severity(
            resource["type"],
            resource["action"],
            resource["changed_attributes"]
        )

        resource["severity"] = severity

    # -----------------------------------------------------
    # 4. Print final structured result
    # -----------------------------------------------------

    print(
        json.dumps(
            resources,
            indent=2
        )
    )


if __name__ == "__main__":
    main()