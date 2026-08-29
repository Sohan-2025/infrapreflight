from analyzer.synthetic import (
    run_synthetic_tests,
    print_synthetic_results,
)


report = run_synthetic_tests(

    configuration={
        "expected_values": {
            "environment": "production",
            "database": "reporting-db",
        },

        "values": {
            "environment": "production",
            "database": "reporting-db",
        },
    },

    file_paths=[
        "hello.txt",
        "application.txt",
    ],
)


print_synthetic_results(report)