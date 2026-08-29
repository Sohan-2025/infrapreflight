from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List
import os
import socket
import urllib.request


@dataclass
class SyntheticTestResult:
    test_name: str
    test_type: str
    status: str
    message: str
    target: str = ""


def test_file_exists(path: str) -> SyntheticTestResult:
    """
    Configuration/deployment sanity check.
    """

    exists = os.path.exists(path)

    if exists:
        return SyntheticTestResult(
            test_name="file_exists",
            test_type="configuration",
            status="PASS",
            message=f"File exists: {path}",
            target=path,
        )

    return SyntheticTestResult(
        test_name="file_exists",
        test_type="configuration",
        status="FAIL",
        message=f"File does not exist: {path}",
        target=path,
    )


def test_tcp_connectivity(
    host: str,
    port: int,
    timeout: float = 2.0,
) -> SyntheticTestResult:
    """
    Test whether a TCP endpoint is reachable.
    """

    try:
        with socket.create_connection(
            (host, port),
            timeout=timeout,
        ):
            return SyntheticTestResult(
                test_name="tcp_connectivity",
                test_type="connectivity",
                status="PASS",
                message=f"TCP connection succeeded: {host}:{port}",
                target=f"{host}:{port}",
            )

    except OSError as exc:
        return SyntheticTestResult(
            test_name="tcp_connectivity",
            test_type="connectivity",
            status="FAIL",
            message=f"TCP connection failed: {host}:{port} ({exc})",
            target=f"{host}:{port}",
        )


def test_http_endpoint(
    url: str,
    timeout: float = 3.0,
) -> SyntheticTestResult:
    """
    Test HTTP/API service reachability.
    """

    try:
        with urllib.request.urlopen(
            url,
            timeout=timeout,
        ) as response:

            status_code = response.status

            if 200 <= status_code < 400:
                return SyntheticTestResult(
                    test_name="http_endpoint",
                    test_type="service_reachability",
                    status="PASS",
                    message=f"HTTP endpoint returned {status_code}",
                    target=url,
                )

            return SyntheticTestResult(
                test_name="http_endpoint",
                test_type="service_reachability",
                status="FAIL",
                message=f"HTTP endpoint returned {status_code}",
                target=url,
            )

    except Exception as exc:
        return SyntheticTestResult(
            test_name="http_endpoint",
            test_type="service_reachability",
            status="FAIL",
            message=f"HTTP request failed: {exc}",
            target=url,
        )


def test_configuration(
    key: str,
    expected_value: str,
    configuration: Dict[str, str],
) -> SyntheticTestResult:
    """
    Validate a configuration value that may affect runtime behavior.
    """

    actual_value = configuration.get(key)

    if actual_value == expected_value:
        return SyntheticTestResult(
            test_name="configuration_check",
            test_type="configuration",
            status="PASS",
            message=f"Configuration {key} has expected value.",
            target=key,
        )

    return SyntheticTestResult(
        test_name="configuration_check",
        test_type="configuration",
        status="FAIL",
        message=(
            f"Configuration mismatch for {key}: "
            f"expected={expected_value!r}, "
            f"actual={actual_value!r}"
        ),
        target=key,
    )


def run_synthetic_tests(
    configuration: Dict[str, str],
    file_paths: List[str] | None = None,
    tcp_targets: List[tuple[str, int]] | None = None,
    http_targets: List[str] | None = None,
) -> Dict:

    file_paths = file_paths or []
    tcp_targets = tcp_targets or []
    http_targets = http_targets or []

    results: List[SyntheticTestResult] = []

    # Configuration tests
    for key, expected_value in configuration.get(
        "expected_values",
        {}
    ).items():

        actual_configuration = configuration.get(
            "values",
            {}
        )

        results.append(
            test_configuration(
                key,
                expected_value,
                actual_configuration,
            )
        )

    # File/configuration tests
    for path in file_paths:
        results.append(
            test_file_exists(path)
        )

    # Connectivity tests
    for host, port in tcp_targets:
        results.append(
            test_tcp_connectivity(
                host,
                port,
            )
        )

    # HTTP/API tests
    for url in http_targets:
        results.append(
            test_http_endpoint(
                url,
            )
        )

    passed = sum(
        result.status == "PASS"
        for result in results
    )

    failed = sum(
        result.status == "FAIL"
        for result in results
    )

    total = len(results)

    if total == 0:
        pass_rate = 0
    else:
        pass_rate = round(
            (passed / total) * 100
        )

    return {
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "results": [
            asdict(result)
            for result in results
        ],
    }


def print_synthetic_results(report: Dict) -> None:

    print("=" * 70)
    print("SYNTHETIC TEST RESULTS")
    print("=" * 70)

    print(f"\nTotal tests : {report['total_tests']}")
    print(f"Passed      : {report['passed']}")
    print(f"Failed      : {report['failed']}")
    print(f"Pass rate   : {report['pass_rate']}%")

    print("\nTEST DETAILS:")

    for result in report["results"]:

        symbol = (
            "+"
            if result["status"] == "PASS"
            else "!"
        )

        print(
            f"  {symbol} "
            f"{result['test_name']} "
            f"-> {result['status']}"
        )

        print(
            f"      {result['message']}"
        )

    print("\n" + "=" * 70)