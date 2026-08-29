from analyzer.synthetic import (
    test_file_exists,
    test_configuration,
    run_synthetic_tests,
)


def test_existing_file():

    result = test_file_exists("hello.txt")

    assert result.status == "PASS"


def test_missing_file():

    result = test_file_exists(
        "this_file_should_not_exist.txt"
    )

    assert result.status == "FAIL"


def test_configuration_pass():

    result = test_configuration(
        "environment",
        "production",
        {
            "environment": "production"
        },
    )

    assert result.status == "PASS"


def test_configuration_fail():

    result = test_configuration(
        "environment",
        "production",
        {
            "environment": "development"
        },
    )

    assert result.status == "FAIL"


def test_synthetic_runner():

    report = run_synthetic_tests(
        configuration={
            "expected_values": {
                "environment": "production"
            },
            "values": {
                "environment": "production"
            },
        },
        file_paths=[
            "hello.txt"
        ],
    )

    assert report["total_tests"] == 2
    assert report["passed"] == 2
    assert report["failed"] == 0
    assert report["pass_rate"] == 100


if __name__ == "__main__":

    test_existing_file()
    test_missing_file()
    test_configuration_pass()
    test_configuration_fail()
    test_synthetic_runner()

    print("All Stage 6 tests passed.")