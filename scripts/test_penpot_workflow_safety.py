"""Documentation contracts only; these do not intercept or execute Penpot writes."""
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = '.cline/skills/penpot-design/SKILL.md'
PROPOSAL = '.cline/skills/functionality-to-design/SKILL.md'
RULES = '.clinerules/design-workflow.md'
RUNBOOK = 'design/CONFORMANCE.md'


def text(path):
    return ' '.join((ROOT / path).read_text(encoding='utf-8').split())


class PenpotWorkflowSafetyTests(unittest.TestCase):
    def test_sync_requires_gate_before_artwork_writes(self):
        skill = text(SKILL)
        self.assertIn('Before writes, complete the native composition capability gate', skill)
        for path in (SKILL, RULES, RUNBOOK):
            with self.subTest(path=path):
                value = text(path)
                self.assertIn('before any artwork writes', value.lower())
                self.assertIn('ancestry', value)
                self.assertIn('Method existence is not', value)

    def test_forbids_copy_structure_mutation_and_implicit_fallbacks(self):
        for path in (SKILL, RULES, RUNBOOK):
            with self.subTest(path=path):
                value = text(path)
                self.assertIn('Never call `appendChild`', value)
                self.assertIn('insertChild', value)
                self.assertIn('inherited', value)
                self.assertRegex(value, r'reparent inherited descendants out of (?:a|their) copy')
                self.assertIn('trial writes', value)
                self.assertIn('fallback', value)

    def test_checks_destinations_before_instance_creation_and_handles_failures(self):
        for path in (SKILL, RULES, RUNBOOK):
            with self.subTest(path=path):
                value = text(path)
                self.assertIn('before creating', value)
                self.assertIn('IDs immediately', value)
                self.assertIn('partial failure', value)
                self.assertIn('fresh complete snapshot', value)
                self.assertIn('cleanup plan', value)
                self.assertIn('preservation', value)

    def test_preserves_scope_and_states_enforcement_limits(self):
        for path in (SKILL, RUNBOOK):
            with self.subTest(path=path):
                value = text(path)
                self.assertIn('before the baseline to evade preservation', value)
                self.assertIn('not an API interceptor', value)
                self.assertIn('nested', value.lower())
                self.assertIn('structurally immutable', value)
        self.assertIn('grants no new component family', text(RUNBOOK))

    def test_proposals_assess_feasibility_without_inventing_wrappers(self):
        value = text(PROPOSAL)
        self.assertIn('assess native rendering feasibility', value)
        self.assertIn('unverified, not supported', value)
        self.assertIn('API restrictions alone do not justify a generic custom wrapper', value)
        self.assertIn('explicit approval', value)
        self.assertIn('before any artwork writes', value)

    def test_ci_covers_safety_instruction_paths_for_push_and_pull_request(self):
        # No YAML dependency needed: inspect the two existing inline path lists.
        workflow = (ROOT / '.github/workflows/design-conformance.yml').read_text()
        filters = [line for line in workflow.splitlines() if line.strip().startswith('paths:')]
        self.assertEqual(2, len(filters))
        for line in filters:
            for path in ('.cline/skills/penpot-design/**',
                         '.cline/skills/functionality-to-design/**', RULES,
                         'design/**', 'scripts/**'):
                with self.subTest(filter=line, path=path):
                    self.assertIn("'" + path + "'", line)


if __name__ == '__main__':
    unittest.main()