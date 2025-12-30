# Functional Testing

Prompt Unifier goes beyond static validation by allowing you to **execute** your prompts with real
AI models and verify their output against expected criteria. This ensures your prompts actually
perform as intended before you deploy them.

## Why Functional Testing?

- **Regression Testing**: Ensure changes to a prompt don't break its core functionality.
- **Model Compatibility**: Verify that a prompt works correctly across different models (e.g., GPT-4
  vs Claude 3).
- **Quality Assurance**: Enforce specific constraints on the output (e.g., "must not contain TODOs",
  "must be valid JSON").

## Getting Started

### 1. Configure API Keys

Create a `.env` file in your project root (or ensure environment variables are set):

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-your-key...

# Mistral
MISTRAL_API_KEY=your-key...

# Optional: Default model (defaults to gpt-4o-mini)
DEFAULT_LLM_MODEL=gpt-4o
```

## Creating Tests

Tests are defined in `.test.yaml` files that sit alongside your prompt files. For a prompt named
`my-prompt.md`, create `my-prompt.md.test.yaml`.

### Test File Structure

```yaml
# Optional: Run scenarios multiple times (useful for checking stability)
iterations: 1

scenarios:
  - description: "Test code generation"
    input: "Write a Python function to add two numbers"

    # List of assertions to validate the AI's response
    expect:
      - type: contains
        value: "def add"
        error: "Function name should be 'add'"

      - type: regex
        value: "return\\s+a\\s*\\+\\s*b"

      - type: not-contains
        value: "TODO"
        case_sensitive: false
```

## Supported Assertions

| Type           | Description                                              | Parameters                                            |
| :------------- | :------------------------------------------------------- | :---------------------------------------------------- |
| `contains`     | Checks if the output contains a specific string.         | `value` (str), `case_sensitive` (bool, default: true) |
| `not-contains` | Checks if the output does NOT contain a specific string. | `value` (str), `case_sensitive` (bool, default: true) |
| `regex`        | Checks if the output matches a regular expression.       | `value` (str - regex pattern)                         |
| `max-length`   | Checks if the output length is below a limit.            | `value` (int - max characters)                        |

## Running Tests

Use the `test` command to execute your functional tests.

### Run tests for a specific prompt

```bash
prompt-unifier test prompts/my-prompt.md
```

### Run tests with verbose output

Use `-v` to see detailed execution logs, including the raw prompt sent to the AI and the full
response.

```bash
prompt-unifier -v test prompts/my-prompt.md
```

## Supported Providers

Prompt Unifier supports any provider compatible with
[LiteLLM](https://docs.litellm.ai/docs/providers):

- **OpenAI**: `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo`
- **Anthropic**: `claude-3-5-sonnet-20241022`, `claude-3-opus-20240229`
- **Mistral**: `mistral/mistral-large-latest`, `mistral/codestral-latest`
- **Ollama**: `ollama/llama2`, `ollama/mistral` (requires local Ollama server)
- **Azure**, **Bedrock**, **Vertex AI**, and many more.

### Local Testing with Ollama

You can test prompts locally without API costs using Ollama.

1. **Install Ollama**: Download from [ollama.com](https://ollama.com).
1. **Start the server**: Ensure Ollama is running.
   ```bash
   ollama serve
   ```
1. **Pull a model**: Download the model you want to test with (e.g., llama3).
   ```bash
   ollama pull llama3
   ```
1. **Configure Provider**: Set the provider in your `.test.yaml` file.
   ```yaml
   provider: ollama/llama3
   ```

> **Tip:** Local models might be slower than cloud APIs. If you encounter timeouts, increase the
> `LITELLM_TIMEOUT` in your `.env` file (default is 60s).
>
> ```bash
> LITELLM_TIMEOUT=300
> ```
