# SPDX-License-Identifier: GPL-3.0-only
import os

import pytest

from tests.integration.utils import DEFAULT_INTEGRATION_TESTS_REPO

ENV_VAR_CLI_MAP = [
    ("HERMETO_TEST_INTEGRATION_TESTS_REPO", "--hermeto-integration-tests-repo"),
    ("HERMETO_TEST_IMAGE", "--hermeto-image"),
    ("HERMETO_TEST_LOCAL_PYPISERVER", "--hermeto-local-pypiserver"),
    ("HERMETO_TEST_PYPISERVER_PORT", "--hermeto-pypiserver-port"),
    ("HERMETO_TEST_LOCAL_DNF_SERVER", "--hermeto-local-dnf-server"),
    ("HERMETO_TEST_DNFSERVER_SSL_PORT", "--hermeto-dnfserver-ssl-port"),
    ("HERMETO_TEST_GENERATE_DATA", "--hermeto-generate-test-data"),
    ("HERMETO_TEST_CONTAINER_ENGINE", "--hermeto-container-engine"),
    ("HERMETO_TEST_LOCAL_NEXUS_PROXY", "--hermeto-local-nexus-proxy"),
    ("HERMETO_TEST_LOCAL_NEXUS_NO_CLEANUP", "--hermeto-local-nexus-no-cleanup"),
]


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register custom CLI options for Hermeto integration tests."""
    group = parser.getgroup("hermeto integration", "hermeto integration test options")
    group.addoption(
        "--hermeto-integration-tests-repo",
        action="store",
        default=os.getenv("HERMETO_TEST_INTEGRATION_TESTS_REPO", DEFAULT_INTEGRATION_TESTS_REPO),
        help="URL of the integration tests repository to clone (env: HERMETO_TEST_INTEGRATION_TESTS_REPO)",
    )
    group.addoption(
        "--hermeto-image",
        action="store",
        default=os.getenv("HERMETO_TEST_IMAGE", ""),
        help="Hermeto container image reference; build local image if not set (env: HERMETO_TEST_IMAGE)",
    )
    group.addoption(
        "--hermeto-local-pypiserver",
        action="store_true",
        default=os.getenv("HERMETO_TEST_LOCAL_PYPISERVER") == "1",
        help="Start local pypiserver for pip tests (env: HERMETO_TEST_LOCAL_PYPISERVER=1)",
    )
    group.addoption(
        "--hermeto-pypiserver-port",
        action="store",
        default=os.getenv("HERMETO_TEST_PYPISERVER_PORT", "8080"),
        help="Port for local pypiserver (env: HERMETO_TEST_PYPISERVER_PORT)",
    )
    group.addoption(
        "--hermeto-local-dnf-server",
        action="store_true",
        default=os.getenv("HERMETO_TEST_LOCAL_DNF_SERVER") == "1",
        help="Start local DNF server for RPM tests (env: HERMETO_TEST_LOCAL_DNF_SERVER=1)",
    )
    group.addoption(
        "--hermeto-dnfserver-ssl-port",
        action="store",
        default=os.getenv("HERMETO_TEST_DNFSERVER_SSL_PORT", "8443"),
        help="SSL port for local DNF server (env: HERMETO_TEST_DNFSERVER_SSL_PORT)",
    )
    group.addoption(
        "--hermeto-generate-test-data",
        action="store_true",
        default=os.getenv("HERMETO_TEST_GENERATE_DATA") == "1",
        help="Regenerate expected test data files (env: HERMETO_TEST_GENERATE_DATA=1)",
    )
    group.addoption(
        "--hermeto-container-engine",
        action="store",
        default=os.getenv("HERMETO_TEST_CONTAINER_ENGINE", "podman"),
        choices=("podman", "buildah"),
        help="Container engine: podman or buildah (env: HERMETO_TEST_CONTAINER_ENGINE)",
    )
    group.addoption(
        "--hermeto-local-nexus-proxy",
        action="store_true",
        default=os.getenv("HERMETO_TEST_LOCAL_NEXUS_PROXY") == "1",
        help="Enable local Nexus proxy for registry tests (env: HERMETO_TEST_LOCAL_NEXUS_PROXY=1)",
    )
    group.addoption(
        "--hermeto-local-nexus-no-cleanup",
        action="store_true",
        default=os.getenv("HERMETO_TEST_LOCAL_NEXUS_NO_CLEANUP") == "1",
        help="Keep Nexus container running after tests (env: HERMETO_TEST_LOCAL_NEXUS_NO_CLEANUP=1)",
    )


def pytest_report_header(config: pytest.Config) -> list[str]:
    """Report effective Hermeto test configuration at the top of the test session."""
    lines = ["Effective Hermeto test environment:"]
    for env_var, cli_opt in ENV_VAR_CLI_MAP:
        value = config.getoption(cli_opt)
        if isinstance(value, bool):
            value = "1" if value else "0"
        lines.append(f"  {env_var}={value}")
    return lines
