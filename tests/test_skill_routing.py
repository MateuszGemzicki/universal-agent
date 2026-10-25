import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
NEW_SKILLS = {
    "typescript-advanced-types", "api-design-principles", "nodejs-backend-patterns",
    "using-git-worktrees", "subagent-driven-development", "vercel-composition-patterns",
    "shadcn", "tailwind-design-system", "accessibility", "performance",
    "docker-project-foundations", "github-actions-templates", "deployment-pipeline-design",
    "secrets-management", "docker-sandboxes-lifecycle", "design-taste-frontend",
    "ui-ux-pro-max", "impeccable", "react-and-nextjs-data-visualization",
    "frontend-design-pipeline",
}


class SkillRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.route = yaml.safe_load((ROOT / "skills" / "skills-routing.yaml").read_text("utf-8"))

    def test_new_skills_are_pinned_and_vendored(self):
        self.assertTrue(NEW_SKILLS <= set(self.route["skills"]))
        self.assertTrue(all(source["pinned_commit"] for source in self.route["sources"].values()))
        for skill in NEW_SKILLS:
            self.assertTrue((ROOT / "skills" / "external" / skill / "SKILL.md").is_file(), skill)
            self.assertTrue((ROOT / ".claude" / "skills" / skill / "SKILL.md").is_file(), skill)

    def test_role_references_and_progressive_disclosure_policy(self):
        known = set(self.route["skills"])
        for role, config in self.route["roles"].items():
            self.assertTrue((ROOT / config["prompt"]).is_file(), role)
            self.assertTrue(set(config["primary"] + config["conditional"]) <= known, role)
            self.assertLessEqual(len(config["primary"]), 3, role)
        self.assertEqual(3, self.route["policy"]["max_active_skills_per_task"])
        self.assertTrue(self.route["policy"]["load_skill_body_only_when_relevant"])

    def test_affected_role_prompts_point_to_their_routing_entry(self):
        for role in ("architect", "data", "developer", "devops", "product", "qa", "reviewer", "security"):
            prompt = (ROOT / self.route["roles"][role]["prompt"]).read_text("utf-8")
            self.assertIn(f"roles.{role}", prompt, role)

    def test_premium_frontend_requires_existing_qa_evidence(self):
        premium = self.route["premium_frontend"]
        self.assertTrue(set(premium["candidate_skills"]) <= set(self.route["skills"]))
        self.assertIn("existing QA and milestone evidence", premium["required_evidence"])


if __name__ == "__main__":
    unittest.main()
