# Dependency Management with Poetry

- Define all dependencies and dev-dependencies in `pyproject.toml`.  
- Use `poetry.lock` to lock versions and ensure reproducible builds.  
- Install with `poetry install --sync`.  
- Cache virtual env and poetry caches in CI.  
- Regularly update and test dependencies.