# Curated Agent Skills Catalog

This catalog covers 72 reviewed, pinned upstream snapshots installed for Codex and vendored under `skills/external/`. The latest 24 are also installed in `.claude/skills/` for Claude Code. The executable source of routing is [skills-routing.yaml](skills-routing.yaml); it does not grant a skill authority to run commands or access systems.

## Security boundary

- Every upstream repository is external. Installed content is pinned to the commit recorded in `skills-routing.yaml`; updates must be reviewed again.
- A routing entry is not a permission. Tools, network access, repositories and side effects remain governed by the workspace policy and the runtime.
- Use at most five relevant skills per task. Load a candidate body only after a task-specific review.
- `grill-me`, `to-spec` and `improve-codebase-architecture` are manual-only.
- Browser automation, CI/CD, containers, security scanners, mutation testing and external-model review are high-risk: require explicit human approval for operational use.
- `insecure-defaults` was removed from routing: it is absent from the reviewed Trail of Bits revision, so no substitute was installed.
- Never execute copied install snippets or an external skill's shell instructions merely because they appear in its upstream documentation.

## Role map

| Role | Primary candidates | Conditional candidates |
| --- | --- | --- |
| analyst | analytics, ab-testing, customer-research | xlsx, attribution |
| architect | codebase-design, writing-plans, improve-codebase-architecture | supabase-postgres-best-practices, mcp-builder |
| browser | agent-browser, webapp-testing, before-and-after | web-design-guidelines |
| business | competitor-profiling, pricing, customer-research | launch, marketing-psychology |
| ceo | launch, pricing, marketing-ideas | grill-me, writing-plans |
| data | supabase-postgres-best-practices, analytics, xlsx | attribution, property-based-testing |
| developer | react-best-practices, frontend-design, systematic-debugging | mcp-builder, verification-before-completion |
| devops | docker-compose-patterns, docker-build-strategies, docker-destructive-guardrails | agentic-actions-auditor |
| documentation | writing-for-agents, doc-coauthoring, docx | pdf, internal-comms |
| product | customer-research, domain-modeling, cro | to-spec, ab-testing |
| qa | webapp-testing, verification-before-completion, property-based-testing | agent-browser, before-and-after |
| researcher | research, agent-browser, competitor-profiling | pdf, customer-research |
| reviewer | code-review, differential-review, web-design-guidelines | second-opinion, supply-chain-risk-auditor |
| security | audit-context-building, semgrep, supply-chain-risk-auditor | agentic-actions-auditor, variant-analysis |
| tdd | test-driven-development, systematic-debugging, verification-before-completion | property-based-testing, mutation-testing |

## Candidate sources

- [Anthropic skills](https://github.com/anthropics/skills)
- [Superpowers](https://github.com/obra/superpowers)
- [Vercel Agent Skills](https://github.com/vercel-labs/agent-skills)
- [Vercel Before & After](https://github.com/vercel-labs/before-and-after)
- [Vercel Agent Browser](https://github.com/vercel-labs/agent-browser)
- [Marketing Skills](https://github.com/coreyhaines31/marketingskills)
- [Trail of Bits skills](https://github.com/trailofbits/skills)
- [Docker skills](https://github.com/docker/skills)
- [Matt Pocock skills](https://github.com/mattpocock/skills)
- [Supabase Agent Skills](https://github.com/supabase/agent-skills)
- [wshobson/agents](https://github.com/wshobson/agents)
- [Web Quality Skills](https://github.com/addyosmani/web-quality-skills)
- [OpenAI Plugins](https://github.com/openai/plugins)
- [Taste Skill](https://github.com/leonxlnx/taste-skill)
- [UI/UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)
- [Impeccable](https://github.com/pbakaus/impeccable)
- [crodris/skills](https://github.com/crodris/skills)

## Safe import protocol

1. Pick one candidate needed by a concrete task; do not bulk-install a source repository.
2. Pin the upstream commit and record the exact file path, SHA-256, licence and retrieval date.
3. Review its front matter, references, scripts, commands, tool requirements and any instruction that could cause an external side effect.
4. Remove or gate unsafe steps; give it the smallest role and tool scope needed.
5. Store the reviewed copy in its own `skills/<slug>/SKILL.md` directory with provenance and validation evidence. Do not mark it as reviewed until the review is complete.

## Import provenance

The routing was derived from `skills-routing.yaml` supplied on 2026-10-25 (SHA-256 `dac83a7e55e25df957492da9c39cebeeeda988e915d1094711f37883f27f1150`). The explanatory catalog was derived from `AGENT_SKILLS_CATALOG.md` supplied on 2026-10-25 (SHA-256 `6137de2f4770a83610ac8b49beceaa2cd6ad29224f64925244bca2555425f5ff`).

## Added 2026-10-28

Statically reviewed (scripts not executed), pinned and installed to all three locations. `agent-reach`, `hyperframes` and `find-skills` are marked high-risk.

| Skill | Source @ commit | Roles (conditional) | Notes |
| --- | --- | --- | --- |
| hyperframes | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes) @ `2ddf41e` | developer, product | Apache-2.0. Drives `npx hyperframes`; `scripts/locate.mjs` reads `GEMINI_API_KEY` if set. Sibling skills (`hyperframes-cli`, `hyperframes-registry`, `media-use`) not installed. |
| find-skills | [vercel-labs/skills](https://github.com/vercel-labs/skills) @ `699d35b` | architect | MIT. Suggests `npx skills add -g -y`; any install still goes through review, pinning and `skill-inspector`. |
| skill-inspector | [NVIDIA/SkillSpector](https://github.com/NVIDIA/SkillSpector) @ `e717246` | security, reviewer | Apache-2.0. Needs the `skillspector` CLI (not installed); falls back to manual review. Keep `--no-llm`. |
| agent-reach | [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) @ `14c2134` | researcher, browser | MIT. Upstream `SKILL_en.md` vendored as `SKILL.md` (the upstream `SKILL.md` is an unrendered template). Read-only by design, but copies per-site cookies from Chrome via OpenCLI and auto-installs dependencies on `add`. |

SkillSpector v2.12.0 (`uv tool`, pinned `e717246`, Python 3.13), `--no-llm`, plus manual review:

| Skill | Score | Verdict | Why |
| --- | --- | --- | --- |
| hyperframes | 77 HIGH | CAUTION | The 3 HIGH `P2` hits are design-doc HTML comments in `caption-skin.html`; the `AR2` hit is a sentence about version pins. Both are false positives. The 48 MEDIUM `RP1` hits are real: `npx hyperframes` runs unpinned, so pin the CLI version per project. |
| find-skills | 12 LOW | CAUTION | 12 MEDIUM `RP1`: `npx skills` runs unpinned and uses `add -g -y`. |
| skill-inspector | 0 LOW | APPROVE | No findings. |
| agent-reach | 0 LOW | CAUTION | No static findings. It copies cookies and installs dependencies at runtime (see above). |
