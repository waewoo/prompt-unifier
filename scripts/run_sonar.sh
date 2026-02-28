#!/usr/bin/env bash

set -e

echo "🔍 coverage.xml: $(ls -lh coverage.xml 2>/dev/null || echo 'absent')"

if [ ! -f .env ]; then
    echo "[ERROR] .env missing"
    exit 1
fi

set +e
docker run --rm \
    --user $(id -u):$(id -g) \
    --env-file .env \
    -v "$(pwd):/usr/src" \
    -w /usr/src \
    sonarsource/sonar-scanner-cli:latest \
    sonar-scanner -Dsonar.qualitygate.wait=true
SCAN_EXIT=$?
set -e

echo "  Scanner exit code: $SCAN_EXIT"
echo "📊 Metrics + Issues:"

if [ -f .env ]; then
    SONAR_TOKEN=$(grep 'SONAR_TOKEN=' .env | cut -d'=' -f2- | head -1 | sed 's/[[:space:]]//g' | tr -d '\r')
    SONAR_HOST=$(grep 'SONAR_HOST_URL=' .env | cut -d'=' -f2- | head -1 | sed 's/[[:space:]]//g' | tr -d '\r')
    SONAR_PROJECT="waewoo_prompt-unifier"
    echo "  Host: $SONAR_HOST"

    if command -v curl >/dev/null 2>&1 && command -v jq >/dev/null 2>&1 && [ -n "$SONAR_TOKEN" ] && [ -n "$SONAR_HOST" ]; then
        BUGS=$(curl -s -u "$SONAR_TOKEN:" \
            "$SONAR_HOST/api/measures/component?component=$SONAR_PROJECT&metricKeys=bugs" \
            | jq -r '.component.measures[0].value // "0"' 2>/dev/null || echo "0")
        SMELLS=$(curl -s -u "$SONAR_TOKEN:" \
            "$SONAR_HOST/api/measures/component?component=$SONAR_PROJECT&metricKeys=code_smells" \
            | jq -r '.component.measures[0].value // "0"' 2>/dev/null || echo "0")
        COV=$(curl -s -u "$SONAR_TOKEN:" \
            "$SONAR_HOST/api/measures/component?component=$SONAR_PROJECT&metricKeys=coverage" \
            | jq -r '.component.measures[0].value // "N/A"' 2>/dev/null || echo "N/A")

        echo "  Bugs: $BUGS | Smells: $SMELLS | Coverage: $COV%"

        if [ "$SMELLS" != "0" ]; then
            echo "  🚨 Code Smells:"
            curl -s -u "$SONAR_TOKEN:" \
                "$SONAR_HOST/api/issues/search?componentKeys=$SONAR_PROJECT&types=CODE_SMELL&resolved=false&ps=5" \
                | jq -r '.issues[]? | "  - " + (.component | ltrimstr("waewoo_prompt-unifier/")) + ":" + (.line | tostring) + " → " + .message' \
                2>/dev/null || echo "    (API error)"
        fi

        if [ "$BUGS" != "0" ]; then
            echo "  🐛 Bugs:"
            curl -s -u "$SONAR_TOKEN:" \
                "$SONAR_HOST/api/issues/search?componentKeys=$SONAR_PROJECT&types=BUG&resolved=false&ps=5" \
                | jq -r '.issues[]? | "  - " + (.component | ltrimstr("waewoo_prompt-unifier/")) + ":" + (.line | tostring) + " → " + .message' \
                2>/dev/null || echo "    (API error)"
        fi

        if [ "$SMELLS" = "0" ] && [ "$BUGS" = "0" ]; then
            echo "  🎉 Quality Gate PASSED!"
        else
            echo "  ⚠️  Quality Gate FAILED!"
        fi

        echo "  👉 $SONAR_HOST/dashboard?id=$SONAR_PROJECT"
    fi
fi

echo "[SUCCESS] $(date +%H:%M)"
exit $SCAN_EXIT
