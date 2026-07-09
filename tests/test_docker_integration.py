"""Integration tests for Docker deployment configuration.

These tests do NOT require a running Docker daemon; they validate that the
compose file references build contexts and Dockerfiles that actually exist,
catching the most common "docker compose up" breakages before CI build.
"""

import os

import pytest
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(__file__))
COMPOSE_PATH = os.path.join(REPO_ROOT, "docker-compose.yml")


def _load_compose():
    with open(COMPOSE_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@pytest.fixture(scope="module")
def compose():
    return _load_compose()


def test_compose_file_present():
    assert os.path.isfile(COMPOSE_PATH), "docker-compose.yml missing at repo root"


def test_all_build_contexts_and_dockerfiles_exist(compose):
    services = compose.get("services", {})
    assert services, "No services defined in docker-compose.yml"

    for name, svc in services.items():
        build = svc.get("build")
        if not build:
            # image-only service (e.g. postgres) -> nothing to build
            assert "image" in svc, f"service '{name}' has neither build nor image"
            continue

        context = build.get("context", ".")
        dockerfile = build.get("dockerfile", "Dockerfile")
        ctx_path = os.path.join(REPO_ROOT, context)
        df_path = os.path.join(ctx_path, dockerfile)

        assert os.path.isdir(ctx_path), f"service '{name}': build context does not exist: {context}"
        assert os.path.isfile(df_path), (
            f"service '{name}': dockerfile does not exist: {dockerfile} (context={context})"
        )


def test_expected_core_services_present(compose):
    services = set(compose.get("services", {}).keys())
    required = {"postgres", "alembic-migrate", "ai-service", "saas-api", "marketplace-api"}
    missing = required - services
    assert not missing, f"Missing required services: {sorted(missing)}"


def test_alembic_migration_depends_on_healthy_postgres(compose):
    alembic = compose["services"]["alembic-migrate"]
    depends = alembic.get("depends_on", {})
    pg = depends.get("postgres", {})
    assert pg.get("condition") == "service_healthy", (
        "alembic-migrate must wait for postgres to be healthy before migrating"
    )
