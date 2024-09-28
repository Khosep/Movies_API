# specify which test fixtures should be automatically imported and used by pytest when running tests
# https://docs.pytest.org/en/7.1.x/how-to/writing_plugins.html#requiring-loading-plugins-in-a-test-module-or-conftest-file
pytest_plugins = [
    'functional.fixtures.base_fixt',
    'functional.fixtures.elastic_fixt',
    'functional.fixtures.redis_fixt',
]
