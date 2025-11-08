# Build System and Packaging

## Makefile Targets
- `install`: install dependencies via Poetry sync  
- `lint`: lint Python code with ruff  
- `format`: format code  
- `type`: type check using mypy strict mode  
- `markdownlint`: lint Markdown docs  
- `test`: run pytest with coverage  
- `test-html`: generate html coverage report  
- `cov-xml`: generate XML coverage for CI  
- `build`: build wheel and sdist in `dist/`  
- `publish`: publish to PyPI (requires `PYPI_TOKEN`)  
- `clean`: remove artifacts and caches  
- `help`: list make targets with descriptions

## Packaging
- Use Poetry `pyproject.toml` for metadata and config.  
- Validate metadata before build.  
- Fail build on errors.

## Scenarios
- Build succeeds with valid metadata producing .whl and .tar.gz.  
- Build fails gracefully if invalid.
