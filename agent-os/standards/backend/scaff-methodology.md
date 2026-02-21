# SCAFF Methodology

Quality standard for **prompt files** (not rule files — SCAFF is auto-disabled for `rules/`).

## Five Components (each 0–20 points, total 0–100)

| Component | What it checks |
|---|---|
| **S**pecific | Concrete requirements, measurable goals, numeric metrics |
| **C**ontextual | Background, audience, situation, problem statement |
| **A**ctionable | Action verbs, imperative bullet points, code blocks |
| **F**ormatted | Markdown structure, headings, lists, Format section |
| **F**ocused | Word count 100–800, single topic, ≤2 top-level headings |

## Mandatory Sections

A prompt must have all 5 sections (missing → component score capped at 10/20):

```markdown
### Situation
### Challenge
### Audience
### Format
### Foundations
```

## Scoring

- Pass threshold: **95/100** — hardcoded, not configurable
- Failures are **warnings only**, never errors (exit 0)
- Run with: `prompt-unifier validate` (SCAFF on by default)
- Disable with: `prompt-unifier validate --no-scaff`

## Tips for High Scores

- Use specific keywords: `must`, `should`, `require`, `at least`, `maximum`
- Include at least 3 action verbs as bullet points: `- Create X`, `- Set Y`
- Use numeric metrics: `100 characters`, `3 attempts`
- Add `### Format` section describing expected output format
- Quote `language: "python"` and use matching ` ```python ` code blocks
