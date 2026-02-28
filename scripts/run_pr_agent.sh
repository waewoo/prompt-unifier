#!/usr/bin/env bash

# Internal helper for pr-agent commands

set -e

CMD=$1
MR_URL=$2
PYTHON_VERSION=${3:-3.13}

if [ -z "$MR_URL" ] || [ -z "$CMD" ]; then
    echo "❌ Usage: $0 <cmd> <mr_url> [python_version]"
    echo "   Example: $0 review https://gitlab.com/.../merge_requests/123 3.13"
    exit 1
fi

echo "🔍 Checking configuration..."
if [ -f .env ]; then
    echo "   Loading .env file..."
    set -a
    . .env
    set +a
else
    echo "   Using environment variables (CI mode)..."
fi

if [ -z "${GITLAB_TOKEN:-}" ]; then
    echo "❌ Error: GITLAB_TOKEN not set"
    exit 1
fi

if [ -z "${PR_AGENT_MODEL:-}" ]; then
    echo "❌ Error: PR_AGENT_MODEL not set in .env"
    echo "   Example: PR_AGENT_MODEL=mistral/devstral-latest"
    exit 1
fi

GITHUB_PLACEHOLDER="PLACEHOLDER_NotARealToken_DoNotReplace"
if [ "$GITHUB_PLACEHOLDER" != "PLACEHOLDER_NotARealToken_DoNotReplace" ]; then
    echo "❌ SECURITY ERROR: GitHub placeholder token was modified!"
    echo "   This placeholder is required due to a pr-agent initialization bug"
    echo "   and must not be replaced with a real token (we use GitLab, not GitHub)."
    exit 1
fi

echo "🤖 Running pr-agent ${CMD}..."
echo "   Provider: ${PR_AGENT_GIT_PROVIDER:-gitlab} | Model: ${PR_AGENT_MODEL}"
echo "   MR: ${MR_URL}"

export MISTRAL_API_KEY="$MISTRAL_API_KEY"
export GITLAB__PERSONAL_ACCESS_TOKEN="$GITLAB_TOKEN"
export CONFIG__GIT_PROVIDER="${PR_AGENT_GIT_PROVIDER:-gitlab}"
export CONFIG__MODEL="$PR_AGENT_MODEL"
export CONFIG__CUSTOM_MODEL_MAX_TOKENS="${PR_AGENT_MAX_TOKENS:-256000}"
export CONFIG__FALLBACK_MODELS="[\"$PR_AGENT_MODEL\"]"
export GITHUB__USER_TOKEN="$GITHUB_PLACEHOLDER"

uvx --python "$PYTHON_VERSION" --with "httpx<0.28.0" pr-agent==0.3.0 --pr_url "$MR_URL" "$CMD"

echo "✅ ${CMD} terminé!"
