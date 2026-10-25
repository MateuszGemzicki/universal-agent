# Skills

Create a directory per reusable workflow with `SKILL.md`: triggers, prerequisites, steps, validation, limitations and provenance. Propose revisions through a reviewed diff; do not silently modify a skill.

## External skill catalog

`skills-routing.yaml` routes the 15 local role prompts to reviewed, pinned snapshots. The 68 available third-party snapshots are vendored under `skills/external/` and installed in `C:\Users\mateu\.codex\skills`; the latest 20 are also available to Claude Code in `.claude/skills/`. This does not grant permissions or authorize commands. `insecure-defaults` was not installed because it no longer exists in the reviewed upstream revision.

Before importing an update, pin a full upstream commit, verify the file hash and licence, review its instructions and scripts, record the reviewer and expose only the minimum required tools. High-risk candidates (browser, CI/CD, infrastructure, security scanners and external-model workflows) require explicit human approval for each operational use. Read the licence notes in `SECURITY_REVIEW.md` before redistributing vendored copies.

## Snapshot integrity and updates

`python scripts/verify_skill_snapshots.py` verifies that every skill named in `skills-routing.yaml` has a matching vendored `SKILL.md` and SHA-256 in `skills/skill-lock.json`. CI runs the same command.

After reviewing an upstream update, update its pin and vendored files, then deliberately refresh the lock with `python scripts/verify_skill_snapshots.py --write-reviewed-lock`. Never use the refresh command as a substitute for source, licence, and script review.

See [SECURITY_REVIEW.md](SECURITY_REVIEW.md) for the assessed risks and [AGENT_SKILLS_CATALOG.md](AGENT_SKILLS_CATALOG.md) for the curated role map.

The latest 20-skill extension is documented in [INSTALL_REPORT_20.md](INSTALL_REPORT_20.md). For landing pages, dashboards, admin panels and SaaS UI, use [PREMIUM_FRONTEND.md](PREMIUM_FRONTEND.md).
