# Tasks: Automated Code Review

- [x] Configuration Files
    - [x] Create `.pr_agent.toml` with default Gemini configuration
    - [x] Create `.env.example` with token templates
    - [x] Add `.env` to `.gitignore`

- [x] CLI Integration (Makefile)
    - [x] Add `install-review` target
    - [x] Add `review` target with MR_URL parameter and env loading
    - [x] Add `check-config` target for validation
    - [x] Add `help` target updates (if needed)

- [x] CI/CD Integration
    - [x] Add `code-review` stage to `.gitlab-ci.yml`
    - [x] Add `pr-agent-review` job definition

- [x] Documentation
    - [x] Update `README.md` with "AI Code Review" section
        - [x] Usage instructions (Local & CI)
        - [x] Configuration guide (Changing LLMs)
        - [x] Troubleshooting

- [x] Verification
    - [x] Verify `make check-config` passes
    - [x] Verify files exist and are correct
