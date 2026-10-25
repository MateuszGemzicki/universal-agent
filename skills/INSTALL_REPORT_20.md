# Installation report: 20 Agent Skills

All entries below were located as real `SKILL.md` files, statically reviewed without executing their scripts, pinned to the stated commit, then installed to `C:\Users\mateu\.codex\skills`, `skills/external/` and `.claude/skills/`.

| Skill | Source @ commit | Assigned roles | Status |
| --- | --- | --- | --- |
| typescript-advanced-types | wshobson/agents @ `0874a27` | developer | installed |
| api-design-principles | wshobson/agents @ `0874a27` | architect, developer | installed |
| nodejs-backend-patterns | wshobson/agents @ `0874a27` | developer | installed |
| using-git-worktrees | obra/superpowers @ `2ce8aa1` | developer, devops | installed |
| subagent-driven-development | obra/superpowers @ `2ce8aa1` | architect, developer | installed |
| vercel-composition-patterns | vercel-labs/agent-skills @ `063bee9` | developer | installed; upstream directory is `composition-patterns` |
| shadcn | openai/plugins @ `0722921` | developer | installed; current equivalent of the requested Vercel entry |
| tailwind-design-system | wshobson/agents @ `0874a27` | developer | installed |
| accessibility | addyosmani/web-quality-skills @ `afa8da9` | qa, reviewer | installed |
| performance | addyosmani/web-quality-skills @ `afa8da9` | developer, qa | installed |
| docker-project-foundations | docker/skills @ `179c9cf` | devops | installed |
| github-actions-templates | wshobson/agents @ `0874a27` | devops | installed |
| deployment-pipeline-design | wshobson/agents @ `0874a27` | devops, architect | installed |
| secrets-management | wshobson/agents @ `0874a27` | devops, security | installed |
| docker-sandboxes-lifecycle | docker/skills @ `179c9cf` | devops, security | installed |
| design-taste-frontend | leonxlnx/taste-skill @ `12af471` | developer, product | installed; upstream directory is `taste-skill` |
| ui-ux-pro-max | nextlevelbuilder/ui-ux-pro-max-skill @ `d14efff` | developer, product | installed |
| impeccable | pbakaus/impeccable @ `4fc2f83` | developer, reviewer, qa | installed |
| react-and-nextjs-data-visualization | openai/plugins @ `0722921` | developer, data | installed |
| frontend-design-pipeline | crodris/skills @ `52eca40` | developer, architect | installed |

## Safety and compatibility

- Routing exposes metadata first; it selects at most three skills and loads a full body only for a matching task.
- The bodies and included scripts were not executed during review or installation. Tool permissions and approvals remain authoritative.
- A static scan of all 20 installed skill directories found no instruction-hijacking pattern. The pinned `SKILL.md` hashes were checked in all three installation locations.
- `shadcn` and `react-and-nextjs-data-visualization` lack a plugin-local licence file in the reviewed snapshot; retain them for local use only until redistribution rights are confirmed.
- Claude Code discovers the workspace copies in `.claude/skills/`; Codex discovers the global copies. The committed `skills/external/` copies are the auditable, pinned source of this integration.
