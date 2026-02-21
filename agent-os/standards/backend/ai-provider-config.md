# AI Provider Configuration

Functional tests run prompts against real AI providers via LiteLLM.

## Provider Resolution Order

1. CLI `--provider` flag
2. `ai_provider` field in `.prompt-unifier/config.yaml`
3. `DEFAULT_LLM_MODEL` environment variable
4. Default: `gpt-4o-mini`

## Provider String Format

```
openai:    "gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"
anthropic: "claude-3-5-sonnet", "claude-3-opus", "claude-3-haiku"
mistral:   "mistral/mistral-large", "mistral/codestral-latest"
ollama:    "ollama/llama2", "ollama/devstral", "ollama/mistral"
```

Non-OpenAI providers use `"provider/model"` format.

## Environment Variables (.env — never in config.yaml)

```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
MISTRAL_API_KEY=...
DEFAULT_LLM_MODEL=gpt-4o-mini   # fallback model
LITELLM_TIMEOUT=60              # request timeout in seconds
```

API keys must **only** live in `.env` (gitignored). Never commit them to `config.yaml`.

## Error Handling

All AI execution errors are wrapped in `AIExecutionError`:

```python
from prompt_unifier.ai.executor import AIExecutor, AIExecutionError

try:
    executor.execute_prompt(system_prompt, user_input, provider)
except AIExecutionError as e:
    # e.__cause__ holds the original exception
```

## Local Testing with Ollama

```bash
ollama serve           # start Ollama daemon
ollama pull devstral   # pull model
# then use provider: "ollama/devstral" — no API key needed
```
