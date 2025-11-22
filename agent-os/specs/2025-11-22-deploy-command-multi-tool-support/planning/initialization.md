# Raw Idea

Complete the Deploy Command with Multi-Tool Support (Roadmap Step 8) by adding the missing functionality:
- Add --dry-run option to preview deployments without executing them
- Call verify_deployment() automatically after each successful deploy
- Extend rollback() to handle files in subdirectories (not just root level)
- These improvements complete the deploy command before adding other tool handlers
