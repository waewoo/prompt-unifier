# Project Structure and Organization

## Directory Layout
```bash
project-root/
├── src/ # Source code
│ └── your_package/
├── tests/ # Tests, mirrors src structure
├── docs/ # Documentation
├── scripts/ # Helper scripts
├── dist/ # Build artifacts
├── .venv/ # Virtual environment
├── Makefile # Dev and build tasks
├── pyproject.toml # Poetry config
├── poetry.lock # Locked dependencies
├── README.md # Project overview
└── .gitignore # Ignored files
```

## Naming Conventions
- Source files and modules: snake_case  
- Classes: PascalCase  
- Functions and variables: snake_case  
- Test files: start with `test_`

## Notes
- Keep tests isolated from source.  
- Use relative imports inside package.  
- Document directories with README if complex.