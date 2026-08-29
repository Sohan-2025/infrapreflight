from analyzer.dependencies import (
    load_application_dependencies,
    convert_dependencies_to_edges
)


dependencies = load_application_dependencies(
    "config/app_dependencies.json"
)


edges = convert_dependencies_to_edges(
    dependencies
)


print("APPLICATION DEPENDENCIES")
print()

for source, target in edges:

    print(
        f"{source} -> {target}"
    )