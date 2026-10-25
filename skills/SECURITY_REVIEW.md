# Security review: external Agent Skills catalog

**Status:** 68 pinned snapshots were reviewed and installed without executing their code. Copies are in `skills/external/` and `C:\Users\mateu\.codex\skills`; the latest 20 are also in `.claude/skills/`. The requested candidate `insecure-defaults` is absent from the reviewed upstream revision and was not replaced.

## Scope and evidence

- `C:\Users\mateu\Downloads\skills-routing.yaml` — SHA-256 `dac83a7e55e25df957492da9c39cebeeeda988e915d1094711f37883f27f1150`.
- `C:\Users\mateu\Downloads\AGENT_SKILLS_CATALOG.md` — SHA-256 `6137de2f4770a83610ac8b49beceaa2cd6ad29224f64925244bca2555425f5ff`.
- Each installed `SKILL.md` hash matches the corresponding file retrieved from its pinned commit in `skills-routing.yaml` (48/48 in both locations).
- No instruction-hijacking pattern was found in the installed skill bodies. One heuristic alert was a security-audit example explaining why restrictive tool allowlists can be abused; it is not an instruction to bypass controls.
- The referenced public repositories were reachable during review. Reachability is not a trust, integrity or licence assessment of changing contents.

## Findings

| Severity | Finding | Treatment in this repository |
| --- | --- | --- |
| High | Upstream content can change or be compromised after review. | All installed copies are pinned to full commits and verified by `SKILL.md` hash; updates require a new review. |
| High | The supplied catalog contains `npx` install/discovery instructions, and several skills contain helper scripts. | No upstream script, package installer, test or browser action was executed during review or installation. Future execution needs task-specific authorization. |
| High | Skill text is untrusted instruction content and can attempt to trigger actions outside its task or tool scope. | A static instruction-hijacking scan found no actionable match; tool permissions remain runtime-enforced and high-risk use needs explicit approval. |
| Medium | Browser, CI/CD, Docker, scanners, mutation testing and external-model review can access data, consume resources or cause side effects. | Marked `high_risk`; operational use needs explicit human approval. |
| Medium | Marketing, research and launch workflows can cause external communication, compliance or reputation risk. | They remain advisory; no outreach, publishing or data collection is authorized by this catalog. |
| Low | Console rendering showed mojibake for Polish characters, while both supplied files decode as valid UTF-8. | Repository copies use UTF-8; review used byte hashes rather than rendered terminal text. |

## Licence observations (not legal advice)

- MIT: Superpowers, Marketing Skills, Matt Pocock and Supabase.
- Apache-2.0: selected Anthropic skills except `doc-coauthoring`, Agent Browser and Docker.
- CC BY-SA 4.0: Trail of Bits; redistribution needs attribution and share-alike handling.
- PolyForm Shield 1.0.0: Before & After; verify that the intended use is permitted before use or redistribution.
- No licence file was found in the reviewed Vercel Agent Skills revision or for Anthropic `doc-coauthoring`; do not redistribute those copies until permission or licensing is verified.

## Residual risk

Installation does not make an upstream skill safe. A reviewed, pinned copy can still contain unsafe or inaccurate instructions, and a safe skill can be used unsafely with overly broad tools. Apply least privilege and verify outcomes independently.
